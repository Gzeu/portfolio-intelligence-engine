from __future__ import annotations

from enum import StrEnum

from portfolio_intelligence.domain.models import StrictModel
from portfolio_intelligence.decision_memory.case import DecisionCase, OutcomeExit


class AttributionLabel(StrEnum):
    CORRECT = "correct"
    WRONG = "wrong"
    GOOD = "good"
    BAD = "bad"
    EXCESSIVE = "excessive"
    PREMATURE = "premature"
    NEUTRAL = "neutral"


class ErrorAttribution(StrictModel):
    case_id: str
    forecast: AttributionLabel
    regime: AttributionLabel
    entry: AttributionLabel
    execution: AttributionLabel
    risk: AttributionLabel
    exit: AttributionLabel


def attribute_error(case: DecisionCase, actual_direction: str, entry_slippage_bps, execution_slippage_bps, risk_budget_used) -> ErrorAttribution:
    if case.outcome is None:
        raise ValueError("cannot attribute error before the case is closed")
    forecast_label = AttributionLabel.CORRECT if case.predicted_direction == actual_direction else AttributionLabel.WRONG
    regime_label = AttributionLabel.NEUTRAL if forecast_label == AttributionLabel.CORRECT else AttributionLabel.WRONG
    entry_label = AttributionLabel.GOOD if entry_slippage_bps <= 10 else AttributionLabel.BAD
    execution_label = AttributionLabel.GOOD if execution_slippage_bps <= 15 else AttributionLabel.BAD
    risk_label = AttributionLabel.EXCESSIVE if risk_budget_used > 1 else AttributionLabel.GOOD
    exit_label = AttributionLabel.PREMATURE if case.outcome.exit_reason == OutcomeExit.MANUAL and case.outcome.mfe > abs(case.outcome.realized_pnl) else AttributionLabel.GOOD
    return ErrorAttribution(case_id=case.case_id, forecast=forecast_label, regime=regime_label, entry=entry_label, execution=execution_label, risk=risk_label, exit=exit_label)
