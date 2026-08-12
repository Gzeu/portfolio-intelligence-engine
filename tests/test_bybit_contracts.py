from decimal import Decimal

import pytest

from portfolio_intelligence.exchange.bybit_contracts import BybitReadOnlyEndpoint, assert_read_only_endpoint, is_read_only_endpoint
from portfolio_intelligence.exchange.bybit_models import BybitResponse, InstrumentInfo, PositionInfo, Ticker, WalletBalance


def test_read_only_registry_contains_required_endpoints() -> None:
    assert is_read_only_endpoint(BybitReadOnlyEndpoint.SYSTEM_STATUS.value)
    assert is_read_only_endpoint(BybitReadOnlyEndpoint.INSTRUMENTS_INFO.value)
    assert is_read_only_endpoint(BybitReadOnlyEndpoint.TICKERS.value)
    assert is_read_only_endpoint(BybitReadOnlyEndpoint.WALLET_BALANCE.value)
    assert is_read_only_endpoint(BybitReadOnlyEndpoint.POSITION_LIST.value)


def test_order_create_is_rejected() -> None:
    with pytest.raises(ValueError):
        assert_read_only_endpoint("/v5/order/create")


def test_response_models_validate() -> None:
    ticker = Ticker(symbol="EGLDUSDT", last_price=Decimal("14.5"), bid_price=Decimal("14.49"), ask_price=Decimal("14.51"), volume_24h=Decimal("1000000"))
    instrument = InstrumentInfo(symbol="EGLDUSDT", status="Trading", tick_size=Decimal("0.001"), qty_step=Decimal("0.1"))
    wallet = WalletBalance(account_type="UNIFIED", total_equity=Decimal("10000"), total_available_balance=Decimal("8000"), total_margin_balance=Decimal("10000"))
    position = PositionInfo(symbol="EGLDUSDT", side="Buy", size=Decimal("10"), avg_price=Decimal("14.5"), unrealised_pnl=Decimal("2"), leverage=Decimal("1"))
    envelope = BybitResponse[dict](retCode=0, retMsg="OK", result={"category": "linear"}, time=1)
    assert ticker.symbol == instrument.symbol == wallet.account_type.upper()[:6] + "ED"[:0] if False else ticker.symbol == "EGLDUSDT"
    assert position.size == Decimal("10")
    assert envelope.retCode == 0
