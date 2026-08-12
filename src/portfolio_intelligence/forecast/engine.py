from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from portfolio_intelligence.domain.models import Forecast, Opportunity
from portfolio_intelligence.market_intelligence.features import MarketFeatures


class ForecastHorizon(StrEnum):
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"


def build_forecast(
    opportunity: Opportunity,
    features: MarketFeatures,
    horizon: ForecastHorizon,
    valid_until: datetime,
    model_version: str = "baseline-distribution-v1",
) -> Forecast:
    if valid_until <= features.timestamp:
        raise ValueError("forecast validity must be after feature timestamp")
    directional = max(Decimal("0"), min(Decimal("1"), abs(features.directional_bias)))
    up = Decimal("0.33") + directional * Decimal("0.40")
    down = Decimal("0.33") - directional * Decimal("0.20")
    range_probability = Decimal("1") - up - down
    if opportunity.side.value == "SHORT":
        up, down = down, up
    distribution = {"up": up, "range": range_probability, "down": down}
    confidence = max(up, down)
    expected_return = (up - down) * max(features.volatility, Decimal("0.001")) * Decimal("10")
    expected_loss = max(Decimal("0"), down * features.volatility * Decimal("10"))
    return Forecast(forecast_id=f"fc_{opportunity.opportunity_id}_{horizon.value}", opportunity_id=opportunity.opportunity_id, horizon=horizon.value, created_at=features.timestamp, valid_until=valid_until, distribution=distribution, expected_return=expected_return, expected_loss=expected_loss, confidence_declared=confidence, model_version=model_version)


def build_multi_horizon_forecasts(opportunity: Opportunity, features: MarketFeatures, validity: dict[ForecastHorizon, datetime], model_version: str = "baseline-distribution-v1") -> list[Forecast]:
    return [build_forecast(opportunity, features, horizon, valid_until, model_version) for horizon, valid_until in validity.items()]
