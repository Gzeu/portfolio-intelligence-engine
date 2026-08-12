from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from portfolio_intelligence.domain.models import Forecast, StrictModel


class RankingInput(StrictModel):
    candidate_id: str
    asset: str
    expected_edge: Decimal
    risk: Decimal = Field(ge=0, le=1)
    correlation: Decimal = Field(ge=-1, le=1)
    liquidity_score: Decimal = Field(ge=0, le=1)
    execution_quality: Decimal = Field(ge=0, le=1)
    forecast_calibration: Decimal = Field(ge=0, le=1)


class RankedCandidate(StrictModel):
    candidate_id: str
    asset: str
    score: Decimal
    rank: int


def score_candidate(candidate: RankingInput) -> Decimal:
    correlation_penalty = abs(candidate.correlation) * Decimal("0.3")
    score = (
        candidate.expected_edge * Decimal("1.0")
        - candidate.risk * Decimal("1.2")
        - correlation_penalty
        + candidate.liquidity_score * Decimal("0.4")
        + candidate.execution_quality * Decimal("0.5")
        + candidate.forecast_calibration * Decimal("0.6")
    )
    return score


def rank_candidates(candidates: list[RankingInput]) -> list[RankedCandidate]:
    scored = sorted(candidates, key=score_candidate, reverse=True)
    return [RankedCandidate(candidate_id=candidate.candidate_id, asset=candidate.asset, score=score_candidate(candidate), rank=index + 1) for index, candidate in enumerate(scored)]


def minimum_confidence_from_forecasts(forecasts: list[Forecast]) -> Decimal:
    if not forecasts:
        return Decimal("0")
    return min(forecast.confidence_declared for forecast in forecasts)
