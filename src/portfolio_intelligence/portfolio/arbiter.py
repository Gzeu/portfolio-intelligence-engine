from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from portfolio_intelligence.config import Settings
from portfolio_intelligence.domain.models import CapitalDecision, DecisionAction, PortfolioSnapshot
from portfolio_intelligence.portfolio.what_if import SimulationResult


def arbitrate(
    candidate_id: str,
    portfolio: PortfolioSnapshot,
    simulation: SimulationResult,
    expected_edge: Decimal,
    confidence: Decimal,
    settings: Settings,
    now: datetime,
) -> CapitalDecision:
    reasons: list[str] = []
    decision = DecisionAction.APPROVE
    approved_size = simulation.candidate_size

    if portfolio.drawdown >= settings.max_portfolio_drawdown:
        decision = DecisionAction.REJECT
        reasons.append("portfolio drawdown limit already reached")
    elif simulation.worst_case_drawdown > settings.max_portfolio_drawdown:
        decision = DecisionAction.REDUCE_SIZE
        approved_size = approved_size * Decimal("0.5")
        reasons.append("worst-case stress drawdown exceeds limit at full size")
    elif confidence < Decimal("0.55"):
        decision = DecisionAction.WAIT
        approved_size = Decimal("0")
        reasons.append("forecast confidence below actionable threshold")
    elif expected_edge <= 0:
        decision = DecisionAction.REJECT
        approved_size = Decimal("0")
        reasons.append("expected edge is non-positive")
    else:
        reasons.append("edge, risk, and stress scenarios within configured limits")

    risk_consumed = min(Decimal("1"), simulation.worst_case_drawdown)
    if decision == DecisionAction.REJECT or decision == DecisionAction.WAIT:
        risk_consumed = Decimal("0")

    return CapitalDecision(
        decision_id=f"cd_{candidate_id}",
        candidate_id=candidate_id,
        decision=decision,
        approved_size=max(Decimal("0"), approved_size),
        risk_consumed=risk_consumed,
        reasons=tuple(reasons),
        created_at=now,
        expires_at=now + timedelta(minutes=5),
    )
