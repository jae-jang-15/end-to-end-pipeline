# Adversarial review — two compliant units that still diverge

**Verdict:** Two holes found; both close with one new AD and one convention.

- **high** Silver schema has no single owner. The Lambda (Parquet writer) and Terraform (`RAW.ORDERS_HISTORY` DDL) can both obey every AD and still disagree on column names, order or types, so Snowpipe loads fail or load NULLs. Same for the run summary JSON vs `RAW.RUNS`. *Fix:* new AD — checked-in schema files are the single source of truth, read by the Lambda's tests and by Terraform; the pipes load by column name.
- **medium** Timestamp precision. pandas writes nanosecond Parquet timestamps; the Snowflake column type was never fixed. *Fix:* convention — Parquet timestamps written at microsecond precision, UTC, loaded as `TIMESTAMP_NTZ`; `unit_price` as decimal(10,2) → `NUMBER(10,2)`.
- **low** `loaded_at` owner unstated. *Fix:* set by the pipe at load time.
