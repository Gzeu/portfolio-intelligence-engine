from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from portfolio_intelligence.domain.models import StrictModel


class OutcomeExit(StrEnum):
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    MANUAL = "MANUAL"
    EXPIRED = "EXPIRED"
    INVALIDATED = "INVALIDATED"


class Outcome(StrictModel):
    realized_pnl: Decimal
    mae: Decimal = Field(ge=0)
    mfe: Decimal = Field(ge=0)
    fees: Decimal = Field(ge=0)
    funding: Decimal = Decimal("0")
    slippage_bps: Decimal = Field(ge=0)
    exit_reason: OutcomeExit
    closed_at: datetime


class DecisionCase(StrictModel):
    case_id: str
    opportunity_id: str
    forecast_id: str
    decision_id: str
    asset: str
    horizon: str
    confidence_declared: Decimal = Field(ge=0, le=1)
    predicted_direction: str
    created_at: datetime
    outcome: Outcome | None = None
    lesson: str | None = None


def close_case(case: DecisionCase, outcome: Outcome, lesson: str | None = None) -> DecisionCase:
    if case.outcome is not None:
        raise ValueError("decision case is already closed")
    if outcome.closed_at < case.created_at:
        raise ValueError("outcome cannot close before the case was created")
    return case.model_copy(update={"outcome": outcome, "lesson": lesson})
