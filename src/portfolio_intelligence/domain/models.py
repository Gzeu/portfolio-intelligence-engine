from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Side(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"


class DecisionAction(StrEnum):
    APPROVE = "APPROVE"
    REDUCE_SIZE = "REDUCE_SIZE"
    WAIT = "WAIT"
    REJECT = "REJECT"


class RegimeLabel(StrEnum):
    TREND = "trend"
    RANGE = "range"
    REVERSAL = "reversal"
    STRESS = "stress"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class AccountState(StrictModel):
    account_id: str
    timestamp: datetime
    equity: Decimal = Field(ge=0)
    available_margin: Decimal = Field(ge=0)
    used_margin: Decimal = Field(ge=0)
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    gross_exposure: Decimal = Field(ge=0)
    net_exposure: Decimal
    leverage: Decimal = Field(ge=0)


class MarketState(StrictModel):
    asset: str
    timestamp: datetime
    price: Decimal = Field(gt=0)
    bid: Decimal = Field(gt=0)
    ask: Decimal = Field(gt=0)
    spread_bps: Decimal = Field(ge=0)
    volume: Decimal = Field(ge=0)
    volatility: Decimal = Field(ge=0)
    liquidity_state: str


class MarketRegime(StrictModel):
    asset_or_universe: str
    timestamp: datetime
    timeframe: str
    label: RegimeLabel
    trend_strength: Decimal = Field(ge=0, le=1)
    volatility_state: str
    stress_score: Decimal = Field(ge=0, le=1)
    probabilities: dict[str, Decimal]
    model_version: str


class Opportunity(StrictModel):
    opportunity_id: str
    asset: str
    side: Side
    detected_at: datetime
    setup_type: str
    timeframe: str
    status: str
    expiry: datetime
    invalidation_conditions: tuple[str, ...] = ()


class Forecast(StrictModel):
    forecast_id: str
    opportunity_id: str
    horizon: str
    created_at: datetime
    valid_until: datetime
    distribution: dict[str, Decimal]
    expected_return: Decimal
    expected_loss: Decimal = Field(ge=0)
    confidence_declared: Decimal = Field(ge=0, le=1)
    confidence_calibrated: Decimal | None = Field(default=None, ge=0, le=1)
    model_version: str


class PortfolioSnapshot(StrictModel):
    portfolio_id: str
    timestamp: datetime
    equity: Decimal = Field(ge=0)
    gross_exposure: Decimal = Field(ge=0)
    net_exposure: Decimal
    concentration: Decimal = Field(ge=0, le=1)
    risk_budget: Decimal = Field(ge=0, le=1)
    margin_headroom: Decimal = Field(ge=0, le=1)
    drawdown: Decimal = Field(ge=0, le=1)
    positions: tuple[dict[str, Any], ...] = ()


class CapitalDecision(StrictModel):
    decision_id: str
    candidate_id: str
    decision: DecisionAction
    approved_size: Decimal = Field(ge=0)
    risk_consumed: Decimal = Field(ge=0, le=1)
    reasons: tuple[str, ...]
    created_at: datetime
    expires_at: datetime
