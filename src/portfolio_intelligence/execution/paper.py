from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from portfolio_intelligence.market_data.orderbook import OrderBook
from portfolio_intelligence.strategy.contracts import OrderIntent, OrderSide


class PaperExecutionError(ValueError):
    pass


@dataclass(frozen=True)
class PaperExecutionConfig:
    fee_bps: Decimal = Decimal("5")
    slippage_bps: Decimal = Decimal("0")
    max_fill_quantity: Decimal | None = None


@dataclass(frozen=True)
class ExecutionReport:
    intent: OrderIntent
    filled_quantity: Decimal
    fill_price: Decimal
    fee_quote: Decimal
    status: str


class PaperExecutionModel:
    def __init__(self, config: PaperExecutionConfig | None = None) -> None:
        self.config = config or PaperExecutionConfig()

    def execute(self, intent: OrderIntent, book: OrderBook) -> ExecutionReport:
        if intent.quantity <= 0 or intent.limit_price <= 0:
            raise PaperExecutionError("intent quantity and price must be positive")
        best = book.best_ask() if intent.side == OrderSide.BUY else book.best_bid()
        if best is None:
            raise PaperExecutionError("book has no executable side")
        if intent.side == OrderSide.BUY and best.price > intent.limit_price:
            return ExecutionReport(intent, Decimal("0"), Decimal("0"), Decimal("0"), "not_filled")
        if intent.side == OrderSide.SELL and best.price < intent.limit_price:
            return ExecutionReport(intent, Decimal("0"), Decimal("0"), Decimal("0"), "not_filled")
        quantity = min(intent.quantity, best.quantity)
        if self.config.max_fill_quantity is not None:
            quantity = min(quantity, self.config.max_fill_quantity)
        direction = Decimal("1") if intent.side == OrderSide.BUY else Decimal("-1")
        fill_price = best.price * (Decimal("1") + direction * self.config.slippage_bps / Decimal("10000"))
        notional = fill_price * quantity
        fee = notional * self.config.fee_bps / Decimal("10000")
        status = "filled" if quantity == intent.quantity else "partial"
        return ExecutionReport(intent, quantity, fill_price, fee, status)
