# 🛒 Nova Retail — Data Story

**MSIS-2402 · Week 1** *(notebook 1)* · **Week 2 — Joins** *(notebook 2)* ·
**Week 3, Part 2 — Advanced SQL** *(notebook 3)*

A synthetic e-commerce dataset (customers, products, orders, order_items)
with three progressively harder notebooks: basics → intermediate →
advanced.

**One of only two stories here with several related tables**, which makes it one of
the two that can teach `JOIN` honestly. (The other is `books_users_ratings/`.)

---

## The schema

```
   customers                orders               order_items            products
┌──────────────┐      ┌──────────────────┐   ┌──────────────────┐   ┌──────────────┐
│ customer_id  │◄──FK─│ customer_id   FK │◄FK│ order_id      FK │   │ product_id PK│
│      PK      │      │ order_id      PK │   │ product_id    FK │──►│ price, name  │
│ name, …      │      │ order_date, …    │   │ quantity, price  │   │ category, …  │
└──────────────┘      └──────────────────┘   └──────────────────┘   └──────────────┘
      1 ─── many              1 ─── many              many ─── 1
```

| Table | Rows | Meaning |
|---|---|---|
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
| `notebook_1_basics_marimo.py` | Basic (5) + Basic+ (10) queries | **1–2** |
| `notebook_2_intermediate_marimo.py` | Basic+ (5) + Intermediate (10) — **12 joins** | **3** |
| `notebook_3_advanced_marimo.py` | Intermediate (5) + Advanced (10) — **13 CTEs, 12 window functions** | **5** |

---

## Pipeline — two stages, run separately

**1. Generate the data** (`data_generator/nova_retail_generator.py`):

```bash
cd data_generator
python3 nova_retail_generator.py --size medium --seed 2026 --out ../data
```

**The `--out ../data` flag is required and easy to miss** — the script's
own default (`--out nova_dataset`, i.e. a new `nova_dataset/` folder
inside `data_generator/`) does **not** point at the `data/` folder the
rest of this pipeline actually reads from. Running the generator with no
arguments silently produces output nobody downstream will ever use.
`--size` is one of `small` (200 customers / 10K orders), `medium` (1,000 /
100K — what `data/` currently contains), or `large` (10,000 / 1M).

This writes `customers.csv`, `products.csv`, `orders.csv`,
`order_items.csv`, `schema.sql`, `data.sql`, `reset_duckdb.sql`, and
`verify_dataset.sql` into `data/`.

**Note:** the current `data/` folder contains only the first six of those —
`reset_duckdb.sql` and `verify_dataset.sql` are absent. That is further evidence
that what is in `data/` today was not produced by a straightforward run of the
current generator (see the note below).

**Note on the data currently in `data/`:** it doesn't exactly match any of
the three presets — real counts are 1,005 customers / 20,000 orders,
while `medium` would produce exactly 1,000/100,000 and `small` exactly
200/10,000. Whatever produced the current `data/` folder wasn't a
straightforward `--size medium` or `--size small` run with current
defaults, and the exact original invocation isn't recorded anywhere.
Regenerating with `--size medium` will **not** reproduce the current
dataset — it'll produce a different (larger) one. That's fine for
teaching purposes (the schema and query patterns don't depend on exact
row counts) but don't assume `--size medium` gets you back to what's
here now.

**2. Build the database** (`build_nova_db.sh`), from **this folder**,
not `data_generator/`:

```bash
./build_nova_db.sh
```

This just replays the pre-generated SQL (`cat data/schema.sql
data/data.sql | duckdb nova_db.duckdb`) — it does **not** re-run the
generator. If you want fresh/different data, run stage 1 first.

## Notebooks

`notebook_1_basics_marimo.py`, `notebook_2_intermediate_marimo.py`,
`notebook_3_advanced_marimo.py` — connect read-only to `nova_db.duckdb`
built in stage 2.

**`build_notebooks.py` is not part of this pipeline** — it's a leftover
generator for `.ipynb` versions of these three notebooks
(`notebook_1_basics.ipynb`, etc.). Those `.ipynb` files are **not present
anywhere in this repo** (verified — zero `.ipynb` files exist under
`github/` or `instructor/`); only the `_marimo.py` versions actually
shipped. Running `build_notebooks.py` would produce `.ipynb` files that
don't currently exist here — do that intentionally, not by accident.
