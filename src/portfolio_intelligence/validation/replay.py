from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from pydantic import Field

from portfolio_intelligence.domain.models import StrictModel


class ReplayEvent(StrictModel):
    timestamp: int
    asset: str
    expected_pnl: Decimal
    fees: Decimal = Field(ge=0)
    slippage_cost: Decimal = Field(ge=0)
    funding_cost: Decimal = Field(ge=0)
    risk_consumed: Decimal = Field(ge=0)
    decision_taken: bool
    decision_correct: bool | None = None


class ReplayResult(StrictModel):
    event_count: int = Field(ge=0)
    net_pnl: Decimal
    gross_pnl: Decimal
    total_costs: Decimal = Field(ge=0)
    equity_curve: tuple[Decimal, ...]
    max_drawdown: Decimal = Field(ge=0)


def run_replay(events: Iterable[ReplayEvent], starting_equity: Decimal) -> ReplayResult:
    if starting_equity <= 0:
        raise ValueError("starting_equity must be positive")
    equity = starting_equity
    peak = equity
    max_drawdown = Decimal("0")
    gross = Decimal("0")
    costs = Decimal("0")
    curve: list[Decimal] = []
    count = 0
    for event in sorted(events, key=lambda item: item.timestamp):
        gross += event.expected_pnl
        event_cost = event.fees + event.slippage_cost + event.funding_cost
        costs += event_cost
        equity += event.expected_pnl - event_cost
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, (peak - equity) / peak)
        curve.append(equity)
        count += 1
    return ReplayResult(event_count=count, net_pnl=equity - starting_equity, gross_pnl=gross, total_costs=costs, equity_curve=tuple(curve), max_drawdown=max_drawdown)
