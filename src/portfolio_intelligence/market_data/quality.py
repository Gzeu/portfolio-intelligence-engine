from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from portfolio_intelligence.market_data.metrics import IncompleteOrderBook, depth_within_band, mid_price, spread_bps, volume_imbalance
from portfolio_intelligence.market_data.orderbook import OrderBook


class MarketQualityStatus(StrEnum):
    READY = "ready"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class MarketQualityThresholds:
    max_spread_bps: Decimal = Decimal("50")
    min_depth_quote: Decimal = Decimal("100")
    depth_band_pct: Decimal = Decimal("0.5")
    degraded_imbalance_abs: Decimal = Decimal("0.75")


@dataclass(frozen=True)
class MarketQualitySnapshot:
    status: MarketQualityStatus
    mid_price: Decimal | None
    spread_bps: Decimal | None
    bid_depth_quote: Decimal
    ask_depth_quote: Decimal
    imbalance: Decimal | None
    reasons: tuple[str, ...]


def assess_market_quality(book: OrderBook, thresholds: MarketQualityThresholds | None = None) -> MarketQualitySnapshot:
    limits = thresholds or MarketQualityThresholds()
    try:
        mid = mid_price(book)
        book_spread_bps = spread_bps(book)
        bid_depth, ask_depth = depth_within_band(book, limits.depth_band_pct)
        imbalance = volume_imbalance(book)
    except IncompleteOrderBook as exc:
        return MarketQualitySnapshot(MarketQualityStatus.BLOCKED, None, None, Decimal("0"), Decimal("0"), None, (str(exc),))

    reasons: list[str] = []
    if book_spread_bps > limits.max_spread_bps:
        reasons.append("spread_above_limit")
    if bid_depth < limits.min_depth_quote or ask_depth < limits.min_depth_quote:
        reasons.append("depth_below_minimum")
    status = MarketQualityStatus.BLOCKED if "spread_above_limit" in reasons else MarketQualityStatus.DEGRADED if reasons or abs(imbalance) >= limits.degraded_imbalance_abs else MarketQualityStatus.READY
    return MarketQualitySnapshot(status, mid, book_spread_bps, bid_depth, ask_depth, imbalance, tuple(reasons))
