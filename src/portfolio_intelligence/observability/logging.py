from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from portfolio_intelligence.hardening.audit import deterministic_json
from portfolio_intelligence.hardening.incidents import redact_secrets


class LogSeverity(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def structured_log(severity: LogSeverity, message: str, component: str, event_id: str | None = None, correlation_id: str | None = None, **fields: Any) -> str:
    payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "severity": severity.value, "message": message, "component": component, "event_id": event_id, "correlation_id": correlation_id, "fields": redact_secrets(fields)}
    return deterministic_json(payload)
