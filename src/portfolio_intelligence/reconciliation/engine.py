from __future__ import annotations

from decimal import Decimal

from portfolio_intelligence.reconciliation.models import BreakType, PositionSnapshot, ReconciliationBreak, ReconciliationReport


def reconcile_positions(internal: list[PositionSnapshot], external: list[PositionSnapshot], quantity_tolerance: Decimal = Decimal("0.000001"), material_difference: Decimal = Decimal("0.001")) -> ReconciliationReport:
    if quantity_tolerance < 0 or material_difference < 0:
        raise ValueError("tolerances must be non-negative")
    internal_by_asset = {position.asset: position for position in internal}
    external_by_asset = {position.asset: position for position in external}
    breaks: list[ReconciliationBreak] = []
    assets = sorted(set(internal_by_asset) | set(external_by_asset))
    for asset in assets:
        local = internal_by_asset.get(asset)
        remote = external_by_asset.get(asset)
        if local is None:
            breaks.append(ReconciliationBreak(asset=asset, break_type=BreakType.MISSING_INTERNAL, external=remote, difference=remote.quantity, material=remote.quantity > material_difference, reason="provider position is absent from internal state"))
        elif remote is None:
            breaks.append(ReconciliationBreak(asset=asset, break_type=BreakType.MISSING_EXTERNAL, internal=local, difference=local.quantity, material=local.quantity > material_difference, reason="internal position is absent from provider state"))
        elif local.side != remote.side:
            breaks.append(ReconciliationBreak(asset=asset, break_type=BreakType.SIDE_MISMATCH, internal=local, external=remote, difference=abs(local.quantity - remote.quantity), material=True, reason="position sides differ"))
        elif abs(local.quantity - remote.quantity) > quantity_tolerance:
            difference = abs(local.quantity - remote.quantity)
            breaks.append(ReconciliationBreak(asset=asset, break_type=BreakType.QUANTITY_MISMATCH, internal=local, external=remote, difference=difference, material=difference > material_difference, reason="position quantities exceed tolerance"))
    clean = not breaks
    return ReconciliationReport(clean=clean, execution_allowed=clean, breaks=tuple(breaks), checked_assets=tuple(assets))
