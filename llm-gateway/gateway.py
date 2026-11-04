"""Shared LLM gateway: OpenAI-compatible and Ollama-compatible surface, with one Gemini key PER TEAM.

LLM_MODE = cloud | ollama | mock. Agents are redirected here by env vars only.
Each agent calls its own prefix (/g1/..., /g2/..., /g8/...), and the gateway uses THAT team's key
(LLM_API_KEY_G1..G8) and, optionally, its own model (LLM_MODEL_G1..G8). This keeps every team inside its own
quota instead of saturating one shared key. Without a team key the call fails with a clear message, unless the
development switch LLM_ALLOW_SHARED_FALLBACK=true lets it use the shared LLM_API_KEY.
Bodies and API keys are never logged and never returned.
"""
import asyncio
import hashlib
import hmac
import json
import logging
import os
import time

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

MODE = os.getenv("LLM_MODE", "cloud").lower()
BASE = os.getenv("LLM_BASE_URL", "").rstrip("/")
SHARED_KEY = os.getenv("LLM_API_KEY", "")
ALLOW_FALLBACK = os.getenv("LLM_ALLOW_SHARED_FALLBACK", "false").lower() == "true"
MODEL = os.getenv("LLM_MODEL", "")
EMBED_MODEL = os.getenv("LLM_EMBED_MODEL", "")
TIMEOUT = float(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))
sem = asyncio.Semaphore(int(os.getenv("LLM_MAX_CONCURRENCY", "4")))
AGENTS = [f"g{i}" for i in range(1, 9)]

if MODE == "ollama" and not BASE:
    BASE = "http://ollama:11434"

logging.basicConfig(level=logging.INFO, format="%(asctime)s gateway %(message)s")
log = logging.getLogger("gateway")
app = FastAPI(title="LLM Gateway")


def _blank():
    return {"requests": 0, "errors": 0, "latency_ms_total": 0.0, "last_latency_ms": None,
            "last_error": None, "prompt_tokens": 0, "completion_tokens": 0, "last_call_at": None}


stats = {a: _blank() for a in AGENTS + ["shared"]}


# Keys that teams set themselves from the web (stored in a volume, mode 600, never returned by any endpoint).
KEYS_FILE = os.getenv("TEAM_KEYS_FILE", "/data/team_keys.json")
ADMIN_TOKEN = os.getenv("GATEWAY_ADMIN_TOKEN", "")
_stored: dict = {"mtime": None, "keys": {}}


def _stored_keys() -> dict:
    try:
        m = os.stat(KEYS_FILE).st_mtime
    except OSError:
        return {}
    if _stored["mtime"] != m:
        try:
            _stored["keys"] = json.load(open(KEYS_FILE, encoding="utf-8"))
            _stored["mtime"] = m
        except (OSError, ValueError):
            return {}
    return _stored["keys"]


def _save_keys(keys: dict) -> None:
    os.makedirs(os.path.dirname(KEYS_FILE) or ".", exist_ok=True)
    tmp = KEYS_FILE + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(keys, f)
    os.replace(tmp, KEYS_FILE)
    _stored["mtime"] = None


def key_source(agent: str) -> str:
    if _stored_keys().get(agent):
        return "web"
    if os.getenv(f"LLM_API_KEY_{agent.upper()}", "").strip():
        return "env"
    return ""


def team_key(agent: str) -> str:
    own = _stored_keys().get(agent) or os.getenv(f"LLM_API_KEY_{agent.upper()}", "").strip()
    if own:
        return own
    return SHARED_KEY if ALLOW_FALLBACK else ""


def team_model(agent: str, requested=None) -> str:
    return os.getenv(f"LLM_MODEL_{agent.upper()}", "").strip() or MODEL or requested


def team_embed_model(agent: str, requested=None) -> str:
    return os.getenv(f"LLM_EMBED_MODEL_{agent.upper()}", "").strip() or EMBED_MODEL or requested


def _agent(req: Request) -> str:
    a = req.path_params.get("agent", "shared")
    if a == "openai":          # "/openai/v1/..." (groq-sdk layout) is the shared surface, not a team named "openai"
        return "shared"
    if a != "shared" and a not in AGENTS:
        raise HTTPException(404, "unknown team")
    return a


