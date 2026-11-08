# Contributing

## Principles

- **Spec first.** Every change traces to an approved requirement in [`docs/02-prd/`](docs/02-prd/) or an [ADR](docs/03-architecture/adr/). If it doesn't, update the spec first.
- **Humans decide, AI executes.** AI-generated code is welcome, but a human reviews and approves every pull request and every `terraform apply`. Architecture choices are recorded as ADRs by a human.
- **Nothing reaches AWS or Snowflake from a laptop** except the one-time bootstrap. Everything else deploys through GitHub Actions.

## Workflow

1. Create a branch from `main`: `feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>`, `infra/<short-name>`.
2. Run `make lint test` locally (pre-commit runs most checks on commit).
3. Open a pull request using the template. CI runs lint, tests and `terraform plan`.
4. A code owner reviews the diff **and the plan output**, then approves.
5. Squash-merge to `main`. The deploy workflow pauses for approval on the `live` environment before applying.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `infra:`, `test:`, `chore:`, `refactor:`.

## Architecture decisions

Copy [`docs/03-architecture/adr/0000-template.md`](docs/03-architecture/adr/0000-template.md) to the next number, fill it in, and submit it in its own pull request. ADRs are never edited after acceptance; a new ADR supersedes an old one.

## Definition of done

- [ ] Linked to a PRD requirement or ADR
- [ ] Unit tests added or updated; `make test` passes
- [ ] dbt tests pass for changed models
- [ ] `terraform plan` reviewed; no unexpected destroys
- [ ] Docs and runbooks updated
