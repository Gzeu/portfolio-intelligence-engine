from decimal import Decimal

import pytest

from portfolio_intelligence.market_data.advanced_metrics import IncompleteAdvancedBook, microprice, top_level_concentration, top_n_depth
from portfolio_intelligence.market_data.events import BookEventType, OrderBookEvent, PriceLevel
from portfolio_intelligence.market_data.orderbook import OrderBook


def make_book() -> OrderBook:
    book = OrderBook()
    book.apply(OrderBookEvent(symbol="EGLDUSDT", event_type=BookEventType.SNAPSHOT, update_id=1, bids=(PriceLevel(price=Decimal("14.49"), quantity=Decimal("100")), PriceLevel(price=Decimal("14.40"), quantity=Decimal("50"))), asks=(PriceLevel(price=Decimal("14.51"), quantity=Decimal("80")), PriceLevel(price=Decimal("14.60"), quantity=Decimal("20"))), timestamp_ms=1723474800000))
    return book


def test_microprice_uses_opposite_queue_sizes() -> None:
    result = microprice(make_book())
    assert result == (Decimal("14.49") * Decimal("80") + Decimal("14.51") * Decimal("100")) / Decimal("180")


def test_top_n_depth_and_concentration() -> None:
    book = make_book()
    assert top_n_depth(book, 1) == (Decimal("1449.00"), Decimal("1160.80"))
    bid_concentration, ask_concentration = top_level_concentration(book, 2)
    assert bid_concentration == Decimal("1449") / Decimal("2169")
    assert ask_concentration == Decimal("1160.8") / Decimal("1452.8")


def test_invalid_or_incomplete_book_fails_closed() -> None:
    with pytest.raises(ValueError):
        top_n_depth(make_book(), 0)
    with pytest.raises(IncompleteAdvancedBook):
        microprice(OrderBook())
