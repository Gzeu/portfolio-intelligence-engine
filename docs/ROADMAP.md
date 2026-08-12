# Roadmap

## Vision
Build a production-grade Portfolio Intelligence & Adaptive Decision Engine that evaluates distributions of market scenarios and selects actions using edge, risk, cost, liquidity, execution quality, calibration, and portfolio capacity.

## Principles
- Forecasts are inputs to decisions, not orders.
- `NO_TRADE` is a valid and measurable outcome.
- Every decision is cost-aware, portfolio-aware, and auditable.
- Learning follows Observation -> Calibration -> Promotion.
- Live promotion requires walk-forward, out-of-sample, cost-aware validation, and drawdown checks.
- Paper trading and shadow mode precede live execution.

## Phases

### Phase 0 — Foundation
- Freeze domain vocabulary, IDs, timestamps, and event schemas.
- Implement deterministic configuration and structured logging.
- Define safety boundaries: maximum position, daily loss, leverage, margin, and kill switch.
- Create replayable fixtures for BTC, ETH, EGLD, and SOL.

### Phase 1 — Market Intelligence
- Account-state adapter.
- Market-data normalization.
- Liquidity, volatility, flow, and structure features.
- Multi-timeframe regime classifier.
- Opportunity scanner producing LONG / SHORT / WAIT candidates.

### Phase 2 — Forecast & Scenario Engine
- Five-minute, fifteen-minute, one-hour, and four-hour forecast contracts.
- Probability buckets, ranges, horizon, confidence, and uncertainty.
- Primary scenario, conditional branches, and explicit invalidation.
- Forecast versioning and point-in-time data guarantees.

### Phase 3 — Portfolio Intelligence
- Exposure and concentration accounting.
- Correlation-aware opportunity ranking.
- What-If Engine with volatility, correlation, gap, and liquidity stress scenarios.
- Capital Arbiter returning APPROVE / REDUCE_SIZE / WAIT / REJECT.

### Phase 4 — Execution & Position Engine
- Execution-quality forecast.
- Passive/aggressive order planner.
- Idempotent order submission and reconciliation.
- Position lifecycle, stops, exits, partial fills, and emergency controls.

### Phase 5 — Decision Memory & Calibration
- Immutable decision cases.
- Outcome attribution: forecast, regime, entry, execution, risk, and exit.
- Reliability diagrams and calibration metrics.
- Similar-case retrieval without leaking future information.
- Promotion gates for strategy changes.

### Phase 6 — Validation and Operations
- Event replay and deterministic backtests.
- Walk-forward and out-of-sample evaluation.
- Transaction costs, slippage, funding, latency, and liquidity impact.
- Paper/shadow/live deployment modes.
- Observability, alerts, audit trail, and rollback procedures.

## Definition of done
A feature is not complete until it has a domain contract, tests, replay fixture, metrics, failure handling, audit fields, and explicit paper-trading validation criteria.

## Non-goals
- Guaranteeing profitable trades.
- Treating confidence as probability without calibration.
- Optimizing trade count.
- Allowing online learning to change live strategy behavior without promotion.
