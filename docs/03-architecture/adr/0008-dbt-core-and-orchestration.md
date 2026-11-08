# ADR-0008: dbt Core run locally; event-driven ingestion, no scheduler

- **Status:** Accepted
- **Date:** 2026-11-04
- **Decider:** Jae (project owner)

## Context

The pipeline processes one file. Orchestration and transformation tooling should not add cost or accounts the project doesn't need.

## Decision

- **Ingestion is event-driven:** an S3 event on the landing prefix invokes the Lambda function; Snowpipe loads silver files on arrival.
- **Transformation:** dbt Core, run from a developer machine in v1 (`dbt build`), with models and tests versioned in `dbt/`.
- No Airflow, Step Functions or dbt Cloud in v1.

## Consequences

- Zero orchestration cost.
- Gold freshness depends on a manual `dbt build`; moving it into GitHub Actions or a scheduler is a later ADR.
