#!/usr/bin/env python3
"""Generate the three Nova Retail SQL notebooks as .ipynb files."""
import json, os

DB_PATH = "nova_db.duckdb"

def nb():
    """Return a blank notebook skeleton."""
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "cells": []
    }

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip().split("\n"), "id": None}

def code(source):
    return {"cell_type": "code", "metadata": {}, "source": source.strip().split("\n"), "outputs": [], "execution_count": None, "id": None}

# fix: source lines need newlines except last
def fix_source(cell):
    lines = cell["source"]
    cell["source"] = [l + "\n" for l in lines[:-1]] + [lines[-1]] if lines else []
    return cell

def build_nb(cells):
    n = nb()
    n["cells"] = [fix_source(c) for c in cells]
    # assign ids
    for i, c in enumerate(n["cells"]):
        c["id"] = f"cell-{i:03d}"
    return n

def save(notebook, path):
    with open(path, "w") as f:
        json.dump(notebook, f, indent=1)
    print(f"  ✓ Saved {path}  ({len(notebook['cells'])} cells)")

# ════════════════════════════════════════════════════════════════
#  NOTEBOOK 1 — BASICS
# ════════════════════════════════════════════════════════════════

nb1_cells = [
    md("""# Notebook 1 — Basic SQL Queries (Nova Retail)

This notebook covers **fundamental SQL concepts** using the Nova Retail DuckDB database.

**Topics covered:** SELECT, WHERE, ORDER BY, LIMIT, COUNT, SUM, AVG, MIN, MAX,
DISTINCT, LIKE, BETWEEN, IN, IS NULL, basic GROUP BY, and simple aggregations.

**Structure:** 5 basic queries + 10 basic+ queries.  
Each query includes an explanation, the SQL, the result, and a plot where appropriate."""),

    # ── Setup ──
    md("## Setup — Connect to the Database"),
    code("""import duckdb
import pandas as pd
import sys, os

# make sure plot_helpers is importable
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
from plot_helpers import (
    plot_bar, plot_hbar, plot_line, plot_pie,
    plot_grouped_bar, plot_stacked_bar
)

# open database in READ-ONLY mode
con = duckdb.connect("nova_db.duckdb", read_only=True)
print("Connected to nova_db.duckdb (read-only)")
print("Tables:", con.execute("SHOW TABLES").fetchdf().to_string(index=False))"""),

    # ─── BASIC QUERIES (1-5) ───────────────────────────────────
    md("---\n## Part A — Basic Queries (5 queries)"),

    # Q1
    md("""### Q1 — Preview the Customers Table
**Concept:** `SELECT` with `LIMIT`  
We start by peeking at the first 10 rows of the `customers` table to understand its structure."""),
    code("""sql = \"\"\"
SELECT *
FROM   customers
LIMIT  10;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q2
    md("""### Q2 — Count the Total Number of Orders
**Concept:** `COUNT(*)` aggregate  
A single-value query that tells us the total volume of orders in the database."""),
    code("""sql = \"\"\"
SELECT COUNT(*) AS total_orders
FROM   orders;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q3
    md("""### Q3 — List All Distinct Product Categories
**Concept:** `SELECT DISTINCT`  
Returns the unique set of product categories available in the catalogue."""),
    code("""sql = \"\"\"
SELECT DISTINCT category
FROM   products
ORDER  BY category;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q4
    md("""### Q4 — Find the Most Expensive Product
**Concept:** `ORDER BY … DESC` with `LIMIT 1`  
Retrieves the single product with the highest price."""),
    code("""sql = \"\"\"
SELECT product_id,
       category,
       price
FROM   products
ORDER  BY price DESC
LIMIT  1;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q5
    md("""### Q5 — Customers Who Signed Up in 2024
**Concept:** `WHERE` with `BETWEEN` on dates  
Filters customers whose `signup_date` falls within the year 2024."""),
    code("""sql = \"\"\"
SELECT customer_id,
       gender,
       country,
       customer_segment,
       signup_date
FROM   customers
WHERE  signup_date BETWEEN '2024-01-01' AND '2024-12-31'
ORDER  BY signup_date
LIMIT  15;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # ─── BASIC+ QUERIES (6-15) ─────────────────────────────────
    md("---\n## Part B — Basic+ Queries (10 queries)"),

    # Q6
    md("""### Q6 — Total Revenue Across All Orders
**Concept:** `SUM()` aggregate  
Computes the grand total of `sales_amount` across all order items."""),
    code("""sql = \"\"\"
SELECT SUM(sales_amount) AS total_revenue
FROM   order_items;
\"\"\"
df = con.execute(sql).fetchdf()
print(f"Total Revenue: ${df['total_revenue'][0]:,.2f}")"""),

    # Q7
    md("""### Q7 — Number of Customers per Country
**Concept:** `GROUP BY` + `COUNT`  
Groups customers by their country and counts how many are in each.
This is one of the most fundamental GROUP BY patterns."""),
    code("""sql = \"\"\"
SELECT   country,
         COUNT(*) AS num_customers
FROM     customers
GROUP BY country
ORDER BY num_customers DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "country", "num_customers",
        title="Number of Customers per Country",
        xlabel="Country", ylabel="Customers")"""),

    # Q8
    md("""### Q8 — Average Product Price by Category
**Concept:** `GROUP BY` + `AVG`  
Shows the average price for each product category — useful for understanding the price tier of each category."""),
    code("""sql = \"\"\"
SELECT   category,
         ROUND(AVG(price), 2) AS avg_price
FROM     products
GROUP BY category
ORDER BY avg_price DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_hbar(df, "category", "avg_price",
         title="Average Product Price by Category",
         xlabel="Average Price ($)", ylabel="Category")"""),

    # Q9
    md("""### Q9 — Orders Placed Each Year  (Derived Column: order_year)
**Concept:** `EXTRACT(YEAR …)` derived column + `GROUP BY`  
We create a derived column `order_year` directly in the SQL using `EXTRACT`, then count orders per year."""),
    code("""sql = \"\"\"
SELECT   EXTRACT(YEAR FROM order_date) AS order_year,
         COUNT(*)                       AS num_orders
FROM     orders
GROUP BY order_year
ORDER BY order_year;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "order_year", "num_orders",
        title="Number of Orders per Year",
        xlabel="Year", ylabel="Orders")"""),

    # Q10
    md("""### Q10 — Revenue by Product Category
**Concept:** `GROUP BY` + `SUM`  
Sums `sales_amount` by category to find out which product lines generate the most revenue."""),
    code("""sql = \"\"\"
SELECT   category,
         ROUND(SUM(sales_amount), 2) AS total_revenue
FROM     order_items
GROUP BY category
ORDER BY total_revenue DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_pie(df, "category", "total_revenue",
        title="Revenue Share by Product Category")"""),

    # Q11
    md("""### Q11 — Top 5 Customers by Total Spending
**Concept:** `GROUP BY` + `SUM` + `ORDER BY … DESC LIMIT`  
Identifies the five biggest spenders by summing their order-item sales."""),
    code("""sql = \"\"\"
SELECT   oi.order_id,
         o.customer_id,
         ROUND(SUM(oi.sales_amount), 2) AS total_spent
FROM     order_items oi
         JOIN orders o ON oi.order_id = o.order_id
GROUP BY oi.order_id, o.customer_id
ORDER BY total_spent DESC
LIMIT    5;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q12
    md("""### Q12 — Customer Segment Distribution
**Concept:** `GROUP BY` + `COUNT` on a categorical column  
Counts how many customers fall into each segment (Consumer, Corporate, VIP, Small Business)."""),
    code("""sql = \"\"\"
SELECT   customer_segment,
         COUNT(*) AS num_customers
FROM     customers
GROUP BY customer_segment
ORDER BY num_customers DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_pie(df, "customer_segment", "num_customers",
        title="Customer Segment Distribution")"""),

    # Q13
    md("""### Q13 — Monthly Order Volume for 2024
**Concept:** `EXTRACT(MONTH …)` derived column + `WHERE` year filter  
Computes the number of orders placed each month during 2024."""),
    code("""sql = \"\"\"
SELECT   EXTRACT(MONTH FROM order_date) AS order_month,
         COUNT(*)                        AS num_orders
FROM     orders
WHERE    EXTRACT(YEAR FROM order_date) = 2024
GROUP BY order_month
ORDER BY order_month;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_line(df, "order_month", "num_orders",
         title="Monthly Order Volume in 2024",
         xlabel="Month", ylabel="Orders")"""),

    # Q14
    md("""### Q14 — Products in the Electronics Category Priced Above $300
**Concept:** `WHERE` with compound conditions (`AND`)  
Filters the product catalog for Electronics items above the $300 price point."""),
    code("""sql = \"\"\"
SELECT   product_id,
         category,
         price
FROM     products
WHERE    category = 'Electronics'
  AND    price > 300
ORDER BY price DESC
LIMIT    10;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q15
    md("""### Q15 — Gender Breakdown of Customers
**Concept:** `GROUP BY` + percentage calculation  
Counts customers by gender and computes each group's share as a percentage."""),
    code("""sql = \"\"\"
SELECT   gender,
         COUNT(*)                                           AS num_customers,
         ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM     customers
GROUP BY gender
ORDER BY num_customers DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "gender", "num_customers",
        title="Customer Gender Distribution",
        xlabel="Gender", ylabel="Customers")"""),

    # ── Cleanup ──
    md("---\n## Cleanup"),
    code("""con.close()
print("Connection closed.")"""),
]

# ════════════════════════════════════════════════════════════════
#  NOTEBOOK 2 — INTERMEDIATE
# ════════════════════════════════════════════════════════════════

nb2_cells = [
    md("""# Notebook 2 — Intermediate SQL Queries (Nova Retail)

This notebook builds on the basics and introduces **intermediate SQL concepts**.

**Topics covered:** JOIN (INNER, LEFT, RIGHT), WHERE vs HAVING, multi-table GROUP BY,
sub-queries, CASE expressions, NULL handling, and compound aggregations.

**Structure:** 5 basic+ queries + 10 intermediate queries.  
Each query includes an explanation, the SQL, the result, and a plot where appropriate."""),

    md("## Setup — Connect to the Database"),
    code("""import duckdb
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
from plot_helpers import (
    plot_bar, plot_hbar, plot_line, plot_pie,
    plot_grouped_bar, plot_stacked_bar, plot_multi_line
)

con = duckdb.connect("nova_db.duckdb", read_only=True)
print("Connected to nova_db.duckdb (read-only)")"""),

    # ─── BASIC+ QUERIES (1-5) ─────────────────────────────────
    md("---\n## Part A — Basic+ Queries (5 queries)"),

    # Q1
    md("""### Q1 — Revenue per Country
**Concept:** `JOIN` + `GROUP BY` + `SUM`  
We join `orders` → `order_items` and then bring in `customers` to aggregate revenue by country."""),
    code("""sql = \"\"\"
SELECT   c.country,
         ROUND(SUM(oi.sales_amount), 2) AS total_revenue
FROM     order_items  oi
         JOIN orders    o  ON oi.order_id   = o.order_id
         JOIN customers c  ON o.customer_id = c.customer_id
GROUP BY c.country
ORDER BY total_revenue DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "country", "total_revenue",
        title="Total Revenue by Country",
        xlabel="Country", ylabel="Revenue ($)")"""),

    # Q2
    md("""### Q2 — Number of Items Sold per Category
**Concept:** `SUM(quantity)` grouped by category  
Tells us which product categories move the most units."""),
    code("""sql = \"\"\"
SELECT   category,
         SUM(quantity) AS units_sold
FROM     order_items
GROUP BY category
ORDER BY units_sold DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_hbar(df, "category", "units_sold",
         title="Units Sold by Category",
         xlabel="Units Sold", ylabel="Category")"""),

    # Q3
    md("""### Q3 — Average Order Value (AOV) per Year
**Concept:** Derived column `order_year` + multi-table join + AVG of sum  
We first compute each order's total, then average those totals by year."""),
    code("""sql = \"\"\"
WITH order_totals AS (
    SELECT o.order_id,
           EXTRACT(YEAR FROM o.order_date) AS order_year,
           SUM(oi.sales_amount)            AS order_total
    FROM   orders      o
           JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id, order_year
)
SELECT   order_year,
         ROUND(AVG(order_total), 2) AS avg_order_value
FROM     order_totals
GROUP BY order_year
ORDER BY order_year;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "order_year", "avg_order_value",
        title="Average Order Value by Year",
        xlabel="Year", ylabel="AOV ($)")"""),

    # Q4
    md("""### Q4 — Top 10 Most-Ordered Products
**Concept:** `GROUP BY product_id` + `SUM(quantity)` + `LIMIT`  
Identifies the products that appear most frequently in orders by total quantity."""),
    code("""sql = \"\"\"
SELECT   oi.product_id,
         p.category,
         ROUND(p.price, 2)  AS unit_price,
         SUM(oi.quantity)    AS total_qty_sold
FROM     order_items oi
         JOIN products p ON oi.product_id = p.product_id
GROUP BY oi.product_id, p.category, p.price
ORDER BY total_qty_sold DESC
LIMIT    10;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q5
    md("""### Q5 — Quarterly Revenue for 2023
**Concept:** `EXTRACT(QUARTER …)` derived column + date filter  
Groups revenue by fiscal quarter for the year 2023."""),
    code("""sql = \"\"\"
SELECT   EXTRACT(QUARTER FROM o.order_date) AS quarter,
         ROUND(SUM(oi.sales_amount), 2)      AS quarterly_revenue
FROM     orders      o
         JOIN order_items oi ON o.order_id = oi.order_id
WHERE    EXTRACT(YEAR FROM o.order_date) = 2023
GROUP BY quarter
ORDER BY quarter;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "quarter", "quarterly_revenue",
        title="Quarterly Revenue — 2023",
        xlabel="Quarter", ylabel="Revenue ($)")"""),

    # ─── INTERMEDIATE QUERIES (6-15) ──────────────────────────
    md("---\n## Part B — Intermediate Queries (10 queries)"),

    # Q6 — WHERE vs HAVING
    md("""### Q6 — WHERE vs HAVING: Categories with Average Sale > $200  
**Concept:** `WHERE` vs `HAVING` — the fundamental distinction  
- `WHERE` filters **rows** *before* grouping.  
- `HAVING` filters **groups** *after* aggregation.

Here we keep only order items with quantity ≥ 2 (`WHERE`), group by category,
and then retain only categories whose average sale exceeds $200 (`HAVING`)."""),
    code("""sql = \"\"\"
SELECT   category,
         COUNT(*)                        AS num_items,
         ROUND(AVG(sales_amount), 2)     AS avg_sale
FROM     order_items
WHERE    quantity >= 2                   -- row-level filter (before grouping)
GROUP BY category
HAVING   AVG(sales_amount) > 200        -- group-level filter (after aggregation)
ORDER BY avg_sale DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "category", "avg_sale",
        title="Categories with Avg Sale > $200 (qty ≥ 2)",
        xlabel="Category", ylabel="Avg Sale ($)")"""),

    # Q7 — INNER JOIN
    md("""### Q7 — INNER JOIN: Orders with Customer and Product Details
**Concept:** `INNER JOIN` across three tables  
An inner join returns only rows with matching keys in **both** tables.
We join `orders` → `customers` and `order_items` → `products` to build a rich order detail view."""),
    code("""sql = \"\"\"
SELECT   o.order_id,
         c.customer_id,
         c.country,
         c.customer_segment,
         oi.product_id,
         p.category,
         oi.quantity,
         ROUND(oi.sales_amount, 2) AS sales_amount,
         o.order_date
FROM     orders       o
         INNER JOIN customers   c  ON o.customer_id  = c.customer_id
         INNER JOIN order_items oi ON o.order_id     = oi.order_id
         INNER JOIN products    p  ON oi.product_id  = p.product_id
ORDER BY o.order_date DESC
LIMIT    15;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q8 — LEFT JOIN — customers who never bought anything
    md("""### Q8 — LEFT JOIN: Customers Who Never Bought Anything
**Concept:** `LEFT JOIN` + `IS NULL` to find non-matching rows  
A LEFT JOIN keeps **all** rows from the left table (customers) even if there is no matching order.
By filtering where `order_id IS NULL`, we find customers with zero purchases."""),
    code("""sql = \"\"\"
SELECT   c.customer_id,
         c.gender,
         c.country,
         c.customer_segment,
         c.signup_date
FROM     customers c
         LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE    o.order_id IS NULL
ORDER BY c.customer_id;
\"\"\"
df = con.execute(sql).fetchdf()
print(f"Customers who never placed an order: {len(df)}")
df"""),

    # Q9 — LEFT JOIN — products never sold
    md("""### Q9 — LEFT JOIN: Products That Were Never Sold
**Concept:** `LEFT JOIN` + `IS NULL` — finding orphan records  
Same pattern as Q8 but from the product side. We left-join `products` to `order_items`
and keep only products that have **no** matching order item."""),
    code("""sql = \"\"\"
SELECT   p.product_id,
         p.category,
         ROUND(p.price, 2) AS price
FROM     products    p
         LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE    oi.order_item_id IS NULL
ORDER BY p.product_id;
\"\"\"
df = con.execute(sql).fetchdf()
print(f"Products never sold: {len(df)}")
df"""),

    # Q10 — RIGHT JOIN
    md("""### Q10 — RIGHT JOIN: All Products and Their Sales (if any)
**Concept:** `RIGHT JOIN`  
A RIGHT JOIN keeps **all** rows from the right table (`products`), even those with no sales.
This is logically equivalent to Q9's LEFT JOIN but written the other way around, 
showing that RIGHT JOIN is the mirror of LEFT JOIN."""),
    code("""sql = \"\"\"
SELECT   p.product_id,
         p.category,
         ROUND(p.price, 2)              AS unit_price,
         COALESCE(SUM(oi.quantity), 0)   AS total_qty_sold,
         ROUND(COALESCE(SUM(oi.sales_amount), 0), 2) AS total_revenue
FROM     order_items oi
         RIGHT JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.category, p.price
ORDER BY total_qty_sold ASC
LIMIT    15;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q11 — CASE expression
    md("""### Q11 — CASE Expression: Revenue Tier per Category
**Concept:** `CASE WHEN … THEN … END` — conditional logic in SQL  
We classify each category's total revenue into tiers: High (> $1.5M), Medium, or Low."""),
    code("""sql = \"\"\"
SELECT   category,
         ROUND(SUM(sales_amount), 2) AS total_revenue,
         CASE
             WHEN SUM(sales_amount) > 1500000 THEN 'High'
             WHEN SUM(sales_amount) > 1000000 THEN 'Medium'
             ELSE 'Low'
         END AS revenue_tier
FROM     order_items
GROUP BY category
ORDER BY total_revenue DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "category", "total_revenue",
        title="Revenue by Category (with Tier Labels)",
        xlabel="Category", ylabel="Revenue ($)", rotate_x=30)"""),

    # Q12 — Subquery
    md("""### Q12 — Subquery: Customers Who Spent More Than Average
**Concept:** Scalar subquery in `HAVING`  
First we compute the average customer total spending (as a subquery),
then keep only customers whose total spending exceeds that average."""),
    code("""sql = \"\"\"
SELECT   o.customer_id,
         ROUND(SUM(oi.sales_amount), 2) AS total_spent
FROM     orders      o
         JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.customer_id
HAVING   SUM(oi.sales_amount) > (
            SELECT AVG(customer_total)
            FROM (
                SELECT SUM(oi2.sales_amount) AS customer_total
                FROM   orders o2
                       JOIN order_items oi2 ON o2.order_id = oi2.order_id
                GROUP BY o2.customer_id
            )
         )
ORDER BY total_spent DESC
LIMIT    15;
\"\"\"
df = con.execute(sql).fetchdf()
print(f"Customers spending above average: {len(con.execute(sql.replace('LIMIT    15', '')).fetchdf())}")
df"""),

    # Q13 — Revenue by segment and year
    md("""### Q13 — Revenue by Customer Segment and Year
**Concept:** Multi-dimensional `GROUP BY` + derived year column  
We group by both `customer_segment` and `order_year` to see how each segment's revenue trends over time."""),
    code("""sql = \"\"\"
SELECT   c.customer_segment,
         EXTRACT(YEAR FROM o.order_date) AS order_year,
         ROUND(SUM(oi.sales_amount), 2)  AS segment_revenue
FROM     order_items  oi
         JOIN orders    o  ON oi.order_id   = o.order_id
         JOIN customers c  ON o.customer_id = c.customer_id
GROUP BY c.customer_segment, order_year
ORDER BY c.customer_segment, order_year;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_multi_line(df, "order_year", "segment_revenue", "customer_segment",
               title="Revenue by Customer Segment Over Years",
               xlabel="Year", ylabel="Revenue ($)")"""),

    # Q14 — BETWEEN with aggregation
    md("""### Q14 — Products with Prices Between $100 and $250: Sales Performance
**Concept:** `WHERE … BETWEEN` + `JOIN` + `GROUP BY`  
We filter mid-range products ($100-$250) and see how each category performs in that price band."""),
    code("""sql = \"\"\"
SELECT   p.category,
         COUNT(DISTINCT p.product_id)       AS num_products,
         SUM(oi.quantity)                    AS units_sold,
         ROUND(SUM(oi.sales_amount), 2)     AS total_revenue
FROM     products    p
         JOIN order_items oi ON p.product_id = oi.product_id
WHERE    p.price BETWEEN 100 AND 250
GROUP BY p.category
ORDER BY total_revenue DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "category", "total_revenue",
        title="Revenue from Mid-Range Products ($100–$250)",
        xlabel="Category", ylabel="Revenue ($)", rotate_x=30)"""),

    # Q15 — Customer tenure derived column
    md("""### Q15 — Customer Tenure: Days Since Signup to Last Order
**Concept:** Derived column with `DATEDIFF` + `MAX`  
We compute each customer's tenure as the number of days between their signup and their most recent order."""),
    code("""sql = \"\"\"
SELECT   c.customer_id,
         c.customer_segment,
         c.signup_date,
         MAX(o.order_date)                                    AS last_order_date,
         DATEDIFF('day', c.signup_date, MAX(o.order_date))    AS tenure_days
FROM     customers c
         JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_segment, c.signup_date
ORDER BY tenure_days DESC
LIMIT    15;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Cleanup
    md("---\n## Cleanup"),
    code("""con.close()
print("Connection closed.")"""),
]

# ════════════════════════════════════════════════════════════════
#  NOTEBOOK 3 — ADVANCED
# ════════════════════════════════════════════════════════════════

nb3_cells = [
    md("""# Notebook 3 — Advanced SQL Queries (Nova Retail)

This notebook introduces **advanced SQL techniques** for analytical workloads.

**Topics covered:** Window functions (ROW_NUMBER, RANK, DENSE_RANK, LAG, SUM OVER),
Common Table Expressions (CTEs / WITH), Top-N per group, time-based analytics,
ranking queries, and DuckDB MACROs.

**Structure:** 5 intermediate queries + 10 intermediate+/advanced queries + 2 MACROs."""),

    md("## Setup — Connect to the Database"),
    code("""import duckdb
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
from plot_helpers import (
    plot_bar, plot_hbar, plot_line, plot_pie,
    plot_grouped_bar, plot_multi_line, plot_scatter
)

con = duckdb.connect("nova_db.duckdb", read_only=True)
print("Connected to nova_db.duckdb (read-only)")"""),

    # ─── INTERMEDIATE QUERIES (1-5) ───────────────────────────
    md("---\n## Part A — Intermediate Queries (5 queries)"),

    # Q1
    md("""### Q1 — Year-over-Year Revenue Growth  
**Concept:** CTE + `LAG()` window function  
We compute yearly revenue with a CTE, then use `LAG` to look at the previous year's value
and calculate the growth percentage."""),
    code("""sql = \"\"\"
WITH yearly_rev AS (
    SELECT   EXTRACT(YEAR FROM o.order_date) AS order_year,
             ROUND(SUM(oi.sales_amount), 2)  AS revenue
    FROM     orders o
             JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY order_year
)
SELECT order_year,
       revenue,
       LAG(revenue) OVER (ORDER BY order_year)                          AS prev_year_revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY order_year))
             / LAG(revenue) OVER (ORDER BY order_year), 1)              AS yoy_growth_pct
FROM   yearly_rev
ORDER BY order_year;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "order_year", "revenue",
        title="Yearly Revenue with YoY Growth",
        xlabel="Year", ylabel="Revenue ($)")"""),

    # Q2
    md("""### Q2 — Monthly Revenue Trend with Running Total  
