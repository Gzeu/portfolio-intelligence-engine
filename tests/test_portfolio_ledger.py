from decimal import Decimal

import pytest

from portfolio_intelligence.execution.paper import ExecutionReport
from portfolio_intelligence.portfolio.ledger import LedgerError, PortfolioLedger
from portfolio_intelligence.strategy.contracts import OrderIntent, OrderSide


def report(side: OrderSide, quantity: str, price: str, fee: str = "0") -> ExecutionReport:
    intent = OrderIntent("EGLDUSDT", side, Decimal(quantity), Decimal(price), "test")
    return ExecutionReport(intent, Decimal(quantity), Decimal(price), Decimal(fee), "filled")


def test_buy_mark_to_market_sell_tracks_pnl() -> None:
    ledger = PortfolioLedger(Decimal("1000"))
    ledger.apply(report(OrderSide.BUY, "10", "10", "1"))
    assert ledger.cash == Decimal("899")
    assert ledger.unrealized_pnl({"EGLDUSDT": Decimal("12")}) == Decimal("20")
    ledger.apply(report(OrderSide.SELL, "10", "12", "1"))
    assert ledger.cash == Decimal("1018")
    assert ledger.realized_pnl() == Decimal("18")
    assert ledger.equity({"EGLDUSDT": Decimal("12")}) == Decimal("1018")


def test_partial_fill_updates_average_entry() -> None:
    ledger = PortfolioLedger(Decimal("1000"))
    ledger.apply(report(OrderSide.BUY, "5", "10"))
    ledger.apply(report(OrderSide.BUY, "5", "12"))
    assert ledger.positions["EGLDUSDT"].quantity == Decimal("10")
    assert ledger.positions["EGLDUSDT"].average_entry == Decimal("11")


def test_oversell_is_rejected() -> None:
    ledger = PortfolioLedger(Decimal("100"))
    with pytest.raises(LedgerError):
        ledger.apply(report(OrderSide.SELL, "1", "10"))
