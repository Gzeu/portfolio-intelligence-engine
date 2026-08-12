from __future__ import annotations

from dataclasses import dataclass

from portfolio_intelligence.execution.paper import ExecutionReport, PaperExecutionModel
from portfolio_intelligence.market_data.events import OrderBookEvent
from portfolio_intelligence.market_data.orderbook import OrderBook, OrderBookGap
from portfolio_intelligence.market_data.quality import MarketQualitySnapshot, assess_market_quality
from portfolio_intelligence.market_data.validation import MarketDataStatus, MarketDataValidation, validate_orderbook_event
from portfolio_intelligence.strategy.contracts import OrderIntent, Strategy


@dataclass(frozen=True)
class PipelineResult:
    validation: MarketDataValidation
    quality: MarketQualitySnapshot | None
    intent: OrderIntent | None
    execution: ExecutionReport | None
    error: str | None = None


class MarketPipeline:
    def __init__(self, strategy: Strategy, execution_model: PaperExecutionModel | None = None) -> None:
        self.strategy = strategy
        self.execution_model = execution_model or PaperExecutionModel()
        self.book = OrderBook()

    def process(self, event: OrderBookEvent, now_ms: int, max_age_ms: int) -> PipelineResult:
        validation = validate_orderbook_event(event, now_ms, max_age_ms, self.book.last_update_id, getattr(self.book, "last_timestamp_ms", None))
        if validation.status != MarketDataStatus.VALID:
            return PipelineResult(validation, None, None, None)
        try:
            self.book.apply(event)
            self.book.last_timestamp_ms = event.timestamp_ms
        except (OrderBookGap, ValueError) as exc:
            return PipelineResult(MarketDataValidation(MarketDataStatus.INVALID, (str(exc),)), None, None, None, str(exc))
        quality = assess_market_quality(self.book)
        intent = self.strategy.decide(quality)
        execution = self.execution_model.execute(intent, self.book) if intent is not None else None
        return PipelineResult(validation, quality, intent, execution)
