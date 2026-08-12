from datetime import datetime, timezone
from decimal import Decimal

import pytest

from portfolio_intelligence.controls.system_status import ProviderStatus
from portfolio_intelligence.exchange.bybit_mapping import instrument_is_tradable, position_to_snapshot, system_status_to_internal, ticker_to_market_state, wallet_to_account_state
from portfolio_intelligence.exchange.bybit_models import InstrumentInfo, PositionInfo, Ticker, WalletBalance


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def test_ticker_maps_to_market_state_and_derives_spread() -> None:
    ticker = Ticker(symbol="EGLDUSDT", last_price=Decimal("14.5"), bid_price=Decimal("14.49"), ask_price=Decimal("14.51"), volume_24h=Decimal("1000000"))
    state = ticker_to_market_state(ticker, NOW)
    assert state.asset == "EGLDUSDT"
    assert state.spread_bps > 0
    assert state.liquidity_state == "healthy"


def test_invalid_ticker_is_rejected() -> None:
    ticker = Ticker(symbol="EGLDUSDT", last_price=Decimal("14.5"), bid_price=Decimal("14.52"), ask_price=Decimal("14.51"), volume_24h=Decimal("1000000"))
    with pytest.raises(ValueError):
        ticker_to_market_state(ticker, NOW)


def test_wallet_maps_to_account_state() -> None:
    wallet = WalletBalance(account_type="UNIFIED", total_equity=Decimal("10000"), total_available_balance=Decimal("8000"), total_margin_balance=Decimal("10000"))
    state = wallet_to_account_state(wallet, "acc_1", NOW)
    assert state.equity == Decimal("10000")
    assert state.used_margin == Decimal("2000")
    assert state.leverage == Decimal("0.2")


def test_position_and_status_mapping() -> None:
    position = PositionInfo(symbol="EGLDUSDT", side="Buy", size=Decimal("10"), avg_price=Decimal("14.5"), unrealised_pnl=Decimal("2"), leverage=Decimal("1"))
    snapshot = position_to_snapshot(position)
    assert snapshot.asset == "EGLDUSDT"
    assert snapshot.quantity == Decimal("10")
    assert system_status_to_internal("normal").status == ProviderStatus.OPERATIONAL
    assert system_status_to_internal("maintenance").status == ProviderStatus.MAINTENANCE
    assert system_status_to_internal("unexpected").status == ProviderStatus.UNKNOWN


def test_instrument_tradability_mapping() -> None:
    instrument = InstrumentInfo(symbol="EGLDUSDT", status="Trading", tick_size=Decimal("0.001"), qty_step=Decimal("0.1"))
    assert instrument_is_tradable(instrument) is True
