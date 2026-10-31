# Week 1 — Class Discussion 2 (Aggregation & KPIs)

Session 2 · work in pairs, just before the lab · **not graded — nothing to submit**

## SQL Features to Learn

| SQL Feature | Description |
|---|---|
| `COUNT`, `SUM`, `AVG` | Aggregate functions — turn many rows into one summary number |
| `GROUP BY` | Compute an aggregate separately for each group (e.g. per country) |
| `HAVING` | Filter groups by an aggregate result, after grouping |
| `WHERE` vs. `HAVING` | `WHERE` filters rows *before* grouping, so it can't use aggregates |
| `ORDER BY` an aggregate | Rank groups, e.g. countries by total revenue |

## Setup

**Dataset:** the table `sales`, from `data/sales_dataset.csv` in this
folder — 200 transactions in 4 countries (USA, UK, Germany, Canada) and 4
products (Laptop, Phone, Tablet, Watch). Columns: `order_id`, `country`,
`product`, `price` (unit price), `quantity`, `sales_amount` (the
transaction's revenue).

1. Open a terminal **in this folder** (the one that contains this file and
   `data/`).
2. Start a notebook with `marimo edit my_discussion.py` — or the DuckDB
   command line with `duckdb`.
3. Load the table once (in Marimo: add a SQL cell):

```sql
CREATE OR REPLACE TABLE sales AS
SELECT * FROM read_csv_auto('data/sales_dataset.csv');
```

## Simple

1. **(Discussion)** An executive almost never asks "show me all 200
   transactions." They ask "what's our total revenue?" or "which market is
   strongest?" What does an aggregate function (`COUNT`, `SUM`, `AVG`, …) do
   that turns 200 rows into an answer to a question like that?

2. **(SQL)** Write three separate queries, each returning one number:
   - `n_transactions` = `COUNT(*)`
   - `total_revenue` = `SUM(sales_amount)`
   - `avg_price` = `AVG(price)`, rounded to 2 decimals

## Intermediate

3. **(SQL + Discussion)** Revenue by country.
   - Columns: `country`, `revenue` = `SUM(sales_amount)`
   - One row per country, sorted by `revenue` descending

   Which market leads? By what percentage does it beat the weakest market —
   (leader − weakest) ÷ weakest × 100, to 1 decimal?

4. **(SQL + Discussion)** Only the countries whose total revenue is **more
   than $95,000**.
   - Columns: `country`, `revenue`
   - Sort: `revenue` descending

   Why does this need `HAVING` instead of `WHERE`? What happens if you write
   `WHERE SUM(sales_amount) > 95000` instead? (Try it.)

## Intermediate+

5. **(SQL + Discussion)** Volume vs. value, per product.
   - Columns: `product`, `revenue` = `SUM(sales_amount)`,
     `n_transactions` = `COUNT(*)`, `avg_price` = `AVG(price)` rounded to 2
     decimals
   - Sort: `revenue` descending

   Is the product with the most transactions also the one with the highest
   average price? What does that tell you about whether this business's
   revenue is driven more by *volume* (many cheaper sales) or *value* (fewer,
   pricier sales)?

6. **(Discussion — debug it)** A classmate's query throws this error:

   ```sql
   SELECT country, SUM(sales_amount)
   FROM sales
   WHERE SUM(sales_amount) > 90000;
   ```

   ```console
   Binder Error: WHERE clause cannot contain aggregates!
   ```

   Explain in your own words *why* `WHERE` refuses to filter on
   `SUM(sales_amount)`, even though the query "looks" like it should work.
   Then rewrite it so it returns each country whose total revenue is above
   90,000 — columns `country`, `revenue`. (The original is missing one more
   clause, too.)
