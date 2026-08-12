from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from portfolio_intelligence.execution.paper import ExecutionReport
from portfolio_intelligence.strategy.contracts import OrderSide


class LedgerError(ValueError):
    pass


@dataclass
class PositionState:
    quantity: Decimal = Decimal("0")
    average_entry: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")


@dataclass
class PortfolioLedger:
    cash: Decimal
    positions: dict[str, PositionState] = field(default_factory=dict)

    def apply(self, report: ExecutionReport) -> None:
        if report.status not in {"filled", "partial"} or report.filled_quantity <= 0:
            return
        symbol = report.intent.symbol
        position = self.positions.setdefault(symbol, PositionState())
        quantity = report.filled_quantity
        notional = report.fill_price * quantity
        total_cost = notional + report.fee_quote
        if report.intent.side == OrderSide.BUY:
            if self.cash < total_cost:
                raise LedgerError("insufficient cash")
            new_quantity = position.quantity + quantity
            position.average_entry = ((position.average_entry * position.quantity) + notional) / new_quantity if new_quantity else Decimal("0")
            position.quantity = new_quantity
            self.cash -= total_cost
        else:
            if quantity > position.quantity:
                raise LedgerError("cannot sell more than current position")
            position.realized_pnl += (report.fill_price - position.average_entry) * quantity - report.fee_quote
            position.quantity -= quantity
            self.cash += notional - report.fee_quote
            if position.quantity == 0:
                position.average_entry = Decimal("0")

    def unrealized_pnl(self, prices: dict[str, Decimal]) -> Decimal:
        return sum(((prices[symbol] - position.average_entry) * position.quantity for symbol, position in self.positions.items() if symbol in prices), Decimal("0"))

    def realized_pnl(self) -> Decimal:
        return sum((position.realized_pnl for position in self.positions.values()), Decimal("0"))

    def equity(self, prices: dict[str, Decimal]) -> Decimal:
        market_value = sum((prices[symbol] * position.quantity for symbol, position in self.positions.items() if symbol in prices), Decimal("0"))
        return self.cash + market_value

    def total_pnl(self, prices: dict[str, Decimal], initial_cash: Decimal) -> Decimal:
        return self.equity(prices) - initial_cash
