from datetime import datetime, timedelta, timezone
from decimal import Decimal

from portfolio_intelligence.config import Settings
from portfolio_intelligence.decision_memory.attribution import AttributionLabel, attribute_error
from portfolio_intelligence.decision_memory.calibration import CalibrationBucketObservation, build_calibration_record
from portfolio_intelligence.decision_memory.case import DecisionCase, Outcome, OutcomeExit, close_case
from portfolio_intelligence.domain.models import DecisionAction, MarketState, PortfolioSnapshot
from portfolio_intelligence.execution.planner import create_execution_plan
from portfolio_intelligence.execution.position import PositionStatus, close_position, open_position
from portfolio_intelligence.forecast.engine import ForecastHorizon, build_forecast
from portfolio_intelligence.forecast.scenarios import ScenarioKind, build_scenario_tree
from portfolio_intelligence.market_intelligence.features import compute_features
from portfolio_intelligence.market_intelligence.regime import classify_regime
from portfolio_intelligence.market_intelligence.scanner import scan_opportunity
from portfolio_intelligence.portfolio.arbiter import arbitrate
from portfolio_intelligence.portfolio.what_if import simulate_what_if


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def test_full_pipeline_from_market_state_to_calibrated_decision_case() -> None:
    settings = Settings()

    market_state = MarketState(asset="EGLDUSDT", timestamp=NOW, price=Decimal("14.5"), bid=Decimal("14.49"), ask=Decimal("14.51"), spread_bps=Decimal("13.79"), volume=Decimal("1000000"), volatility=Decimal("0.018"), liquidity_state="healthy")
    features = compute_features(market_state, previous_close=Decimal("14.0"))
    regime = classify_regime(features, timeframe="15m")

    opportunity = scan_opportunity(features, regime)
    assert opportunity is not None

    forecast = build_forecast(opportunity, features, ForecastHorizon.M15, NOW + timedelta(minutes=15))
    scenario_tree = build_scenario_tree(forecast)
    assert any(node.kind == ScenarioKind.INVALIDATION for node in scenario_tree)

    portfolio = PortfolioSnapshot(portfolio_id="pf_e2e", timestamp=NOW, equity=Decimal("10000"), gross_exposure=Decimal("2000"), net_exposure=Decimal("500"), concentration=Decimal("0.2"), risk_budget=Decimal("0.01"), margin_headroom=Decimal("0.75"), drawdown=Decimal("0.02"))
    candidate_size = Decimal("300")
    simulation = simulate_what_if(portfolio, opportunity.asset, candidate_size, market_state.volatility, correlation_to_portfolio=Decimal("0.3"))

    decision = arbitrate(opportunity.opportunity_id, portfolio, simulation, forecast.expected_return, forecast.confidence_declared, settings, NOW)
    assert decision.decision in (DecisionAction.APPROVE, DecisionAction.REDUCE_SIZE)

    plan = create_execution_plan(decision, opportunity.asset, opportunity.side.value, market_state.price, market_state.volatility, features.liquidity_score, portfolio.equity, NOW)
    assert plan.size == decision.approved_size

    position = open_position("pos_e2e", opportunity.asset, opportunity.side.value, plan.size, market_state.price)
    assert position.status == PositionStatus.OPEN
    closed_position = close_position(position, market_state.price + Decimal("0.30"))
    assert closed_position.status == PositionStatus.CLOSED

    case = DecisionCase(case_id=f"case_{opportunity.opportunity_id}", opportunity_id=opportunity.opportunity_id, forecast_id=forecast.forecast_id, decision_id=decision.decision_id, asset=opportunity.asset, horizon=forecast.horizon, confidence_declared=forecast.confidence_declared, predicted_direction="up" if opportunity.side.value == "LONG" else "down", created_at=NOW)
    outcome = Outcome(realized_pnl=closed_position.realized_pnl, mae=Decimal("0.10"), mfe=Decimal("0.35"), fees=closed_position.fees, slippage_bps=plan.costs.slippage_bps, exit_reason=OutcomeExit.TAKE_PROFIT, closed_at=NOW + timedelta(minutes=15))
    closed_case = close_case(case, outcome)

    attribution = attribute_error(closed_case, actual_direction="up", entry_slippage_bps=8, execution_slippage_bps=plan.costs.slippage_bps, risk_budget_used=decision.risk_consumed)
    assert attribution.forecast == AttributionLabel.CORRECT

    calibration = build_calibration_record(opportunity.asset, forecast.horizon, [CalibrationBucketObservation(declared_confidence=forecast.confidence_declared, was_correct=True)])
    assert calibration.sample_count == 1


def test_wait_decision_never_reaches_execution_plan() -> None:
    settings = Settings()
    market_state = MarketState(asset="EGLDUSDT", timestamp=NOW, price=Decimal("14.5"), bid=Decimal("14.49"), ask=Decimal("14.51"), spread_bps=Decimal("13.79"), volume=Decimal("1000000"), volatility=Decimal("0.018"), liquidity_state="healthy")
    features = compute_features(market_state, previous_close=Decimal("14.49"))
    portfolio = PortfolioSnapshot(portfolio_id="pf_wait", timestamp=NOW, equity=Decimal("10000"), gross_exposure=Decimal("2000"), net_exposure=Decimal("500"), concentration=Decimal("0.2"), risk_budget=Decimal("0.01"), margin_headroom=Decimal("0.75"), drawdown=Decimal("0.02"))
    simulation = simulate_what_if(portfolio, "EGLDUSDT", Decimal("300"), market_state.volatility, Decimal("0.3"))
    low_confidence_decision = arbitrate("opp_wait", portfolio, simulation, Decimal("0.01"), Decimal("0.30"), settings, NOW)
    assert low_confidence_decision.decision == DecisionAction.WAIT
    try:
        create_execution_plan(low_confidence_decision, "EGLDUSDT", "LONG", market_state.price, market_state.volatility, features.liquidity_score, portfolio.equity, NOW)
        raised = False
    except ValueError:
        raised = True
    assert raised
