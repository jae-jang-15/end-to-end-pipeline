# PRD: Orders Medallion Pipeline

**Version:** 1.0 · **Status:** Approved by the owner (Jae), 2026-11-14 · **Owner:** Jae · **Inputs:** [Project brief v1.1](../01-brief/project-brief.md), [ADR-0001 – ADR-0009](../03-architecture/adr/), [sample data dictionary](../../data/README.md)

*Working files (decision log, review): [`_bmad-output/planning-artifacts/prds/prd-end-to-end-pipeline-2026-11-11/`](../../_bmad-output/planning-artifacts/prds/prd-end-to-end-pipeline-2026-11-11/).*

## 0. Document purpose

This PRD turns the approved project brief into numbered, testable requirements. It is written for an engineer who has never seen the project: a reviewer, a future contributor, or the AI assistant that will implement it.

- **Fixed inputs.** Every row in the brief's Decisions table and every accepted ADR is a constraint here, not an open question. Where a requirement depends on one, it cites the ADR.
- **What, not how.** Requirements state observable behaviour. Mechanisms (bucket names, key layouts, IAM policies, Snowflake object definitions) belong to the architecture document; the few that surfaced during discovery are parked in [`addendum.md`](addendum.md).
- **Vocabulary.** Terms in §3 Glossary are used exactly; no synonyms.
- **Assumptions.** Points first inferred during drafting were confirmed by the owner on 2026-11-14 and are listed in §11.

## 1. Vision

A small batch pipeline that takes a raw file of online orders and turns it into analyst-ready tables in Snowflake, with every row accounted for along the way. A file dropped into S3 is copied untouched, cleaned, checked and loaded automatically; an analyst then queries daily sales and customer summaries built by dbt.

The data is deliberately trivial — one 1,000-row file — so the project can be judged on how it is built rather than on volume. Three properties matter more than features: **nothing is lost silently** (every row ends up in silver, in rejected rows, or counted as a duplicate), **nothing changes without a human decision** (specs, architecture choices and every deployment pass a recorded approval), and **everything is reproducible from the repository** (infrastructure in Terraform, deployment through gated CI/CD, operating knowledge in runbooks).

## 2. Target users

### 2.1 Jobs to be done

- **Pipeline owner** (Jae): land a source file and know within minutes whether it processed correctly, with exact counts for every step, without opening the AWS console.
- **Analyst**: answer "how are sales trending by day, category and state?" and "who are our customers and how much have they spent?" from tables that can be trusted without re-cleaning.
- **Reviewer** (an outside engineer, hiring manager or future contributor): trace any table, line of code or cloud resource back to an approved requirement or decision, and deploy the project from the repository alone.

### 2.2 Non-users (v1)

- Real-time or operational consumers (order-fulfilment systems, customer-facing apps).
- BI dashboard users — gold tables are queried with SQL in v1.
- Multiple source teams sending files on a schedule.

### 2.3 Key user journeys

- **UJ-1. Jae lands the sample file and checks the counts.**
  Jae uploads `sample_orders.csv` to the landing area. Within a few minutes the run summary shows 1,000 rows received, 40 rejected (10 per reason), 50 duplicates removed and 910 written to silver, and the Snowflake silver table holds 910 rows. **Edge case:** if he uploads the same file again, the counts repeat exactly and the silver table still holds 910 rows.

- **UJ-2. Priya, a sales analyst, checks last week's revenue by category.**
  Priya opens a Snowflake worksheet after Jae runs `dbt build` and queries the daily sales gold model filtered to the last seven days. She trusts the numbers because dbt tests passed and revenue in gold reconciles to silver. She then looks up the top ten customers by lifetime revenue in the customer summary.

- **UJ-3. Sam, a reviewer, follows a change from requirement to deployment.**
  Sam opens a merged pull request that added a gold column. The PR cites FR-14, CI shows tests and a Terraform plan, and the deployment run shows Jae's approval at the `live` environment gate. Sam reads ADR-0004 to understand why loading uses Snowpipe.

## 3. Glossary

