# Portfolio Intelligence Engine

A read-only, replay-first toolkit for exchange integration, market-data quality, reconciliation, and portfolio analytics. The project currently targets Bybit's V5 API for market data and account read paths. No live order placement is implemented; safety gates are designed to fail closed.

## Project status

- Read-only exchange integration (system status, tickers, instruments, wallet balance, positions).
- Replayable order book processing with sequence-gap detection.
- Market microstructure metrics: spread, mid-price, depth, imbalance, microprice, top-N depth.
- Market quality gating (`READY` / `DEGRADED` / `BLOCKED`).
- Market-data validation and freshness gating (`VALID` / `STALE` / `INVALID`).
- Position reconciliation between internal and exchange state.
- Readiness reporting and a circuit breaker gated on provider system status.
- CI pipeline running the full pytest suite on every push and pull request.

## Repository layout

```text
src/portfolio_intelligence/
  config.py            # settings
  controls/            # circuit breaker, system status
  decision_memory/      # decision history
  domain/               # shared strict models
  events/               # event definitions
  exchange/             # Bybit read-only client, mapping, transport, contracts
  execution/            # execution planning primitives
  forecast/             # forecasting components
  hardening/            # readiness checks
  market_data/          # orderbook, metrics, quality, validation
  market_intelligence/  # market analysis
  observability/        # logging/metrics scaffolding
  portfolio/            # portfolio state
  reconciliation/       # position reconciliation engine
  risk/                 # risk controls
  validation/            # validation helpers
tests/
  fixtures/bybit/        # Bybit V5-shaped JSON fixtures for replay tests
  test_*.py              # unit and integration tests
```

## Getting started

```bash
python -m venv .venv
. .venv/bin/activate
make install
make test
```

Copy `.env.example` to `.env` for local configuration; no real credentials are required to run the test suite, since all exchange interactions in tests are replayed from fixtures.

## Key concepts

- **Replay transport**: `ReplayTransport` serves fixture responses so exchange-dependent code can be tested deterministically and offline.
- **Fail-closed gates**: reconciliation, readiness, market quality, and market-data validation all default to blocking or degrading rather than passing ambiguous states.
- **Market quality**: `MarketQualitySnapshot` combines spread, depth, and imbalance into a single `READY` / `DEGRADED` / `BLOCKED` status with explicit reasons.
- **Market-data validation**: `validate_orderbook_event` rejects crossed books, invalid prices/quantities, regressive update IDs, and non-monotonic timestamps, and flags stale or future-dated events.

## Contributing

See `CONTRIBUTING.md` for local setup and development principles, and `docs/TESTING.md` for the testing and fixture conventions. See `SECURITY.md` for vulnerability reporting and credential-handling policy.

## Continuous integration

Every push and pull request to `main` runs the pytest suite via `.github/workflows/validation.yml`. No live exchange credentials are used in CI.
