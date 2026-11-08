# ADR-0004: Load silver into Snowflake with Snowpipe auto-ingest

- **Status:** Accepted
- **Date:** 2026-11-04
- **Decider:** Jae (project owner)

## Context

Silver Parquet files in S3 must reach a Snowflake silver table.

## Options considered

1. **Snowpipe auto-ingest** — S3 event notifications trigger loads automatically; serverless billing per file.
2. **Scheduled `COPY INTO`** — simple, but needs a scheduler and a running warehouse.
3. **Lambda writes directly to Snowflake** — couples compute to the warehouse and puts Snowflake credentials in Lambda.

## Decision

Option 1, using a Snowflake **storage integration** (IAM role trust, no access keys), an external stage on the silver prefix, and a pipe with `AUTO_INGEST = TRUE`.

## Consequences

- No scheduler; new files load within about a minute.
- The S3 ↔ Snowflake trust spans both platforms, which is why Terraform manages both (ADR-0005).
