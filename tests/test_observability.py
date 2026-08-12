from decimal import Decimal
import json

import pytest

from portfolio_intelligence.observability.health import HealthStatus, aggregate_health
from portfolio_intelligence.observability.logging import LogSeverity, structured_log
from portfolio_intelligence.observability.metrics import MetricsRegistry


def test_structured_log_is_json_and_redacts_secrets() -> None:
    record = json.loads(structured_log(LogSeverity.INFO, "decision evaluated", "capital_arbiter", api_key="secret", asset="EGLDUSDT"))
    assert record["severity"] == "INFO"
    assert record["fields"]["api_key"] == "[REDACTED]"
    assert record["fields"]["asset"] == "EGLDUSDT"


def test_health_aggregation_fails_closed() -> None:
    assert aggregate_health([]).healthy is False
    report = aggregate_health([HealthStatus(component="market", healthy=True, details="ok"), HealthStatus(component="bybit", healthy=False, details="readiness failed")])
    assert report.healthy is False


def test_metrics_registry_tracks_counters_latency_and_gauges() -> None:
    registry = MetricsRegistry()
    registry.increment("decision.approved")
    registry.increment("decision.approved", 2)
    registry.observe_latency("forecast.ms", Decimal("12.5"))
    registry.set_gauge("portfolio.drawdown", Decimal("0.02"))
    snapshot = registry.snapshot()
    assert snapshot["counters"]["decision.approved"] == 3
    assert snapshot["latency_ms"]["forecast.ms"] == (Decimal("12.5"),)
    assert snapshot["gauges"]["portfolio.drawdown"] == Decimal("0.02")
    with pytest.raises(ValueError):
        registry.observe_latency("bad", Decimal("-1"))
