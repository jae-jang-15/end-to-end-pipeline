# ADR-0012: One Snowflake database with RAW, SILVER and GOLD schemas; analysts read gold only

- **Status:** Accepted
- **Date:** 2026-11-16
- **Decider:** Jae (project owner)

## Context

Snowflake holds the silver history table, the latest-run silver view and two dbt gold models. Terraform, Snowpipe, dbt and analysts need different access (resolves PRD open question Q3).

## Options considered

1. **Analysts read gold only** — only tested, reconciled tables are exposed; silver stays an internal contract; analysts can't inspect rows themselves.
2. **Analysts read silver and gold** — row-level self-service; reports built on silver make silver hard to change.

## Decision

One database (`ORDERS_PIPELINE`) with schemas `RAW`, `SILVER`, `GOLD`, and option 1. Roles: `LOADER` writes `RAW`; `TRANSFORMER` (dbt) reads `SILVER` and `RAW.RUNS`, writes `GOLD`; `ANALYST` reads `GOLD`; `DEPLOYER` (Terraform) creates objects and grants.

## Consequences

- Silver can change without breaking analyst reports.
- Granting analysts read access to `SILVER` later is a single grant.
