from __future__ import annotations

from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import Field

from portfolio_intelligence.domain.models import StrictModel

T = TypeVar("T")


class BybitResponse(StrictModel, Generic[T]):
    retCode: int
    retMsg: str
    result: T
    time: int = Field(ge=0)


class InstrumentInfo(StrictModel):
    symbol: str
    contract_type: str | None = None
    status: str
    base_coin: str | None = None
    quote_coin: str | None = None
    tick_size: Decimal = Field(gt=0)
    qty_step: Decimal = Field(gt=0)


class Ticker(StrictModel):
    symbol: str
    last_price: Decimal = Field(gt=0)
    bid_price: Decimal = Field(ge=0)
    ask_price: Decimal = Field(ge=0)
    volume_24h: Decimal = Field(ge=0)


class WalletBalance(StrictModel):
    account_type: str
    total_equity: Decimal = Field(ge=0)
    total_available_balance: Decimal = Field(ge=0)
    total_margin_balance: Decimal = Field(ge=0)


class PositionInfo(StrictModel):
    symbol: str
    side: str
    size: Decimal = Field(ge=0)
    avg_price: Decimal = Field(gt=0)
    unrealised_pnl: Decimal
    leverage: Decimal = Field(ge=0)
