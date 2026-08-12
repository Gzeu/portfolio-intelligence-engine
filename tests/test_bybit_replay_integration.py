import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from portfolio_intelligence.config import Settings
from portfolio_intelligence.controls.circuit_breaker import CircuitBreaker
from portfolio_intelligence.controls.system_status import ProviderStatus
from portfolio_intelligence.exchange.bybit_contracts import BybitReadOnlyEndpoint
from portfolio_intelligence.exchange.bybit_mapping import position_to_snapshot, system_status_to_internal, ticker_to_market_state
from portfolio_intelligence.exchange.bybit_models import PositionInfo, Ticker
from portfolio_intelligence.exchange.bybit_readonly_client import BybitReadOnlyClient
from portfolio_intelligence.exchange.bybit import BybitProvider
from portfolio_intelligence.exchange.transport import ReplayTransport
from portfolio_intelligence.hardening.readiness import build_readiness_report
from portfolio_intelligence.reconciliation.engine import reconcile_positions
from portfolio_intelligence.reconciliation.models import PositionSnapshot


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)
FIXTURES = Path(__file__).parent / "fixtures" / "bybit"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@pytest.mark.asyncio
async def test_bybit_replay_flows_to_internal_state_and_safety_controls() -> None:
    responses = {
        BybitReadOnlyEndpoint.SYSTEM_STATUS.value: fixture("system_status.json"),
        BybitReadOnlyEndpoint.TICKERS.value: fixture("ticker_egldusdt.json"),
        BybitReadOnlyEndpoint.POSITION_LIST.value: fixture("position_list.json"),
    }
    transport = ReplayTransport(responses)
    client = BybitReadOnlyClient(transport)

    status_payload = await client.system_status()
    status = system_status_to_internal(status_payload["result"]["status"], status_id=status_payload["result"]["statusId"])
    ticker_payload = await client.ticker("linear", "EGLDUSDT")
    ticker_data = ticker_payload["result"]["list"][0]
    market = ticker_to_market_state(Ticker(symbol=ticker_data["symbol"], last_price=Decimal(ticker_data["lastPrice"]), bid_price=Decimal(ticker_data["bid1Price"]), ask_price=Decimal(ticker_data["ask1Price"]), volume_24h=Decimal(ticker_data["volume24h"])), NOW)
    position_payload = await client.position_list("linear", "EGLDUSDT")
    position_data = position_payload["result"]["list"][0]
    external = position_to_snapshot(PositionInfo(symbol=position_data["symbol"], side=position_data["side"], size=Decimal(position_data["size"]), avg_price=Decimal(position_data["avgPrice"]), unrealised_pnl=Decimal(position_data["unrealisedPnl"]), leverage=Decimal(position_data["leverage"])))

    internal = PositionSnapshot(asset="EGLDUSDT", side="Buy", quantity=Decimal("10"), average_entry=Decimal("14.500"))
    reconciliation = reconcile_positions([internal], [external])
    readiness = build_readiness_report(Settings(), BybitProvider())
    breaker = CircuitBreaker()

    assert market.asset == "EGLDUSDT"
    assert status.status == ProviderStatus.OPERATIONAL
    assert reconciliation.clean is True
    assert readiness.ready is True
    assert breaker.execution_allowed(status) is True
    assert transport.calls[0][0] == BybitReadOnlyEndpoint.SYSTEM_STATUS.value


def test_fixture_files_are_present() -> None:
    required = {"system_status.json", "ticker_egldusdt.json", "instrument_egldusdt.json", "wallet_balance.json", "position_list.json", "orderbook_egldusdt.json"}
    assert required.issubset({path.name for path in FIXTURES.iterdir()})
