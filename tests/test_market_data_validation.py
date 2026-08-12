from decimal import Decimal

from portfolio_intelligence.market_data.events import BookEventType, OrderBookEvent, PriceLevel
from portfolio_intelligence.market_data.validation import MarketDataStatus, validate_orderbook_event


NOW = 1_723_474_800_000


def make_event(update_id: int = 1, timestamp_ms: int = NOW, bid: str = "14.49", ask: str = "14.51") -> OrderBookEvent:
    return OrderBookEvent(symbol="EGLDUSDT", event_type=BookEventType.SNAPSHOT, update_id=update_id, bids=(PriceLevel(price=Decimal(bid), quantity=Decimal("100")),), asks=(PriceLevel(price=Decimal(ask), quantity=Decimal("100")),), timestamp_ms=timestamp_ms)


def test_valid_event() -> None:
    assert validate_orderbook_event(make_event(), NOW, 1_000).status == MarketDataStatus.VALID


def test_stale_event() -> None:
    result = validate_orderbook_event(make_event(timestamp_ms=NOW - 2_000), NOW, 1_000)
    assert result.status == MarketDataStatus.STALE


def test_crossed_book_is_invalid() -> None:
    result = validate_orderbook_event(make_event(ask="14.40"), NOW, 1_000)
    assert result.status == MarketDataStatus.INVALID
    assert "crossed_book" in result.reasons


def test_regressive_update_and_timestamp_are_invalid() -> None:
    result = validate_orderbook_event(make_event(update_id=4, timestamp_ms=NOW - 10), NOW, 1_000, previous_update_id=4, previous_timestamp_ms=NOW)
    assert result.status == MarketDataStatus.INVALID
    assert "duplicate_or_regressive_update_id" in result.reasons
    assert "non_monotonic_timestamp" in result.reasons


def test_future_event_is_stale() -> None:
    assert validate_orderbook_event(make_event(timestamp_ms=NOW + 1), NOW, 1_000).status == MarketDataStatus.STALE
