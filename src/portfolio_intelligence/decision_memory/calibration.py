from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from portfolio_intelligence.domain.models import StrictModel


class CalibrationBucketObservation(StrictModel):
    declared_confidence: Decimal = Field(ge=0, le=1)
    was_correct: bool


class CalibrationRecord(StrictModel):
    segment: str
    horizon: str
    sample_count: int = Field(ge=0)
    declared_mean: Decimal = Field(ge=0, le=1)
    empirical_rate: Decimal = Field(ge=0, le=1)
    calibration_error: Decimal = Field(ge=0, le=1)


def build_calibration_record(segment: str, horizon: str, observations: list[CalibrationBucketObservation]) -> CalibrationRecord:
    if not observations:
        return CalibrationRecord(segment=segment, horizon=horizon, sample_count=0, declared_mean=Decimal("0"), empirical_rate=Decimal("0"), calibration_error=Decimal("0"))
    declared_mean = sum(observation.declared_confidence for observation in observations) / len(observations)
    empirical_rate = Decimal(sum(1 for observation in observations if observation.was_correct)) / len(observations)
    calibration_error = abs(declared_mean - empirical_rate)
    return CalibrationRecord(segment=segment, horizon=horizon, sample_count=len(observations), declared_mean=declared_mean, empirical_rate=empirical_rate, calibration_error=calibration_error)


def expected_calibration_error(records: list[CalibrationRecord]) -> Decimal:
    total_samples = sum(record.sample_count for record in records)
    if total_samples == 0:
        return Decimal("0")
    weighted = sum(record.calibration_error * record.sample_count for record in records)
    return weighted / total_samples
