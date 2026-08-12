from __future__ import annotations

from enum import StrEnum

from portfolio_intelligence.domain.models import StrictModel


class ProviderStatus(StrEnum):
    OPERATIONAL = "OPERATIONAL"
    MAINTENANCE = "MAINTENANCE"
    INCIDENT = "INCIDENT"
    UNKNOWN = "UNKNOWN"


class SystemStatus(StrictModel):
    provider: str
    status: ProviderStatus
    status_id: str | None = None
    details: str = ""


def execution_allowed_for_status(status: SystemStatus) -> bool:
    return status.status == ProviderStatus.OPERATIONAL
