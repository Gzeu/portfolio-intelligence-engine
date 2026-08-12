from __future__ import annotations

from datetime import datetime

from portfolio_intelligence.domain.models import AccountState, MarketState
from portfolio_intelligence.exchange.config import BybitSettings
from portfolio_intelligence.exchange.contracts import ExchangeOrderRequest, ExchangeOrderResult


class BybitProvider:
    """Bybit V5 boundary. Network transport is intentionally not implemented yet."""

    name = "bybit"
    api_version = "v5"

    def __init__(self, settings: BybitSettings | None = None) -> None:
        self.settings = settings or BybitSettings()

    async def get_market_state(self, asset: str, timestamp: datetime) -> MarketState:
        raise NotImplementedError("Bybit market transport is reserved for the provider integration phase")

    async def get_account_state(self, account_id: str, timestamp: datetime) -> AccountState:
        raise NotImplementedError("Bybit account transport is reserved for the provider integration phase")

    async def submit_order(self, request: ExchangeOrderRequest) -> ExchangeOrderResult:
        if not self.settings.can_submit_orders():
            return ExchangeOrderResult(accepted=False, status="BLOCKED", reason="Bybit order submission is disabled")
        raise NotImplementedError("Bybit order transport requires a separately approved live integration")
