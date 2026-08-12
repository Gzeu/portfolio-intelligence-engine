from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class MetricsRegistry:
    counters: dict[str, int] = field(default_factory=dict)
    latency_ms: dict[str, list[Decimal]] = field(default_factory=dict)
    gauges: dict[str, Decimal] = field(default_factory=dict)

    def increment(self, name: str, value: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + value

    def observe_latency(self, name: str, value_ms: Decimal) -> None:
        if value_ms < 0:
            raise ValueError("latency cannot be negative")
        self.latency_ms.setdefault(name, []).append(value_ms)

    def set_gauge(self, name: str, value: Decimal) -> None:
        self.gauges[name] = value

    def snapshot(self) -> dict[str, object]:
        return {"counters": dict(self.counters), "latency_ms": {key: tuple(values) for key, values in self.latency_ms.items()}, "gauges": dict(self.gauges)}
