# Architecture

**Status:** Draft for owner approval (BMAD gate 3), 2026-11-16.

- [Architecture overview](overview.md) — readable walkthrough with diagrams.
- [Architecture spine](architecture-spine.md) — the binding rules (AD-1 – AD-12) implementers follow.
- Working files: [`_bmad-output/planning-artifacts/architecture/architecture-end-to-end-pipeline-2026-11-15/`](../../_bmad-output/planning-artifacts/architecture/architecture-end-to-end-pipeline-2026-11-15/) (decision log, reviews).

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
| [0010](adr/0010-reprocessing-run-scoped-history-latest-view.md) | Reprocess safely: run-scoped files, append-only history, latest-run view | Accepted |
| [0011](adr/0011-one-s3-bucket-per-layer.md) | One S3 bucket per medallion layer | Accepted |
| [0012](adr/0012-snowflake-layout-gold-only-analyst-access.md) | Snowflake RAW/SILVER/GOLD schemas; analysts read gold only | Accepted |
| [0013](adr/0013-atomic-run-publish-and-run-summaries-in-snowflake.md) | Atomic run publish; run summaries loaded into Snowflake | Accepted |
