# ADR-0009: Cost guardrails

- **Status:** Accepted
- **Date:** 2026-11-04
- **Decider:** Jae (project owner)

## Context

The AWS account runs on free-plan credits (about $120 remaining at decision time). Credits can hide real spending until they run out.

## Decision

- An **AWS Budgets** alert at **$5/month**, emailing at 50% and 100%, measured on usage **before credits**.
- A **timeout** on the Lambda function so a stuck invocation cannot run up cost.
- One **X-Small** Snowflake warehouse with **auto-suspend** and auto-resume.
- All guardrails are defined in Terraform, not configured by hand.

## Consequences

- Unexpected spend is visible early, even while credits are covering it.
- Guardrails are reviewed in the same pull requests as the resources they protect.
