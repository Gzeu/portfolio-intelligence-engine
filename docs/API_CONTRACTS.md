# API Contracts

## Contract conventions
JSON over HTTPS for control-plane APIs and WebSocket/event streams for real-time state. All write operations require an idempotency key. Responses include `request_id`, `timestamp`, `status`, and `schema_version`. Timestamps are ISO-8601 UTC.

## Common error

```json
{
  "error": {"code": "RISK_LIMIT_EXCEEDED", "message": "candidate exceeds portfolio risk budget", "details": {}},
  "request_id": "req_...",
  "schema_version": "1.0"
}
```

## `POST /v1/opportunities/evaluate`
Evaluates a candidate against current market, account, and portfolio state.

```json
{
  "asset": "EGLDUSDT",
  "side": "LONG",
  "setup_type": "breakout_pullback",
  "requested_horizons": ["5m", "15m", "1h", "4h"],
  "as_of": "2026-08-12T15:00:00Z"
}
```

Returns an `Opportunity`, linked `Forecast[]`, `ScenarioNode[]`, and `CapitalDecision`.

## `POST /v1/portfolio/simulations`

```json
{
  "portfolio_snapshot_id": "pf_...",
  "candidate": {"asset": "EGLDUSDT", "side": "LONG", "size": 100},
  "stress_scenarios": ["BASE", "VOLATILITY_2X", "CORRELATION_1", "LIQUIDITY_50PCT"]
}
```

Returns `SimulationResult` with expected PnL, drawdown, margin impact, and constraint violations.

## `POST /v1/capital-decisions`
Creates an auditable APPROVE, REDUCE_SIZE, WAIT, or REJECT decision. It must not submit an exchange order.

## `POST /v1/execution-plans`
Creates an execution plan only for an approved and unexpired decision. The planner must enforce approved size, maximum slippage, stop policy, and expiry.

## `POST /v1/orders`
Submits an order using an execution plan. Requires `Idempotency-Key`. Live submission is disabled in analysis and paper modes.

## `GET /v1/portfolio/state`
Returns the latest reconciled account state, positions, exposure, margin, drawdown, and risk budget.

## `GET /v1/decision-cases/{decision_id}`
Returns the complete immutable audit case and its outcome, if closed.

## `POST /v1/calibration/observations`
Records forecast-vs-reality observations. This endpoint cannot promote a strategy or mutate live configuration.

## `POST /v1/calibration/promotions`
Promotes a validated candidate configuration only when all promotion gates pass: minimum sample, walk-forward, out-of-sample, cost-aware validation, and drawdown check.

## Event topics
- `account.state.updated`
- `market.state.updated`
- `regime.updated`
- `opportunity.created`
- `forecast.created`
- `capital.decision.created`
- `execution.order.updated`
- `position.updated`
- `outcome.closed`
- `calibration.updated`
- `incident.created`

## Safety requirements
- Default mode is `analysis`; `paper` and `live` are explicit.
- Authentication, authorization, rate limits, and audit logging are mandatory.
- Kill switch and daily loss limits are evaluated before every live order.
- Reconciliation is required after restart, timeout, rejected order, and exchange disconnect.
- Secrets never appear in logs, events, fixtures, or error payloads.
