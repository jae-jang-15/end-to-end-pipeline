# Runbooks

**Status:** Outline — each runbook is written during the Development and Deployment stages and tested before it is marked complete.

| Runbook | Purpose |
|---|---|
| `bootstrap.md` | One-time: create the Terraform state bucket and GitHub OIDC roles (`infra/bootstrap`) |
| `github-setup.md` | Create the `live` environment with a required reviewer, set repository variables and secrets, enable branch protection |
| `deploy.md` | Normal change flow: branch → pull request → plan review → merge → environment approval → apply |
| `run-pipeline.md` | Upload a file to landing, verify bronze/silver/Snowflake row counts, run `dbt build` |
| `teardown.md` | `terraform destroy` order, emptying buckets, removing the bootstrap last |

## Repository settings referenced by the workflows

| Kind | Name | Used by |
|---|---|---|
| Variable | `AWS_REGION` | ci.yml, deploy.yml |
| Variable | `AWS_PLAN_ROLE_ARN` | ci.yml |
| Variable | `AWS_DEPLOY_ROLE_ARN` | deploy.yml |
| Variable | `SNOWFLAKE_ROLE` | ci.yml, deploy.yml |
| Secret | `SNOWFLAKE_ORGANIZATION_NAME`, `SNOWFLAKE_ACCOUNT_NAME` | ci.yml, deploy.yml |
| Secret | `SNOWFLAKE_USER`, `SNOWFLAKE_PRIVATE_KEY` | ci.yml, deploy.yml |
| Environment | `live` (required reviewer) | deploy.yml |
