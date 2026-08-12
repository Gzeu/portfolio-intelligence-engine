from __future__ import annotations

from decimal import Decimal

from portfolio_intelligence.market_data.events import BookEventType, OrderBookEvent, PriceLevel


class OrderBookGap(RuntimeError):
    pass


class OrderBook:
    def __init__(self) -> None:
        self.symbol: str | None = None
        self.last_update_id: int | None = None
        self.bids: dict[Decimal, Decimal] = {}
        self.asks: dict[Decimal, Decimal] = {}

    def apply(self, event: OrderBookEvent) -> None:
        if self.symbol is not None and event.symbol != self.symbol:
            raise ValueError("orderbook symbol mismatch")
        if event.event_type == BookEventType.SNAPSHOT:
            self.symbol = event.symbol
            self.bids = {level.price: level.quantity for level in event.bids if level.quantity > 0}
            self.asks = {level.price: level.quantity for level in event.asks if level.quantity > 0}
            self.last_update_id = event.update_id
            return
        if self.last_update_id is None:
            raise OrderBookGap("delta received before snapshot")
        if event.update_id != self.last_update_id + 1:
            raise OrderBookGap(f"expected update {self.last_update_id + 1}, got {event.update_id}")
        self._apply_levels(self.bids, event.bids)
        self._apply_levels(self.asks, event.asks)
        self.last_update_id = event.update_id

    @staticmethod
    def _apply_levels(book: dict[Decimal, Decimal], levels: tuple[PriceLevel, ...]) -> None:
        for level in levels:
            if level.quantity == 0:
                book.pop(level.price, None)
            else:
                book[level.price] = level.quantity

    def best_bid(self) -> PriceLevel | None:
        return self._best(self.bids, reverse=True)

    def best_ask(self) -> PriceLevel | None:
        return self._best(self.asks, reverse=False)

    @staticmethod
    def _best(book: dict[Decimal, Decimal], reverse: bool) -> PriceLevel | None:
        if not book:
            return None
        price = sorted(book, reverse=reverse)[0]
        return PriceLevel(price=price, quantity=book[price])
