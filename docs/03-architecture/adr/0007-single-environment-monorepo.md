# ADR-0007: Single environment in a monorepo

- **Status:** Accepted
- **Date:** 2026-11-04
- **Decider:** Jae (project owner)

## Context

Enterprise projects often run dev/staging/prod. This project has a fixed small budget and one data source.

## Decision

- Deploy **one environment** (`live`). The `infra/live` root module and `infra/modules` split allows another environment to be added later as a sibling folder without moving code.
- Keep infrastructure, Lambda source, dbt project, tests and documentation in **one repository**, so a single pull request can carry a requirement, its code and its infrastructure together.

## Consequences

- Lower cost and less configuration drift to manage.
- Changes are exercised directly in the only environment, which makes the review gates and tests more important.
