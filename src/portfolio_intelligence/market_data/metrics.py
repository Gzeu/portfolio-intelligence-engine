from __future__ import annotations

from decimal import Decimal

from portfolio_intelligence.market_data.orderbook import OrderBook


class IncompleteOrderBook(ValueError):
    pass


def mid_price(book: OrderBook) -> Decimal:
    bid = book.best_bid()
    ask = book.best_ask()
    if bid is None or ask is None:
        raise IncompleteOrderBook("mid-price requires both best bid and best ask")
    return (bid.price + ask.price) / Decimal("2")


def spread(book: OrderBook) -> Decimal:
    bid = book.best_bid()
    ask = book.best_ask()
    if bid is None or ask is None:
        raise IncompleteOrderBook("spread requires both best bid and best ask")
    return ask.price - bid.price


def spread_bps(book: OrderBook) -> Decimal:
    return spread(book) / mid_price(book) * Decimal("10000")


def depth_within_band(book: OrderBook, band_pct: Decimal) -> tuple[Decimal, Decimal]:
    if band_pct < 0:
        raise ValueError("band_pct must be non-negative")
    mid = mid_price(book)
    band = band_pct / Decimal("100")
    bid_floor = mid * (Decimal("1") - band)
    ask_ceiling = mid * (Decimal("1") + band)
    bid_depth = sum((price * qty for price, qty in book.bids.items() if price >= bid_floor), Decimal("0"))
    ask_depth = sum((price * qty for price, qty in book.asks.items() if price <= ask_ceiling), Decimal("0"))
    return bid_depth, ask_depth


def volume_imbalance(book: OrderBook) -> Decimal:
    bid_volume = sum(book.bids.values(), Decimal("0"))
    ask_volume = sum(book.asks.values(), Decimal("0"))
    total = bid_volume + ask_volume
    if total == 0:
        raise IncompleteOrderBook("volume imbalance requires non-empty depth")
    return (bid_volume - ask_volume) / total
