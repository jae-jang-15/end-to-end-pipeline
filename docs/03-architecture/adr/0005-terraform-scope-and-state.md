# ADR-0005: Terraform manages AWS and Snowflake; S3 remote state

- **Status:** Accepted
- **Date:** 2026-11-04
- **Decider:** Jae (project owner)

## Context

Infrastructure spans AWS and Snowflake, and deployments run from GitHub Actions as well as a laptop. Local state cannot be shared with CI.

## Decision

- One Terraform configuration (`infra/live`) uses the AWS and Snowflake providers, composed from modules in `infra/modules`.
- State lives in an **S3 backend** with versioning, encryption and **native S3 state locking** (`use_lockfile`, Terraform ≥ 1.10).
- The state bucket and the GitHub OIDC roles are created once by `infra/bootstrap`, which keeps its own local state and is applied manually by the owner.

## Consequences

- Plans and applies behave the same from CI and from a laptop.
- The bootstrap step is the only manual infrastructure action.
- `.terraform.lock.hcl` is committed to pin provider versions.
