from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from portfolio_intelligence.domain.models import AccountState, MarketState
from portfolio_intelligence.exchange.bybit_models import InstrumentInfo, PositionInfo, Ticker, WalletBalance
from portfolio_intelligence.controls.system_status import ProviderStatus, SystemStatus
from portfolio_intelligence.reconciliation.models import PositionSnapshot


def ticker_to_market_state(ticker: Ticker, timestamp: datetime) -> MarketState:
    if ticker.bid_price > ticker.ask_price:
        raise ValueError("ticker bid price cannot exceed ask price")
    mid = (ticker.bid_price + ticker.ask_price) / Decimal("2")
    spread_bps = Decimal("0") if mid == 0 else ((ticker.ask_price - ticker.bid_price) / mid) * Decimal("10000")
    return MarketState(asset=ticker.symbol, timestamp=timestamp, price=ticker.last_price, bid=ticker.bid_price, ask=ticker.ask_price, spread_bps=spread_bps, volume=ticker.volume_24h, volatility=Decimal("0"), liquidity_state="healthy" if spread_bps <= Decimal("25") else "degraded")


def wallet_to_account_state(wallet: WalletBalance, account_id: str, timestamp: datetime) -> AccountState:
    used_margin = max(Decimal("0"), wallet.total_margin_balance - wallet.total_available_balance)
    leverage = Decimal("0") if wallet.total_equity == 0 else used_margin / wallet.total_equity
    return AccountState(account_id=account_id, timestamp=timestamp, equity=wallet.total_equity, available_margin=wallet.total_available_balance, used_margin=used_margin, unrealized_pnl=Decimal("0"), realized_pnl=Decimal("0"), gross_exposure=Decimal("0"), net_exposure=Decimal("0"), leverage=leverage)


def position_to_snapshot(position: PositionInfo) -> PositionSnapshot:
    return PositionSnapshot(asset=position.symbol, side=position.side, quantity=position.size, average_entry=position.avg_price)


def system_status_to_internal(status: str, details: str = "", status_id: str | None = None) -> SystemStatus:
    normalized = status.strip().lower()
    mapping = {"normal": ProviderStatus.OPERATIONAL, "operational": ProviderStatus.OPERATIONAL, "maintenance": ProviderStatus.MAINTENANCE, "incident": ProviderStatus.INCIDENT}
    return SystemStatus(provider="bybit", status=mapping.get(normalized, ProviderStatus.UNKNOWN), status_id=status_id, details=details)


def instrument_is_tradable(instrument: InstrumentInfo) -> bool:
    return instrument.status.lower() in {"trading", "online", "launched"}