def _need_key(agent: str) -> str:
    key = team_key(agent) if agent != "shared" else (SHARED_KEY or next((team_key(a) for a in AGENTS if team_key(a)), ""))
    if MODE == "cloud" and not key:
        raise PermissionError(f"missing key for {agent}: set LLM_API_KEY_{agent.upper()}")
    return key


def _oa_base() -> str:
    """OpenAI-compatible base URL of the active backend."""
    return f"{BASE}/v1" if MODE == "ollama" else BASE


async def _post(path: str, payload: dict, key: str, retry_429: bool = False) -> dict:
    last = None
    headers = {"Authorization": f"Bearer {key}"} if key and MODE == "cloud" else {}
    for attempt in range(RETRIES + 1 + (4 if retry_429 else 0)):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as c:
                r = await c.post(f"{_oa_base()}{path}", json=payload, headers=headers)
            if r.status_code == 429 and retry_429 and attempt < RETRIES + 4:
                await asyncio.sleep(15)          # quota window of THIS team's key: wait it out
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


def _track(agent, t0, usage=None, err=None):
    st = stats[agent]
    ms = (time.time() - t0) * 1000
    st["requests"] += 1
    st["latency_ms_total"] += ms
    st["last_latency_ms"] = round(ms)
    st["last_call_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if usage:
        st["prompt_tokens"] += usage.get("prompt_tokens", 0) or 0
        st["completion_tokens"] += usage.get("completion_tokens", 0) or 0
    if err:
        st["errors"] += 1
        st["last_error"] = type(err).__name__
    log.info("team=%s mode=%s ms=%d ok=%s", agent, MODE, ms, err is None)


# ---- Gemini 3 thought signatures (tool calls) ----
_sigs: dict = {}   # tool_call id -> provider extra_content
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


# ---- embeddings: provider-safe batches and a per-team per-minute budget ----
EMBED_BATCH = int(os.getenv("LLM_EMBED_BATCH", "100"))   # Gemini rejects >100 inputs per request
EMBED_ITEMS_PER_MIN = int(os.getenv("LLM_EMBED_ITEMS_PER_MIN", "80"))
_embed_window: dict = {}   # agent -> [(timestamp, items)]


async def _embed_throttle(agent: str, n: int) -> None:
    """Sliding 60 s window per team (each team has its own quota): wait until n more items fit."""
    win = _embed_window.setdefault(agent, [])
    while True:
        now = time.time()
        win[:] = [(t, k) for t, k in win if now - t < 60]
        if sum(k for _, k in win) + n <= EMBED_ITEMS_PER_MIN:
            win.append((now, n))
            return
        await asyncio.sleep(2)


async def _embed(agent: str, model, inputs: list, key: str, extra: dict | None = None) -> dict:
    data: list = []
    last = {}
    for i in range(0, len(inputs), EMBED_BATCH):
        chunk = inputs[i:i + EMBED_BATCH]
        body = {**(extra or {}), "model": model, "input": chunk}
        await _embed_throttle(agent, len(chunk))
        last = await _post("/embeddings", body, key, retry_429=True)
        for d in last["data"]:
            data.append({**d, "index": i + d.get("index", 0)})
    return {**last, "data": data}


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


async def _chat(agent: str, payload: dict) -> dict:
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
                key = _need_key(agent)
                payload = {**payload, "model": team_model(agent if agent != "shared" else "g8", payload.get("model"))}
                payload = {k: v for k, v in payload.items() if v is not None}
                if GEMINI and payload.get("messages"):
                    payload["messages"] = _restore_signatures(payload["messages"])
                out = await _post("/chat/completions", payload, key)
                if GEMINI:
                    _remember_signatures(out)
        _track(agent, t0, out.get("usage"))
        return out
    except Exception as e:  # noqa: BLE001
        _track(agent, t0, err=e)
        raise


def _err(e: Exception):
    if isinstance(e, PermissionError):
        return JSONResponse({"error": {"message": str(e), "code": "missing_team_key"}}, status_code=401)
    return JSONResponse({"error": {"message": f"gateway upstream error: {type(e).__name__}"}}, status_code=502)


def _both(method, path):
    """Register a route for the shared surface and for each team prefix (/g1/..., /g2/...)."""
    def deco(fn):
        getattr(app, method)(path)(fn)
        getattr(app, method)("/{agent}" + path)(fn)
        return fn
    return deco


# ---------------------------------------------------------------- status
@app.get("/health")
async def health():
    return {"ok": True, "mode": MODE, "model": MODEL or None, "embed_model": EMBED_MODEL or None,
            "simulated": MODE == "mock", "data_leaves_machine": MODE == "cloud"}


@app.get("/teams")
async def teams():
    """Which teams have their own key (never the key itself) and what each has used."""
    out = {}
    for a in AGENTS:
        s = stats[a]
        own = bool(key_source(a))
        out[a] = {"own_key": own, "key_source": key_source(a) or None, "usable": own or (ALLOW_FALLBACK and bool(SHARED_KEY)) or MODE != "cloud",
                  "model": team_model(a), "requests": s["requests"], "errors": s["errors"],
                  "prompt_tokens": s["prompt_tokens"], "completion_tokens": s["completion_tokens"],
                  "last_latency_ms": s["last_latency_ms"], "last_error": s["last_error"], "last_call_at": s["last_call_at"]}
    return {"mode": MODE, "shared_fallback": ALLOW_FALLBACK, "teams": out}


@app.get("/metrics")
async def metrics():
    tot = _blank()
    for s in stats.values():
        for k in ("requests", "errors", "latency_ms_total", "prompt_tokens", "completion_tokens"):
            tot[k] += s[k]
        if s["last_call_at"] and (tot["last_call_at"] or "") < s["last_call_at"]:
            tot["last_call_at"], tot["last_latency_ms"], tot["last_error"] = s["last_call_at"], s["last_latency_ms"], s["last_error"]
    n = tot["requests"] or 1
    return {**tot, "avg_latency_ms": round(tot["latency_ms_total"] / n), "mode": MODE, "model": MODEL or None}


@app.get("/probe")
async def probe(team: str = ""):
    """Real round trip to the backend with a team's key (default: the first team that has one)."""
    agent = team if team in AGENTS else next((a for a in AGENTS if team_key(a)), "shared")
    try:
        out = await _chat(agent, {"messages": [{"role": "user", "content": "ping"}], "max_tokens": 5})
        return {"ok": True, "mode": MODE, "team": agent, "latency_ms": stats[agent]["last_latency_ms"],
                "simulated": MODE == "mock", "model": out.get("model")}
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"ok": False, "mode": MODE, "team": agent, "error": type(e).__name__}, status_code=502)


