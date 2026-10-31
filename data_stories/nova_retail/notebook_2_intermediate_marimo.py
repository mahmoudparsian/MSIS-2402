import marimo


__generated_with = "0.23.10"

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Notebook 2 — Intermediate SQL Queries (Nova Retail)

    This notebook builds on the basics and introduces **intermediate SQL concepts**.

    **Topics covered:** JOIN (INNER, LEFT, RIGHT), WHERE vs HAVING, multi-table GROUP BY,
    sub-queries, CASE expressions, NULL handling, and compound aggregations.

    **Structure:** 5 basic+ queries + 10 intermediate queries.  
    Each query includes an explanation, the SQL, the result, and a plot where appropriate.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup — Connect to the Database
    """)
    return


@app.cell
def _():
    import duckdb
    import pandas as pd
    import sys, os

    sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
    from plot_helpers import (
        plot_bar, plot_hbar, plot_line, plot_pie,
        plot_grouped_bar, plot_stacked_bar, plot_multi_line
    )

    con = duckdb.connect("nova_db.duckdb", read_only=True)
    print("Connected to nova_db.duckdb (read-only)")
    return con, plot_bar, plot_hbar, plot_multi_line


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Quick Check — Row Counts for All Tables
    Before diving into queries, let's confirm the size of each table in the database.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            'customers' AS table_name,
            COUNT(*) AS row_count
        FROM customers
        UNION ALL
        SELECT
            'orders',
            COUNT(*)
        FROM orders
        UNION ALL
        SELECT
            'order_items',
            COUNT(*)
        FROM order_items
        UNION ALL
        SELECT
            'products',
            COUNT(*)
        FROM products
        ORDER BY row_count DESC;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part A — Basic+ Queries (5 queries)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q1 — Revenue per Country
    **Concept:** `JOIN` + `GROUP BY` + `SUM`  
    We join `orders` → `order_items` and then bring in `customers` to aggregate revenue by country.
    """)
    return


@app.cell
def _(con, mo):
    df = mo.sql(
        f"""
        SELECT
            c.country,
            ROUND(SUM(oi.sales_amount), 2) AS total_revenue
        FROM order_items oi
        JOIN orders o
        ON oi.order_id = o.order_id
        JOIN customers c
        ON o.customer_id = c.customer_id
        GROUP BY c.country
        ORDER BY total_revenue DESC;
        """,
        engine=con
    )
    return (df,)


@app.cell
def _(df, plot_bar):
    plot_bar(df, "country", "total_revenue",
            title="Total Revenue by Country",
            xlabel="Country", ylabel="Revenue ($)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q2 — Number of Items Sold per Category
    **Concept:** `SUM(quantity)` grouped by category  
    Tells us which product categories move the most units.
    """)
    return


@app.cell
def _(con, mo):
    df_2 = mo.sql(
        f"""
        SELECT
            category,
            SUM(quantity) AS units_sold
        FROM order_items
        GROUP BY category
        ORDER BY units_sold DESC;
        """,
        engine=con
    )
    return (df_2,)


@app.cell
def _(df_2, plot_hbar):
    plot_hbar(df_2, "category", "units_sold",
             title="Units Sold by Category",
             xlabel="Units Sold", ylabel="Category")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q3 — Average Order Value (AOV) per Year
    **Concept:** Derived column `order_year` + multi-table join + AVG of sum  
    We first compute each order's total, then average those totals by year.
    """)
    return


@app.cell
def _(con, mo):
    df_3 = mo.sql(
        f"""
        WITH order_totals AS (SELECT o.order_id, EXTRACT(YEAR FROM o.order_date) AS order_year, SUM(oi.sales_amount) AS order_total FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.order_id, order_year)
        SELECT
            order_year,
            ROUND(AVG(order_total), 2) AS avg_order_value
        FROM order_totals
        GROUP BY order_year
        ORDER BY order_year;
        """,
        engine=con
    )
    return (df_3,)


