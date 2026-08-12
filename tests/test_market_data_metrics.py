from decimal import Decimal

import pytest

from portfolio_intelligence.market_data.events import BookEventType, OrderBookEvent, PriceLevel
from portfolio_intelligence.market_data.metrics import IncompleteOrderBook, depth_within_band, mid_price, spread, spread_bps, volume_imbalance
from portfolio_intelligence.market_data.orderbook import OrderBook


def make_book() -> OrderBook:
    book = OrderBook()
    book.apply(OrderBookEvent(symbol="EGLDUSDT", event_type=BookEventType.SNAPSHOT, update_id=1, bids=(PriceLevel(price=Decimal("14.49"), quantity=Decimal("100")), PriceLevel(price=Decimal("14.40"), quantity=Decimal("50"))), asks=(PriceLevel(price=Decimal("14.51"), quantity=Decimal("80")), PriceLevel(price=Decimal("14.60"), quantity=Decimal("20"))), timestamp_ms=1723474800000))
    return book


def test_top_of_book_metrics() -> None:
    book = make_book()
    assert mid_price(book) == Decimal("14.50")
    assert spread(book) == Decimal("0.02")
    assert spread_bps(book) == pytest.approx(Decimal("13.79310344827586206896551724"))


def test_depth_and_imbalance() -> None:
    book = make_book()
    assert depth_within_band(book, Decimal("0.5")) == (Decimal("1449.00"), Decimal("1160.80"))
    assert volume_imbalance(book) == Decimal("50") / Decimal("250")


def test_incomplete_book_fails_closed() -> None:
    with pytest.raises(IncompleteOrderBook):
        mid_price(OrderBook())


def test_negative_band_is_rejected() -> None:
    with pytest.raises(ValueError):
        depth_within_band(make_book(), Decimal("-1"))
