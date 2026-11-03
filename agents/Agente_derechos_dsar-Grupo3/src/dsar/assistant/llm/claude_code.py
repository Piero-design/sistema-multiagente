"""Claude por la CLI de Claude Code, sin herramientas y en un directorio temporal vacío."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from typing import Any

from dsar.assistant.llm.base import LLMError, LlmResult, Message, Timer, failure, prompt_hash

DEFAULT_MODEL = "claude-haiku-5-5"
TIMEOUT = 120


def result_event(data: Any) -> dict[str, Any]:
    if isinstance(data, list):
        return next((item for item in reversed(data) if isinstance(item, dict) and item.get("type") == "result"), {})
    return data if isinstance(data, dict) else {}


def command(system: str, model: str) -> list[str]:
    # Sin herramientas, MCP ni comandos: Claude solo redacta con lo que recibe.
    return ["claude", "-p", "--model", model, "--output-format", "json", "--system-prompt", system,
            "--tools", "", "--strict-mcp-config", "--no-session-persistence", "--disable-slash-commands"]


def run(system: str, user: str, model: str) -> subprocess.CompletedProcess[str]:
    # Directorio vacío: Claude Code no puede leer los datos sintéticos del proyecto.
    with tempfile.TemporaryDirectory(prefix="dsar-claude-") as workdir:
        try:
            return subprocess.run(command(system, model), input=user, capture_output=True, text=True,
                                  encoding="utf-8", timeout=TIMEOUT, cwd=workdir, check=False)
        except FileNotFoundError as exc:
            raise LLMError("Claude Code no está instalado en este equipo (comando 'claude').") from exc
        except subprocess.TimeoutExpired as exc:
            raise LLMError("Claude Code no respondió a tiempo.") from exc


def parse_output(completed: subprocess.CompletedProcess[str]) -> tuple[str, dict[str, Any]]:
    if completed.returncode != 0:
        raise LLMError(f"Claude Code terminó con error: {completed.stderr.strip()[:300]}")
    try:
        data = result_event(json.loads(completed.stdout))
        text = str(data.get("result", "")).strip()
    except ValueError:
        data, text = {}, completed.stdout.strip()
    if not text:
        raise LLMError("Claude Code devolvió una respuesta vacía.")
    return text, data


class ClaudeCodeProvider:
    name = "claude_code"
    label = "Claude Code (pruebas)"
    cloud = True

    @property
    def default_model(self) -> str:
        return os.environ.get("CLAUDE_CODE_MODEL", DEFAULT_MODEL)

    def complete(self, system: str, user: str, model: str | None = None,
                 history: list[Message] | None = None) -> LlmResult:
        model = model or self.default_model
        timer = Timer()
        try:
            text, data = parse_output(run(system, user, model))
        except LLMError as exc:
            raise failure(self.name, model, system, user, timer, exc) from exc
        used = ", ".join(sorted((data.get("modelUsage") or {}).keys())) or None
        cost = round(float(data["total_cost_usd"]), 6) if data.get("total_cost_usd") is not None else None
        return LlmResult(text=text, provider=self.name, model=used or model, prompt_sha256=prompt_hash(system, user),
                         at=timer.at, latency_s=timer.elapsed(), model_requested=model if used else None,
                         cost_usd=cost)
