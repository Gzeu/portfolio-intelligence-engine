from __future__ import annotations

from decimal import Decimal
from pydantic import Field

from portfolio_intelligence.domain.models import MarketState, StrictModel


class MarketFeatures(StrictModel):
    asset: str
    timestamp: object
    mid_price: Decimal = Field(gt=0)
    spread_bps: Decimal = Field(ge=0)
    return_pct: Decimal
    volatility: Decimal = Field(ge=0)
    volume: Decimal = Field(ge=0)
    liquidity_score: Decimal = Field(ge=0, le=1)
    directional_bias: Decimal = Field(ge=-1, le=1)


def compute_features(current: MarketState, previous_close: Decimal | None = None) -> MarketFeatures:
    if previous_close is not None and previous_close <= 0:
        raise ValueError("previous_close must be positive")
    mid = (current.bid + current.ask) / Decimal("2")
    return_pct = Decimal("0") if previous_close is None else ((mid / previous_close) - 1) * 100
    spread_penalty = min(current.spread_bps / Decimal("100"), Decimal("1"))
    liquidity_score = max(Decimal("0"), min(Decimal("1"), (Decimal("1") - spread_penalty) * (Decimal("1") if current.volume > 0 else Decimal("0"))))
    directional_bias = max(Decimal("-1"), min(Decimal("1"), return_pct / Decimal("5")))
    return MarketFeatures(asset=current.asset, timestamp=current.timestamp, mid_price=mid, spread_bps=current.spread_bps, return_pct=return_pct, volatility=current.volatility, volume=current.volume, liquidity_score=liquidity_score, directional_bias=directional_bias)
