from datetime import datetime, timezone

from portfolio_intelligence.controls.circuit_breaker import BreakerScope, CircuitBreaker
from portfolio_intelligence.controls.system_status import ProviderStatus, SystemStatus, execution_allowed_for_status


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def test_unknown_provider_status_fails_closed() -> None:
    status = SystemStatus(provider="bybit", status=ProviderStatus.UNKNOWN)
    assert execution_allowed_for_status(status) is False


def test_maintenance_and_incident_block_execution() -> None:
    for provider_status in (ProviderStatus.MAINTENANCE, ProviderStatus.INCIDENT):
        status = SystemStatus(provider="bybit", status=provider_status)
        assert execution_allowed_for_status(status) is False


def test_circuit_breaker_trips_and_resets() -> None:
    breaker = CircuitBreaker()
    operational = SystemStatus(provider="bybit", status=ProviderStatus.OPERATIONAL)
    assert breaker.execution_allowed(operational) is True
    state = breaker.trip("reconciliation break", BreakerScope.SYMBOL, NOW)
    assert state.active is True
    assert breaker.execution_allowed(operational) is False
    reset = breaker.reset(NOW)
    assert reset.active is False
    assert breaker.execution_allowed(operational) is True
