from __future__ import annotations

from portfolio_intelligence.config import Settings
from portfolio_intelligence.exchange.bybit import BybitProvider
from portfolio_intelligence.domain.models import StrictModel


class ReadinessCheck(StrictModel):
    name: str
    passed: bool
    reason: str


class ReadinessReport(StrictModel):
    ready: bool
    checks: tuple[ReadinessCheck, ...]


def build_readiness_report(settings: Settings, provider: BybitProvider) -> ReadinessReport:
    checks = (
        ReadinessCheck(name="runtime_mode", passed=settings.runtime_mode.value in {"analysis", "paper", "shadow"}, reason="live mode is not allowed during readiness"),
        ReadinessCheck(name="provider", passed=provider.name == "bybit" and provider.api_version == "v5", reason="Bybit V5 provider boundary is configured"),
        ReadinessCheck(name="testnet", passed=provider.settings.environment.value == "testnet", reason="provider must target Bybit testnet"),
        ReadinessCheck(name="read_only", passed=provider.settings.read_only, reason="provider must remain read-only"),
        ReadinessCheck(name="live_orders", passed=not provider.settings.live_orders_enabled, reason="live orders must remain disabled"),
        ReadinessCheck(name="risk_limits", passed=settings.max_position_risk > 0 and settings.max_portfolio_drawdown > 0, reason="risk limits must be configured"),
    )
    return ReadinessReport(ready=all(check.passed for check in checks), checks=checks)
