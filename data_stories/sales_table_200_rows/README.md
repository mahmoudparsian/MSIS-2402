# 🧾 Sales Table — 200 Rows

**MSIS-2402 · Week 1, Part 1 — SQL Foundations**

The smallest data story in the folder, and deliberately so. **200 rows, one table** —
small enough that a student can open the CSV, scroll to the bottom, and check any
answer by hand.

**Use this first.** It is the only story here where "count them yourself" is a
realistic way to verify a query.

---

## Run it

```bash
cd data_stories/sales_table_200_rows                 # from the course repository folder
marimo edit sales_queries_marimo.py    # interactive
marimo run  sales_queries_marimo.py    # read-only, for students
```

| File | Role |
|---|---|
| `sales_queries_marimo.py` | The notebook — 25 queries in three tiers |
| `plot_helpers.py` | Chart functions, kept out of the notebook |
| `sales.csv` | **200 sales** (207 lines including duplicates) |
| `sales_db.duckdb` | The database, built by the notebook |

---

## The data

One table, seven columns:

```
sales(sale_id, sale_date, product_id, product_category,
      quantity, unit_price, total_amount)
```

- **`sale_date`** makes date filtering and grouping possible
- **`product_category`** is the natural `GROUP BY` column
- **`total_amount`** is `quantity × unit_price`, so students can check the arithmetic

---

## What it covers

| Section | Queries | Techniques |
|---|---|---|
| 1 — Basic | 5 | `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT` |
| 2 — Basic+ | 10 | `COUNT`, `SUM`, `AVG`, `GROUP BY`, `BETWEEN`, `LIKE` |
| 3 — Intermediate | 10 | `HAVING`, `CASE`, subqueries, light window functions |

The notebook also **deduplicates on load** — `sales.csv` has a few full duplicate
rows, and the notebook shows the count before and after removing them. That is a
small, honest first look at data quality before anything else happens.

---

## Why start this small

- **Every result fits on one screen.** Nothing is hidden below a scroll bar.
- **A student can verify by counting.** If a query says 43 sales are in
  "Electronics", they can check.
- **Mistakes are obvious.** On 200 rows a wrong `WHERE` clause produces a visibly
  wrong answer; on a million rows it produces a plausible one.

Every other story in this folder is at least 60,000 rows. This is the only chance
students get to build trust in their SQL by direct inspection — worth taking.

---

## Where to go next

| When students are ready for… | Go to |
|---|---|
| Aggregation on real volume | `coffee_shop_149K_records/` or `olympic_120_years/` |
| More than one table (joins) | `nova_retail/` or `books_users_ratings/` |
| Time-series and window functions | `taxi_210K_trips/` or `citi_bike_one_million/` |

---

## Teaching notes

- **Open `sales.csv` in a spreadsheet alongside the notebook.** Seeing the same data
  in both places is what makes a query feel like a question rather than a spell.
- The dedup step is worth a minute: ask why duplicate rows are a problem *before*
  showing the fix.
- Good exercise: have students compute one `GROUP BY` result by hand from the CSV,
  then write the SQL and compare. It takes five minutes and settles a lot of doubt.
