"""Common integration contract. Implemented by adapters, never by the original agents."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

# Statuses reported to the dashboard
OPERATIVO, DEGRADADO, CAIDO, PARCIAL, FUERA_DE_ALCANCE = (
    "operativo", "degradado", "caido", "parcial", "fuera_de_alcance")


class ExecutionRequest(dict):
    """{'action': str, 'input': dict}"""


class AgentAdapter(ABC):
    id: str = ""
    group: int = 0
    name: str = ""
    responsibility: str = ""
    route: str = ""

    def get_info(self) -> dict[str, Any]:
        return {"id": self.id, "group": self.group, "name": self.name,
                "responsibility": self.responsibility, "route": self.route}

    @abstractmethod
    def get_capabilities(self) -> list[dict[str, Any]]:
        """Only capabilities that really exist: [{'action', 'description', 'input'}]."""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """{'status': operativo|degradado|caido|parcial|fuera_de_alcance, 'reason': str|None, 'detail': {}}"""

    @abstractmethod
    async def execute(self, request: ExecutionRequest) -> dict[str, Any]:
        """Runs the native operation and returns a normalized result:
        {'output': Any, 'native_status': int|None, 'simulated': bool}.
        Raises on failure; the orchestrator records the error and isolates it."""

    # get_status / get_result / get_history are provided by the orchestrator (persisted in PostgreSQL).
