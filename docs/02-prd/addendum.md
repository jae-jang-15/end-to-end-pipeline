# Addendum — PRD: Orders Medallion Pipeline

Material that surfaced during PRD discovery but belongs to the architecture document, not the PRD. Each item names the requirement it supports.

## A1. Silver table consistency on reprocessing (FR-9, FR-12)

Snowpipe skips files it has already loaded (by path, for 14 days), so overwriting a silver dataset at the same path may not reload it. The architecture must choose one mechanism that satisfies FR-12, for example:

- write each run to a run-scoped path and replace the source file's rows in the silver table (delete + load, or `MERGE` on `order_id` and source file), or
- keep the silver table as an append log and expose a de-duplicated view as the dbt source.

## A2. Run summary storage (FR-16)

Candidate: a JSON summary file next to the run's silver dataset, plus one structured CloudWatch log entry. Whether summaries are loaded into Snowflake for trend analysis is open (PRD §10 Q2).

## A3. Verification oracle (FR-4 – FR-10)

The PRD's repair, rejection and de-duplication rules were checked against `data/sample_orders.csv` while drafting: 10 rows per rejection reason, no row with more than one reason, 50 duplicates, and `1,000 = 910 + 40 + 50`. Unit tests should assert the same numbers.
