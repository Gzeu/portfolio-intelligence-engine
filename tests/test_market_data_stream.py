from decimal import Decimal

import pytest

from portfolio_intelligence.market_data.events import BookEventType, OrderBookEvent, PriceLevel
from portfolio_intelligence.market_data.orderbook import OrderBook, OrderBookGap


def event(kind: BookEventType, update_id: int, bid_qty: str = "100") -> OrderBookEvent:
    return OrderBookEvent(symbol="EGLDUSDT", event_type=kind, update_id=update_id, bids=(PriceLevel(price=Decimal("14.49"), quantity=Decimal(bid_qty)),), asks=(PriceLevel(price=Decimal("14.51"), quantity=Decimal("100")),), timestamp_ms=1723474800000)


def test_snapshot_and_contiguous_delta_update_book() -> None:
    book = OrderBook()
    book.apply(event(BookEventType.SNAPSHOT, 1))
    book.apply(event(BookEventType.DELTA, 2, bid_qty="80"))
    assert book.best_bid().quantity == Decimal("80")
    assert book.best_ask().price == Decimal("14.51")
    assert book.last_update_id == 2


def test_delta_before_snapshot_fails_closed() -> None:
    with pytest.raises(OrderBookGap):
        OrderBook().apply(event(BookEventType.DELTA, 1))


def test_update_gap_fails_closed() -> None:
    book = OrderBook()
    book.apply(event(BookEventType.SNAPSHOT, 10))
    with pytest.raises(OrderBookGap):
        book.apply(event(BookEventType.DELTA, 12))


def test_zero_quantity_removes_level() -> None:
    book = OrderBook()
    book.apply(event(BookEventType.SNAPSHOT, 1))
    book.apply(event(BookEventType.DELTA, 2, bid_qty="0"))
    assert book.best_bid() is None
