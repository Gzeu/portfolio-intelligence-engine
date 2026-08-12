from __future__ import annotations

from decimal import Decimal

from portfolio_intelligence.domain.models import MarketRegime, RegimeLabel
from portfolio_intelligence.market_intelligence.features import MarketFeatures


def classify_regime(features: MarketFeatures, timeframe: str, model_version: str = "deterministic-v1") -> MarketRegime:
    stress = min(Decimal("1"), features.volatility / Decimal("0.10"))
    if stress >= Decimal("0.80") or features.liquidity_score < Decimal("0.25"):
        label = RegimeLabel.STRESS
    elif abs(features.directional_bias) >= Decimal("0.35"):
        label = RegimeLabel.TREND
    elif features.volatility < Decimal("0.01"):
        label = RegimeLabel.RANGE
    else:
        label = RegimeLabel.REVERSAL
    trend_strength = min(Decimal("1"), abs(features.directional_bias))
    probabilities = {name.value: Decimal("0") for name in RegimeLabel}
    probabilities[label.value] = Decimal("1")
    return MarketRegime(asset_or_universe=features.asset, timestamp=features.timestamp, timeframe=timeframe, label=label, trend_strength=trend_strength, volatility_state="high" if stress >= Decimal("0.5") else "normal", stress_score=stress, probabilities=probabilities, model_version=model_version)
