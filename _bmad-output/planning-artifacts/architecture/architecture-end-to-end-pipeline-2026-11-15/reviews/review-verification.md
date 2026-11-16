# Verification review — named technology

**Verdict:** All named tech was checked on the web on 2026-11-16 and logged in the memlog.

- Snowpipe same-name reload behaviour — docs.snowflake.com (data-load-snowpipe-intro). OK.
- AWS SDK for pandas managed layer supports Python 3.12 — aws-sdk-pandas.readthedocs.io. OK.
- snowflakedb/snowflake provider 2.20.0; storage integration resource `snowflake_storage_integration_aws`. OK.
- hashicorp/aws 6.63.0. OK. dbt-core / dbt-snowflake 1.12.x. OK.
- **low** S3 conditional writes (`If-None-Match`) are relied on by the AD-2 fix; confirm the boto3 `put_object(IfNoneMatch="*")` parameter during implementation.
