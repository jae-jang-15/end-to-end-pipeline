"""Generate the synthetic sample dataset ``sample_orders.csv``.

The file holds 1,000 fictional online-retail orders for October 2026 with deliberately
planted data-quality issues, so the bronze -> silver cleaning step has known answers to
test against. Output is deterministic (fixed seed).

Expected reconciliation after cleaning:
    1,000 bronze = 910 silver + 40 rejected + 50 duplicates removed

Usage:
    python generate_sample_orders.py [output_path]
"""

from __future__ import annotations

import csv
import random
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

SEED = 42
CLEAN_ROWS = 950
DUPLICATE_ROWS = 50
TS_FORMAT = "%Y-%m-%d %H:%M:%S"
WINDOW_START = datetime(2026, 10, 1)
WINDOW_SECONDS = 30 * 86_400

COLUMNS = [
    "order_id",
    "order_date",
    "customer_id",
    "product_id",
    "product_name",
    "category",
    "quantity",
    "unit_price",
    "currency",
    "order_status",
    "payment_method",
    "ship_city",
    "ship_state",
    "ship_postal_code",
    "updated_at",
]

# (product_id, product_name, category, unit_price)
PRODUCTS = [
    ("B0A1K2E3L4", "Wireless Earbuds", "Electronics", 29.99),
    ("B0B2M3N4P5", "USB-C Charging Cable 6ft", "Electronics", 9.49),
    ("B0C3Q4R5S6", "Stainless Steel Water Bottle", "Home & Kitchen", 18.95),
    ("B0D4T5U6V7", "Non-Stick Frying Pan 10in", "Home & Kitchen", 24.99),
    ("B0E5W6X7Y8", "Yoga Mat", "Sports & Outdoors", 21.50),
    ("B0F6Z7A8B9", "Resistance Bands Set", "Sports & Outdoors", 14.99),
    ("B0G7C8D9E0", "Paperback Novel", "Books", 12.99),
    ("B0H8F9G0H1", "Kids Coloring Book", "Books", 6.99),
    ("B0I9J0K1L2", "LED Desk Lamp", "Office Products", 34.99),
    ("B0J0M1N2O3", "Gel Pens 24-Pack", "Office Products", 11.99),
    ("B0K1P2Q3R4", "Dog Chew Toy", "Pet Supplies", 8.99),
    ("B0L2S3T4U5", "Cat Litter 20lb", "Pet Supplies", 19.99),
    ("B0M3V4W5X6", "Bluetooth Speaker", "Electronics", 45.00),
    ("B0N4Y5Z6A7", "Coffee Grinder", "Home & Kitchen", 39.99),
    ("B0O5B6C7D8", "Hiking Backpack 30L", "Sports & Outdoors", 59.99),
]

# (city, state, postal_code)
CITIES = [
    ("Seattle", "WA", "98101"),
    ("Austin", "TX", "73301"),
    ("Chantilly", "VA", "20151"),
    ("Denver", "CO", "80202"),
    ("Miami", "FL", "33101"),
    ("Chicago", "IL", "60601"),
    ("Boston", "MA", "02108"),
    ("Phoenix", "AZ", "85001"),
    ("Atlanta", "GA", "30301"),
    ("Portland", "OR", "97201"),
]

# Weighted lists: repetition sets the relative frequency.
STATUSES = ["DELIVERED"] * 6 + ["SHIPPED"] * 2 + ["PENDING", "CANCELLED", "RETURNED"]
PAYMENT_METHODS = ["CREDIT_CARD"] * 5 + ["DEBIT_CARD"] * 2 + ["GIFT_CARD", "PAYPAL"]
QUANTITIES = [1, 1, 1, 1, 2, 2, 3, 4]

Row = dict[str, str]


