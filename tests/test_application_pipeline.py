from decimal import Decimal

from portfolio_intelligence.application.pipeline import MarketPipeline
from portfolio_intelligence.execution.paper import PaperExecutionModel
from portfolio_intelligence.market_data.events import BookEventType, OrderBookEvent, PriceLevel
from portfolio_intelligence.market_data.quality import MarketQualityStatus
from portfolio_intelligence.strategy.contracts import OrderSide, QualityGatedStrategy


def make_event(update_id: int = 1, timestamp_ms: int = 1_000) -> OrderBookEvent:
    return OrderBookEvent(symbol="EGLDUSDT", event_type=BookEventType.SNAPSHOT, update_id=update_id, bids=(PriceLevel(price=Decimal("14.49"), quantity=Decimal("100")),), asks=(PriceLevel(price=Decimal("14.51"), quantity=Decimal("100")),), timestamp_ms=timestamp_ms)


def test_pipeline_integrates_validation_quality_strategy_and_paper_execution() -> None:
    strategy = QualityGatedStrategy("EGLDUSDT", OrderSide.BUY, Decimal("2"), Decimal("10"))
    result = MarketPipeline(strategy, PaperExecutionModel()).process(make_event(), now_ms=1_000, max_age_ms=100)
    assert result.validation.status.value == "valid"
    assert result.quality is not None
    assert result.quality.status == MarketQualityStatus.READY
    assert result.intent is not None
    assert result.execution is not None
    assert result.execution.status == "not_filled"


def test_pipeline_blocks_stale_event_before_mutating_book() -> None:
    strategy = QualityGatedStrategy("EGLDUSDT", OrderSide.BUY, Decimal("1"), Decimal("10"))
    pipeline = MarketPipeline(strategy)
    result = pipeline.process(make_event(timestamp_ms=1_000), now_ms=2_000, max_age_ms=100)
    assert result.validation.status.value == "stale"
    assert pipeline.book.last_update_id is None