- **Source file** — a CSV of orders with the 15 columns in the data dictionary. v1 has exactly one: `data/sample_orders.csv`.
- **Landing area** — the S3 location where source files arrive. Arrival of a source file starts a run.
- **Rejected area** — the S3 location where a run writes its rejected rows.
- **Bronze copy** — a byte-for-byte copy of a source file, never modified after it is written.
- **Run** — one processing of one source file, from landing to silver. Identified by a run ID.
- **Repair** — a deterministic fix to a value that makes a row valid (e.g. trimming whitespace). Repaired rows continue to silver.
- **Rejected row** — a row that fails a validation rule. It is kept, with its original values and a rejection reason, and never reaches silver.
- **Rejection reason** — a fixed code naming the rule a rejected row failed.
- **Duplicate** — a row whose `order_id` appears again in the same source file with a later `updated_at` (or, on equal `updated_at`, later in the file). Only the latest version of each order continues to silver.
- **Silver dataset** — the cleaned, typed, de-duplicated output of a run, stored as Parquet in S3.
- **Silver table** — the Snowflake table loaded from silver datasets.
- **Gold model** — a dbt model built from the silver table for a specific analytical question. v1 has two: daily sales and customer summary.
- **Run summary** — the record of one run's counts at every step, emitted as a structured log entry and a summary file.
- **Reconciliation** — the check that, for a run, rows received = rows in silver + rejected rows + duplicates.
- **Gate** — a recorded human approval: a merged pull request for specs and code, an environment approval for deployments.

## 4. Features

### 4.1 Ingestion and bronze

**Description:** Uploading a source file to the landing area starts a run automatically (ADR-0008). The first thing a run does is write the bronze copy, so the original bytes survive whatever happens next and silver can always be rebuilt from bronze (ADR-0003). Realizes UJ-1.

#### FR-1: Event-driven start
A run starts automatically when a source file lands in the landing area; no manual trigger or schedule is needed.
- Uploading a `.csv` object to the landing area starts a run. If the event is delivered more than once, the outputs are the same as for a single run (FR-9).
- Objects outside the landing area, or without a `.csv` extension, start no run.

#### FR-2: Immutable bronze copy
Each run writes a bronze copy of its source file before any validation.
- The bronze copy is byte-identical to the source file (same checksum).
- No pipeline component modifies or deletes a bronze copy after it is written.
- A bronze copy is written even when the run later fails.

#### FR-3: Structural check
A run verifies the source file's structure before processing rows.
- A file whose header does not match the 15 expected column names, in order, fails the run as a whole: no silver dataset or rejected rows are written for it, and the failure is alerted (FR-16).
- An empty file (header only) completes with zero rows and a run summary showing zeros.

### 4.2 Cleaning, validation and de-duplication

**Description:** The run turns bronze rows into the silver dataset. It repairs what can be fixed deterministically, rejects what cannot, removes duplicates, and enforces reconciliation. The pandas script owns all cleaning; dbt does none (brief, decided 2026-11-07). Realizes UJ-1.

#### FR-4: Repairs
The run repairs these issues and keeps the rows:

| Issue | Repair |
|---|---|
| `order_status` in mixed or lower case | Converted to upper case |
| Leading/trailing whitespace in any text column | Trimmed |
| `$` prefix in `unit_price` | Removed, value parsed as a decimal |
| `order_date` in `MM/DD/YYYY HH:MM` format | Parsed as a timestamp |

- For the sample file, all 60 planted repairable values are repaired and none causes a rejection on its own.
- After repair, `order_status` is one of `DELIVERED`, `SHIPPED`, `PENDING`, `CANCELLED`, `RETURNED`.

#### FR-5: Validation and rejection
A row is rejected when any rule fails, with these rejection reasons:

| Rejection reason | Rule |
|---|---|
| `MISSING_ORDER_ID` | `order_id` empty after trimming |
| `MISSING_CUSTOMER_ID` | `customer_id` empty after trimming |
| `INVALID_QUANTITY` | `quantity` not a whole number ≥ 1 |
| `INVALID_ORDER_DATE` | `order_date` not parseable in either accepted format |

- For the sample file: exactly 40 rejected rows, 10 per reason.
- A row failing several rules is rejected once, with all failing reasons listed (comma-separated, fixed order).
- Other columns that cannot be parsed (`unit_price`, `updated_at`) are rejected with reasons `INVALID_UNIT_PRICE` / `INVALID_UPDATED_AT`; the sample file has none.

#### FR-6: De-duplication
Within a source file, only the latest version of each order reaches silver.
- Among rows sharing an `order_id`, the row with the latest `updated_at` is kept; on equal `updated_at`, the row appearing last in the source file is kept. The others are counted as duplicates.
- For the sample file: exactly 50 duplicates removed.
- De-duplication runs after validation, so rejected rows are never counted as duplicates.

#### FR-7: Silver dataset
The run writes valid, de-duplicated rows as a typed Parquet silver dataset (ADR-0003).
- Column types: `order_date` and `updated_at` timestamps; `quantity` integer; `unit_price` decimal with 2 decimal places; all other columns strings.
- Each row carries the run ID and source file name.
- For the sample file: 910 rows, `order_id` unique.

#### FR-8: Rejected rows output
The run writes rejected rows to the rejected area in S3 as Parquet.
- Each rejected row keeps its original, unrepaired values plus `rejection_reason`, run ID and source file name.
- Rejected rows are not loaded into Snowflake in v1.

