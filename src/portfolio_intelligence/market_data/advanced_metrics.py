from __future__ import annotations

from decimal import Decimal

from portfolio_intelligence.market_data.orderbook import OrderBook


class IncompleteAdvancedBook(ValueError):
    pass


def microprice(book: OrderBook) -> Decimal:
    bid = book.best_bid()
    ask = book.best_ask()
    if bid is None or ask is None or bid.quantity + ask.quantity == 0:
        raise IncompleteAdvancedBook("microprice requires non-empty best bid and ask")
    return (bid.price * ask.quantity + ask.price * bid.quantity) / (bid.quantity + ask.quantity)


def top_n_depth(book: OrderBook, levels: int) -> tuple[Decimal, Decimal]:
    if levels < 1:
        raise ValueError("levels must be positive")
    bids = sorted(book.bids.items(), reverse=True)[:levels]
    asks = sorted(book.asks.items())[:levels]
    if not bids or not asks:
        raise IncompleteAdvancedBook("top-N depth requires both sides of the book")
    bid_depth = sum((price * quantity for price, quantity in bids), Decimal("0"))
    ask_depth = sum((price * quantity for price, quantity in asks), Decimal("0"))
    return bid_depth, ask_depth


def top_level_concentration(book: OrderBook, levels: int) -> tuple[Decimal, Decimal]:
    bid_depth, ask_depth = top_n_depth(book, levels)
    bid = book.best_bid()
    ask = book.best_ask()
    assert bid is not None and ask is not None
    return bid.price * bid.quantity / bid_depth, ask.price * ask.quantity / ask_depth
