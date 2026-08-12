from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from portfolio_intelligence.domain.models import MarketState, Opportunity, Side
from portfolio_intelligence.forecast.engine import ForecastHorizon, build_forecast, build_multi_horizon_forecasts
from portfolio_intelligence.forecast.scenarios import ScenarioKind, build_scenario_tree, validate_point_in_time
from portfolio_intelligence.market_intelligence.features import compute_features


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def test_forecast_has_distribution_that_sums_to_one() -> None:
    state = MarketState(asset="EGLDUSDT", timestamp=NOW, price=Decimal("14.5"), bid=Decimal("14.49"), ask=Decimal("14.51"), spread_bps=Decimal("13.79"), volume=Decimal("1000000"), volatility=Decimal("0.018"), liquidity_state="healthy")
    features = compute_features(state, Decimal("14.0"))
    opportunity = Opportunity(opportunity_id="opp_1", asset="EGLDUSDT", side=Side.LONG, detected_at=NOW, setup_type="breakout", timeframe="15m", status="DETECTED", expiry=NOW + timedelta(minutes=15))
    forecast = build_forecast(opportunity, features, ForecastHorizon.M15, NOW + timedelta(minutes=15))
    assert sum(forecast.distribution.values()) == Decimal("1")
    assert all(Decimal("0") <= value <= Decimal("1") for value in forecast.distribution.values())


def test_multi_horizon_forecast_is_explicitly_versioned() -> None:
    state = MarketState(asset="EGLDUSDT", timestamp=NOW, price=Decimal("14.5"), bid=Decimal("14.49"), ask=Decimal("14.51"), spread_bps=Decimal("13.79"), volume=Decimal("1000000"), volatility=Decimal("0.018"), liquidity_state="healthy")
    features = compute_features(state, Decimal("14.0"))
    opportunity = Opportunity(opportunity_id="opp_2", asset="EGLDUSDT", side=Side.LONG, detected_at=NOW, setup_type="breakout", timeframe="15m", status="DETECTED", expiry=NOW + timedelta(minutes=15))
    forecasts = build_multi_horizon_forecasts(opportunity, features, {h: NOW + timedelta(minutes=15) for h in ForecastHorizon})
    assert {forecast.horizon for forecast in forecasts} == {h.value for h in ForecastHorizon}
    assert all(forecast.model_version == "baseline-distribution-v1" for forecast in forecasts)


def test_scenario_tree_contains_invalidation() -> None:
    state = MarketState(asset="EGLDUSDT", timestamp=NOW, price=Decimal("14.5"), bid=Decimal("14.49"), ask=Decimal("14.51"), spread_bps=Decimal("13.79"), volume=Decimal("1000000"), volatility=Decimal("0.018"), liquidity_state="healthy")
    features = compute_features(state, Decimal("14.0"))
    opportunity = Opportunity(opportunity_id="opp_3", asset="EGLDUSDT", side=Side.LONG, detected_at=NOW, setup_type="breakout", timeframe="15m", status="DETECTED", expiry=NOW + timedelta(minutes=15))
    forecast = build_forecast(opportunity, features, ForecastHorizon.M15, NOW + timedelta(minutes=15))
    tree = build_scenario_tree(forecast)
    assert any(node.kind == ScenarioKind.PRIMARY for node in tree)
    assert any(node.kind == ScenarioKind.IF for node in tree)
    assert any(node.kind == ScenarioKind.INVALIDATION for node in tree)


def test_point_in_time_guard_rejects_future_feature_timestamp() -> None:
    state = MarketState(asset="EGLDUSDT", timestamp=NOW, price=Decimal("14.5"), bid=Decimal("14.49"), ask=Decimal("14.51"), spread_bps=Decimal("13.79"), volume=Decimal("1000000"), volatility=Decimal("0.018"), liquidity_state="healthy")
    features = compute_features(state, Decimal("14.0"))
    opportunity = Opportunity(opportunity_id="opp_4", asset="EGLDUSDT", side=Side.LONG, detected_at=NOW, setup_type="breakout", timeframe="15m", status="DETECTED", expiry=NOW + timedelta(minutes=15))
    forecast = build_forecast(opportunity, features, ForecastHorizon.M15, NOW + timedelta(minutes=15))
    with pytest.raises(ValueError):
        validate_point_in_time(forecast, NOW + timedelta(seconds=1))
