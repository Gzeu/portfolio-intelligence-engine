from decimal import Decimal

from portfolio_intelligence.execution.paper import PaperExecutionConfig, PaperExecutionModel
from portfolio_intelligence.market_data.events import BookEventType, OrderBookEvent, PriceLevel
from portfolio_intelligence.market_data.orderbook import OrderBook
from portfolio_intelligence.strategy.contracts import OrderIntent, OrderSide, QualityGatedStrategy
from portfolio_intelligence.market_data.quality import MarketQualityStatus, MarketQualitySnapshot


def make_book() -> OrderBook:
    book = OrderBook()
    book.apply(OrderBookEvent(symbol="EGLDUSDT", event_type=BookEventType.SNAPSHOT, update_id=1, bids=(PriceLevel(price=Decimal("14.49"), quantity=Decimal("10")),), asks=(PriceLevel(price=Decimal("14.51"), quantity=Decimal("5")),), timestamp_ms=1))
    return book


def test_buy_is_filled_at_ask_with_fee_and_slippage() -> None:
    intent = OrderIntent("EGLDUSDT", OrderSide.BUY, Decimal("3"), Decimal("14.60"), "test")
    report = PaperExecutionModel(PaperExecutionConfig(fee_bps=Decimal("10"), slippage_bps=Decimal("5"))).execute(intent, make_book())
    assert report.status == "filled"
    assert report.fill_price == Decimal("14.517255")
    assert report.filled_quantity == Decimal("3")


def test_buy_is_partial_when_depth_is_insufficient() -> None:
    intent = OrderIntent("EGLDUSDT", OrderSide.BUY, Decimal("8"), Decimal("14.60"), "test")
    report = PaperExecutionModel().execute(intent, make_book())
    assert report.status == "partial"
    assert report.filled_quantity == Decimal("5")


def test_strategy_is_blocked_by_market_quality() -> None:
    market = MarketQualitySnapshot(MarketQualityStatus.DEGRADED, Decimal("14.50"), Decimal("20"), Decimal("1000"), Decimal("1000"), Decimal("0.1"), ("depth_below_minimum",))
    strategy = QualityGatedStrategy("EGLDUSDT", OrderSide.BUY, Decimal("1"), Decimal("10"))
    assert strategy.decide(market) is None
