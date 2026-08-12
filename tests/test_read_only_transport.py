import pytest

from portfolio_intelligence.exchange.bybit_contracts import BybitReadOnlyEndpoint
from portfolio_intelligence.exchange.bybit_readonly_client import BybitReadOnlyClient
from portfolio_intelligence.exchange.transport import ReplayTransport, RetryPolicy, TransportError


@pytest.mark.asyncio
async def test_replay_transport_returns_fixture_and_records_call() -> None:
    transport = ReplayTransport({BybitReadOnlyEndpoint.TICKERS.value: {"retCode": 0, "retMsg": "OK", "result": {"list": []}, "time": 1}})
    client = BybitReadOnlyClient(transport)
    response = await client.ticker("linear", "EGLDUSDT")
    assert response["retCode"] == 0
    assert transport.calls == [(BybitReadOnlyEndpoint.TICKERS.value, {"category": "linear", "symbol": "EGLDUSDT"})]


@pytest.mark.asyncio
async def test_order_endpoint_is_rejected_before_transport() -> None:
    transport = ReplayTransport({})
    client = BybitReadOnlyClient(transport)
    with pytest.raises(ValueError):
        await client.get("/v5/order/create")
    assert transport.calls == []


@pytest.mark.asyncio
async def test_missing_fixture_is_transport_error() -> None:
    client = BybitReadOnlyClient(ReplayTransport({}))
    with pytest.raises(TransportError):
        await client.system_status()


def test_retry_policy_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)
