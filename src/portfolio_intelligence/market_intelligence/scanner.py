from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import Iterable
from uuid import uuid4

from portfolio_intelligence.domain.models import MarketRegime, Opportunity, RegimeLabel, Side
from portfolio_intelligence.market_intelligence.features import MarketFeatures


def scan_opportunity(features: MarketFeatures, regime: MarketRegime, now=None) -> Opportunity | None:
    timestamp = features.timestamp if now is None else now
    if regime.label == RegimeLabel.STRESS or features.liquidity_score < Decimal("0.25"):
        return None
    if abs(features.directional_bias) < Decimal("0.10"):
        return None
    side = Side.LONG if features.directional_bias > 0 else Side.SHORT
    setup = "trend_continuation" if regime.label == RegimeLabel.TREND else "mean_reversion_candidate"
    return Opportunity(opportunity_id=f"opp_{uuid4().hex[:12]}", asset=features.asset, side=side, detected_at=timestamp, setup_type=setup, timeframe=regime.timeframe, status="DETECTED", expiry=timestamp + timedelta(minutes=15), invalidation_conditions=("liquidity_score < 0.25", "regime becomes stress"))


def scan_universe(items: Iterable[tuple[MarketFeatures, MarketRegime]]) -> list[Opportunity]:
    return [opportunity for features, regime in items if (opportunity := scan_opportunity(features, regime)) is not None]
