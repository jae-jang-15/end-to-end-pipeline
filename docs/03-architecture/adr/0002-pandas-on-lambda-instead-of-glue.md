# ADR-0002: Clean data with pandas on AWS Lambda instead of AWS Glue

- **Status:** Accepted
- **Date:** 2026-11-04
- **Decider:** Jae (project owner)

## Context

Bronze-to-silver cleaning needs a compute service. The input is one small CSV (1,000 rows). The project runs on an AWS free-plan account with limited credits.

## Options considered

1. **AWS Glue job** — managed ETL, scales to large data; billed at $0.44 per DPU-hour with no free tier for job runs.
2. **pandas on AWS Lambda** — event-driven, within the Lambda always-free monthly allowance; limited to 15 minutes and 10 GB memory per invocation.
3. **pandas run locally** — free, but the cleaning step would sit outside the deployed pipeline.

## Decision

Option 2. A Python 3.12 Lambda function using pandas (from the AWS-managed *AWS SDK for pandas* layer) performs both the landing → bronze copy and the bronze → silver cleaning. The same module runs locally for unit tests.

## Consequences

- Effectively zero compute cost at this data volume.
- Spark-scale data would require revisiting this ADR (Glue or EMR Serverless).
- Package size must stay within Lambda limits; pandas comes from the managed layer, not the deployment zip.
