from __future__ import annotations

from decimal import Decimal

from portfolio_intelligence.validation.replay import ReplayResult


def capital_productivity(result: ReplayResult, risk_consumed: Decimal) -> Decimal:
    if risk_consumed <= 0:
        return Decimal("0")
    return result.net_pnl / risk_consumed


def risk_productivity(expected_edge: Decimal, portfolio_risk_consumed: Decimal) -> Decimal:
    if portfolio_risk_consumed <= 0:
        return Decimal("0")
    return expected_edge / portfolio_risk_consumed


def decision_efficiency(correct_decisions: int, decisions_taken: int) -> Decimal:
    if decisions_taken <= 0:
        return Decimal("0")
    return Decimal(correct_decisions) / Decimal(decisions_taken)
