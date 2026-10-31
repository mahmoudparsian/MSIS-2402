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
    # Week 3 — Full Operational Database Exploration

    This notebook uses the full operational schema:

    - `customers`
    - `products`
    - `stores`
    - `orders`
    - `order_items`
    - `payments`
    - `shipments`

    ## Learning goals
    - explore a realistic business schema
    - combine operational, financial, and logistics tables
    - perform multi-table analytics
    - run basic data-quality checks
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # DuckDB Notebook Setup

    These notebooks are designed for **MSIS-2402** and assume your generated datasets live in a folder named `datasets_2026`.

    Each notebook:
    - connects to DuckDB
    - loads the relevant CSV files
    - presents **10 English business questions**
    - gives the SQL query
    - explains the query in plain English
    - visualizes selected results with Python

    The notebooks are designed to be **ready to run** after you place them in the same project folder that contains `datasets_2026/`.
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
    return con, plt, show_query


@app.cell
def _(con, show_query):
    TABLES = ["customers", "products", "stores", "orders", "order_items", "payments", "shipments"]

    for table in TABLES:
        con.execute(f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT *
            FROM read_csv_auto('{(f"../../datasets/oltp_database/{table}.csv")}')
        """)

    show_query("SELECT COUNT(*) AS num_orders FROM orders;")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 1 — Count the number of customers.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q1 = mo.sql(
        f"""
        SELECT COUNT(*) AS num_customers
        FROM customers;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query counts the rows in the customers table.
    - It provides a quick measure of customer base size.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 2 — Count the number of orders.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q2 = mo.sql(
        f"""
        SELECT COUNT(*) AS num_orders
        FROM orders;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query counts orders in the operational system.
    - It is a useful first check on transaction volume.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 3 — Count the number of stores by store_type.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q3 = mo.sql(
        f"""
        SELECT
            store_type,
            COUNT(*) AS num_stores
        FROM stores
        GROUP BY store_type
        ORDER BY num_stores DESC;
        """,
        engine=con
    )
    return (df_q3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query groups stores by operational type.
    - It shows whether the business is more online, retail, or warehouse-oriented.
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
    plt.bar(df_q3["store_type"], df_q3["num_stores"])
    plt.title("Week 3: Number of Stores by Type")
    plt.xlabel("Store Type")
    plt.ylabel("Number of Stores")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 4 — Orders by country.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q4 = mo.sql(
        f"""
        SELECT
            c.country,
            COUNT(o.order_id) AS num_orders
        FROM customers c
        JOIN orders o
        ON c.customer_id = o.customer_id
        GROUP BY c.country
        ORDER BY num_orders DESC;
        """,
        engine=con
    )
    return (df_q4,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query joins customers and orders to analyze geography.
    - It shows where transaction activity is concentrated.
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
    plt.bar(df_q4["country"], df_q4["num_orders"])
    plt.title("Week 3: Orders by Country")
    plt.xlabel("Country")
    plt.ylabel("Number of Orders")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 5 — Revenue by category.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q5 = mo.sql(
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
    return (df_q5,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query calculates category-level revenue.
    - It is a core business performance metric.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization
    """)
    return


@app.cell
def _(df_q5, plt):
    plt.figure(figsize=(8,4))
    plt.bar(df_q5["category"], df_q5["revenue"])
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
    ## Question 6 — Revenue by store type.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q6 = mo.sql(
        f"""
        SELECT
            s.store_type,
            SUM(oi.sales_amount) AS revenue
        FROM stores s
        JOIN orders o
        ON s.store_id = o.store_id
        JOIN order_items oi
        ON o.order_id = oi.order_id
        GROUP BY s.store_type
        ORDER BY revenue DESC;
        """,
        engine=con
    )
    return (df_q6,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query connects store operations to sales outcomes.
    - It helps compare online, retail, and warehouse performance.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization
    """)
    return


@app.cell
def _(df_q6, plt):
    plt.figure(figsize=(8,4))
    plt.bar(df_q6["store_type"], df_q6["revenue"])
    plt.title("Week 3: Revenue by Store Type")
    plt.xlabel("Store Type")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 7 — Total payments by payment method.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q7 = mo.sql(
        f"""
        SELECT
            payment_method,
            SUM(payment_amount) AS total_paid
        FROM payments
        GROUP BY payment_method
        ORDER BY total_paid DESC;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query summarizes money received by payment method.
    - It introduces financial analysis into the operational database.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 8 — Shipments by carrier.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q8 = mo.sql(
        f"""
        SELECT
            carrier,
            COUNT(*) AS shipment_count
        FROM shipments
        GROUP BY carrier
        ORDER BY shipment_count DESC;
        """,
        engine=con
    )
    return (df_q8,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query counts shipment volume by carrier.
    - It is a simple logistics performance summary.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization
    """)
    return


@app.cell
def _(df_q8, plt):
    plt.figure(figsize=(8,4))
    plt.bar(df_q8["carrier"], df_q8["shipment_count"])
    plt.title("Week 3: Shipments by Carrier")
    plt.xlabel("Carrier")
    plt.ylabel("Shipment Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 9 — Top 10 products by revenue.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q9 = mo.sql(
        f"""
        SELECT
            product_id,
            SUM(sales_amount) AS revenue
        FROM order_items
        GROUP BY product_id
        ORDER BY revenue DESC
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query highlights the strongest products.
    - It gives students a concrete top-N business analysis pattern.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 10 — Data quality check: orders with missing customer_id.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q10 = mo.sql(
        f"""
        SELECT *
        FROM orders
        WHERE customer_id IS NULL;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query looks for missing foreign-key values in orders.
    - It introduces data-quality thinking inside SQL analysis.
    """)
    return


if __name__ == "__main__":
    app.run()

