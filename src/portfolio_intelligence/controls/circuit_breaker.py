from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from portfolio_intelligence.domain.models import StrictModel
from portfolio_intelligence.controls.system_status import SystemStatus, execution_allowed_for_status


class BreakerScope(StrEnum):
    ACCOUNT = "ACCOUNT"
    SYMBOL = "SYMBOL"
    GLOBAL = "GLOBAL"


class CircuitBreakerState(StrictModel):
    active: bool = False
    scope: BreakerScope = BreakerScope.GLOBAL
    reason: str = ""
    tripped_at: datetime | None = None
    reset_at: datetime | None = None


class CircuitBreaker:
    def __init__(self) -> None:
        self._state = CircuitBreakerState()

    @property
    def state(self) -> CircuitBreakerState:
        return self._state

    def trip(self, reason: str, scope: BreakerScope = BreakerScope.GLOBAL, now: datetime | None = None) -> CircuitBreakerState:
        self._state = CircuitBreakerState(active=True, scope=scope, reason=reason, tripped_at=now or datetime.now(timezone.utc))
        return self._state

    def reset(self, now: datetime | None = None) -> CircuitBreakerState:
        if not self._state.active:
            return self._state
        self._state = self._state.model_copy(update={"active": False, "reset_at": now or datetime.now(timezone.utc)})
        return self._state

    def execution_allowed(self, provider_status: SystemStatus) -> bool:
        return not self._state.active and execution_allowed_for_status(provider_status)
