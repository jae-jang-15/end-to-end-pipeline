# Sample data — `sample_orders.csv`

Synthetic online-retail orders for the spec-driven pipeline. 1,000 rows, fictional customers and products, October 2026. Regenerate identically with `python generate_sample_orders.py` (seed 42).

## Columns

| Column | Type (after cleaning) | Example |
|---|---|---|
| order_id | string, key | 112-9519948-2344047 |
| order_date | timestamp | 2026-10-26 18:48:24 |
| customer_id | string | CUST00096 |
| product_id | string | B0C3Q4R5S6 |
| product_name | string | Stainless Steel Water Bottle |
| category | string | Home & Kitchen |
| quantity | integer > 0 | 1 |
| unit_price | decimal(10,2) | 18.95 |
| currency | string | USD |
| order_status | uppercase enum: DELIVERED, SHIPPED, PENDING, CANCELLED, RETURNED | DELIVERED |
| payment_method | string | CREDIT_CARD |
| ship_city / ship_state / ship_postal_code | string | Seattle / WA / 98101 |
| updated_at | timestamp, used for de-duplication | 2026-10-28 01:48:24 |

## Planted data-quality issues

| Issue | Rows | Expected handling |
|---|---|---|
| lowercase `order_status` | 25 | Repair: uppercase |
| padded `ship_city` | 15 | Repair: trim |
| `$` in `unit_price` | 10 | Repair: strip, cast to decimal |
| `order_date` in MM/DD/YYYY HH:MM | 10 | Repair: parse second format |
| missing `order_id` | 10 | Reject |
| `quantity` of -1, 0 or "two" | 10 | Reject |
| `order_date` = "not-a-date" | 10 | Reject |
| missing `customer_id` | 10 | Reject |
| duplicate `order_id` (later `updated_at`) | 50 | De-duplicate, keep latest `updated_at` |

Some repairable issues land on rows that are also rejected, so don't sum the repair counts.

## Reconciliation target

```
1,000 bronze = 910 silver + 40 rejected + 50 duplicates removed
```
