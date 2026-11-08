# ADR-0006: Gated GitHub Actions deployments with OIDC

- **Status:** Accepted
- **Date:** 2026-11-04
- **Decider:** Jae (project owner)

## Context

The project should deploy the way an enterprise team would, while keeping the human-in-the-loop rule that no infrastructure change is applied without human approval.

## Decision

- **Pull requests** (`ci.yml`): every pre-commit hook re-run in CI (including private-key detection, so local hooks are never the only line of defence), ruff lint and format check, pytest, `terraform fmt`, `validate` and `plan`, with the plan written to the job summary.
- **Merges to `main`** (`deploy.yml`): a fresh plan followed by `apply`, running in the GitHub environment `live`, which requires a reviewer's approval before the job starts.
- **AWS authentication** through GitHub's OIDC provider: a read-only *plan* role for pull requests and a *deploy* role for `main`, each trusted only for this repository. No AWS keys are stored in GitHub.
- **Snowflake authentication** through key-pair auth for a dedicated service user, stored as GitHub secrets.
- Branch protection on `main`: pull request required, CI must pass, code-owner review required.

## Consequences

- Every change to production is reviewed twice: the code in the pull request, and the plan at the environment gate.
- First-time setup requires creating the OIDC roles, the `live` environment and the secrets (see `docs/04-runbooks/`).
