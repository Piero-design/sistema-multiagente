"""Shared LLM gateway: OpenAI-compatible and Ollama-compatible surface.

LLM_MODE = cloud | ollama | mock. Agents are redirected here by env vars only.
Bodies and API keys are never logged.
"""
import asyncio
import hashlib
import logging
import os
import time

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

MODE = os.getenv("LLM_MODE", "cloud").lower()
BASE = os.getenv("LLM_BASE_URL", "").rstrip("/")
KEY = os.getenv("LLM_API_KEY", "")
MODEL = os.getenv("LLM_MODEL", "")
EMBED_MODEL = os.getenv("LLM_EMBED_MODEL", "")
TIMEOUT = float(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))
sem = asyncio.Semaphore(int(os.getenv("LLM_MAX_CONCURRENCY", "4")))

if MODE == "ollama" and not BASE:
    BASE = "http://ollama:11434"

logging.basicConfig(level=logging.INFO, format="%(asctime)s gateway %(message)s")
log = logging.getLogger("gateway")
app = FastAPI(title="LLM Gateway")
stats = {"requests": 0, "errors": 0, "latency_ms_total": 0.0, "last_latency_ms": None,
         "last_error": None, "prompt_tokens": 0, "completion_tokens": 0, "last_call_at": None}


def _oa_base() -> str:
    """OpenAI-compatible base URL of the active backend."""
    return f"{BASE}/v1" if MODE == "ollama" else BASE


def _headers() -> dict:
    return {"Authorization": f"Bearer {KEY}"} if KEY and MODE == "cloud" else {}


def _model(requested):
    # Agents ask for their own default names; the gateway enforces the configured one.
    return MODEL or requested


async def _post(path: str, payload: dict, retry_429: bool = False) -> dict:
    last = None
    for attempt in range(RETRIES + 1 + (4 if retry_429 else 0)):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as c:
                r = await c.post(f"{_oa_base()}{path}", json=payload, headers=_headers())
            if r.status_code == 429 and retry_429 and attempt < RETRIES + 4:
                await asyncio.sleep(15)          # quota window: wait it out
                continue
            if r.status_code in (429, 500, 502, 503) and attempt < RETRIES:
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < RETRIES:
                await asyncio.sleep(1.5 * (attempt + 1))
    raise last


