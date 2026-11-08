# Product requirements (PRD)

**Status:** Not started — next BMAD stage after the approved [brief](../01-brief/project-brief.md).

The PRD will define:

- Functional requirements (FR-n) for each pipeline step, including the cleaning, rejection and de-duplication rules applied to [`data/sample_orders.csv`](../../data/README.md)
- Non-functional requirements (NFR-n): cost ceiling, idempotency, observability, security (least-privilege IAM, no stored credentials)
- Acceptance criteria that tests can verify, including the reconciliation target `1,000 bronze = 910 silver + 40 rejected + 50 duplicates`
- Out-of-scope items carried over from the brief
