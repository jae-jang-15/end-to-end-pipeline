# ADR-0011: One S3 bucket per medallion layer

- **Status:** Accepted
- **Date:** 2026-11-16
- **Decider:** Jae (project owner)

## Context

Landing, bronze and silver data (plus rejected rows and run summaries) could share one bucket with prefixes or use separate buckets. The Lambda is triggered by uploads and also writes data.

## Options considered

1. **One bucket, prefixes per layer** — fewer resources; risk of the Lambda triggering itself if a prefix filter is wrong; folder-level IAM.
2. **One bucket per layer** — Lambda never writes where it is triggered; one simple access rule per bucket; a little more Terraform.

## Decision

Option 2: buckets `landing`, `bronze` and `silver` (silver holds `data/`, `rejected/` and `runs/`). The Lambda never writes to landing, writes bronze only with a conditional create, and Snowflake can read only silver.

## Consequences

- A recursive invocation loop is impossible by construction.
- Permissions map one-to-one onto buckets.
