from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from portfolio_intelligence.domain.models import Forecast, StrictModel


class ScenarioKind(StrEnum):
    PRIMARY = "PRIMARY"
    IF = "IF"
    INVALIDATION = "INVALIDATION"


class ScenarioNode(StrictModel):
    node_id: str
    forecast_id: str
    kind: ScenarioKind
    condition: str
    probability: Decimal = Field(ge=0, le=1)
    action_effect: str
    parent_node_id: str | None = None


def build_scenario_tree(forecast: Forecast, setup: str = "continuation") -> tuple[ScenarioNode, ...]:
    primary_id = f"{forecast.forecast_id}:primary"
    return (
        ScenarioNode(node_id=primary_id, forecast_id=forecast.forecast_id, kind=ScenarioKind.PRIMARY, condition=setup, probability=forecast.confidence_declared, action_effect="maintain opportunity quality"),
        ScenarioNode(node_id=f"{forecast.forecast_id}:confirm", forecast_id=forecast.forecast_id, kind=ScenarioKind.IF, condition="breakout and volume confirmation", probability=Decimal("0.50"), action_effect="increase opportunity quality", parent_node_id=primary_id),
        ScenarioNode(node_id=f"{forecast.forecast_id}:pullback", forecast_id=forecast.forecast_id, kind=ScenarioKind.IF, condition="pullback and structure holds", probability=Decimal("0.35"), action_effect="passive entry opportunity", parent_node_id=primary_id),
        ScenarioNode(node_id=f"{forecast.forecast_id}:invalid", forecast_id=forecast.forecast_id, kind=ScenarioKind.INVALIDATION, condition="15m structure breaks or liquidity becomes unhealthy", probability=Decimal("1"), action_effect="invalidate forecast", parent_node_id=primary_id),
    )


def validate_point_in_time(forecast: Forecast, feature_timestamp) -> None:
    if forecast.created_at < feature_timestamp:
        raise ValueError("forecast cannot be created before its feature snapshot")
