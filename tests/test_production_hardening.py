from datetime import datetime, timezone

from portfolio_intelligence.config import Settings
from portfolio_intelligence.exchange.bybit import BybitProvider
from portfolio_intelligence.exchange.config import BybitSettings
from portfolio_intelligence.hardening.audit import AuditRecord, deterministic_json
from portfolio_intelligence.hardening.incidents import redact_secrets
from portfolio_intelligence.hardening.readiness import build_readiness_report


NOW = datetime(2026, 8, 12, 15, 0, tzinfo=timezone.utc)


def test_audit_hash_is_deterministic() -> None:
    record = AuditRecord(record_id="r1", event_type="decision.created", aggregate_id="d1", occurred_at=NOW, payload={"b": 2, "a": 1})
    assert record.with_hash().record_hash == record.with_hash().record_hash
    assert deterministic_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'


def test_secret_redaction_is_recursive() -> None:
    value = {"api_key": "key", "nested": {"api_secret": "secret", "safe": "value"}}
    redacted = redact_secrets(value)
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["api_secret"] == "[REDACTED]"
    assert redacted["nested"]["safe"] == "value"


def test_bybit_readiness_is_ready_only_in_safe_mode() -> None:
    report = build_readiness_report(Settings(), BybitProvider(BybitSettings()))
    assert report.ready is True
    assert all(check.passed for check in report.checks)


def test_readiness_rejects_mainnet_provider() -> None:
    report = build_readiness_report(Settings(), BybitProvider(BybitSettings(environment="mainnet")))
    assert report.ready is False