@app.cell
def _(df_3, plot_bar):
    plot_bar(df_3, "order_year", "avg_order_value",
            title="Average Order Value by Year",
            xlabel="Year", ylabel="AOV ($)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q4 — Top 10 Most-Ordered Products
    **Concept:** `GROUP BY product_id` + `SUM(quantity)` + `LIMIT`  
    Identifies the products that appear most frequently in orders by total quantity.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            oi.product_id,
            p.category,
            ROUND(p.price, 2) AS unit_price,
            SUM(oi.quantity) AS total_qty_sold
        FROM order_items oi
        JOIN products p
        ON oi.product_id = p.product_id
        GROUP BY
            oi.product_id,
            p.category,
            p.price
        ORDER BY total_qty_sold DESC
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q5 — Quarterly Revenue for 2023
    **Concept:** `EXTRACT(QUARTER …)` derived column + date filter  
    Groups revenue by fiscal quarter for the year 2023.
    """)
    return


@app.cell
def _(con, mo):
    df_4 = mo.sql(
        f"""
        SELECT
            EXTRACT(QUARTER FROM o.order_date) AS quarter,
            ROUND(SUM(oi.sales_amount), 2) AS quarterly_revenue
        FROM orders o
        JOIN order_items oi
        ON o.order_id = oi.order_id
        WHERE EXTRACT(YEAR FROM o.order_date) = 2023
        GROUP BY quarter
        ORDER BY quarter;
        """,
        engine=con
    )
    return (df_4,)


@app.cell
def _(df_4, plot_bar):
    plot_bar(df_4, "quarter", "quarterly_revenue",
            title="Quarterly Revenue — 2023",
            xlabel="Quarter", ylabel="Revenue ($)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part B — Intermediate Queries (10 queries)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q6 — WHERE vs HAVING: Categories with Average Sale > $200  
    **Concept:** `WHERE` vs `HAVING` — the fundamental distinction  
    - `WHERE` filters **rows** *before* grouping.  
    - `HAVING` filters **groups** *after* aggregation.

    Here we keep only order items with quantity ≥ 2 (`WHERE`), group by category,
    and then retain only categories whose average sale exceeds $200 (`HAVING`).
    """)
    return


@app.cell
def _(con, mo):
    df_5 = mo.sql(
        f"""
        SELECT
            category,
            COUNT(*) AS num_items,
            ROUND(AVG(sales_amount), 2) AS avg_sale
        FROM order_items
        WHERE quantity >= 2 -- row-level filter (before grouping)
        GROUP BY category
        HAVING AVG(sales_amount) > 200 -- group-level filter (after aggregation)
        ORDER BY avg_sale DESC;
        """,
        engine=con
    )
    return (df_5,)


@app.cell
def _(df_5, plot_bar):
    plot_bar(df_5, "category", "avg_sale",
            title="Categories with Avg Sale > $200 (qty ≥ 2)",
            xlabel="Category", ylabel="Avg Sale ($)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q7 — INNER JOIN: Orders with Customer and Product Details
    **Concept:** `INNER JOIN` across three tables  
    An inner join returns only rows with matching keys in **both** tables.
    We join `orders` → `customers` and `order_items` → `products` to build a rich order detail view.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            o.order_id,
            c.customer_id,
            c.country,
            c.customer_segment,
            oi.product_id,
            p.category,
            oi.quantity,
            ROUND(oi.sales_amount, 2) AS sales_amount,
            o.order_date
        FROM orders o
        INNER JOIN customers c
        ON o.customer_id = c.customer_id
        INNER JOIN order_items oi
        ON o.order_id = oi.order_id
        INNER JOIN products p
        ON oi.product_id = p.product_id
        ORDER BY o.order_date DESC
        LIMIT 15;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q8 — LEFT JOIN: Customers Who Never Bought Anything
    **Concept:** `LEFT JOIN` + `IS NULL` to find non-matching rows  
    A LEFT JOIN keeps **all** rows from the left table (customers) even if there is no matching order.
    By filtering where `order_id IS NULL`, we find customers with zero purchases.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            c.customer_id,
            c.gender,
            c.country,
            c.customer_segment,
            c.signup_date
        FROM customers c
        LEFT JOIN orders o
        ON c.customer_id = o.customer_id
        WHERE o.order_id IS NULL
        ORDER BY c.customer_id;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q9 — LEFT JOIN: Products That Were Never Sold
    **Concept:** `LEFT JOIN` + `IS NULL` — finding orphan records  
    Same pattern as Q8 but from the product side. We left-join `products` to `order_items`
    and keep only products that have **no** matching order item.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            p.product_id,
            p.category,
            ROUND(p.price, 2) AS price
        FROM products p
        LEFT JOIN order_items oi
        ON p.product_id = oi.product_id
        WHERE oi.order_item_id IS NULL
        ORDER BY p.product_id;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q10 — RIGHT JOIN: All Products and Their Sales (if any)
    **Concept:** `RIGHT JOIN`  
    A RIGHT JOIN keeps **all** rows from the right table (`products`), even those with no sales.
    This is logically equivalent to Q9's LEFT JOIN but written the other way around, 
    showing that RIGHT JOIN is the mirror of LEFT JOIN.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            p.product_id,
            p.category,
            ROUND(p.price, 2) AS unit_price,
            COALESCE(SUM(oi.quantity), 0) AS total_qty_sold,
            ROUND(COALESCE(SUM(oi.sales_amount), 0), 2) AS total_revenue
        FROM order_items oi
        RIGHT JOIN products p
        ON oi.product_id = p.product_id
        GROUP BY
            p.product_id,
            p.category,
            p.price
        ORDER BY total_qty_sold ASC
        LIMIT 15;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q11 — CASE Expression: Revenue Tier per Category
    **Concept:** `CASE WHEN … THEN … END` — conditional logic in SQL  
    We classify each category's total revenue into tiers: High (> $1.5M), Medium, or Low.
    """)
    return


@app.cell
def _(con, mo):
    df_6 = mo.sql(
        f"""
        SELECT
            category,
            ROUND(SUM(sales_amount), 2) AS total_revenue,
            CASE WHEN SUM(sales_amount) > 1500000 THEN 'High' WHEN SUM(sales_amount) > 1000000 THEN 'Medium' ELSE 'Low' END AS revenue_tier
        FROM order_items
        GROUP BY category
        ORDER BY total_revenue DESC;
        """,
        engine=con
    )
    return (df_6,)


@app.cell
def _(df_6, plot_bar):
    plot_bar(df_6, "category", "total_revenue",
            title="Revenue by Category (with Tier Labels)",
            xlabel="Category", ylabel="Revenue ($)", rotate_x=30)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q12 — Subquery: Customers Who Spent More Than Average
    **Concept:** Scalar subquery in `HAVING`  
    First we compute the average customer total spending (as a subquery),
    then keep only customers whose total spending exceeds that average.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            o.customer_id,
            ROUND(SUM(oi.sales_amount), 2) AS total_spent
        FROM orders o
        JOIN order_items oi
        ON o.order_id = oi.order_id
        GROUP BY o.customer_id
        HAVING SUM(oi.sales_amount) > (SELECT AVG(customer_total) FROM (SELECT SUM(oi2.sales_amount) AS customer_total FROM orders o2 JOIN order_items oi2 ON o2.order_id = oi2.order_id GROUP BY o2.customer_id))
        ORDER BY total_spent DESC
        LIMIT 15;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q13 — Revenue by Customer Segment and Year
    **Concept:** Multi-dimensional `GROUP BY` + derived year column  
    We group by both `customer_segment` and `order_year` to see how each segment's revenue trends over time.
    """)
    return


