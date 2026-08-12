from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from portfolio_intelligence.market_data.events import OrderBookEvent


class MarketDataStatus(StrEnum):
    VALID = "valid"
    STALE = "stale"
    INVALID = "invalid"


@dataclass(frozen=True)
class MarketDataValidation:
    status: MarketDataStatus
    reasons: tuple[str, ...]


def validate_orderbook_event(event: OrderBookEvent, now_ms: int, max_age_ms: int, previous_update_id: int | None = None, previous_timestamp_ms: int | None = None) -> MarketDataValidation:
    reasons: list[str] = []
    if max_age_ms < 0:
        raise ValueError("max_age_ms must be non-negative")
    if event.update_id < 0:
        reasons.append("negative_update_id")
    if previous_update_id is not None and event.update_id <= previous_update_id:
        reasons.append("duplicate_or_regressive_update_id")
    if previous_timestamp_ms is not None and event.timestamp_ms < previous_timestamp_ms:
        reasons.append("non_monotonic_timestamp")
    if any(level.price <= 0 or level.quantity < 0 for level in (*event.bids, *event.asks)):
        reasons.append("invalid_price_or_quantity")
    best_bid = max((level.price for level in event.bids if level.quantity > 0), default=None)
    best_ask = min((level.price for level in event.asks if level.quantity > 0), default=None)
    if best_bid is not None and best_ask is not None and best_bid > best_ask:
        reasons.append("crossed_book")
    if reasons:
        return MarketDataValidation(MarketDataStatus.INVALID, tuple(reasons))
    if event.timestamp_ms > now_ms or now_ms - event.timestamp_ms > max_age_ms:
        return MarketDataValidation(MarketDataStatus.STALE, ("stale_or_future_timestamp",))
    return MarketDataValidation(MarketDataStatus.VALID, ())
