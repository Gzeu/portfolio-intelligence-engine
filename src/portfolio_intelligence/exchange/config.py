from __future__ import annotations

from enum import StrEnum

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BybitEnvironment(StrEnum):
    TESTNET = "testnet"
    MAINNET = "mainnet"


class BybitSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BYBIT_", extra="ignore")

    environment: BybitEnvironment = BybitEnvironment.TESTNET
    api_key: str | None = None
    api_secret: SecretStr | None = None
    read_only: bool = True
    live_orders_enabled: bool = False

    @property
    def rest_base_url(self) -> str:
        return "https://api-testnet.bybit.com" if self.environment == BybitEnvironment.TESTNET else "https://api.bybit.com"

    @property
    def websocket_base_url(self) -> str:
        return "wss://stream-testnet.bybit.com" if self.environment == BybitEnvironment.TESTNET else "wss://stream.bybit.com"

    def can_submit_orders(self) -> bool:
        return bool(self.live_orders_enabled and not self.read_only and self.api_key and self.api_secret)
