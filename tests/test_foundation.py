from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path

import pytest

from portfolio_intelligence.config import RuntimeMode, Settings
from portfolio_intelligence.domain.models import AccountState, CapitalDecision, DecisionAction, MarketState, PortfolioSnapshot
from portfolio_intelligence.events.schemas import EventEnvelope, validate_event_type
from portfolio_intelligence.risk.limits import RiskViolation, assert_live_orders_allowed, validate_capital_decision


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def load_fixture(name: str) -> dict:
    return json.loads((Path(__file__).parent / "fixtures" / name).read_text())


def test_fixtures_validate_as_domain_models() -> None:
    MarketState.model_validate(load_fixture("market_state.json"))
    PortfolioSnapshot.model_validate(load_fixture("portfolio_state.json"))


def test_settings_are_fail_closed_by_default() -> None:
    settings = Settings()
    assert settings.runtime_mode == RuntimeMode.ANALYSIS
    assert not settings.can_submit_live_orders()
    with pytest.raises(RiskViolation):
        assert_live_orders_allowed(settings)


def test_event_type_is_allowlisted() -> None:
    event = EventEnvelope(event_id="evt_1", event_type="market.state.updated", occurred_at=NOW, aggregate_id="EGLDUSDT", source="fixture")
    assert validate_event_type(event).event_type == "market.state.updated"
    invalid = event.model_copy(update={"event_type": "unknown.event"})
    with pytest.raises(ValueError):
        validate_event_type(invalid)


def test_risk_rejects_excessive_position_risk() -> None:
    account = AccountState(account_id="acc", timestamp=NOW, equity=Decimal("10000"), available_margin=Decimal("7000"), used_margin=Decimal("3000"), unrealized_pnl=Decimal("0"), realized_pnl=Decimal("0"), gross_exposure=Decimal("2500"), net_exposure=Decimal("500"), leverage=Decimal("1"))
    portfolio = PortfolioSnapshot.model_validate(load_fixture("portfolio_state.json"))
    decision = CapitalDecision(decision_id="d1", candidate_id="o1", decision=DecisionAction.APPROVE, approved_size=Decimal("100"), risk_consumed=Decimal("0.02"), reasons=("test",), created_at=NOW, expires_at=NOW.replace(minute=30))
    with pytest.raises(RiskViolation):
        validate_capital_decision(decision, account, portfolio, Settings())
