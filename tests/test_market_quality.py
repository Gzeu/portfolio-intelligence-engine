from decimal import Decimal

from portfolio_intelligence.market_data.events import BookEventType, OrderBookEvent, PriceLevel
from portfolio_intelligence.market_data.orderbook import OrderBook
from portfolio_intelligence.market_data.quality import MarketQualityStatus, MarketQualityThresholds, assess_market_quality


def make_book(bid_qty: str = "100", ask_qty: str = "100", ask_price: str = "14.51") -> OrderBook:
    book = OrderBook()
    book.apply(OrderBookEvent(symbol="EGLDUSDT", event_type=BookEventType.SNAPSHOT, update_id=1, bids=(PriceLevel(price=Decimal("14.49"), quantity=Decimal(bid_qty)),), asks=(PriceLevel(price=Decimal(ask_price), quantity=Decimal(ask_qty)),), timestamp_ms=1723474800000))
    return book


def test_balanced_book_is_ready() -> None:
    result = assess_market_quality(make_book())
    assert result.status == MarketQualityStatus.READY
    assert result.reasons == ()


def test_imbalance_degrades_but_does_not_block() -> None:
    result = assess_market_quality(make_book(bid_qty="700", ask_qty="100"))
    assert result.status == MarketQualityStatus.DEGRADED
    assert result.imbalance == Decimal("0.75")


def test_wide_spread_blocks() -> None:
    result = assess_market_quality(make_book(ask_price="15.00"))
    assert result.status == MarketQualityStatus.BLOCKED
    assert "spread_above_limit" in result.reasons


def test_low_depth_is_reported() -> None:
    result = assess_market_quality(make_book(bid_qty="1", ask_qty="1"), MarketQualityThresholds(min_depth_quote=Decimal("100")))
    assert result.status == MarketQualityStatus.DEGRADED
    assert "depth_below_minimum" in result.reasons