@app.cell
def _(con, mo):
    df_7 = mo.sql(
        f"""
        SELECT
            c.customer_segment,
            EXTRACT(YEAR FROM o.order_date) AS order_year,
            ROUND(SUM(oi.sales_amount), 2) AS segment_revenue
        FROM order_items oi
        JOIN orders o
        ON oi.order_id = o.order_id
        JOIN customers c
        ON o.customer_id = c.customer_id
        GROUP BY
            c.customer_segment,
            order_year
        ORDER BY
            c.customer_segment,
            order_year;
        """,
        engine=con
    )
    return (df_7,)


@app.cell
def _(df_7, plot_multi_line):
    plot_multi_line(df_7, "order_year", "segment_revenue", "customer_segment",
                   title="Revenue by Customer Segment Over Years",
                   xlabel="Year", ylabel="Revenue ($)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q14 — Products with Prices Between $100 and $250: Sales Performance
    **Concept:** `WHERE … BETWEEN` + `JOIN` + `GROUP BY`  
    We filter mid-range products ($100-$250) and see how each category performs in that price band.
    """)
    return


@app.cell
def _(con, mo):
    df_8 = mo.sql(
        f"""
        SELECT
            p.category,
            COUNT(DISTINCT p.product_id) AS num_products,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.sales_amount), 2) AS total_revenue
        FROM products p
        JOIN order_items oi
        ON p.product_id = oi.product_id
        WHERE p.price BETWEEN 100 AND 250
        GROUP BY p.category
        ORDER BY total_revenue DESC;
        """,
        engine=con
    )
    return (df_8,)


@app.cell
def _(df_8, plot_bar):
    plot_bar(df_8, "category", "total_revenue",
            title="Revenue from Mid-Range Products ($100–$250)",
            xlabel="Category", ylabel="Revenue ($)", rotate_x=30)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q15 — Customer Tenure: Days Since Signup to Last Order
    **Concept:** Derived column with `DATEDIFF` + `MAX`  
    We compute each customer's tenure as the number of days between their signup and their most recent order.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            c.customer_id,
            c.customer_segment,
            c.signup_date,
            MAX(o.order_date) AS last_order_date,
            DATEDIFF('day', c.signup_date, MAX(o.order_date)) AS tenure_days
        FROM customers c
        JOIN orders o
        ON c.customer_id = o.customer_id
        GROUP BY
            c.customer_id,
            c.customer_segment,
            c.signup_date
        ORDER BY tenure_days DESC
        LIMIT 15;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Cleanup
    """)
    return


@app.cell
def _(con):
    con.close()
    print("Connection closed.")
    return


if __name__ == "__main__":
    app.run()

