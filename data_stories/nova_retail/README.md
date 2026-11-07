# 🛒 Nova Retail — Data Story

[← Data stories](../README.md) · **Nova Retail**

**MSIS-2402 · Week 1** *(notebook 1)* · **Week 2 — Joins** *(notebook 2)* ·
**Week 3, Part 2 — Advanced SQL** *(notebook 3)*

A synthetic e-commerce dataset (customers, products, orders, order_items)
with three progressively harder notebooks: basics → intermediate →
advanced.

**One of only two stories here with several related tables**, which makes it one of
the two that can teach `JOIN` honestly. (The other is `books_users_ratings/`.)

---

## The schema

| Table | Columns |
|---|---|
| `customers` | `customer_id`, `gender`, `country`, `customer_segment`, `signup_date` |
| `products` | `product_id`, `category`, `price` |
| `orders` | `order_id`, `customer_id`, `order_date` |
| `order_items` | `order_item_id`, `order_id`, `product_id`, `quantity`, `category`, `price`, `sales_amount` |

How they join:

```
customers.customer_id  1 ──< many  orders.customer_id
orders.order_id        1 ──< many  order_items.order_id
products.product_id    1 ──< many  order_items.product_id
```

These are the **logical** keys the joins use (`customer_id`, `order_id`,
`product_id`). `data/schema.sql` declares no `PRIMARY KEY` or `FOREIGN KEY`
constraints, so DuckDB does not enforce them — for a story with enforced keys,
see `books_users_ratings/`.

| Table | Rows | Meaning |
|---|---:|---|
| `customers` | 1,005 | One row per customer |
| `products` | 2,004 | One row per product |
| `orders` | 20,000 | One row per order |
| `order_items` | 60,000 | **One row per line on an order** |

`order_items` is the junction table: an order contains many products, and a product
appears on many orders. It also carries `quantity` and `price` — data that belongs to
the *relationship*, not to either side.

---

## Which notebook belongs to which week

| Notebook | Content | Week |
|---|---|---|
| `notebook_1_basics_marimo.py` | Basic (5) + Basic+ (10) queries | **1** |
| `notebook_2_intermediate_marimo.py` | Basic+ (5) + Intermediate (10) — **12 queries with joins** | **2** |
| `notebook_3_advanced_marimo.py` | Intermediate (5) + Advanced (10) — **13 queries with CTEs, 12 with window functions** | **3, Part 2** |

---

## Run it

All commands start in the course repository folder (`MSIS-2402-main` if you
downloaded the ZIP).

**1. Build the database once** — about 15 seconds; it creates `nova_db.duckdb`
from `data/schema.sql` and `data/data.sql`:

```bash
cd data_stories/nova_retail
python3 -c "import duckdb; con = duckdb.connect('nova_db.duckdb'); [con.execute(open(f).read()) for f in ('data/schema.sql', 'data/data.sql')]"
```

On Windows, type `python` instead of `python3`. (`./build_nova_db.sh` does the
same, but needs a bash shell and the DuckDB command-line tool.) To rebuild,
delete `nova_db.duckdb` first — the `CREATE TABLE` statements fail if the tables
already exist.

**2. Open a notebook** — from the same folder:

```bash
marimo edit notebook_1_basics_marimo.py
```

The notebooks open `nova_db.duckdb` **read-only**, so they can't change the data.

---

## Regenerating the data (optional — not needed for the course)

`data/` is pre-generated; you never need to regenerate it. If you want
different data, the generator is `data_generator/nova_retail_generator.py`:

```bash
cd data_stories/nova_retail/data_generator
python3 nova_retail_generator.py --size small --seed 2026 --out ../data
```

- `--out ../data` is required: without it, the output goes to a new
  `data_generator/nova_dataset/` folder that nothing else reads.
- `--size` is `small` (200 customers / 10,000 orders), `medium`
  (1,000 / 100,000), or `large` (10,000 / 1,000,000).
- The data in `data/` matches **none** of these presets (1,005 customers /
  20,000 orders), so regenerating replaces it with a different dataset — and
  the numbers quoted in the notebooks' text will no longer match.

Then delete `nova_db.duckdb` and build again (step 1 above).

`build_notebooks.py` is an old generator script for Jupyter (`.ipynb`)
versions of the notebooks — it is not part of the course; the notebooks you
open are the `*_marimo.py` files.

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
