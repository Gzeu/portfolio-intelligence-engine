from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from portfolio_intelligence.domain.models import PortfolioSnapshot, StrictModel


class StressScenario(StrEnum):
    BASE = "BASE"
    VOLATILITY_2X = "VOLATILITY_2X"
    CORRELATION_1 = "CORRELATION_1"
    LIQUIDITY_50PCT = "LIQUIDITY_50PCT"


class ScenarioImpact(StrictModel):
    scenario: StressScenario
    projected_drawdown: Decimal = Field(ge=0, le=1)
    margin_impact: Decimal = Field(ge=0, le=1)
    liquidity_impact: Decimal = Field(ge=0, le=1)


class SimulationResult(StrictModel):
    portfolio_id: str
    candidate_asset: str
    candidate_size: Decimal = Field(ge=0)
    impacts: tuple[ScenarioImpact, ...]
    worst_case_drawdown: Decimal = Field(ge=0, le=1)


def _candidate_weight(portfolio: PortfolioSnapshot, candidate_size: Decimal) -> Decimal:
    total = portfolio.equity if portfolio.equity > 0 else Decimal("1")
    return min(Decimal("1"), candidate_size / total)


def simulate_what_if(portfolio: PortfolioSnapshot, candidate_asset: str, candidate_size: Decimal, candidate_volatility: Decimal, correlation_to_portfolio: Decimal) -> SimulationResult:
    if candidate_size < 0:
        raise ValueError("candidate_size must be non-negative")
    weight = _candidate_weight(portfolio, candidate_size)
    base_drawdown = portfolio.drawdown + weight * candidate_volatility
    impacts = [
        ScenarioImpact(scenario=StressScenario.BASE, projected_drawdown=min(Decimal("1"), base_drawdown), margin_impact=min(Decimal("1"), Decimal("1") - portfolio.margin_headroom + weight * Decimal("0.05")), liquidity_impact=min(Decimal("1"), weight * Decimal("0.10"))),
        ScenarioImpact(scenario=StressScenario.VOLATILITY_2X, projected_drawdown=min(Decimal("1"), base_drawdown + weight * candidate_volatility), margin_impact=min(Decimal("1"), Decimal("1") - portfolio.margin_headroom + weight * Decimal("0.10")), liquidity_impact=min(Decimal("1"), weight * Decimal("0.20"))),
        ScenarioImpact(scenario=StressScenario.CORRELATION_1, projected_drawdown=min(Decimal("1"), base_drawdown + weight * max(correlation_to_portfolio, Decimal("0.5")) * portfolio.concentration), margin_impact=min(Decimal("1"), Decimal("1") - portfolio.margin_headroom + weight * Decimal("0.07")), liquidity_impact=min(Decimal("1"), weight * Decimal("0.15"))),
        ScenarioImpact(scenario=StressScenario.LIQUIDITY_50PCT, projected_drawdown=min(Decimal("1"), base_drawdown + weight * Decimal("0.05")), margin_impact=min(Decimal("1"), Decimal("1") - portfolio.margin_headroom + weight * Decimal("0.08")), liquidity_impact=min(Decimal("1"), weight * Decimal("0.35"))),
    ]
    worst_case = max(impact.projected_drawdown for impact in impacts)
    return SimulationResult(portfolio_id=portfolio.portfolio_id, candidate_asset=candidate_asset, candidate_size=candidate_size, impacts=tuple(impacts), worst_case_drawdown=worst_case)
