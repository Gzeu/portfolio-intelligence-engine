from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from portfolio_intelligence.domain.models import CapitalDecision, DecisionAction, StrictModel
from portfolio_intelligence.execution.costs import ExecutionCostEstimate, estimate_costs


class OrderType(StrEnum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class ExecutionPolicy(StrEnum):
    PASSIVE = "PASSIVE"
    AGGRESSIVE = "AGGRESSIVE"
    TWAP_SIMULATION = "TWAP_SIMULATION"


class ExecutionPlan(StrictModel):
    plan_id: str
    idempotency_key: str
    decision_id: str
    asset: str
    side: str
    size: Decimal = Field(gt=0)
    order_type: OrderType
    policy: ExecutionPolicy
    limit_price: Decimal | None = Field(default=None, gt=0)
    max_slippage_bps: Decimal = Field(ge=0)
    costs: ExecutionCostEstimate
    created_at: datetime
    expires_at: datetime


def create_execution_plan(decision: CapitalDecision, asset: str, side: str, arrival_price: Decimal, volatility: Decimal, liquidity_score: Decimal, equity: Decimal, now: datetime, max_slippage_bps: Decimal = Decimal("25"), policy: ExecutionPolicy = ExecutionPolicy.PASSIVE) -> ExecutionPlan:
    if decision.decision not in (DecisionAction.APPROVE, DecisionAction.REDUCE_SIZE):
        raise ValueError("only APPROVE or REDUCE_SIZE decisions can create execution plans")
    if decision.expires_at <= now:
        raise ValueError("capital decision is expired")
    if decision.approved_size <= 0:
        raise ValueError("capital decision has no approved size")
    costs = estimate_costs(arrival_price, Decimal("10"), volatility, liquidity_score, decision.approved_size, equity)
    if costs.total_cost_bps > max_slippage_bps:
        raise ValueError("estimated execution cost exceeds slippage limit")
    order_type = OrderType.LIMIT if policy == ExecutionPolicy.PASSIVE else OrderType.MARKET
    limit_price = arrival_price if order_type == OrderType.LIMIT else None
    return ExecutionPlan(plan_id=f"plan_{decision.decision_id}", idempotency_key=f"idem_{decision.decision_id}", decision_id=decision.decision_id, asset=asset, side=side, size=decision.approved_size, order_type=order_type, policy=policy, limit_price=limit_price, max_slippage_bps=max_slippage_bps, costs=costs, created_at=now, expires_at=min(decision.expires_at, now + timedelta(minutes=2)))
