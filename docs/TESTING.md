# Testing Guide

## Principles

- All exchange-facing tests run against replay fixtures in `tests/fixtures/`, never against live endpoints.
- New market-data features must include tests for the valid case and at least one fail-closed case (incomplete book, stale data, crossed book, or invalid sequence).
- Safety gates (circuit breaker, readiness, market quality, market-data validation) must default to blocking or degrading when inputs are ambiguous.

## Running tests

```bash
make install
make test
```

## Fixture contracts

Fixtures under `tests/fixtures/bybit/` mirror the Bybit V5 response envelope (`retCode`, `retMsg`, `result`, `time`). Contract tests assert this envelope shape so that fixtures stay representative of the real API without making live calls.

## Adding new fixtures

1. Add the JSON fixture under `tests/fixtures/bybit/`.
2. Add a contract test asserting the envelope and required fields.
3. Add an integration or unit test that exercises the mapping/validation code using the fixture.
