from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from portfolio_intelligence.decision_memory.calibration import CalibrationRecord
from portfolio_intelligence.domain.models import StrictModel


class PromotionStage(StrEnum):
    OBSERVATION = "OBSERVATION"
    CALIBRATION = "CALIBRATION"
    CANDIDATE_PROMOTION = "CANDIDATE_PROMOTION"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"


class PromotionRequest(StrictModel):
    candidate_name: str
    sample_count: int = Field(ge=0)
    walk_forward_passed: bool
    out_of_sample_passed: bool
    cost_aware_validation_passed: bool
    max_drawdown: Decimal = Field(ge=0, le=1)


class PromotionDecision(StrictModel):
    candidate_name: str
    stage: PromotionStage
    reasons: tuple[str, ...]


def evaluate_promotion(request: PromotionRequest, calibration: CalibrationRecord, minimum_sample: int = 100, max_allowed_drawdown: Decimal = Decimal("0.10"), max_calibration_error: Decimal = Decimal("0.15")) -> PromotionDecision:
    reasons: list[str] = []
    if request.sample_count < minimum_sample:
        reasons.append(f"sample_count {request.sample_count} below minimum {minimum_sample}")
    if not request.walk_forward_passed:
        reasons.append("walk-forward validation failed")
    if not request.out_of_sample_passed:
        reasons.append("out-of-sample validation failed")
    if not request.cost_aware_validation_passed:
        reasons.append("cost-aware validation failed")
    if request.max_drawdown > max_allowed_drawdown:
        reasons.append("max_drawdown exceeds allowed threshold")
    if calibration.calibration_error > max_calibration_error:
        reasons.append("calibration error exceeds allowed threshold")

    if reasons:
        stage = PromotionStage.REJECTED
    else:
        stage = PromotionStage.PROMOTED
        reasons.append("all promotion gates passed")

    return PromotionDecision(candidate_name=request.candidate_name, stage=stage, reasons=tuple(reasons))