#### FR-9: Safe reprocessing
Processing the same source file again produces the same outcome and never double-counts.
- Re-uploading an identical source file replaces that file's earlier silver dataset and rejected rows; it does not add to them.
- After any number of re-uploads of the sample file, the silver table holds 910 rows.
- Duplicates across different source files are out of scope for v1.

#### FR-10: Reconciliation enforced
Every run checks reconciliation before publishing its outputs.
- If rows received ≠ silver rows + rejected rows + duplicates, the run fails, publishes nothing to silver, and alerts (FR-16).
- For the sample file: 1,000 = 910 + 40 + 50.

### 4.3 Loading into Snowflake

**Description:** New silver datasets load into the silver table automatically through Snowpipe and a storage integration, with no stored AWS keys (ADR-0004). Realizes UJ-1, UJ-2.

#### FR-11: Automatic load
A new silver dataset loads into the silver table without manual action.
- The silver table reflects a new silver dataset within 5 minutes of its source file landing.
- Column types in the silver table match FR-7.

#### FR-12: Load consistency
The silver table holds exactly one row per `order_id` per source file, from that file's latest run.
- After re-uploading the sample file (FR-9), the silver table still holds 910 rows and `order_id` remains unique.
- The mechanism (overwrite, merge or load-history handling) is decided in the architecture document; see addendum A1.

### 4.4 Gold models

**Description:** dbt Core builds two gold models from the silver table, run manually with `dbt build` in v1 (ADR-0008). Realizes UJ-2.

#### FR-13: Daily sales
A gold model with one row per order date, category and ship state.
- Columns: `order_date` (date), `category`, `ship_state`, `orders` (count), `units` (sum of quantity), `gross_revenue` (sum of quantity × unit_price), `net_revenue`.
- `net_revenue` excludes orders with status `CANCELLED` or `RETURNED`; `gross_revenue` includes all statuses.
- Sum of `gross_revenue` across the model equals sum of quantity × unit_price across the silver table, to the cent.

#### FR-14: Customer summary
A gold model with one row per customer.
- Columns: `customer_id`, `orders`, `lifetime_revenue` (net, as in FR-13), `first_order_date`, `last_order_date`.
- Row count equals the number of distinct `customer_id` values in the silver table.

#### FR-15: Data tests
Every `dbt build` runs tests on the silver table and both gold models, and the build fails if any test fails.
- Silver: `order_id` unique and not null; `customer_id` not null; `order_status` in the accepted set; `quantity` ≥ 1.
- Gold: grain columns unique together; revenue reconciles to silver (FR-13).

### 4.5 Run reporting and alerting

**Description:** Every run reports what it did, so the owner never has to inspect files to know the outcome. Realizes UJ-1.

#### FR-16: Run summary
Every run emits one structured log entry and writes one summary file.
- Both contain: run ID, source file name, start and end time, status (`SUCCEEDED`/`FAILED`), rows received, rows repaired (rows with at least one repair), rejected rows by reason, duplicates removed, rows written to silver.
- For the sample file, the counts match FR-5, FR-6, FR-7 and FR-10.

#### FR-17: Failure alert
A failed run notifies the owner by email through AWS SNS.
- The email arrives within 5 minutes of the failure and includes the run ID, source file name and failure reason.
- A successful run sends no email.

### 4.6 Delivery and deployment

**Description:** The project deploys the way an enterprise team would, while keeping a human at every gate (ADR-0005, ADR-0006). Realizes UJ-3.

#### FR-18: Infrastructure as code
All AWS and Snowflake resources are defined in Terraform; nothing is created by hand except the one-time bootstrap (state bucket and GitHub OIDC roles).
- `terraform plan` on an unchanged `main` reports no changes.

#### FR-19: Gated changes
Every change reaches `main` through a pull request with passing CI and an approving review.
- CI runs pre-commit hooks, lint, unit tests, `terraform fmt`, `validate` and `plan`.
- Unit tests assert FR-4 to FR-10 against the sample file, including the reconciliation target.

#### FR-20: Gated deployment
Deployment runs only from `main` and only after a human approves the `live` environment.
- AWS access uses GitHub OIDC; no long-lived AWS keys exist in GitHub.
- Snowflake access uses key-pair authentication for a dedicated service user.

#### FR-21: Clean teardown
The whole environment can be removed.
- `terraform destroy` followed by the documented bootstrap teardown leaves no billable resources in AWS or Snowflake.

## 5. Cross-cutting non-functional requirements

