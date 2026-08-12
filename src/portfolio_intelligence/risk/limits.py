from __future__ import annotations

from portfolio_intelligence.config import Settings
from portfolio_intelligence.domain.models import AccountState, CapitalDecision, DecisionAction, PortfolioSnapshot


class RiskViolation(ValueError):
    """Raised when a proposed action violates a hard safety limit."""


def validate_capital_decision(
    decision: CapitalDecision,
    account: AccountState,
    portfolio: PortfolioSnapshot,
    settings: Settings,
) -> None:
    if decision.decision == DecisionAction.APPROVE and decision.approved_size <= 0:
        raise RiskViolation("approved decision must have positive size")
    if decision.risk_consumed > settings.max_position_risk:
        raise RiskViolation("position risk exceeds configured maximum")
    if portfolio.drawdown >= settings.max_portfolio_drawdown:
        raise RiskViolation("portfolio drawdown limit reached")
    if account.leverage > settings.max_leverage:
        raise RiskViolation("account leverage exceeds configured maximum")
    if decision.expires_at <= decision.created_at:
        raise RiskViolation("decision must expire after creation")


def assert_live_orders_allowed(settings: Settings) -> None:
    if not settings.can_submit_live_orders():
        raise RiskViolation("live order submission is disabled")
