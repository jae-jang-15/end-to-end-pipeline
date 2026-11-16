# ADR-0013: Publish each run atomically; load run summaries into Snowflake

- **Status:** Accepted
- **Date:** 2026-11-16
- **Decider:** Jae (project owner)

## Context

The silver view (ADR-0010) serves each source file's latest run, so a partial run must never become "latest". Run summaries (PRD FR-16) could live only in S3 and CloudWatch, or also in Snowflake (resolves PRD open question Q2).

## Decision

- The Lambda processes the whole file in memory, checks reconciliation, and only then writes rejected rows, then exactly one silver Parquet object, then the run summary. A failed run writes only its bronze copy and a `FAILED` summary.
- A second Snowpipe loads run summaries into `RAW.RUNS`. A dbt test asserts each run's silver row count equals the count its summary reports.

## Consequences

- A run either has its complete silver file or none.
- Reconciliation is verified inside the warehouse on every `dbt build`, not only claimed by the Lambda.
