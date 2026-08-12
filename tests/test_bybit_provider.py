from decimal import Decimal

import pytest

from portfolio_intelligence.exchange.bybit import BybitProvider
from portfolio_intelligence.exchange.config import BybitEnvironment, BybitSettings
from portfolio_intelligence.exchange.contracts import ExchangeOrderRequest


@pytest.mark.asyncio
async def test_bybit_defaults_to_testnet_read_only() -> None:
    provider = BybitProvider()
    assert provider.name == "bybit"
    assert provider.api_version == "v5"
    assert provider.settings.environment == BybitEnvironment.TESTNET
    assert provider.settings.read_only is True
    assert provider.settings.can_submit_orders() is False


@pytest.mark.asyncio
async def test_order_submission_is_blocked_without_live_flags() -> None:
    provider = BybitProvider(BybitSettings(read_only=True, live_orders_enabled=False))
    request = ExchangeOrderRequest(client_order_id="test-1", asset="EGLDUSDT", side="Buy", quantity=Decimal("1"), order_type="Limit", price=Decimal("14.5"))
    result = await provider.submit_order(request)
    assert result.accepted is False
    assert result.status == "BLOCKED"


def test_bybit_environment_urls_are_explicit() -> None:
    assert BybitSettings(environment=BybitEnvironment.TESTNET).rest_base_url == "https://api-testnet.bybit.com"
    assert BybitSettings(environment=BybitEnvironment.MAINNET).rest_base_url == "https://api.bybit.com"
