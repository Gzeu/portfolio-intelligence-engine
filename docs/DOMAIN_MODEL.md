# Domain Model

## Design rules
All entities are immutable event snapshots unless explicitly marked as mutable state. Every timestamp is UTC, every decision has a unique ID, and every model/configuration change is versioned. Historical decisions must be reproducible from point-in-time inputs.

## Core entities

### AccountState
`account_id`, `timestamp`, `equity`, `available_margin`, `used_margin`, `maintenance_margin`, `unrealized_pnl`, `realized_pnl`, `gross_exposure`, `net_exposure`, `leverage`, `positions_version`.

### MarketState
`asset`, `timestamp`, `price`, `bid`, `ask`, `spread_bps`, `volume`, `orderbook_depth`, `volatility`, `funding_rate`, `open_interest`, `returns`, `data_quality`.

### MarketRegime
`asset_or_universe`, `timestamp`, `timeframe`, `label`, `trend_strength`, `volatility_state`, `liquidity_state`, `stress_score`, `probabilities`, `model_version`.

### Opportunity
`opportunity_id`, `asset`, `side`, `detected_at`, `setup_type`, `timeframe`, `raw_features`, `regime_id`, `status`, `expiry`, `invalidation_conditions`.

### Forecast
`forecast_id`, `opportunity_id`, `horizon`, `created_at`, `valid_until`, `distribution`, `target_range`, `expected_return`, `expected_loss`, `confidence_declared`, `confidence_calibrated`, `uncertainty`, `model_version`, `feature_snapshot_id`.

### ScenarioNode
`node_id`, `forecast_id`, `kind` (PRIMARY / IF / INVALIDATION), `condition`, `probability`, `price_range`, `time_range`, `action_effect`, `parent_node_id`.

### PortfolioSnapshot
`portfolio_id`, `timestamp`, `equity`, `positions`, `gross_exposure`, `net_exposure`, `concentration`, `correlation_matrix_version`, `risk_budget`, `margin_headroom`, `drawdown`.

### SimulationResult
`simulation_id`, `portfolio_snapshot_id`, `candidate_id`, `scenarios`, `expected_pnl`, `expected_drawdown`, `worst_case_drawdown`, `margin_impact`, `liquidity_impact`, `correlation_stress`, `created_at`.

### CapitalDecision
`decision_id`, `candidate_id`, `decision`, `rank`, `score_components`, `approved_size`, `risk_consumed`, `reasons`, `constraints_triggered`, `arbiter_version`, `created_at`, `expires_at`.

### ExecutionPlan
`plan_id`, `decision_id`, `asset`, `side`, `size`, `entry_policy`, `order_type`, `limit_price`, `stop_loss`, `take_profit`, `max_slippage_bps`, `time_in_force`, `valid_until`, `execution_forecast`.

### Order / Position / Outcome
Orders are exchange intents and acknowledgements. Positions represent reconciled exposure. Outcomes close the decision horizon and contain realized PnL, MAE, MFE, fees, funding, slippage, and exit reason.

### DecisionCase
The complete audit unit: account state, market state, regime, opportunity, forecasts, scenario tree, simulation, capital decision, execution plan, orders, position lifecycle, outcome, error attribution, and lesson.

### CalibrationRecord
`segment`, `horizon`, `model_version`, `declared_bucket`, `sample_count`, `empirical_rate`, `calibration_error`, `utility_loss`, `window`, `validation_method`, `promotion_status`.

## State transitions

```text
Opportunity: DETECTED -> EVALUATED -> RANKED -> EXPIRED | REJECTED | APPROVED
Decision: PROPOSED -> APPROVED | REDUCE_SIZE | WAIT | REJECTED | EXPIRED
Order: PLANNED -> SUBMITTED -> PARTIALLY_FILLED -> FILLED | CANCELLED | FAILED
Position: OPENING -> OPEN -> REDUCING -> CLOSED | LIQUIDATED
Learning: OBSERVATION -> CALIBRATION -> CANDIDATE_PROMOTION -> PROMOTED | REJECTED
```

## Invariants
- No order may exist without a valid, unexpired CapitalDecision.
- No live order may exceed approved size or risk budget.
- A forecast cannot use data newer than its `created_at`.
- An outcome cannot modify the original forecast; attribution is append-only.
- Calibration samples must be separated from training and promotion evaluation windows.
- Exchange state wins during reconciliation; discrepancies create an incident.
