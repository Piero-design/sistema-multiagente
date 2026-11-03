"""Ollama local (solo 127.0.0.1)."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, parse, request

from dsar.assistant.llm.base import LLMError, LlmResult, Message, Timer, failure, prompt_hash

DEFAULT_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:3b"
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
HISTORY_TURNS = 4
OPTIONS = {"temperature": 0.1, "num_predict": 600, "num_ctx": 8192}
JSON_OPTIONS = {"temperature": 0, "num_predict": 300, "num_ctx": 4096}
DEFAULT_JSON_TIMEOUT = 90


def base_url() -> str:
    url = os.environ.get("OLLAMA_URL", DEFAULT_URL).rstrip("/")
    if parse.urlparse(url).hostname not in LOOPBACK_HOSTS:
        raise LLMError("OLLAMA_URL debe apuntar a 127.0.0.1: el modelo local no puede estar en otra maquina.")
    return url


def call(endpoint: str, payload: dict[str, Any] | None = None, timeout: int = 5) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(base_url() + endpoint, data=data, headers={"Content-Type": "application/json"})
    try:
        # La conexión local no debe pasar por un proxy corporativo.
        opener = request.build_opener(request.ProxyHandler({}))
        with opener.open(req, timeout=timeout) as response:
            return json.load(response)
    except (error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise LLMError(f"Ollama no respondió: {exc}") from exc


def available_models() -> list[str]:
    return [item["name"] for item in call("/api/tags").get("models", [])]


def build_messages(system: str, user: str, history: list[Message] | None) -> list[Message]:
    messages = [{"role": "system", "content": system}]
    for turn in (history or [])[-HISTORY_TURNS:]:
        if turn.get("role") in {"user", "assistant"}:
            messages.append({"role": turn["role"], "content": str(turn["content"])[:2000]})
    return messages + [{"role": "user", "content": user}]


class OllamaProvider:
    name = "ollama"
    label = "Ollama local"
    cloud = False

    @property
    def default_model(self) -> str:
        return os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)

    def complete(self, system: str, user: str, model: str | None = None,
                 history: list[Message] | None = None) -> LlmResult:
        model = model or self.default_model
        timer = Timer()
        try:
            response = call("/api/chat", {"model": model, "messages": build_messages(system, user, history),
                                          "stream": False, "options": OPTIONS, "keep_alive": "10m"}, timeout=180)
            text = response.get("message", {}).get("content", "").strip()
            if not text:
                raise LLMError("El modelo devolvió una respuesta vacía.")
        except LLMError as exc:
            raise failure(self.name, model, system, user, timer, exc) from exc
        return LlmResult(text=text, provider=self.name, model=model, prompt_sha256=prompt_hash(system, user),
                         at=timer.at, latency_s=timer.elapsed())

    def complete_json(self, system: str, user: str, schema: dict[str, Any], model: str | None = None) -> LlmResult:
        """Salida estructurada (`format` con esquema JSON), determinista y corta."""
        model = model or os.environ.get("DSAR_MAIL_MODEL") or self.default_model
        timer = Timer()
        try:
            response = call("/api/chat", {"model": model, "messages": build_messages(system, user, None),
                                          "stream": False, "format": schema, "options": JSON_OPTIONS,
                                          "keep_alive": "30m"}, timeout=json_timeout())
            text = response.get("message", {}).get("content", "").strip()
            if not text:
                raise LLMError("El modelo devolvió una respuesta vacía.")
        except LLMError as exc:
            raise failure(self.name, model, system, user, timer, exc) from exc
        return LlmResult(text=text, provider=self.name, model=model, prompt_sha256=prompt_hash(system, user),
                         at=timer.at, latency_s=timer.elapsed())


def json_timeout() -> int:
    value = os.environ.get("DSAR_MAIL_MODEL_TIMEOUT", "").strip()
    return int(value) if value.isdigit() and int(value) > 0 else DEFAULT_JSON_TIMEOUT
