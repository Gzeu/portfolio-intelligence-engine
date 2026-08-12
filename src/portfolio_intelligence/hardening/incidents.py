from __future__ import annotations

from enum import StrEnum
from typing import Any

from portfolio_intelligence.domain.models import StrictModel


class IncidentSeverity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(StrEnum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class Incident(StrictModel):
    incident_id: str
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.OPEN
    code: str
    message: str
    metadata: dict[str, Any] = {}


def redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: ("[REDACTED]" if any(token in key.lower() for token in ("secret", "password", "token", "api_key")) else redact_secrets(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    return value
