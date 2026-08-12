from datetime import datetime, timezone
from decimal import Decimal

from portfolio_intelligence.domain.models import MarketState, RegimeLabel
from portfolio_intelligence.market_intelligence.features import compute_features
from portfolio_intelligence.market_intelligence.regime import classify_regime
from portfolio_intelligence.market_intelligence.scanner import scan_opportunity


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def market(*, price: str = "14.50", bid: str = "14.49", ask: str = "14.51", volatility: str = "0.018", volume: str = "1250000", spread: str = "13.79") -> MarketState:
    return MarketState(asset="EGLDUSDT", timestamp=NOW, price=Decimal(price), bid=Decimal(bid), ask=Decimal(ask), spread_bps=Decimal(spread), volume=Decimal(volume), volatility=Decimal(volatility), liquidity_state="healthy")


def test_features_are_deterministic_and_normalized() -> None:
    features = compute_features(market(), Decimal("14.00"))
    assert features.mid_price == Decimal("14.50")
    assert features.return_pct > 0
    assert Decimal("0") <= features.liquidity_score <= Decimal("1")


def test_high_positive_return_is_trend() -> None:
    features = compute_features(market(), Decimal("13.50"))
    regime = classify_regime(features, "15m")
    assert regime.label == RegimeLabel.TREND
    assert regime.probabilities[RegimeLabel.TREND.value] == Decimal("1")


def test_high_volatility_is_stress() -> None:
    features = compute_features(market(volatility="0.12"), Decimal("14.00"))
    regime = classify_regime(features, "5m")
    assert regime.label == RegimeLabel.STRESS
    assert scan_opportunity(features, regime) is None


def test_directional_candidate_is_created_without_execution() -> None:
    features = compute_features(market(), Decimal("14.00"))
    regime = classify_regime(features, "15m")
    opportunity = scan_opportunity(features, regime)
    assert opportunity is not None
    assert opportunity.status == "DETECTED"
    assert opportunity.asset == "EGLDUSDT"
