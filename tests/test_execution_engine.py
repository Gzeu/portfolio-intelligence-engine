from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from portfolio_intelligence.domain.models import CapitalDecision, DecisionAction
from portfolio_intelligence.execution.costs import estimate_costs
from portfolio_intelligence.execution.planner import ExecutionPolicy, create_execution_plan
from portfolio_intelligence.execution.position import PositionStatus, close_position, open_position


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def decision(action=DecisionAction.APPROVE, size="100"):
    return CapitalDecision(decision_id="cd_1", candidate_id="opp_1", decision=action, approved_size=Decimal(size), risk_consumed=Decimal("0.005"), reasons=("test",), created_at=NOW, expires_at=NOW + timedelta(minutes=5))


def test_cost_estimate_contains_slippage_components() -> None:
    costs = estimate_costs(Decimal("14.5"), Decimal("10"), Decimal("0.018"), Decimal("0.9"), Decimal("100"), Decimal("10000"))
    assert costs.total_cost_bps == costs.spread_cost_bps + costs.slippage_bps + costs.market_impact_bps + costs.fee_bps


def test_passive_plan_uses_limit_order_and_idempotency() -> None:
    plan = create_execution_plan(decision(), "EGLDUSDT", "LONG", Decimal("14.5"), Decimal("0.018"), Decimal("0.9"), Decimal("10000"), NOW)
    assert plan.policy == ExecutionPolicy.PASSIVE
    assert plan.limit_price == Decimal("14.5")
    assert plan.idempotency_key == "idem_cd_1"


def test_wait_cannot_create_execution_plan() -> None:
    with pytest.raises(ValueError):
        create_execution_plan(decision(DecisionAction.WAIT), "EGLDUSDT", "LONG", Decimal("14.5"), Decimal("0.018"), Decimal("0.9"), Decimal("10000"), NOW)


def test_position_lifecycle_open_to_closed() -> None:
    position = open_position("pos_1", "EGLDUSDT", "LONG", Decimal("10"), Decimal("14.5"))
    assert position.status == PositionStatus.OPEN
    closed = close_position(position, Decimal("15.0"))
    assert closed.status == PositionStatus.CLOSED
    assert closed.realized_pnl == Decimal("5.0")


def test_short_position_pnl_is_directional() -> None:
    position = open_position("pos_2", "EGLDUSDT", "SHORT", Decimal("10"), Decimal("14.5"))
    closed = close_position(position, Decimal("14.0"))
    assert closed.realized_pnl == Decimal("5.0")
