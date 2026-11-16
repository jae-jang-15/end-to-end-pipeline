# Rubric review — ARCHITECTURE-SPINE.md (draft)

**Verdict:** Fixes the real divergence points (run identity, reprocessing, publish order, cleaning ownership, notification ownership); two gaps in the operational envelope and one unenforceable rule.

- **high** AD-2 "write-once bronze" is not enforceable by IAM alone (a PutObject to an existing key overwrites). *Fix:* conditional write (`If-None-Match: *`) for bronze objects plus no `s3:DeleteObject` for the Lambda role; teardown deletes via the deployer role (`force_destroy`), keeping FR-21 possible.
- **medium** Region not decided (operational envelope). Cross-region S3 → Snowflake adds egress cost and latency. *Fix:* convention — AWS region equals the Snowflake account's AWS region.
- **medium** Compute for dbt unstated (AD-8). *Fix:* one X-Small `TRANSFORM_WH`, auto-suspend 60 s, used only by `TRANSFORMER`; Snowpipe is serverless.
- **low** Deferred list is complete for v1; no silent dimension otherwise.
