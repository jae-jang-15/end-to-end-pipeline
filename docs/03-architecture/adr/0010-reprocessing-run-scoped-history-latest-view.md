# ADR-0010: Reprocess safely with run-scoped files, an append-only history and a latest-run view

- **Status:** Accepted
- **Date:** 2026-11-16
- **Decider:** Jae (project owner)

## Context

Re-uploading a source file must not double-count (PRD FR-9, FR-12). Snowpipe records each loaded file's path and name and will not load a file with the same name again, even if it was modified, for 14 days. Overwriting a silver file in place would therefore be silently skipped.

## Options considered

1. **Run-scoped files + append-only history + latest-run view** — no extra compute; full run history; two Snowflake objects instead of one.
2. **Run-scoped files + stream and scheduled task `MERGE`** — one physical table, but a scheduler consumes warehouse credits and conflicts with ADR-0008.
3. **Lambda runs `DELETE` + `COPY INTO`, no Snowpipe** — simplest model, but reverses ADR-0004 and puts Snowflake credentials in Lambda.

## Decision

Option 1. Every run writes silver under `run_id`-scoped keys. Snowpipe appends every file to `RAW.ORDERS_HISTORY`. `SILVER.ORDERS` is a view returning, for each source file, only the rows of its latest run. dbt reads the view.

## Consequences

- Reloads are safe and free, and every run stays auditable.
- The PRD glossary distinguishes the silver history table from the silver table (the view).
- Run IDs must sort by time (architecture spine AD-3).