# ---------------------------------------------------------------- OpenAI-compatible
@_both("post", "/v1/chat/completions")
async def oa_chat(req: Request):
    try:
        return await _chat(_agent(req), await req.json())
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        return _err(e)


@app.post("/{agent}/openai/v1/chat/completions")   # groq-sdk base-URL layout (Group 8)
@app.post("/openai/v1/chat/completions")
async def oa_chat_groq(req: Request):
    return await oa_chat(req)


@_both("post", "/v1/embeddings")
async def oa_embed(req: Request):
    agent = _agent(req)
    body = await req.json()
    t0 = time.time()
    try:
        inp = body.get("input", [])
        inp = [inp] if isinstance(inp, str) else inp
        if MODE == "mock":
            data = [{"object": "embedding", "index": i, "embedding": _mock_vec(t)} for i, t in enumerate(inp)]
            _track(agent, t0)
            return {"object": "list", "data": data, "model": "mock"}
        key = _need_key(agent)
        extra = {k: v for k, v in body.items() if k not in ("model", "input")}
        async with sem:
            out = await _embed(agent, team_embed_model(agent, body.get("model")), inp, key, extra)
        _track(agent, t0)
        return out
    except Exception as e:  # noqa: BLE001
        _track(agent, t0, err=e)
        return _err(e)


