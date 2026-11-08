# Infrastructure (Terraform)

**Status:** Structure in place; Terraform code is written in the Development stage after the PRD and architecture document are approved. See [ADR-0005](../docs/03-architecture/adr/0005-terraform-scope-and-state.md) and [ADR-0006](../docs/03-architecture/adr/0006-gated-github-actions-deployments.md).

## Layout

```text
infra/
├── bootstrap/   one-time, applied manually: state bucket + GitHub OIDC provider and roles (local state)
├── modules/     reusable building blocks, no provider or backend config
│   ├── storage/          landing, bronze, silver buckets + event notifications
│   ├── lambda_cleaner/   function, IAM role, SDK-for-pandas layer, timeout
│   ├── snowflake_ingest/ storage integration, stage, pipe, silver table, warehouse
│   └── budget/           AWS Budgets alert
└── live/        the deployed root module: providers, S3 backend, module wiring
```

## Order of operations

1. **Bootstrap (once, by the owner):** `terraform -chdir=infra/bootstrap init && terraform -chdir=infra/bootstrap apply`. Outputs the state bucket name and the two role ARNs.
2. **Configure GitHub:** set the repository variables and secrets listed in [`docs/04-runbooks/`](../docs/04-runbooks/README.md), create the `live` environment with a required reviewer.
3. **Everything else** deploys through pull requests and the `Deploy` workflow. Nothing in `live/` is applied from a laptop.

## Conventions

- Terraform ≥ 1.10; provider versions pinned in `versions.tf`; `.terraform.lock.hcl` committed.
- Resource names: `orders-pipeline-<component>`; S3 buckets add the account ID for global uniqueness.
- Every resource carries tags `project = orders-pipeline`, `managed_by = terraform`, `owner`.
- No secrets in `.tf` or `.tfvars` files; credentials come from OIDC (AWS) and environment variables (Snowflake).