**Concept:** `SUM() OVER (ORDER BY …)` — cumulative window function  
We compute monthly revenue, then add a running total that accumulates month by month."""),
    code("""sql = \"\"\"
WITH monthly AS (
    SELECT   STRFTIME(o.order_date, '%Y-%m')   AS year_month,
             ROUND(SUM(oi.sales_amount), 2)    AS monthly_revenue
    FROM     orders o
             JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY year_month
)
SELECT year_month,
       monthly_revenue,
       ROUND(SUM(monthly_revenue) OVER (ORDER BY year_month), 2) AS running_total
FROM   monthly
ORDER BY year_month;
\"\"\"
df = con.execute(sql).fetchdf()
df.head(20)"""),
    code("""plot_line(df, "year_month", "running_total",
         title="Cumulative Revenue Over Time",
         xlabel="Month", ylabel="Running Total ($)",
         figsize=(12, 4))"""),

    # Q3
    md("""### Q3 — Top 3 Products per Category by Revenue  
**Concept:** `ROW_NUMBER() OVER (PARTITION BY … ORDER BY …)` + CTE for Top-N per group  
We rank products within each category and keep only the top 3."""),
    code("""sql = \"\"\"
WITH ranked AS (
    SELECT   oi.product_id,
             p.category,
             ROUND(p.price, 2)            AS unit_price,
             ROUND(SUM(oi.sales_amount), 2) AS product_revenue,
             ROW_NUMBER() OVER (
                 PARTITION BY p.category
                 ORDER BY SUM(oi.sales_amount) DESC
             ) AS rn
    FROM     order_items oi
             JOIN products p ON oi.product_id = p.product_id
    GROUP BY oi.product_id, p.category, p.price
)
SELECT product_id, category, unit_price, product_revenue, rn
FROM   ranked
WHERE  rn <= 3
ORDER BY category, rn;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q4
    md("""### Q4 — Customer Order Frequency Distribution  
**Concept:** CTE + `GROUP BY` on derived frequency  
First we count orders per customer, then group by that count to see the distribution:
how many customers placed exactly 1 order, 2 orders, etc."""),
    code("""sql = \"\"\"
WITH cust_orders AS (
    SELECT   customer_id,
             COUNT(*) AS num_orders
    FROM     orders
    GROUP BY customer_id
)
SELECT   num_orders,
         COUNT(*) AS num_customers
FROM     cust_orders
GROUP BY num_orders
ORDER BY num_orders;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "num_orders", "num_customers",
        title="Customer Order Frequency Distribution",
        xlabel="Number of Orders", ylabel="Number of Customers",
        figsize=(10, 4))"""),

    # Q5
    md("""### Q5 — Revenue by Country and Category  
**Concept:** Multi-dimensional aggregation across 3 tables  
A cross-tab view showing revenue broken down by both country and product category."""),
    code("""sql = \"\"\"
SELECT   c.country,
         oi.category,
         ROUND(SUM(oi.sales_amount), 2) AS revenue
FROM     order_items  oi
         JOIN orders    o  ON oi.order_id   = o.order_id
         JOIN customers c  ON o.customer_id = c.customer_id
GROUP BY c.country, oi.category
ORDER BY c.country, revenue DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df.head(20)"""),
    code("""# Pivot for stacked bar
pivot = df.pivot_table(index="country", columns="category", values="revenue", fill_value=0)
plot_stacked_bar(pivot,
    title="Revenue by Country and Category",
    xlabel="Country", ylabel="Revenue ($)")"""),

    # ─── ADVANCED QUERIES (6-15) ──────────────────────────────
    md("---\n## Part B — Intermediate+ / Advanced Queries (10 queries)"),

    # Q6 — RANK and DENSE_RANK
    md("""### Q6 — RANK vs DENSE_RANK: Top Revenue Categories  
**Concept:** `RANK()` and `DENSE_RANK()` window functions  
We demonstrate the difference between RANK (gaps after ties) and DENSE_RANK (no gaps).
Both rank categories by total revenue."""),
    code("""sql = \"\"\"
WITH cat_rev AS (
    SELECT   category,
             ROUND(SUM(sales_amount), 2) AS total_revenue
    FROM     order_items
    GROUP BY category
)
SELECT category,
       total_revenue,
       RANK()       OVER (ORDER BY total_revenue DESC) AS rank_val,
       DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS dense_rank_val
FROM   cat_rev
ORDER BY total_revenue DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_hbar(df, "category", "total_revenue",
         title="Category Revenue Ranking",
         xlabel="Revenue ($)", ylabel="Category")"""),

    # Q7 — Percentile / NTILE
    md("""### Q7 — Customer Spending Quartiles Using NTILE  
**Concept:** `NTILE(4)` window function — divides into equal-sized buckets  
We split customers into 4 spending quartiles and show summary stats for each."""),
    code("""sql = \"\"\"
WITH cust_spend AS (
    SELECT   o.customer_id,
             ROUND(SUM(oi.sales_amount), 2) AS total_spent
    FROM     orders o
             JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
),
quartiled AS (
    SELECT *,
           NTILE(4) OVER (ORDER BY total_spent) AS spending_quartile
    FROM   cust_spend
)
SELECT   spending_quartile,
         COUNT(*)                        AS num_customers,
         ROUND(MIN(total_spent), 2)      AS min_spent,
         ROUND(AVG(total_spent), 2)      AS avg_spent,
         ROUND(MAX(total_spent), 2)      AS max_spent
FROM     quartiled
GROUP BY spending_quartile
ORDER BY spending_quartile;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "spending_quartile", "avg_spent",
        title="Average Spending by Customer Quartile",
        xlabel="Quartile (1=Lowest, 4=Highest)", ylabel="Avg Spent ($)")"""),

    # Q8 — Month-over-month change with LAG
    md("""### Q8 — Month-over-Month Revenue Change  
**Concept:** `LAG()` for time-series comparison  
We compute each month's revenue and the absolute/percentage change from the prior month."""),
    code("""sql = \"\"\"
WITH monthly AS (
    SELECT   STRFTIME(o.order_date, '%Y-%m')  AS year_month,
             ROUND(SUM(oi.sales_amount), 2)   AS revenue
    FROM     orders o
             JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY year_month
)
SELECT year_month,
       revenue,
       LAG(revenue) OVER (ORDER BY year_month)               AS prev_month,
       ROUND(revenue - LAG(revenue) OVER (ORDER BY year_month), 2) AS mom_change,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year_month))
             / LAG(revenue) OVER (ORDER BY year_month), 1)   AS mom_pct
FROM   monthly
ORDER BY year_month;
\"\"\"
df = con.execute(sql).fetchdf()
df.head(15)"""),
    code("""# Plot only MoM % change (skip first row which is NULL)
df_plot = df.dropna(subset=["mom_pct"])
plot_line(df_plot, "year_month", "mom_pct",
         title="Month-over-Month Revenue Growth (%)",
         xlabel="Month", ylabel="MoM Change (%)",
         figsize=(12, 4))"""),

    # Q9 — Ranking customers within each segment
    md("""### Q9 — Top 3 Customers per Segment by Spending (Ranking + CTE)  
**Concept:** `WITH` subquery + `ROW_NUMBER() OVER (PARTITION BY …)` — ranking within groups  
We rank customers by total spending within each segment and keep only the top 3."""),
    code("""sql = \"\"\"
WITH customer_spend AS (
    SELECT   c.customer_id,
             c.customer_segment,
             c.country,
             ROUND(SUM(oi.sales_amount), 2) AS total_spent,
             ROW_NUMBER() OVER (
                 PARTITION BY c.customer_segment
                 ORDER BY SUM(oi.sales_amount) DESC
             ) AS rn
    FROM     customers c
             JOIN orders      o  ON c.customer_id = o.customer_id
             JOIN order_items oi ON o.order_id    = oi.order_id
    GROUP BY c.customer_id, c.customer_segment, c.country
)
SELECT customer_id,
       customer_segment,
       country,
       total_spent,
       rn AS rank_in_segment
FROM   customer_spend
WHERE  rn <= 3
ORDER BY customer_segment, rn;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q10 — Moving average
    md("""### Q10 — 3-Month Moving Average of Revenue  
**Concept:** `AVG() OVER (… ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` — sliding window  
A moving average smooths out noise in monthly data and reveals the underlying trend."""),
    code("""sql = \"\"\"
WITH monthly AS (
    SELECT   STRFTIME(o.order_date, '%Y-%m')  AS year_month,
             ROUND(SUM(oi.sales_amount), 2)   AS revenue
    FROM     orders o
             JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY year_month
)
SELECT year_month,
       revenue,
       ROUND(AVG(revenue) OVER (
           ORDER BY year_month
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ), 2) AS moving_avg_3m
FROM   monthly
ORDER BY year_month;
\"\"\"
df = con.execute(sql).fetchdf()
df.head(15)"""),
    code("""import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(df["year_month"].astype(str), df["revenue"],
        marker=".", color="#4C72B0", linewidth=1, alpha=0.5, label="Monthly Revenue")
ax.plot(df["year_month"].astype(str), df["moving_avg_3m"],
        marker="o", color="#DD8452", linewidth=2, markersize=3, label="3-Month Moving Avg")
ax.legend()
ax.set_title("Monthly Revenue vs 3-Month Moving Average", fontsize=13, fontweight="bold")
ax.set_xlabel("Month"); ax.set_ylabel("Revenue ($)")
plt.xticks(rotation=45, ha="right")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout(); plt.show()"""),

    # Q11 — Cohort: signup year retention
    md("""### Q11 — Signup Cohort Analysis: Orders per Cohort Year  
**Concept:** Time-based analytics + multi-table CTE  
We group customers by their signup year (cohort) and measure how many orders
each cohort placed in each calendar year."""),
    code("""sql = \"\"\"
WITH cohort AS (
    SELECT customer_id,
           EXTRACT(YEAR FROM signup_date) AS cohort_year
    FROM   customers
)
SELECT   co.cohort_year,
         EXTRACT(YEAR FROM o.order_date) AS order_year,
         COUNT(*)                         AS num_orders
FROM     cohort co
         JOIN orders o ON co.customer_id = o.customer_id
GROUP BY co.cohort_year, order_year
ORDER BY co.cohort_year, order_year;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_multi_line(df, "order_year", "num_orders", "cohort_year",
               title="Orders by Signup Cohort Year",
               xlabel="Order Year", ylabel="Number of Orders")"""),

    # Q12 — Percent of total using window
    md("""### Q12 — Category Revenue as Percent of Total (Window Function)  
**Concept:** `SUM() OVER ()` — window without PARTITION (grand total)  
We compute each category's share of total revenue using a window function —
no subquery needed."""),
    code("""sql = \"\"\"
SELECT   category,
         ROUND(SUM(sales_amount), 2)                                       AS cat_revenue,
         ROUND(SUM(sales_amount) / SUM(SUM(sales_amount)) OVER () * 100, 1) AS pct_of_total
FROM     order_items
GROUP BY category
ORDER BY cat_revenue DESC;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_pie(df, "category", "cat_revenue",
        title="Revenue Share by Category")"""),

    # Q13 — FIRST_VALUE / LAST_VALUE
    md("""### Q13 — First and Last Order per Customer  
**Concept:** `FIRST_VALUE()` and `LAST_VALUE()` window functions  
For each customer we find the date and amount of their very first and very last orders."""),
    code("""sql = \"\"\"
WITH order_detail AS (
    SELECT   o.customer_id,
             o.order_date,
             ROUND(SUM(oi.sales_amount), 2) AS order_total
    FROM     orders o
             JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id, o.order_id, o.order_date
),
windowed AS (
    SELECT customer_id,
           FIRST_VALUE(order_date)  OVER w AS first_order_date,
           FIRST_VALUE(order_total) OVER w AS first_order_amount,
           LAST_VALUE(order_date)   OVER (
               PARTITION BY customer_id
               ORDER BY order_date
               ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
           ) AS last_order_date,
           LAST_VALUE(order_total) OVER (
               PARTITION BY customer_id
               ORDER BY order_date
               ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
           ) AS last_order_amount
    FROM   order_detail
    WINDOW w AS (PARTITION BY customer_id ORDER BY order_date)
)
SELECT DISTINCT
       customer_id,
       first_order_date,
       first_order_amount,
       last_order_date,
       last_order_amount
FROM   windowed
ORDER BY customer_id
LIMIT  15;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q14 — Gap analysis: days between orders
    md("""### Q14 — Average Days Between Consecutive Orders per Customer  
**Concept:** `LAG()` for gap analysis  
Using LAG to compute the gap (in days) between consecutive orders for each customer,
then averaging those gaps."""),
    code("""sql = \"\"\"
WITH ordered AS (
    SELECT customer_id,
           order_date,
           LAG(order_date) OVER (
               PARTITION BY customer_id ORDER BY order_date
           ) AS prev_order_date
    FROM   orders
),
gaps AS (
    SELECT customer_id,
           DATEDIFF('day', prev_order_date, order_date) AS days_between
    FROM   ordered
    WHERE  prev_order_date IS NOT NULL
)
SELECT   customer_id,
         COUNT(*)                    AS num_gaps,
         ROUND(AVG(days_between), 1) AS avg_days_between,
         MIN(days_between)           AS min_gap,
         MAX(days_between)           AS max_gap
FROM     gaps
GROUP BY customer_id
ORDER BY avg_days_between
LIMIT    15;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),

    # Q15 — Complex ranking with multiple CTEs
    md("""### Q15 — Country + Segment Revenue Ranking  
**Concept:** Multiple CTEs + `DENSE_RANK` — complex ranking  
We rank every (country, segment) combination by revenue and identify the top performer
in each country."""),
    code("""sql = \"\"\"
WITH segment_rev AS (
    SELECT   c.country,
             c.customer_segment,
             ROUND(SUM(oi.sales_amount), 2) AS segment_revenue
    FROM     customers   c
             JOIN orders      o  ON c.customer_id = o.customer_id
             JOIN order_items oi ON o.order_id    = oi.order_id
    GROUP BY c.country, c.customer_segment
),
ranked AS (
    SELECT *,
           DENSE_RANK() OVER (
               PARTITION BY country
               ORDER BY segment_revenue DESC
           ) AS segment_rank
    FROM   segment_rev
)
SELECT country,
       customer_segment,
       segment_revenue,
       segment_rank
FROM   ranked
WHERE  segment_rank <= 3
ORDER BY country, segment_rank;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_grouped_bar(df, "country", "segment_revenue", "customer_segment",
                 title="Top 3 Segments by Revenue per Country",
                 xlabel="Country", ylabel="Revenue ($)", rotate_x=30)"""),

    # ─── MACROS ───────────────────────────────────────────────
    md("""---
## DuckDB MACROs

DuckDB supports **MACROs** — reusable SQL functions stored in the database.
They simplify repetitive queries and promote consistency.

> **Note:** Since we opened the database in read-only mode, we create these macros
> as temporary (`TEMP`) macros that live for the duration of this session.
> In a read-write connection you could omit `TEMP` to persist them."""),

    # MACRO 1
    md("""### MACRO 1 — `customer_lifetime_value(cid)`
**Justification:** Computing a customer's total lifetime spending is a very common
analytical operation. Wrapping it in a macro means any analyst can call
`customer_lifetime_value(42)` instead of writing a multi-table join every time."""),
    code("""# Create the macro
con.execute(\"\"\"
CREATE OR REPLACE TEMP MACRO customer_lifetime_value(cid) AS (
    SELECT ROUND(COALESCE(SUM(oi.sales_amount), 0), 2)
    FROM   orders o
           JOIN order_items oi ON o.order_id = oi.order_id
    WHERE  o.customer_id = cid
);
\"\"\")
print("Macro 'customer_lifetime_value' created.")"""),
    code("""# Use the macro — get lifetime value for customers 1-10
sql = \"\"\"
SELECT customer_id,
       customer_lifetime_value(customer_id) AS lifetime_value
FROM   customers
WHERE  customer_id <= 10
ORDER BY customer_id;
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "customer_id", "lifetime_value",
        title="Lifetime Value — Customers 1-10",
        xlabel="Customer ID", ylabel="Lifetime Value ($)")"""),

    # MACRO 2
    md("""### MACRO 2 — `category_revenue_in_year(cat, yr)`
**Justification:** Analysts frequently need to pull revenue for a specific category
in a specific year. This macro encapsulates the date filtering and aggregation
so the call becomes a simple two-argument function."""),
    code("""# Create the macro
con.execute(\"\"\"
CREATE OR REPLACE TEMP MACRO category_revenue_in_year(cat, yr) AS (
    SELECT ROUND(COALESCE(SUM(oi.sales_amount), 0), 2)
    FROM   order_items oi
           JOIN orders o ON oi.order_id = o.order_id
    WHERE  oi.category = cat
      AND  EXTRACT(YEAR FROM o.order_date) = yr
);
\"\"\")
print("Macro 'category_revenue_in_year' created.")"""),
    code("""# Use the macro — compare Electronics revenue across years
sql = \"\"\"
SELECT 2021 AS year, category_revenue_in_year('Electronics', 2021) AS revenue
UNION ALL
SELECT 2022, category_revenue_in_year('Electronics', 2022)
UNION ALL
SELECT 2023, category_revenue_in_year('Electronics', 2023)
UNION ALL
SELECT 2024, category_revenue_in_year('Electronics', 2024);
\"\"\"
df = con.execute(sql).fetchdf()
df"""),
    code("""plot_bar(df, "year", "revenue",
        title="Electronics Revenue by Year (via MACRO)",
        xlabel="Year", ylabel="Revenue ($)")"""),

    # Cleanup
    md("---\n## Cleanup"),
    code("""con.close()
print("Connection closed.")"""),
]

# ════════════════════════════════════════════════════════════════
#  SAVE ALL NOTEBOOKS
# ════════════════════════════════════════════════════════════════

print("Building notebooks...")
save(build_nb(nb1_cells), "notebook_1_basics.ipynb")
save(build_nb(nb2_cells), "notebook_2_intermediate.ipynb")
save(build_nb(nb3_cells), "notebook_3_advanced.ipynb")
print("Done!")
