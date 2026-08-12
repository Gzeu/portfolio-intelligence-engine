from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from portfolio_intelligence.decision_memory.attribution import AttributionLabel, attribute_error
from portfolio_intelligence.decision_memory.calibration import CalibrationBucketObservation, build_calibration_record, expected_calibration_error
from portfolio_intelligence.decision_memory.case import DecisionCase, Outcome, OutcomeExit, close_case
from portfolio_intelligence.decision_memory.promotion import PromotionRequest, PromotionStage, evaluate_promotion


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def test_case_cannot_close_twice() -> None:
    case = DecisionCase(case_id="case_1", opportunity_id="opp_1", forecast_id="fc_1", decision_id="cd_1", asset="EGLDUSDT", horizon="15m", confidence_declared=Decimal("0.72"), predicted_direction="up", created_at=NOW)
    outcome = Outcome(realized_pnl=Decimal("12.5"), mae=Decimal("3"), mfe=Decimal("15"), fees=Decimal("1.2"), slippage_bps=Decimal("8"), exit_reason=OutcomeExit.TAKE_PROFIT, closed_at=NOW + timedelta(minutes=15))
    closed = close_case(case, outcome)
    assert closed.outcome is not None
    with pytest.raises(ValueError):
        close_case(closed, outcome)


def test_error_attribution_marks_correct_forecast_and_good_execution() -> None:
    case = DecisionCase(case_id="case_2", opportunity_id="opp_2", forecast_id="fc_2", decision_id="cd_2", asset="EGLDUSDT", horizon="15m", confidence_declared=Decimal("0.80"), predicted_direction="up", created_at=NOW)
    outcome = Outcome(realized_pnl=Decimal("20"), mae=Decimal("2"), mfe=Decimal("21"), fees=Decimal("1"), slippage_bps=Decimal("6"), exit_reason=OutcomeExit.TAKE_PROFIT, closed_at=NOW + timedelta(minutes=15))
    closed = close_case(case, outcome)
    attribution = attribute_error(closed, actual_direction="up", entry_slippage_bps=5, execution_slippage_bps=8, risk_budget_used=Decimal("0.6"))
    assert attribution.forecast == AttributionLabel.CORRECT
    assert attribution.entry == AttributionLabel.GOOD
    assert attribution.execution == AttributionLabel.GOOD


def test_calibration_record_detects_overconfidence() -> None:
    observations = [CalibrationBucketObservation(declared_confidence=Decimal("0.80"), was_correct=(i < 73)) for i in range(100)]
    record = build_calibration_record("EGLDUSDT", "15m", observations)
    assert record.sample_count == 100
    assert record.empirical_rate == Decimal("0.73")
    assert record.calibration_error == Decimal("0.07")
    assert expected_calibration_error([record]) == record.calibration_error


def test_promotion_rejects_when_sample_too_small() -> None:
    calibration = build_calibration_record("EGLDUSDT", "15m", [CalibrationBucketObservation(declared_confidence=Decimal("0.8"), was_correct=True)])
    request = PromotionRequest(candidate_name="breakout_v2", sample_count=20, walk_forward_passed=True, out_of_sample_passed=True, cost_aware_validation_passed=True, max_drawdown=Decimal("0.05"))
    decision = evaluate_promotion(request, calibration)
    assert decision.stage == PromotionStage.REJECTED
    assert any("sample_count" in reason for reason in decision.reasons)


def test_promotion_passes_when_all_gates_are_satisfied() -> None:
    observations = [CalibrationBucketObservation(declared_confidence=Decimal("0.75"), was_correct=(i < 113)) for i in range(150)]
    calibration = build_calibration_record("EGLDUSDT", "15m", observations)
    request = PromotionRequest(candidate_name="breakout_v2", sample_count=150, walk_forward_passed=True, out_of_sample_passed=True, cost_aware_validation_passed=True, max_drawdown=Decimal("0.06"))
    decision = evaluate_promotion(request, calibration)
    assert decision.stage == PromotionStage.PROMOTED
