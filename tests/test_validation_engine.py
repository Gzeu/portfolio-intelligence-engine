from decimal import Decimal

from portfolio_intelligence.validation.metrics import capital_productivity, decision_efficiency, risk_productivity
from portfolio_intelligence.validation.replay import ReplayEvent, run_replay
from portfolio_intelligence.validation.walk_forward import assert_no_temporal_leakage, build_walk_forward_splits


def test_replay_is_sorted_and_cost_aware() -> None:
    events = [
        ReplayEvent(timestamp=2, asset="EGLDUSDT", expected_pnl=Decimal("5"), fees=Decimal("1"), slippage_cost=Decimal("0.5"), funding_cost=Decimal("0"), risk_consumed=Decimal("10"), decision_taken=True),
        ReplayEvent(timestamp=1, asset="EGLDUSDT", expected_pnl=Decimal("-2"), fees=Decimal("1"), slippage_cost=Decimal("0.5"), funding_cost=Decimal("0.2"), risk_consumed=Decimal("10"), decision_taken=True),
    ]
    result = run_replay(events, Decimal("100"))
    assert result.event_count == 2
    assert result.gross_pnl == Decimal("3")
    assert result.total_costs == Decimal("3.2")
    assert result.net_pnl == Decimal("-0.2")


def test_walk_forward_windows_do_not_overlap() -> None:
    splits = build_walk_forward_splits(0, 100, train_size=40, validation_size=10, test_size=10, step=10)
    assert len(splits) == 5
    for split in splits:
        assert_no_temporal_leakage(split)
        assert split.train.end <= split.validation.start <= split.validation.end <= split.test.start


def test_metrics_are_safe_for_zero_denominators() -> None:
    result = run_replay([], Decimal("100"))
    assert capital_productivity(result, Decimal("0")) == Decimal("0")
    assert risk_productivity(Decimal("1"), Decimal("0")) == Decimal("0")
    assert decision_efficiency(0, 0) == Decimal("0")