def _track(t0, usage=None, err=None):
    ms = (time.time() - t0) * 1000
    stats["requests"] += 1
    stats["latency_ms_total"] += ms
    stats["last_latency_ms"] = round(ms)
    stats["last_call_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if usage:
        stats["prompt_tokens"] += usage.get("prompt_tokens", 0) or 0
        stats["completion_tokens"] += usage.get("completion_tokens", 0) or 0
    if err:
        stats["errors"] += 1
        stats["last_error"] = type(err).__name__
    log.info("mode=%s ms=%d ok=%s", MODE, ms, err is None)


EMBED_BATCH = int(os.getenv("LLM_EMBED_BATCH", "100"))   # Gemini rejects >100 inputs per request


EMBED_ITEMS_PER_MIN = int(os.getenv("LLM_EMBED_ITEMS_PER_MIN", "80"))   # provider quota guard (free tiers)
_embed_window: list = []   # (timestamp, items)


async def _embed_throttle(n: int) -> None:
    """Sliding 60 s window: wait until n more items fit under the per-minute budget."""
    while True:
        now = time.time()
        _embed_window[:] = [(t, k) for t, k in _embed_window if now - t < 60]
        if sum(k for _, k in _embed_window) + n <= EMBED_ITEMS_PER_MIN:
            _embed_window.append((now, n))
            return
        await asyncio.sleep(2)


async def _embed(model: str | None, inputs: list, extra: dict | None = None) -> dict:
    """Embeddings in provider-safe batches; returns an OpenAI-style {'data': [...]} in input order."""
    data: list = []
    last = {}
    for i in range(0, len(inputs), EMBED_BATCH):
        chunk = inputs[i:i + EMBED_BATCH]
        body = {**(extra or {}), "model": model, "input": chunk}
        await _embed_throttle(len(chunk))
        last = await _post("/embeddings", body, retry_429=True)
        for d in last["data"]:
            data.append({**d, "index": i + d.get("index", 0)})
    return {**last, "data": data}


_sigs: dict = {}   # tool_call id -> provider extra_content (Gemini "thought_signature")
GEMINI = "generativelanguage.googleapis.com" in BASE
_SKIP_SIG = {"google": {"thought_signature": "skip_thought_signature_validator"}}


def _restore_signatures(messages: list) -> list:
    """Gemini 3 requires the thought_signature of each tool call to come back in the next turn.
    OpenAI-style clients (LangChain/n8n) drop it, so the gateway remembers it and re-attaches it."""
    for m in messages or []:
        for tc in (m.get("tool_calls") or []) if m.get("role") == "assistant" else []:
            if not tc.get("extra_content"):
                tc["extra_content"] = _sigs.get(tc.get("id")) or _SKIP_SIG
    return messages


def _remember_signatures(out: dict) -> None:
    for ch in out.get("choices", []):
        for tc in (ch.get("message") or {}).get("tool_calls") or []:
            if tc.get("id") and tc.get("extra_content"):
                _sigs[tc["id"]] = tc["extra_content"]
                if len(_sigs) > 2000:
                    _sigs.pop(next(iter(_sigs)))


def _mock_text(messages) -> str:
    last = ""
    for m in messages or []:
        if m.get("role") == "user":
            last = str(m.get("content", ""))
    digest = hashlib.sha256(last.encode()).hexdigest()[:8]
    return f"[RESPUESTA SIMULADA - modo mock, no es salida de un modelo real] eco={digest}"


def _mock_vec(text: str, dim: int = 64):
    h = hashlib.sha256(text.encode()).digest()
    return [(h[i % 32] / 255.0) - 0.5 for i in range(dim)]


async def _chat(payload: dict) -> dict:
    """Core call, returns an OpenAI chat.completion dict."""
    t0 = time.time()
    try:
        async with sem:
            if MODE == "mock":
                text = _mock_text(payload.get("messages"))
                out = {"id": "mock", "object": "chat.completion", "model": "mock",
                       "choices": [{"index": 0, "finish_reason": "stop",
                                    "message": {"role": "assistant", "content": text}}],
                       "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}
            else:
                payload = {**payload, "model": _model(payload.get("model"))}
                payload = {k: v for k, v in payload.items() if v is not None}
                if GEMINI and payload.get("messages"):
                    payload["messages"] = _restore_signatures(payload["messages"])
                out = await _post("/chat/completions", payload)
                if GEMINI:
                    _remember_signatures(out)
        _track(t0, out.get("usage"))
        return out
    except Exception as e:  # noqa: BLE001
        _track(t0, err=e)
        raise


def _err(e: Exception):
    return JSONResponse({"error": {"message": f"gateway upstream error: {type(e).__name__}"}},
                        status_code=502)


@app.get("/health")
async def health():
    return {"ok": True, "mode": MODE, "model": MODEL or None, "embed_model": EMBED_MODEL or None,
            "simulated": MODE == "mock", "data_leaves_machine": MODE == "cloud"}


@app.get("/metrics")
async def metrics():
    n = stats["requests"] or 1
    return {**stats, "avg_latency_ms": round(stats["latency_ms_total"] / n), "mode": MODE,
            "model": MODEL or None}


@app.get("/probe")
async def probe():
    """Real round trip to the backend (used by the dashboard)."""
    try:
        out = await _chat({"messages": [{"role": "user", "content": "ping"}], "max_tokens": 5})
        return {"ok": True, "mode": MODE, "latency_ms": stats["last_latency_ms"],
                "simulated": MODE == "mock", "model": out.get("model")}
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"ok": False, "mode": MODE, "error": type(e).__name__}, status_code=502)


