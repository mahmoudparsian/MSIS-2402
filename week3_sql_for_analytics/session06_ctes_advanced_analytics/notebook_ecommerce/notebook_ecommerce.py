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
    # Session 6 — Advanced SQL Analytics with DuckDB

    This notebook focuses on advanced analytics patterns:

    - Common Table Expressions (CTE)
    - window functions
    - ranking
    - running totals

    ## Learning goals
    - write readable multi-step SQL with `WITH`
    - use window functions for ranking and analytics
    - solve business questions that require more than basic aggregation
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # DuckDB Notebook Setup

    This notebook is part of **MSIS-2402**. It loads `customers`, `products`, `stores`, `orders`, `order_items` from the course's shared dataset, `../../../datasets/oltp_database/`.

    This notebook:
    - connects to DuckDB
    - loads the relevant CSV files
    - presents **10 English business questions**
    - gives the SQL query
    - explains the query in plain English
    - visualizes selected results with Python

    **Run it from its own folder** so that path works — from the course repository folder:
    `cd week3_sql_for_analytics/session06_ctes_advanced_analytics/notebook_ecommerce`, then `marimo edit notebook_ecommerce.py`.
    """)
    return


@app.cell
def _():
    from pathlib import Path
    import duckdb
    import pandas as pd
    import matplotlib.pyplot as plt

    con = duckdb.connect()


    def show_query(sql: str):
        print(sql)
        return con.execute(sql).df()

    print("DuckDB version:", duckdb.__version__)
    return con, pd, plt, show_query


@app.cell
def _(con, show_query):
    for table in ["customers", "products", "stores", "orders", "order_items"]:
        con.execute(f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT *
            FROM read_csv_auto('{(f"../../../datasets/oltp_database/{table}.csv")}')
        """)

    show_query("SELECT * FROM order_items LIMIT 5;")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 1 — Top 10 customers by revenue.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q1 = mo.sql(
        f"""
        SELECT
            o.customer_id,
            SUM(oi.sales_amount) AS revenue
        FROM orders o
        JOIN order_items oi
        ON o.order_id = oi.order_id
        GROUP BY o.customer_id
        ORDER BY revenue DESC
        LIMIT 10;
        """,
        engine=con
    )
    if hasattr(df_q1, "to_pandas"):
        df_q1 = df_q1.to_pandas()
    return (df_q1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query aggregates revenue at the customer level.
    - It identifies the highest-value customers in the dataset.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization
    """)
    return


@app.cell
def _(df_q1, plt):
    plt.figure(figsize=(8,4))
    plt.bar(df_q1["customer_id"].astype(str), df_q1["revenue"])
    plt.title("Week 3: Top 10 Customers by Revenue")
    plt.xlabel("Customer ID")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 2 — Rank customers by revenue.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q2 = mo.sql(
        f"""
        SELECT
            o.customer_id,
            SUM(oi.sales_amount) AS revenue,
            RANK() OVER(ORDER BY SUM(oi.sales_amount) DESC) AS revenue_rank
        FROM orders o
        JOIN order_items oi
        ON o.order_id = oi.order_id
        GROUP BY o.customer_id
        ORDER BY revenue_rank;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query applies a window function after aggregation.
    - It shows how ranking differs from simply sorting.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 3 — Revenue by category.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q3 = mo.sql(
        f"""
        SELECT
            p.category,
            SUM(oi.sales_amount) AS revenue
        FROM order_items oi
        JOIN products p
        ON oi.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue DESC;
        """,
        engine=con
    )
    if hasattr(df_q3, "to_pandas"):
        df_q3 = df_q3.to_pandas()
    return (df_q3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query summarizes revenue by category.
    - It creates a compact business-performance table for category comparison.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization
    """)
    return


@app.cell
def _(df_q3, plt):
    plt.figure(figsize=(8,4))
    plt.bar(df_q3["category"], df_q3["revenue"])
    plt.title("Week 3: Revenue by Category")
    plt.xlabel("Category")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 4 — Rank categories by revenue.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q4 = mo.sql(
        f"""
        SELECT
            p.category,
            SUM(oi.sales_amount) AS revenue,
            RANK() OVER(ORDER BY SUM(oi.sales_amount) DESC) AS revenue_rank
        FROM order_items oi
        JOIN products p
        ON oi.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue_rank;
        """,
        engine=con
    )
    if hasattr(df_q4, "to_pandas"):
        df_q4 = df_q4.to_pandas()
    return (df_q4,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query combines aggregation with ranking.
    - It is a common business-dashboard pattern.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization
    """)
    return


@app.cell
def _(df_q4, plt):
    plt.figure(figsize=(8,4))
    plt.bar(df_q4["category"], df_q4["revenue_rank"])
    plt.title("Week 3: Category Revenue Rank")
    plt.xlabel("Category")
    plt.ylabel("Rank")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 5 — Top product in each category.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q5 = mo.sql(
        f"""
        WITH product_sales AS (SELECT p.category, p.product_id, SUM(oi.sales_amount) AS revenue FROM order_items oi JOIN products p ON oi.product_id = p.product_id GROUP BY p.category, p.product_id)
        SELECT *
        FROM (SELECT *, ROW_NUMBER() OVER(PARTITION BY category ORDER BY revenue DESC) AS rn FROM product_sales) t
        WHERE rn = 1
        ORDER BY category;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query uses a CTE to make the logic easier to read.
    - It finds one best-performing product inside each category.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 6 — Running daily revenue total.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q6 = mo.sql(
        f"""
        SELECT
            order_date,
            SUM(daily_revenue) OVER(ORDER BY order_date) AS running_revenue
        FROM (SELECT o.order_date, SUM(oi.sales_amount) AS daily_revenue FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.order_date) t
        ORDER BY order_date;
        """,
        engine=con
    )
    if hasattr(df_q6, "to_pandas"):
        df_q6 = df_q6.to_pandas()
    return (df_q6,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query first computes daily revenue, then applies a running total.
    - Running totals are common in financial and time-series analysis.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization
    """)
    return


@app.cell
def _(df_q6, pd, plt):
    df_plot = df_q6.copy()
    df_plot["order_date"] = pd.to_datetime(df_plot["order_date"])
    plt.figure(figsize=(8,4))
    plt.plot(df_plot["order_date"], df_plot["running_revenue"])
    plt.title("Week 3: Running Revenue Over Time")
    plt.xlabel("Order Date")
    plt.ylabel("Running Revenue")
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 7 — Average order revenue by customer.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q7 = mo.sql(
        f"""
        SELECT
            customer_id,
            AVG(order_revenue) AS avg_order_revenue
        FROM (SELECT o.order_id, o.customer_id, SUM(oi.sales_amount) AS order_revenue FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.order_id, o.customer_id) t
        GROUP BY customer_id
        ORDER BY avg_order_revenue DESC
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query creates order-level revenue first, then averages it by customer.
    - It distinguishes order value from total customer revenue.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 8 — Customers above average revenue.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q8 = mo.sql(
        f"""
        WITH customer_revenue AS (SELECT o.customer_id, SUM(oi.sales_amount) AS revenue FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.customer_id), avg_revenue AS (SELECT AVG(revenue) AS avg_rev FROM customer_revenue)
        SELECT cr.*
        FROM customer_revenue cr, avg_revenue ar
        WHERE cr.revenue > ar.avg_rev
        ORDER BY cr.revenue DESC;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query uses two CTEs: one for customer revenue and one for the overall average.
    - It shows how CTEs support step-by-step analytical logic.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 9 — Rank stores by revenue.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q9 = mo.sql(
        f"""
        SELECT
            s.store_id,
            s.store_type,
            SUM(oi.sales_amount) AS revenue,
            RANK() OVER(ORDER BY SUM(oi.sales_amount) DESC) AS revenue_rank
        FROM stores s
        JOIN orders o
        ON s.store_id = o.store_id
        JOIN order_items oi
        ON o.order_id = oi.order_id
        GROUP BY
            s.store_id,
            s.store_type
        ORDER BY revenue_rank;
        """,
        engine=con
    )
    if hasattr(df_q9, "to_pandas"):
        df_q9 = df_q9.to_pandas()
    return (df_q9,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query compares store performance with ranking.
    - It supports managerial analysis of store-level outcomes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization
    """)
    return


@app.cell
def _(df_q9, plt):
    plt.figure(figsize=(8,4))
    plt.bar(df_q9["store_id"].astype(str), df_q9["revenue"])
    plt.title("Week 3: Store Revenue Ranking")
    plt.xlabel("Store ID")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 10 — Revenue share by category.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q10 = mo.sql(
        f"""
        SELECT
            category,
            revenue,
            revenue / SUM(revenue) OVER() AS revenue_share
        FROM (SELECT p.category, SUM(oi.sales_amount) AS revenue FROM order_items oi JOIN products p ON oi.product_id = p.product_id GROUP BY p.category) t
        ORDER BY revenue DESC;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query computes each category's share of total revenue.
    - It demonstrates a powerful use of window functions beyond ranking.
    """)
    return


if __name__ == "__main__":
    app.run()

