# Contributing

## Development principles

- Keep exchange integrations read-only until explicitly reviewed.
- Use replay fixtures for tests; do not call live exchange endpoints from CI.
- Preserve fail-closed behavior in reconciliation, validation, readiness, and risk controls.
- Never commit API keys, secrets, private account data, or live order payloads.

## Local setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .[dev]
pip install pytest pytest-asyncio
```

## Validation

Run `make test` before opening a pull request. New exchange behavior should include deterministic fixtures and tests for malformed, stale, duplicated, and out-of-order data.

## Pull requests

Describe the behavior changed, the safety impact, and the tests executed. Keep commits focused and do not mix live execution with market-data or analytics changes.
