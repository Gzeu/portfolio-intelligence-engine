from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Protocol

from portfolio_intelligence.market_data.quality import MarketQualitySnapshot, MarketQualityStatus


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class OrderIntent:
    symbol: str
    side: OrderSide
    quantity: Decimal
    limit_price: Decimal
    reason: str


class Strategy(Protocol):
    def decide(self, market: MarketQualitySnapshot) -> OrderIntent | None:
        ...


@dataclass(frozen=True)
class QualityGatedStrategy:
    symbol: str
    side: OrderSide
    quantity: Decimal
    min_mid_price: Decimal

    def decide(self, market: MarketQualitySnapshot) -> OrderIntent | None:
        if market.status != MarketQualityStatus.READY or market.mid_price is None or market.mid_price < self.min_mid_price:
            return None
        return OrderIntent(self.symbol, self.side, self.quantity, market.mid_price, "quality_gate_passed")
