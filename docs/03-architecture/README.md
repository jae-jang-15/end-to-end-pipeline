# Architecture

**Status:** Decisions accepted as ADRs; the architecture document is drafted after the PRD is approved.

## Decision records

| ADR | Title | Status |
|---|---|---|
| [0001](adr/0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](adr/0002-pandas-on-lambda-instead-of-glue.md) | Clean data with pandas on AWS Lambda instead of AWS Glue | Accepted |
| [0003](adr/0003-medallion-storage-layout.md) | Medallion layout: S3 landing/bronze/silver, Parquet silver | Accepted |
| [0004](adr/0004-snowpipe-auto-ingest.md) | Load silver into Snowflake with Snowpipe auto-ingest | Accepted |
| [0005](adr/0005-terraform-scope-and-state.md) | Terraform manages AWS and Snowflake; S3 remote state | Accepted |
| [0006](adr/0006-gated-github-actions-deployments.md) | Gated GitHub Actions deployments with OIDC | Accepted |
| [0007](adr/0007-single-environment-monorepo.md) | Single environment in a monorepo | Accepted |
| [0008](adr/0008-dbt-core-and-orchestration.md) | dbt Core run locally; event-driven ingestion, no scheduler | Accepted |
| [0009](adr/0009-cost-guardrails.md) | Cost guardrails: budget alert, timeouts, auto-suspend | Accepted |

## Pending for the architecture document

- Component diagram and IAM trust relationships (Lambda role, Snowflake storage integration role, GitHub OIDC roles)
- S3 key conventions and event notification wiring
- Snowflake object model (database, schemas, stage, pipe, warehouse, roles)
- Error handling: where rejected rows are written and how they are reported
- Open question carried from the brief: confirm the pandas script owns all cleaning and dbt only models silver → gold
