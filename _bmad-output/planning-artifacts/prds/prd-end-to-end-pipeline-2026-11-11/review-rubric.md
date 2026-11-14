# PRD Quality Review — Orders Medallion Pipeline (draft v0.1)

## Overall verdict
Ready to finalize after three small fixes. Requirements are concrete and verified against the sample data, and every ADR is respected; the gaps are a missing tie-break rule for duplicates, one undefined Glossary term, and S3's at-least-once event delivery left implicit.

## Decision-readiness — strong
Fixed constraints are cited per requirement (ADR-0002 – ADR-0009). Open Questions §10 are genuinely open and correctly deferred to architecture; addendum A1 names the Snowpipe reload trade-off instead of hiding it.

## Substance over theater — strong
NFRs carry thresholds ($5/month, 60 s, 5 min, two hours). Three user journeys, each driving FRs; no persona or vision furniture.

## Strategic coherence — strong
Thesis is explicit in §1 (nothing lost silently, nothing changes without a human decision, everything reproducible) and SM-1 – SM-3 measure exactly those; counter-metrics SM-C1 and SM-C2 guard against loosening validation and buying latency with cost.

### Findings
- none

## Done-ness clarity — adequate
Most FRs have numeric, sample-backed consequences (FR-5 – FR-10).

### Findings
- **high** Duplicate tie-break undefined (§3 Duplicate, FR-6) — "later or equal `updated_at`" does not say which row survives a tie. *Fix:* on equal `updated_at`, keep the row that appears last in the source file.
- **medium** At-least-once events (FR-1) — S3 can deliver the same event twice; "exactly one run" is untestable as written. *Fix:* restate as "duplicate event deliveries produce the same outputs as one run (FR-9)".
- **low** "Rows repaired" in FR-16 lacks a definition. *Fix:* count rows with at least one repair.

## Scope honesty — strong
Non-goals and MVP deferrals are explicit; seven assumptions indexed and since confirmed by the owner.

## Downstream usability — adequate
IDs contiguous (FR-1 – FR-21, NFR-1 – NFR-7, UJ-1 – UJ-3, SM-1 – SM-5).

### Findings
- **medium** "Rejected area" used in FR-8 but not in the Glossary. *Fix:* add it beside Landing area.

## Shape fit — strong
Internal-tool capability spec with light journeys; matches the agreed stakes.

## Mechanical notes
- Inline `[ASSUMPTION]` tags must be cleared and §11 converted to confirmed assumptions at close.
- Relative links need rewriting when the PRD moves to `docs/02-prd/`.
