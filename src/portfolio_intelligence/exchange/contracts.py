from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Protocol

from portfolio_intelligence.domain.models import AccountState, MarketState, StrictModel


class ExchangeOrderRequest(StrictModel):
    client_order_id: str
    asset: str
    side: str
    quantity: Decimal
    order_type: str
    price: Decimal | None = None


class ExchangeOrderResult(StrictModel):
    accepted: bool
    exchange_order_id: str | None = None
    status: str
    reason: str | None = None


class ExchangeProvider(Protocol):
    async def get_market_state(self, asset: str, timestamp: datetime) -> MarketState: ...
    async def get_account_state(self, account_id: str, timestamp: datetime) -> AccountState: ...
    async def submit_order(self, request: ExchangeOrderRequest) -> ExchangeOrderResult: ...