def make_order(rng: random.Random) -> Row:
    """Build one valid order row."""
    ordered = WINDOW_START + timedelta(seconds=rng.randint(0, WINDOW_SECONDS))
    product_id, product_name, category, price = rng.choice(PRODUCTS)
    city, state, postal = rng.choice(CITIES)
    order_id = f"112-{rng.randint(1_000_000, 9_999_999)}-{rng.randint(1_000_000, 9_999_999)}"
    return {
        "order_id": order_id,
        "order_date": ordered.strftime(TS_FORMAT),
        "customer_id": f"CUST{rng.randint(1, 300):05d}",
        "product_id": product_id,
        "product_name": product_name,
        "category": category,
        "quantity": str(rng.choice(QUANTITIES)),
        "unit_price": f"{price:.2f}",
        "currency": "USD",
        "order_status": rng.choice(STATUSES),
        "payment_method": rng.choice(PAYMENT_METHODS),
        "ship_city": city,
        "ship_state": state,
        "ship_postal_code": postal,
        "updated_at": (ordered + timedelta(hours=rng.randint(1, 72))).strftime(TS_FORMAT),
    }


def plant_repairable_issues(rng: random.Random, rows: list[Row], tally: Counter) -> None:
    """Dirty values that cleaning should normalise, not reject."""
    for row in rng.sample(rows, 25):
        row["order_status"] = row["order_status"].lower()
        tally["repair: lowercase order_status"] += 1
    for row in rng.sample(rows, 15):
        row["ship_city"] = f"  {row['ship_city']} "
        tally["repair: padded ship_city"] += 1
    for row in rng.sample(rows, 10):
        row["unit_price"] = f"${row['unit_price']}"
        tally["repair: '$' in unit_price"] += 1
    for row in rng.sample(rows, 10):
        parsed = datetime.strptime(row["order_date"], TS_FORMAT)
        row["order_date"] = parsed.strftime("%m/%d/%Y %H:%M")
        tally["repair: MM/DD/YYYY order_date"] += 1


def plant_rejectable_issues(rng: random.Random, rows: list[Row], tally: Counter) -> list[Row]:
    """Dirty values that cleaning should reject. Returns the 40 rejected rows."""
    bad = rng.sample(rows, 40)
    for row in bad[:10]:
        row["order_id"] = ""
        tally["reject: missing order_id"] += 1
    for row in bad[10:20]:
        row["quantity"] = rng.choice(["-1", "0", "two"])
        tally["reject: invalid quantity"] += 1
    for row in bad[20:30]:
        row["order_date"] = "not-a-date"
        tally["reject: unparseable order_date"] += 1
    for row in bad[30:40]:
        row["customer_id"] = ""
        tally["reject: missing customer_id"] += 1
    return bad


def plant_duplicates(rng: random.Random, rows: list[Row], bad: list[Row], tally: Counter) -> None:
    """Re-send valid orders with a later updated_at; cleaning keeps the latest version."""
    bad_ids = {id(row) for row in bad}
    candidates = [row for row in rows if id(row) not in bad_ids]
    for original in rng.sample(candidates, DUPLICATE_ROWS):
        duplicate = dict(original)
        updated = datetime.strptime(original["updated_at"], TS_FORMAT)
        later = updated + timedelta(hours=rng.randint(1, 48))
        duplicate["updated_at"] = later.strftime(TS_FORMAT)
        duplicate["order_status"] = rng.choice(["DELIVERED", "RETURNED"])
        rows.append(duplicate)
        tally["dedupe: duplicate order_id"] += 1


def generate(seed: int = SEED) -> tuple[list[Row], Counter]:
    """Return the shuffled rows and a tally of every planted issue."""
    rng = random.Random(seed)  # noqa: S311 - synthetic test data, not security-sensitive
    rows = [make_order(rng) for _ in range(CLEAN_ROWS)]
    tally: Counter = Counter()
    plant_repairable_issues(rng, rows, tally)
    bad = plant_rejectable_issues(rng, rows, tally)
    plant_duplicates(rng, rows, bad, tally)
    rng.shuffle(rows)
    return rows, tally


def main() -> None:
    default = Path(__file__).with_name("sample_orders.csv")
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    rows, tally = generate()
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows):,} rows to {output}")
    for issue, count in sorted(tally.items()):
        print(f"  {issue}: {count}")


if __name__ == "__main__":
    main()