@_both("get", "/v1/models")
async def oa_models(req: Request):
    _agent(req)
    return {"object": "list", "data": [{"id": MODEL or "mock", "object": "model"}]}


# ---------------------------------------------------------------- Ollama-compatible
@_both("get", "/api/tags")
async def tags(req: Request):
    _agent(req)
    names = [m for m in (MODEL, EMBED_MODEL) if m] or ["mock"]
    return {"models": [{"name": n, "model": n} for n in names]}


@_both("post", "/api/chat")
async def api_chat(req: Request):
    agent = _agent(req)
    body = await req.json()
    try:
        out = await _chat(agent, {"messages": body.get("messages", []), "model": body.get("model"),
                                  "temperature": (body.get("options") or {}).get("temperature")})
        msg = out["choices"][0]["message"]
        return {"model": out.get("model"),
                "message": {"role": "assistant", "content": msg.get("content") or ""},
                "done": True, "eval_count": (out.get("usage") or {}).get("completion_tokens", 0)}
    except Exception as e:  # noqa: BLE001
        return _err(e)


@_both("post", "/api/generate")
async def api_generate(req: Request):
    agent = _agent(req)
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
        out = await _chat(agent, payload)
        usage = out.get("usage") or {}
        return {"model": out.get("model"),
                "response": out["choices"][0]["message"].get("content") or "",
                "done": True, "eval_count": usage.get("completion_tokens", 0),
                "prompt_eval_count": usage.get("prompt_tokens", 0)}
    except Exception as e:  # noqa: BLE001
        return _err(e)


@_both("post", "/api/embed")
async def api_embed(req: Request):
    agent = _agent(req)
    body = await req.json()
    inp = body.get("input", [])
    inp = [inp] if isinstance(inp, str) else inp
    t0 = time.time()
    try:
        if MODE == "mock":
            _track(agent, t0)
            return {"model": "mock", "embeddings": [_mock_vec(t) for t in inp]}
        key = _need_key(agent)
        async with sem:
            out = await _embed(agent, team_embed_model(agent, body.get("model")), inp, key)
        _track(agent, t0)
        return {"model": out.get("model"), "embeddings": [d["embedding"] for d in out["data"]]}
    except Exception as e:  # noqa: BLE001
        _track(agent, t0, err=e)
        return _err(e)


# ---------------------------------------------------------------- team key administration (backend only)
def _admin(req: Request) -> None:
    tok = req.headers.get("x-admin-token", "")
    if not ADMIN_TOKEN or not hmac.compare_digest(tok, ADMIN_TOKEN):
        raise HTTPException(401, "admin token required")


async def _key_works(key: str) -> bool:
    """Cheap real check against the provider (lists models); the key is never logged."""
    if MODE != "cloud":
        return True
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"{_oa_base()}/models", headers={"Authorization": f"Bearer {key}"})
        return r.status_code == 200
    except Exception:  # noqa: BLE001
        return False


@app.put("/teams/{agent}/key")
async def set_team_key(agent: str, req: Request):
    _admin(req)
    if agent not in AGENTS:
        raise HTTPException(404, "unknown team")
    key = str((await req.json()).get("key", "")).strip()
    if len(key) < 20 or any(c.isspace() for c in key):
        return JSONResponse({"ok": False, "error": "La clave no tiene el formato de una clave de API."}, status_code=400)
    if not await _key_works(key):
        return JSONResponse({"ok": False, "error": "El proveedor rechazó la clave: revisa que esté completa y activa."}, status_code=400)
    keys = dict(_stored_keys())
    keys[agent] = key
    _save_keys(keys)
    log.info("team=%s key set from web", agent)
    return {"ok": True, "team": agent, "key_source": "web"}


@app.delete("/teams/{agent}/key")
async def delete_team_key(agent: str, req: Request):
    _admin(req)
    if agent not in AGENTS:
        raise HTTPException(404, "unknown team")
    keys = dict(_stored_keys())
    keys.pop(agent, None)
    _save_keys(keys)
    log.info("team=%s web key removed", agent)
    return {"ok": True, "team": agent, "key_source": key_source(agent) or None}
