from decimal import Decimal

from portfolio_intelligence.reconciliation.engine import reconcile_positions
from portfolio_intelligence.reconciliation.models import BreakType, PositionSnapshot


def position(asset: str, side: str = "LONG", quantity: str = "10") -> PositionSnapshot:
    return PositionSnapshot(asset=asset, side=side, quantity=Decimal(quantity), average_entry=Decimal("14.5"))


def test_matching_snapshots_are_clean() -> None:
    report = reconcile_positions([position("EGLDUSDT")], [position("EGLDUSDT")])
    assert report.clean is True
    assert report.execution_allowed is True
    assert report.breaks == ()


def test_quantity_mismatch_blocks_execution() -> None:
    report = reconcile_positions([position("EGLDUSDT", quantity="10")], [position("EGLDUSDT", quantity="12")])
    assert report.clean is False
    assert report.execution_allowed is False
    assert report.breaks[0].break_type == BreakType.QUANTITY_MISMATCH


def test_missing_provider_position_is_material() -> None:
    report = reconcile_positions([position("EGLDUSDT")], [])
    assert report.breaks[0].break_type == BreakType.MISSING_EXTERNAL
    assert report.breaks[0].material is True


def test_side_mismatch_is_always_material() -> None:
    report = reconcile_positions([position("EGLDUSDT", "LONG")], [position("EGLDUSDT", "SHORT")])
    assert report.breaks[0].break_type == BreakType.SIDE_MISMATCH
    assert report.execution_allowed is False
