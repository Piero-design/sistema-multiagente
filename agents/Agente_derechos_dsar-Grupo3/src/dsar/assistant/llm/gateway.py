"""Gateway LLM de la plataforma multiagente (API compatible con OpenAI).

Se trata como un proveedor en la nube: según la configuración de la plataforma puede reenviar a Gemini,
así que solo recibe hechos minimizados y sin historial. Se activa con DSAR_GATEWAY_URL.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request

from dsar.assistant.llm.base import LLMError, LlmResult, Message, Timer, failure, prompt_hash

DEFAULT_MODEL = "plataforma"   # el gateway usa el modelo que tenga configurado
OPTIONS = {"temperature": 0.1, "max_tokens": 800}
TIMEOUT = 120


def base_url() -> str:
    return os.environ.get("DSAR_GATEWAY_URL", "").strip().rstrip("/")


def parse_response(data: dict[str, Any]) -> str:
    choice = (data.get("choices") or [{}])[0]
    if choice.get("finish_reason") == "length":
        raise LLMError("El gateway cortó la respuesta por el límite de tokens; no se muestra un texto incompleto.")
    text = str((choice.get("message") or {}).get("content") or "").strip()
    if not text:
        raise LLMError("El gateway devolvió una respuesta vacía.")
    return text


def post(model: str, system: str, user: str) -> dict[str, Any]:
    url = base_url()
    if not url:
        raise LLMError("Falta DSAR_GATEWAY_URL: el gateway de la plataforma no está configurado.")
    body = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            **OPTIONS}
    req = request.Request(url + "/chat/completions", data=json.dumps(body).encode("utf-8"),
                          headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=TIMEOUT) as response:
            return json.load(response)
    except (error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise LLMError(f"El gateway no respondió: {exc}") from exc


class GatewayProvider:
    name = "gateway"
    label = "Gateway de la plataforma (puede usar la nube)"
    cloud = True

    @property
    def default_model(self) -> str:
        return os.environ.get("DSAR_GATEWAY_MODEL", DEFAULT_MODEL)

    def complete(self, system: str, user: str, model: str | None = None,
                 history: list[Message] | None = None) -> LlmResult:
        # Sin historial, como cualquier proveedor en la nube.
        model = model or self.default_model
        timer = Timer()
        try:
            data = post(model, system, user)
            text = parse_response(data)
        except LLMError as exc:
            raise failure(self.name, model, system, user, timer, exc) from exc
        return LlmResult(text=text, provider=self.name, model=str(data.get("model") or model),
                         prompt_sha256=prompt_hash(system, user), at=timer.at, latency_s=timer.elapsed(),
                         model_requested=model)
