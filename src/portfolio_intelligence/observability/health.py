from __future__ import annotations

from portfolio_intelligence.domain.models import StrictModel


class HealthStatus(StrictModel):
    component: str
    healthy: bool
    details: str


class AggregateHealth(StrictModel):
    healthy: bool
    statuses: tuple[HealthStatus, ...]


def aggregate_health(statuses: list[HealthStatus]) -> AggregateHealth:
    return AggregateHealth(healthy=bool(statuses) and all(status.healthy for status in statuses), statuses=tuple(statuses))
