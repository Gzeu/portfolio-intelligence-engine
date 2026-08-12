from __future__ import annotations

from typing import Any

from portfolio_intelligence.exchange.bybit_contracts import assert_read_only_endpoint
from portfolio_intelligence.exchange.transport import ReadOnlyTransport, RetryPolicy


class BybitReadOnlyClient:
    def __init__(self, transport: ReadOnlyTransport, retry_policy: RetryPolicy | None = None) -> None:
        self.transport = transport
        self.retry_policy = retry_policy or RetryPolicy()

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        assert_read_only_endpoint(path)
        return await self.transport.get(path, params)

    async def system_status(self) -> dict[str, Any]:
        from portfolio_intelligence.exchange.bybit_contracts import BybitReadOnlyEndpoint
        return await self.get(BybitReadOnlyEndpoint.SYSTEM_STATUS.value)

    async def ticker(self, category: str, symbol: str) -> dict[str, Any]:
        from portfolio_intelligence.exchange.bybit_contracts import BybitReadOnlyEndpoint
        return await self.get(BybitReadOnlyEndpoint.TICKERS.value, {"category": category, "symbol": symbol})

    async def position_list(self, category: str, symbol: str | None = None) -> dict[str, Any]:
        from portfolio_intelligence.exchange.bybit_contracts import BybitReadOnlyEndpoint
        params = {"category": category}
        if symbol is not None:
            params["symbol"] = symbol
        return await self.get(BybitReadOnlyEndpoint.POSITION_LIST.value, params)
