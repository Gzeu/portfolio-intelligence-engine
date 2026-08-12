from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from portfolio_intelligence.domain.models import StrictModel


class EventEnvelope(StrictModel):
    event_id: str
    event_type: str
    schema_version: str = "1.0"
    occurred_at: datetime
    aggregate_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    source: str
    correlation_id: str | None = None


EVENT_TYPES = frozenset(
    {
        "account.state.updated",
        "market.state.updated",
        "regime.updated",
        "opportunity.created",
        "forecast.created",
        "capital.decision.created",
        "execution.order.updated",
        "position.updated",
        "outcome.closed",
        "calibration.updated",
        "incident.created",
    }
)


def validate_event_type(event: EventEnvelope) -> EventEnvelope:
    if event.event_type not in EVENT_TYPES:
        raise ValueError(f"unsupported event type: {event.event_type}")
    return event
