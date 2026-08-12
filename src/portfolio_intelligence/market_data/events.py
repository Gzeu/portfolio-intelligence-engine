from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from portfolio_intelligence.domain.models import StrictModel


class BookEventType(StrEnum):
    SNAPSHOT = "snapshot"
    DELTA = "delta"


class PriceLevel(StrictModel):
    price: Decimal = Field(gt=0)
    quantity: Decimal = Field(ge=0)


class OrderBookEvent(StrictModel):
    symbol: str
    event_type: BookEventType
    update_id: int = Field(ge=0)
    bids: tuple[PriceLevel, ...] = ()
    asks: tuple[PriceLevel, ...] = ()
    timestamp_ms: int = Field(ge=0)


class TickerEvent(StrictModel):
    symbol: str
    last_price: Decimal = Field(gt=0)
    bid_price: Decimal = Field(ge=0)
    ask_price: Decimal = Field(ge=0)
    timestamp_ms: int = Field(ge=0)
