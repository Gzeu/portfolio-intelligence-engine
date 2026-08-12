from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from portfolio_intelligence.domain.models import StrictModel


class ExecutionCostEstimate(StrictModel):
    arrival_price: Decimal = Field(gt=0)
    expected_price: Decimal = Field(gt=0)
    spread_cost_bps: Decimal = Field(ge=0)
    slippage_bps: Decimal = Field(ge=0)
    market_impact_bps: Decimal = Field(ge=0)
    fee_bps: Decimal = Field(ge=0)
    total_cost_bps: Decimal = Field(ge=0)


def estimate_costs(arrival_price: Decimal, spread_bps: Decimal, volatility: Decimal, liquidity_score: Decimal, size: Decimal, equity: Decimal, fee_bps: Decimal = Decimal("5")) -> ExecutionCostEstimate:
    if arrival_price <= 0 or size < 0 or equity <= 0:
        raise ValueError("arrival_price must be positive, size non-negative, equity positive")
    if not Decimal("0") <= liquidity_score <= Decimal("1"):
        raise ValueError("liquidity_score must be between 0 and 1")
    participation = min(Decimal("1"), size / equity)
    slippage = volatility * Decimal("100") * (Decimal("1") - liquidity_score) * Decimal("10")
    impact = participation * (Decimal("1") + volatility * Decimal("100")) * Decimal("20")
    total = spread_bps + slippage + impact + fee_bps
    return ExecutionCostEstimate(arrival_price=arrival_price, expected_price=arrival_price, spread_cost_bps=spread_bps, slippage_bps=slippage, market_impact_bps=impact, fee_bps=fee_bps, total_cost_bps=total)
