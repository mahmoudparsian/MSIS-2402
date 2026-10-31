import json, uuid

def uid():
    return uuid.uuid4().hex[:8]

def md(src):
    lines = src.strip().split('\n')
    lines = [l + '\n' for l in lines[:-1]] + [lines[-1]]
    return {'cell_type':'markdown','metadata':{},'source':lines,'id':uid()}

def code(src):
    lines = src.strip().split('\n')
    lines = [l + '\n' for l in lines[:-1]] + [lines[-1]]
    return {'cell_type':'code','metadata':{},'source':lines,'outputs':[],'execution_count':None,'id':uid()}

nb = {
    'nbformat': 4, 'nbformat_minor': 5,
    'metadata': {
        'kernelspec': {'display_name': 'Python 3 (ipykernel)', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.11.0'}
    },
    'cells': []
}
c = nb['cells']

# ═══════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════
c.append(md("""# Coffee Shop Sales — SQL Analysis Notebook

This notebook opens the DuckDB database created by **Notebook 1**
(`coffee_shop_sales.duckdb`) and runs **30 progressive SQL queries**
organized by difficulty:

| Level | Count | Key Concepts |
|---|---|---|
| **Basic** | 5 | `SELECT`, `COUNT`, `SUM`, `DISTINCT`, `ORDER BY`, `LIMIT` |
| **Basic+** | 10 | `GROUP BY`, `WHERE`, `HAVING`, `ROUND`, aggregation functions |
| **Intermediate** | 10 | Multi-column `GROUP BY`, `CASE`, subqueries, `JOIN`-style thinking, time analytics |
| **Ranking / Window** | 5 | `WITH` (CTEs), `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, running totals |

### Design
- Each cell starts with a Markdown explanation (**what** and **why**).
- SQL is formatted for readability.
- Results are displayed as DataFrames.
- Plots use the decoupled `plot_helpers.py` module.

> **Prerequisite:** run `coffee_shop_build_db.ipynb` first to create the `.duckdb` file."""))

# ═══════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════
c.append(md("""## Setup — Import libraries and open the database"""))

c.append(code("""import warnings
warnings.filterwarnings("ignore")

import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# Decoupled plotting helpers
from plot_helpers import (
    bar_chart, hbar_chart, line_chart,
    multi_line_chart, pie_chart, heatmap_chart,
    grouped_bar_chart
)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 160)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

con = duckdb.connect("coffee_shop_sales.duckdb", read_only=True)
print("Database opened. Tables:")
con.execute("SHOW TABLES").df()"""))

# ═══════════════════════════════════════════════
#  SECTION A — 5 BASIC QUERIES
# ═══════════════════════════════════════════════
c.append(md("""---
# Part A — Basic Queries (5)

These queries use only **SELECT**, **COUNT**, **SUM**, **DISTINCT**,
**ORDER BY**, and **LIMIT** — no grouping yet."""))

# --- A1 ---
c.append(md("""## A1 — How many rows are in the sales table?

### What are we doing?
We count the total number of rows (transaction lines).

### SQL concept
`COUNT(*)` counts every row, including those with NULLs in some columns."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT COUNT(*) AS total_rows
    FROM sales
\"\"\").df()
q"""))

# --- A2 ---
c.append(md("""## A2 — Show the first 10 transactions

### What are we doing?
We retrieve the first 10 rows to get a quick feel for the data.

### SQL concept
`LIMIT` restricts the result set to a fixed number of rows."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT *
    FROM sales
    ORDER BY transaction_id
    LIMIT 10
\"\"\").df()
q"""))

# --- A3 ---
c.append(md("""## A3 — How many distinct stores are there?

### What are we doing?
We count the number of unique `store_id` values.

### SQL concept
`COUNT(DISTINCT col)` counts unique values only."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT COUNT(DISTINCT store_id)   AS distinct_stores,
           COUNT(DISTINCT store_location) AS distinct_locations
    FROM sales
\"\"\").df()
q"""))

# --- A4 ---
c.append(md("""## A4 — What is the overall total revenue?

### What are we doing?
We sum `sales_amount` across all rows.

### SQL concept
`SUM()` is the most fundamental aggregation function."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT ROUND(SUM(sales_amount), 2) AS total_revenue,
           SUM(transaction_qty)         AS total_units_sold
    FROM sales
\"\"\").df()
q"""))

# --- A5 ---
c.append(md("""## A5 — List all distinct product categories

### What are we doing?
We retrieve every unique product category in the dataset.

### SQL concept
`SELECT DISTINCT` eliminates duplicate values from the result."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT DISTINCT product_category
    FROM sales
    ORDER BY product_category
\"\"\").df()
q"""))

# ═══════════════════════════════════════════════
#  SECTION B — 10 BASIC+ QUERIES
# ═══════════════════════════════════════════════
c.append(md("""---
# Part B — Basic+ Queries (10)

These queries introduce **GROUP BY**, **WHERE**, **HAVING**, and
multi-column aggregations."""))

# --- B1 ---
c.append(md("""## B1 — Total revenue by store location

### What are we doing?
We group all transaction lines by `store_location` and sum revenue.

### SQL concept
`GROUP BY` collapses rows that share the same value into a single
summary row. Combined with `SUM()`, it produces per-group totals."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   store_location,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    GROUP BY store_location
    ORDER BY revenue DESC
\"\"\").df()

bar_chart(q, "store_location", "revenue",
          title="Total Revenue by Store Location",
          xlabel="Store", ylabel="Revenue ($)")
q"""))

# --- B2 ---
c.append(md("""## B2 — Total revenue by product category

### What are we doing?
We roll up revenue to the product-category level — the broadest
product grouping.

### SQL concept
Same `GROUP BY` + `SUM` pattern, different column."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   product_category,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    GROUP BY product_category
    ORDER BY revenue DESC
\"\"\").df()

bar_chart(q, "product_category", "revenue",
          title="Revenue by Product Category",
          xlabel="Category", ylabel="Revenue ($)", rotation=30)
q"""))

# --- B3 ---
c.append(md("""## B3 — Number of transaction lines per store

### What are we doing?
We count how many transaction lines each store produced.

### SQL concept
`COUNT(*)` inside a `GROUP BY` gives us per-group counts — useful
for understanding volume vs. revenue."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   store_location,
             COUNT(*) AS transaction_lines
    FROM     sales
    GROUP BY store_location
    ORDER BY transaction_lines DESC
\"\"\").df()

bar_chart(q, "store_location", "transaction_lines",
          title="Transaction Lines by Store",
          xlabel="Store", ylabel="Transaction Lines")
q"""))

# --- B4 ---
c.append(md("""## B4 — Average unit price by product category

### What are we doing?
We compute the mean `unit_price` for each category to compare
pricing levels.

### SQL concept
`AVG()` — another aggregation function. Combined with `ROUND()`,
it keeps output readable."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   product_category,
             ROUND(AVG(unit_price), 2) AS avg_price
    FROM     sales
    GROUP BY product_category
    ORDER BY avg_price DESC
\"\"\").df()

bar_chart(q, "product_category", "avg_price",
          title="Average Unit Price by Category",
          xlabel="Category", ylabel="Avg Price ($)", rotation=30)
q"""))

# --- B5 ---
c.append(md("""## B5 — Revenue for Coffee products only (WHERE filter)

### What are we doing?
We filter for `product_category = 'Coffee'` and then aggregate
by `product_type`.

### SQL concept
`WHERE` filters rows **before** grouping. This is different from
`HAVING`, which filters **after** grouping."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   product_type,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    WHERE    product_category = 'Coffee'
    GROUP BY product_type
    ORDER BY revenue DESC
\"\"\").df()

bar_chart(q, "product_type", "revenue",
          title="Coffee Sub-Types by Revenue",
          xlabel="Product Type", ylabel="Revenue ($)", rotation=25)
q"""))

# --- B6 ---
c.append(md("""## B6 — Monthly revenue

### What are we doing?
We group by `month` and `month_name` to see revenue month over month.

### SQL concept
Grouping by two columns — the numeric `month` for ordering and
the text `month_name` for display."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   month,
             month_name,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    GROUP BY month, month_name
    ORDER BY month
\"\"\").df()

bar_chart(q, "month_name", "revenue",
          title="Monthly Revenue (Jan – Jun 2023)",
          xlabel="Month", ylabel="Revenue ($)")
q"""))

# --- B7 ---
c.append(md("""## B7 — Revenue by day of the week

### What are we doing?
We aggregate revenue by `day_name` to discover which weekdays
perform best.

### SQL concept
Using `CASE` inside `ORDER BY` to sort weekdays in calendar order
instead of alphabetical order."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   day_name,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    GROUP BY day_name
    ORDER BY CASE day_name
                 WHEN 'Monday'    THEN 1
                 WHEN 'Tuesday'   THEN 2
                 WHEN 'Wednesday' THEN 3
                 WHEN 'Thursday'  THEN 4
                 WHEN 'Friday'    THEN 5
                 WHEN 'Saturday'  THEN 6
                 WHEN 'Sunday'    THEN 7
             END
\"\"\").df()

bar_chart(q, "day_name", "revenue",
          title="Revenue by Day of Week",
          xlabel="Day", ylabel="Revenue ($)")
q"""))

# --- B8 ---
c.append(md("""## B8 — Top 10 best-selling product details by units sold

### What are we doing?
We rank individual products (`product_detail`) by total quantity sold.

### SQL concept
`SUM(transaction_qty)` + `ORDER BY … DESC` + `LIMIT 10` produces
a classic **Top-N** query."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   product_detail,
             SUM(transaction_qty) AS units_sold
    FROM     sales
    GROUP BY product_detail
    ORDER BY units_sold DESC
    LIMIT    10
\"\"\").df()

hbar_chart(q, "product_detail", "units_sold",
           title="Top 10 Products by Units Sold",
           xlabel="Units Sold", ylabel="Product")
q"""))

# --- B9 ---
c.append(md("""## B9 — Product categories with revenue above $50,000 (HAVING)

### What are we doing?
We filter *after* grouping to keep only high-revenue categories.

### SQL concept
`HAVING` applies a condition to the aggregated result.
Compare with `WHERE`, which filters individual rows *before* grouping.

> **Rule of thumb:** use `WHERE` for row-level filters,
> `HAVING` for aggregate-level filters."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   product_category,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    GROUP BY product_category
    HAVING   SUM(sales_amount) > 50000
    ORDER BY revenue DESC
\"\"\").df()

bar_chart(q, "product_category", "revenue",
          title="Categories with Revenue > $50K",
          xlabel="Category", ylabel="Revenue ($)", rotation=25)
q"""))

# --- B10 ---
c.append(md("""## B10 — Minimum, maximum, and average sales amount per store

### What are we doing?
We compute `MIN`, `MAX`, and `AVG` of `sales_amount` grouped by store.

### SQL concept
Multiple aggregation functions in one `SELECT` — a common pattern
for building business summary reports."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   store_location,
             ROUND(MIN(sales_amount), 2)  AS min_sale,
             ROUND(AVG(sales_amount), 2)  AS avg_sale,
             ROUND(MAX(sales_amount), 2)  AS max_sale,
             COUNT(*)                      AS total_lines
    FROM     sales
    GROUP BY store_location
    ORDER BY avg_sale DESC
\"\"\").df()
q"""))

# ═══════════════════════════════════════════════
#  SECTION C — 10 INTERMEDIATE QUERIES
# ═══════════════════════════════════════════════
c.append(md("""---
# Part C — Intermediate Queries (10)

These queries combine multiple concepts: multi-column `GROUP BY`,
`CASE` expressions, subqueries, time-based analytics, and cross-
dimensional analysis."""))

# --- C1 ---
c.append(md("""## C1 — Revenue by hour of day

### What are we doing?
We aggregate revenue by `hour` to find peak business hours.

### SQL concept
Grouping by a numeric derived column. The result drives staffing
and promotional decisions."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   hour,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    GROUP BY hour
    ORDER BY hour
\"\"\").df()

line_chart(q, "hour", "revenue",
           title="Revenue by Hour of Day",
           xlabel="Hour", ylabel="Revenue ($)")
q"""))

# --- C2 ---
c.append(md("""## C2 — Morning vs. Afternoon vs. Evening sales (CASE)

### What are we doing?
We classify each transaction into a **day part** using a `CASE`
expression, then aggregate revenue by day part.

### SQL concept
`CASE WHEN … THEN … END` creates computed columns inside SQL —
similar to an if/else ladder."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT
        CASE
            WHEN hour BETWEEN  6 AND 11 THEN 'Morning   (6–11)'
            WHEN hour BETWEEN 12 AND 16 THEN 'Afternoon (12–16)'
            WHEN hour BETWEEN 17 AND 20 THEN 'Evening   (17–20)'
            ELSE 'Other'
        END AS day_part,
        ROUND(SUM(sales_amount), 2) AS revenue,
        COUNT(*)                     AS transaction_lines
    FROM     sales
    GROUP BY day_part
    ORDER BY revenue DESC
\"\"\").df()

bar_chart(q, "day_part", "revenue",
          title="Revenue by Day Part",
          xlabel="Day Part", ylabel="Revenue ($)")
q"""))

# --- C3 ---
c.append(md("""## C3 — Coffee vs. Tea: monthly revenue comparison

### What are we doing?
We compare the two largest categories — Coffee and Tea — month by month.

### SQL concept
`WHERE … IN (…)` combined with multi-column `GROUP BY` produces a
useful cross-tabulation that can be pivoted for visualization."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   month,
             month_name,
             product_category,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    WHERE    product_category IN ('Coffee', 'Tea')
    GROUP BY month, month_name, product_category
    ORDER BY month, product_category
\"\"\").df()

grouped_bar_chart(q, "month_name", "product_category", "revenue",
                  title="Coffee vs Tea — Monthly Revenue",
                  xlabel="Month", ylabel="Revenue ($)")
q"""))

# --- C4 ---
c.append(md("""## C4 — Daily revenue trend

### What are we doing?
We compute total revenue for each calendar date and plot it as a
time series.

### SQL concept
Grouping by a date column reveals business trends and seasonality."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   transaction_date,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    GROUP BY transaction_date
    ORDER BY transaction_date
\"\"\").df()

line_chart(q, "transaction_date", "revenue",
           title="Daily Revenue Trend (Jan – Jun 2023)",
           xlabel="Date", ylabel="Revenue ($)", marker=None)
q.head(10)"""))

# --- C5 ---
c.append(md("""## C5 — Revenue per store per month

### What are we doing?
We break down revenue by **store and month** simultaneously.

### SQL concept
Multi-column `GROUP BY` with three grouping columns — a common
pattern in business reporting."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   store_location,
             month,
             month_name,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    GROUP BY store_location, month, month_name
    ORDER BY store_location, month
\"\"\").df()

grouped_bar_chart(q, "month_name", "store_location", "revenue",
                  title="Revenue by Store and Month",
                  xlabel="Month", ylabel="Revenue ($)")
q"""))

# --- C6 ---
c.append(md("""## C6 — Top 15 products by revenue

### What are we doing?
We rank individual menu items (product_detail) by total revenue.

### SQL concept
A Top-N query at the most granular product level."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   product_detail,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    GROUP BY product_detail
    ORDER BY revenue DESC
    LIMIT    15
\"\"\").df()

hbar_chart(q, "product_detail", "revenue",
           title="Top 15 Products by Revenue",
           xlabel="Revenue ($)", ylabel="Product")
q"""))

# --- C7 ---
c.append(md("""## C7 — Revenue heatmap: day of week × hour

### What are we doing?
We build a two-dimensional summary — revenue by **weekday** and
**hour** — and visualize it as a heatmap.

### SQL concept
Multi-column `GROUP BY` where one column becomes the row axis and
the other becomes the column axis. This is a common OLAP pattern."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   day_name,
             hour,
             ROUND(SUM(sales_amount), 2) AS revenue
    FROM     sales
    GROUP BY day_name, hour
    ORDER BY day_name, hour
\"\"\").df()

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

heatmap_chart(q, "day_name", "hour", "revenue",
              title="Revenue Heatmap: Day × Hour",
              xlabel="Hour", ylabel="Day of Week",
              index_order=day_order)"""))

# --- C8 ---
c.append(md("""## C8 — Stores where Tea revenue exceeds $60,000

### What are we doing?
We combine `WHERE` (to filter for Tea) and `HAVING` (to filter
on the aggregate) in one query.

### SQL concept
`WHERE` + `GROUP BY` + `HAVING` in sequence — a powerful trio for
targeted business questions."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   store_location,
             ROUND(SUM(sales_amount), 2) AS tea_revenue
    FROM     sales
    WHERE    product_category = 'Tea'
    GROUP BY store_location
    HAVING   SUM(sales_amount) > 60000
    ORDER BY tea_revenue DESC
\"\"\").df()

bar_chart(q, "store_location", "tea_revenue",
          title="Stores with Tea Revenue > $60K",
          xlabel="Store", ylabel="Tea Revenue ($)")
q"""))

# --- C9 ---
c.append(md("""## C9 — Category revenue share (percentage of total)

### What are we doing?
We compute each category's share of total revenue using a **scalar
subquery** that returns the overall total.

### SQL concept
A subquery in the `SELECT` clause — sometimes called a **scalar
subquery** because it returns exactly one value."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   product_category,
             ROUND(SUM(sales_amount), 2)  AS revenue,
             ROUND(
                 SUM(sales_amount) * 100.0
                 / (SELECT SUM(sales_amount) FROM sales),
             1) AS pct_of_total
    FROM     sales
    GROUP BY product_category
    ORDER BY revenue DESC
\"\"\").df()

pie_chart(q, "product_category", "revenue",
          title="Revenue Share by Product Category")
q"""))

# --- C10 ---
c.append(md("""## C10 — Top 10 busiest days (by transaction count)

### What are we doing?
We find the 10 calendar dates with the most transaction lines.

### SQL concept
Combining `GROUP BY`, `COUNT`, `ORDER BY DESC`, and `LIMIT` —
a classic reporting query."""))

c.append(code("""q = con.execute(\"\"\"
    SELECT   transaction_date,
             day_name,
             COUNT(*)                     AS transaction_lines,
             ROUND(SUM(sales_amount), 2)  AS revenue
    FROM     sales
    GROUP BY transaction_date, day_name
    ORDER BY transaction_lines DESC
    LIMIT    10
\"\"\").df()

bar_chart(q, "transaction_date", "transaction_lines",
          title="Top 10 Busiest Days",
          xlabel="Date", ylabel="Transaction Lines", rotation=45)
q"""))

# ═══════════════════════════════════════════════
#  SECTION D — 5 RANKING / WINDOW FUNCTION QUERIES
# ═══════════════════════════════════════════════
c.append(md("""---
# Part D — Ranking & Window Function Queries (5)

These queries use **Common Table Expressions (CTEs)** with the `WITH`
keyword and **window functions**: `ROW_NUMBER`, `RANK`, `DENSE_RANK`,
`NTILE`, and running totals with `SUM() OVER`.

### What is a CTE?
A CTE (Common Table Expression) is a named temporary result set
defined with `WITH`. It makes complex queries easier to read by
breaking them into logical steps.

### What are window functions?
Window functions compute values across a set of rows related to the
current row **without collapsing the result set** the way `GROUP BY`
does. They use the `OVER (PARTITION BY … ORDER BY …)` clause."""))

# --- D1 ---
c.append(md("""## D1 — Rank stores by revenue using ROW_NUMBER

### What are we doing?
We use a CTE to aggregate revenue by store, then apply `ROW_NUMBER()`
to assign a sequential rank.

### SQL concept
`ROW_NUMBER() OVER (ORDER BY …)` assigns 1, 2, 3, … with no ties —
each row gets a unique number."""))

c.append(code("""q = con.execute(\"\"\"
    WITH store_rev AS (
        SELECT   store_location,
                 ROUND(SUM(sales_amount), 2) AS revenue
        FROM     sales
        GROUP BY store_location
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rank_num,
        store_location,
        revenue
    FROM store_rev
\"\"\").df()
q"""))

# --- D2 ---
c.append(md("""## D2 — Top 3 products per category using RANK

### What are we doing?
For each product category, we rank products by revenue and keep
only the top 3.

### SQL concept
`RANK() OVER (PARTITION BY … ORDER BY …)` assigns ranks **within
each partition**. Ties receive the same rank, and the next rank
is skipped (e.g., 1, 2, 2, 4).

The outer `WHERE rnk <= 3` filters after ranking."""))

c.append(code("""q = con.execute(\"\"\"
    WITH product_rev AS (
        SELECT   product_category,
                 product_type,
                 ROUND(SUM(sales_amount), 2) AS revenue
        FROM     sales
        GROUP BY product_category, product_type
    ),
    ranked AS (
        SELECT *,
               RANK() OVER (
                   PARTITION BY product_category
                   ORDER BY revenue DESC
               ) AS rnk
        FROM product_rev
    )
    SELECT product_category,
           product_type,
           revenue,
           rnk
    FROM   ranked
    WHERE  rnk <= 3
    ORDER BY product_category, rnk
\"\"\").df()
q"""))

# --- D3 ---
c.append(md("""## D3 — Monthly revenue with running total (cumulative sum)

### What are we doing?
We compute monthly revenue and add a running total that accumulates
from January through June.

### SQL concept
`SUM(revenue) OVER (ORDER BY month)` computes a **cumulative sum**
— one of the most useful window-function patterns in business
analytics."""))

c.append(code("""q = con.execute(\"\"\"
    WITH monthly AS (
        SELECT   month,
                 month_name,
                 ROUND(SUM(sales_amount), 2) AS revenue
        FROM     sales
        GROUP BY month, month_name
    )
    SELECT
        month,
        month_name,
        revenue,
        ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS running_total
    FROM monthly
    ORDER BY month
\"\"\").df()

multi_line_chart(q, "month_name",
                 ["revenue", "running_total"],
                 labels=["Monthly Revenue", "Running Total"],
                 title="Monthly Revenue with Running Total",
                 xlabel="Month", ylabel="Revenue ($)")
q"""))

# --- D4 ---
c.append(md("""## D4 — Assign product categories to revenue quartiles using NTILE

### What are we doing?
We divide product categories into 4 equal-sized buckets (quartiles)
based on revenue. `NTILE(4)` assigns a bucket number 1–4.

### SQL concept
`NTILE(n)` divides the ordered result set into `n` roughly equal
groups. It is useful for segmentation — e.g., "top 25 %", "bottom 25 %"."""))

c.append(code("""q = con.execute(\"\"\"
    WITH cat_rev AS (
        SELECT   product_category,
                 ROUND(SUM(sales_amount), 2) AS revenue
        FROM     sales
        GROUP BY product_category
    )
    SELECT
        product_category,
        revenue,
        NTILE(4) OVER (ORDER BY revenue DESC) AS quartile
    FROM cat_rev
    ORDER BY revenue DESC
\"\"\").df()
q"""))

# --- D5 ---
c.append(md("""## D5 — DENSE_RANK products within each store

### What are we doing?
For each store, we rank the top 5 product types by revenue using
`DENSE_RANK`. Unlike `RANK`, `DENSE_RANK` never skips numbers
after a tie (e.g., 1, 2, 2, **3** instead of 1, 2, 2, **4**).

### SQL concept
`DENSE_RANK() OVER (PARTITION BY … ORDER BY …)` is preferred when
you want consecutive rank numbers even when there are ties."""))

c.append(code("""q = con.execute(\"\"\"
    WITH store_product AS (
        SELECT   store_location,
                 product_type,
                 ROUND(SUM(sales_amount), 2) AS revenue
        FROM     sales
        GROUP BY store_location, product_type
    ),
    ranked AS (
        SELECT *,
               DENSE_RANK() OVER (
                   PARTITION BY store_location
                   ORDER BY revenue DESC
               ) AS drnk
        FROM store_product
    )
    SELECT store_location,
           product_type,
           revenue,
           drnk
    FROM   ranked
    WHERE  drnk <= 5
    ORDER BY store_location, drnk
\"\"\").df()

print(q.to_string(index=False))"""))

# ═══════════════════════════════════════════════
# WRAP-UP
# ═══════════════════════════════════════════════
c.append(md("""---
## Summary

We ran **30 SQL queries** at four difficulty levels:

| Level | Concepts Practiced |
|---|---|
| Basic (5) | `SELECT`, `COUNT`, `SUM`, `DISTINCT`, `LIMIT` |
| Basic+ (10) | `GROUP BY`, `WHERE`, `HAVING`, `AVG`, `MIN`, `MAX`, Top-N |
| Intermediate (10) | `CASE`, subqueries, multi-column grouping, time analytics, heatmaps |
| Ranking (5) | CTEs (`WITH`), `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, running totals |

### Key takeaways
- `WHERE` filters rows **before** grouping; `HAVING` filters **after** grouping.
- Window functions (`OVER`) compute across rows without collapsing the result set.
- CTEs (`WITH`) improve readability by naming intermediate result sets.
- Real-world analytics often combine multiple concepts in a single query.

### Suggested extensions
- Add month-over-month growth percentages using `LAG()`
- Build store-level forecasts
- Create dashboards with Streamlit or Plotly"""))

c.append(code("""con.close()
print("All 30 queries executed. Database connection closed.")"""))

# Write the notebook
with open('/sessions/happy-laughing-dijkstra/mnt/coffee_shop/coffee_shop_sql_analysis.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Notebook 2 written successfully. Total cells: {len(c)}")
