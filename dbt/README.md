# dbt project

dbt Core project that builds gold models from the Snowflake silver table ([ADR-0008](../docs/03-architecture/adr/0008-dbt-core-and-orchestration.md)).

**Status:** Written in the Development stage.

Local use: `pip install -e ".[dbt]"`, create `~/.dbt/profiles.yml` (never committed), then `dbt build --project-dir dbt`.
