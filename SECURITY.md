# Security Policy

## Reporting a vulnerability

Open a private security advisory on this repository or contact the maintainer directly instead of filing a public issue. Do not include secrets, API keys, or account data in any report.

## Handling of credentials

- Exchange API keys must never be committed to this repository.
- `.env.example` contains placeholders only; real credentials belong in local, untracked `.env` files or a secrets manager.
- CI does not use live exchange credentials. All exchange behavior is tested against replay fixtures.

## Scope

This project currently ships read-only market-data tooling, reconciliation, validation, and analytics. Any addition of live order placement must go through explicit review and cannot bypass the existing circuit breaker and readiness gates.
