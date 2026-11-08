# ADR-0001: Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-11-04
- **Decider:** Jae (project owner)

## Context

The project uses a human-in-the-loop process: an AI assistant proposes options and writes code, and a human makes every architecture decision. Those decisions must be visible to anyone reading the repository later, together with the reasoning.

## Decision

Record every architecture decision as a short ADR in `docs/03-architecture/adr/`, numbered sequentially, using [`0000-template.md`](0000-template.md). Accepted ADRs are immutable; a change is a new ADR that supersedes the old one.

## Consequences

- Reviewers can trace any piece of infrastructure or code to the decision behind it.
- Each ADR is approved through a pull request, which records the human approval.