- **NFR-1 Cost.** Monthly AWS spend stays under $5 measured before credits, with an AWS Budgets alert at 50% and 100% (ADR-0009). Snowflake uses one X-Small warehouse with auto-suspend.
- **NFR-2 Security.** Least-privilege IAM for every role; S3 buckets block public access and encrypt at rest; no secrets in the repository, Terraform files or logs; `detect-private-key` runs in CI.
- **NFR-3 Reliability.** The cleaning function has a timeout; retries never produce double-counted data (FR-9, FR-12).
- **NFR-4 Performance.** Processing the 1,000-row sample file takes under 60 seconds end to end in Lambda.
- **NFR-5 Observability.** Every run is traceable by run ID across the bronze copy, silver dataset, rejected rows, run summary and silver table rows.
- **NFR-6 Reproducibility.** A new engineer can bootstrap, deploy, run the sample file and tear down using only the repository's runbooks, within two hours.
- **NFR-7 Documentation.** Every BMAD artifact, ADR and runbook is written for an outside engineer; every requirement in this PRD is cited by at least one test or story.

## 6. Constraints and guardrails

- **Fixed decisions.** The brief's Decisions table and ADR-0001 – ADR-0009 are binding. Changing one requires a new ADR.
- **Free-tier first.** No AWS Glue, schedulers, Step Functions or dbt Cloud in v1 (ADR-0002, ADR-0008).
- **Single environment.** One deployed environment, `live` (ADR-0007).
- **Human decides, AI executes.** The AI assistant drafts and builds; it never merges, approves a deployment, or changes scope.

## 7. Non-goals (explicit)

- Not a streaming or near-real-time pipeline.
- Not a general ingestion framework for arbitrary schemas or many sources.
- Not a BI or dashboarding product.
- No order status mix (cancellation/return rates) gold model in v1.
- No cross-file de-duplication or change-data-capture history (SCD) in v1.

## 8. MVP scope

### 8.1 In scope
- FR-1 – FR-21 and NFR-1 – NFR-7.
- One source file (`data/sample_orders.csv`), one environment, two gold models.
- Runbooks: bootstrap, GitHub setup, deploy, run the pipeline, teardown.

### 8.2 Out of scope for MVP
- Scheduled or automated `dbt build` — v2, likely in GitHub Actions.
- Loading rejected rows into Snowflake — v2 if analysts need them.
- Multiple environments (dev/prod) — v2 if the project grows.
- Order status mix gold model — v2.

## 9. Success metrics

**Primary**
- **SM-1 Exact reconciliation.** Every run of the sample file reports 1,000 = 910 + 40 + 50, and the silver table holds 910 rows. Validates FR-5 – FR-10, FR-12.
- **SM-2 Freshness.** Source file landing → rows in the silver table in ≤ 5 minutes, in 3 of 3 test uploads. Validates FR-1, FR-11.
- **SM-3 Gate coverage.** 100% of merges to `main` have a passing CI run and an approving review; 100% of deployments have a recorded environment approval. Validates FR-19, FR-20.

**Secondary**
- **SM-4 Cost.** AWS spend ≤ $5/month before credits for every month the project runs. Validates NFR-1.
- **SM-5 Reproducibility.** An engineer other than the owner completes deploy → run → teardown from the runbooks. Validates NFR-6, FR-21.

**Counter-metrics (do not optimize)**
- **SM-C1 Rejection count.** Do not reduce rejected rows by loosening validation rules; the 40 rejections are correct. Counterbalances SM-1.
- **SM-C2 Latency.** Do not add schedulers, always-on compute or polling to beat the 5-minute target. Counterbalances SM-2 and SM-4.

## 10. Open questions

1. How does the silver table stay consistent on reprocessing (FR-12): overwrite by source file, merge on `order_id`, or Snowpipe load-history handling? → architecture document.
2. Where does the run summary file live, and is it ever loaded into Snowflake? → architecture document.
3. Should the analyst role in Snowflake be read-only on gold only, or also read silver? → architecture document.

## 11. Confirmed assumptions

Inferred during drafting and confirmed by the owner on 2026-11-14:

- §4.1 FR-1 — non-`.csv` objects and objects outside the landing area start no run.
- §4.1 FR-3 — a wrong header fails the whole file; an empty file succeeds with zero rows.
- §4.2 FR-5 — a row failing several rules lists all reasons; `INVALID_UNIT_PRICE` and `INVALID_UPDATED_AT` exist as reasons.
- §4.2 FR-7 — silver rows carry run ID and source file name.
- §4.4 FR-13 — `net_revenue` excludes `CANCELLED` and `RETURNED` orders; `gross_revenue` includes all.
- §5 NFR-4 — the sample file processes in under 60 seconds.
- §5 NFR-6 — a new engineer completes the runbooks within two hours.
