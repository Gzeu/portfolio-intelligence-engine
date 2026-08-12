from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class TransportError(RuntimeError):
    pass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        if self.max_attempts <= 0 or self.timeout_seconds <= 0:
            raise ValueError("retry attempts and timeout must be positive")


class ReadOnlyTransport(Protocol):
    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]: ...


class ReplayTransport:
    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        self.responses = dict(responses)
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = dict(params or {})
        self.calls.append((path, normalized))
        if path not in self.responses:
            raise TransportError(f"no replay fixture for {path}")
        return self.responses[path]
