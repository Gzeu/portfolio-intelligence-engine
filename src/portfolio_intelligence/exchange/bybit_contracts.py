from __future__ import annotations

from enum import StrEnum


class BybitReadOnlyEndpoint(StrEnum):
    SYSTEM_STATUS = "/v5/system/status"
    INSTRUMENTS_INFO = "/v5/market/instruments-info"
    TICKERS = "/v5/market/tickers"
    WALLET_BALANCE = "/v5/account/wallet-balance"
    POSITION_LIST = "/v5/position/list"


READ_ONLY_ENDPOINTS = frozenset(BybitReadOnlyEndpoint)


def is_read_only_endpoint(path: str) -> bool:
    return path in READ_ONLY_ENDPOINTS


def assert_read_only_endpoint(path: str) -> None:
    if not is_read_only_endpoint(path):
        raise ValueError(f"endpoint is not allowed in read-only mode: {path}")
