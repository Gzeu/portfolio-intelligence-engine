from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from portfolio_intelligence.domain.models import StrictModel


class PositionStatus(StrEnum):
    OPENING = "OPENING"
    OPEN = "OPEN"
    REDUCING = "REDUCING"
    CLOSED = "CLOSED"


class Position(StrictModel):
    position_id: str
    asset: str
    side: str
    status: PositionStatus
    quantity: Decimal = Field(ge=0)
    average_entry: Decimal = Field(gt=0)
    realized_pnl: Decimal = Decimal("0")
    fees: Decimal = Field(ge=0)


def open_position(position_id: str, asset: str, side: str, quantity: Decimal, entry_price: Decimal, fees: Decimal = Decimal("0")) -> Position:
    if quantity <= 0 or entry_price <= 0:
        raise ValueError("quantity and entry_price must be positive")
    return Position(position_id=position_id, asset=asset, side=side, status=PositionStatus.OPEN, quantity=quantity, average_entry=entry_price, fees=fees)


def close_position(position: Position, exit_price: Decimal, quantity: Decimal | None = None, fees: Decimal = Decimal("0")) -> Position:
    if exit_price <= 0:
        raise ValueError("exit_price must be positive")
    closing = position.quantity if quantity is None else quantity
    if closing <= 0 or closing > position.quantity:
        raise ValueError("closing quantity must be positive and not exceed position")
    direction = Decimal("1") if position.side == "LONG" else Decimal("-1")
    pnl = (exit_price - position.average_entry) * closing * direction
    remaining = position.quantity - closing
    status = PositionStatus.CLOSED if remaining == 0 else PositionStatus.REDUCING
    return position.model_copy(update={"status": status, "quantity": remaining, "realized_pnl": position.realized_pnl + pnl, "fees": position.fees + fees})
