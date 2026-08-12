from datetime import datetime, timezone
from decimal import Decimal

from portfolio_intelligence.config import Settings
from portfolio_intelligence.domain.models import DecisionAction, PortfolioSnapshot
from portfolio_intelligence.portfolio.arbiter import arbitrate
from portfolio_intelligence.portfolio.ranking import RankingInput, rank_candidates
from portfolio_intelligence.portfolio.what_if import simulate_what_if


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def portfolio(drawdown: str = "0.02") -> PortfolioSnapshot:
    return PortfolioSnapshot(portfolio_id="pf_fixture", timestamp=NOW, equity=Decimal("10000"), gross_exposure=Decimal("2500"), net_exposure=Decimal("500"), concentration=Decimal("0.25"), risk_budget=Decimal("0.01"), margin_headroom=Decimal("0.70"), drawdown=Decimal(drawdown))


def test_what_if_produces_four_stress_scenarios() -> None:
    result = simulate_what_if(portfolio(), "EGLDUSDT", Decimal("500"), Decimal("0.05"), Decimal("0.4"))
    assert len(result.impacts) == 4
    assert result.worst_case_drawdown >= result.impacts[0].projected_drawdown


def test_ranking_penalizes_correlation_and_risk() -> None:
    candidates = [
        RankingInput(candidate_id="egld", asset="EGLDUSDT", expected_edge=Decimal("0.018"), risk=Decimal("0.01"), correlation=Decimal("0.1"), liquidity_score=Decimal("0.9"), execution_quality=Decimal("0.8"), forecast_calibration=Decimal("0.75")),
        RankingInput(candidate_id="sol", asset="SOLUSDT", expected_edge=Decimal("0.020"), risk=Decimal("0.02"), correlation=Decimal("0.8"), liquidity_score=Decimal("0.6"), execution_quality=Decimal("0.6"), forecast_calibration=Decimal("0.60")),
    ]
    ranked = rank_candidates(candidates)
    assert ranked[0].candidate_id == "egld"
    assert ranked[0].rank == 1


def test_arbiter_rejects_when_drawdown_limit_already_reached() -> None:
    pf = portfolio(drawdown="0.11")
    simulation = simulate_what_if(pf, "EGLDUSDT", Decimal("500"), Decimal("0.05"), Decimal("0.4"))
    decision = arbitrate("opp_1", pf, simulation, Decimal("0.02"), Decimal("0.8"), Settings(), NOW)
    assert decision.decision == DecisionAction.REJECT
    assert decision.approved_size == Decimal("0")


def test_arbiter_waits_on_low_confidence() -> None:
    pf = portfolio()
    simulation = simulate_what_if(pf, "EGLDUSDT", Decimal("500"), Decimal("0.05"), Decimal("0.4"))
    decision = arbitrate("opp_2", pf, simulation, Decimal("0.02"), Decimal("0.40"), Settings(), NOW)
    assert decision.decision == DecisionAction.WAIT
    assert decision.approved_size == Decimal("0")


def test_arbiter_reduces_size_on_stress_breach() -> None:
    pf = portfolio()
    simulation = simulate_what_if(pf, "EGLDUSDT", Decimal("9000"), Decimal("0.30"), Decimal("0.9"))
    decision = arbitrate("opp_3", pf, simulation, Decimal("0.02"), Decimal("0.80"), Settings(), NOW)
    assert decision.decision == DecisionAction.REDUCE_SIZE
    assert decision.approved_size < simulation.candidate_size