# ---- OpenAI-compatible ----
@app.post("/v1/chat/completions")
@app.post("/openai/v1/chat/completions")  # groq-sdk base-URL layout (Group 8)
async def oa_chat(req: Request):
    try:
        return await _chat(await req.json())
    except Exception as e:  # noqa: BLE001
        return _err(e)


@app.post("/v1/embeddings")
async def oa_embed(req: Request):
    body = await req.json()
    t0 = time.time()
    try:
        if MODE == "mock":
            inp = body.get("input", [])
            inp = [inp] if isinstance(inp, str) else inp
            data = [{"object": "embedding", "index": i, "embedding": _mock_vec(t)}
                    for i, t in enumerate(inp)]
            _track(t0)
            return {"object": "list", "data": data, "model": "mock"}
        inp = body.get("input", [])
        inp = [inp] if isinstance(inp, str) else inp
        extra = {k: v for k, v in body.items() if k not in ("model", "input")}
        async with sem:
            out = await _embed(EMBED_MODEL or body.get("model"), inp, extra)
        _track(t0)
        return out
    except Exception as e:  # noqa: BLE001
        _track(t0, err=e)
        return _err(e)


@app.get("/v1/models")
async def oa_models():
    return {"object": "list", "data": [{"id": MODEL or "mock", "object": "model"}]}


# ---- Ollama-compatible ----
@app.get("/api/tags")
async def tags():
    names = [m for m in (MODEL, EMBED_MODEL) if m] or ["mock"]
    return {"models": [{"name": n, "model": n} for n in names]}


@app.post("/api/chat")
async def api_chat(req: Request):
    body = await req.json()
    try:
        out = await _chat({"messages": body.get("messages", []), "model": body.get("model"),
                           "temperature": (body.get("options") or {}).get("temperature")})
        msg = out["choices"][0]["message"]
        return {"model": out.get("model"),
                "message": {"role": "assistant", "content": msg.get("content") or ""},
                "done": True, "eval_count": (out.get("usage") or {}).get("completion_tokens", 0)}
    except Exception as e:  # noqa: BLE001
        return _err(e)


@app.post("/api/generate")
async def api_generate(req: Request):
    body = await req.json()
    msgs = []
    if body.get("system"):
        msgs.append({"role": "system", "content": body["system"]})
    msgs.append({"role": "user", "content": body.get("prompt", "")})
    payload = {"messages": msgs, "model": body.get("model")}
    opts = body.get("options") or {}
    if "temperature" in opts:
        payload["temperature"] = opts["temperature"]
    if opts.get("num_predict"):
        payload["max_tokens"] = opts["num_predict"]
    if body.get("format") == "json":
        payload["response_format"] = {"type": "json_object"}
    try:
        out = await _chat(payload)
        usage = out.get("usage") or {}
        return {"model": out.get("model"),
                "response": out["choices"][0]["message"].get("content") or "",
                "done": True, "eval_count": usage.get("completion_tokens", 0),
                "prompt_eval_count": usage.get("prompt_tokens", 0)}
    except Exception as e:  # noqa: BLE001
        return _err(e)


@app.post("/api/embed")
async def api_embed(req: Request):
    body = await req.json()
    inp = body.get("input", [])
    inp = [inp] if isinstance(inp, str) else inp
    t0 = time.time()
    try:
        if MODE == "mock":
            _track(t0)
            return {"model": "mock", "embeddings": [_mock_vec(t) for t in inp]}
        async with sem:
            out = await _embed(EMBED_MODEL or body.get("model"), inp)
        _track(t0)
        return {"model": out.get("model"), "embeddings": [d["embedding"] for d in out["data"]]}
    except Exception as e:  # noqa: BLE001
        _track(t0, err=e)
        return _err(e)
