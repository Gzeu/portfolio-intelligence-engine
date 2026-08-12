from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeMode(StrEnum):
    ANALYSIS = "analysis"
    PAPER = "paper"
    SHADOW = "shadow"
    LIVE = "live"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIE_", extra="ignore")

    app_name: str = "portfolio-intelligence-engine"
    environment: str = "development"
    runtime_mode: RuntimeMode = RuntimeMode.ANALYSIS
    schema_version: str = "1.0"
    timezone: str = "UTC"
    max_position_risk: Decimal = Decimal("0.01")
    max_daily_loss: Decimal = Decimal("0.03")
    max_leverage: Decimal = Decimal("3")
    max_portfolio_drawdown: Decimal = Decimal("0.10")
    max_slippage_bps: Decimal = Decimal("25")
    live_trading_enabled: bool = False

    def can_submit_live_orders(self) -> bool:
        return self.runtime_mode == RuntimeMode.LIVE and self.live_trading_enabled


def load_settings() -> Settings:
    return Settings()
