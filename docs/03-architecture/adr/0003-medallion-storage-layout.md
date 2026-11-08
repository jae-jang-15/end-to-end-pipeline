# ADR-0003: Medallion layout on S3 with Parquet silver

- **Status:** Accepted
- **Date:** 2026-11-04
- **Decider:** Jae (project owner)

## Context

Data must move through raw, cleaned and modelled layers, with the ability to reprocess cleaned data without re-receiving source files.

## Decision

- **Landing** (S3): files as delivered by the source.
- **Bronze** (S3): an untouched copy written by the Lambda function. Never modified; the replay source for silver.
- **Silver** (S3): cleaned, typed, de-duplicated data written as **Parquet**, so column types survive the hand-off to Snowflake. Rejected rows are kept, not dropped (location defined in the architecture document).
- **Gold** (Snowflake): dbt models built from the Snowflake silver table.

## Consequences

- Silver can be rebuilt from bronze at any time.
- Parquet removes type inference from the Snowflake load.
- Requires `pyarrow` alongside pandas in the Lambda runtime.
