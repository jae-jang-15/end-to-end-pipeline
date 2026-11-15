# Documentation

All project knowledge lives here, versioned with the code. Documents are written for an engineer who has never seen the project.

## Delivery process

The project follows **BMAD** (Brief → PRD → Architecture → Development → Deployment) with a **human-in-the-loop** operating model:

- **The human decides.** Scope, requirements, architecture options, code acceptance and every `terraform apply`.
- **The AI executes.** Drafting each artifact, laying out options with trade-offs, writing code, tests and Terraform.
- **Each stage ends at a gate.** The next stage starts only after the owner approves the current artifact. Approvals are recorded in the artifact's header and in pull-request reviews.

## Document map

| Folder | Contents | Status |
|---|---|---|
| [01-brief](01-brief/project-brief.md) | Problem, scope, success criteria, constraints, decisions | Approved v1.1 |
| [02-prd](02-prd/prd.md) | Functional and non-functional requirements, acceptance criteria | Approved v1.0 |
| [03-architecture](03-architecture/) | System design and [architecture decision records](03-architecture/adr/) | ADRs accepted; design doc pending |
| [04-runbooks](04-runbooks/) | Bootstrap, deploy, operate, tear down | Not started |
| [assets](assets/) | Diagrams referenced by the documents | — |

## Conventions

- Every artifact starts with a header line: version, date, owner, status.
- Status values: `Draft` → `In review` → `Approved` → `Superseded`.
- Approved documents change only through a new version and a new approval.
- Diagrams live in `assets/` and are referenced with relative links.
