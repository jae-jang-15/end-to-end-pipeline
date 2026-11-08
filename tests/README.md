# Tests

- `unit/` — pure-Python tests of the cleaning logic against `data/sample_orders.csv`; no cloud access. Run with `make test`.
- `integration/` — marked `@pytest.mark.integration`; run against deployed resources only.

The key acceptance test asserts the reconciliation target from the brief: `1,000 bronze = 910 silver + 40 rejected + 50 duplicates removed`.
