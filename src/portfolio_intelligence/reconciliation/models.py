from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from portfolio_intelligence.domain.models import StrictModel


class BreakType(StrEnum):
    MISSING_INTERNAL = "MISSING_INTERNAL"
    MISSING_EXTERNAL = "MISSING_EXTERNAL"
    QUANTITY_MISMATCH = "QUANTITY_MISMATCH"
    SIDE_MISMATCH = "SIDE_MISMATCH"


class PositionSnapshot(StrictModel):
    asset: str
    side: str
    quantity: Decimal = Field(ge=0)
    average_entry: Decimal = Field(gt=0)


class ReconciliationBreak(StrictModel):
    asset: str
    break_type: BreakType
    internal: PositionSnapshot | None = None
    external: PositionSnapshot | None = None
    difference: Decimal = Field(ge=0)
    material: bool
    reason: str


class ReconciliationReport(StrictModel):
    clean: bool
    execution_allowed: bool
    breaks: tuple[ReconciliationBreak, ...]
    checked_assets: tuple[str, ...]
