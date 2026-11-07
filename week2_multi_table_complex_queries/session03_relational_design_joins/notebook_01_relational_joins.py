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
    # Week 2 — Relational Databases and JOINs

    This notebook uses the Week 2 relational dataset:

    - `customers`
    - `orders`
    - `products`

    ## Learning goals
    - understand relationships across tables
    - practice `JOIN`
    - use `GROUP BY` with joined data
    - answer basic business questions from a relational database
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # DuckDB Notebook Setup

    This notebook is part of **MSIS-2402**. It loads `customers`, `orders`, `products` from this folder's own `data/` folder (`data/customers.csv`, `data/orders.csv`, `data/products.csv`).

    This notebook:
    - connects to DuckDB
    - loads the relevant CSV files
    - presents **10 English business questions**
    - gives the SQL query
    - explains the query in plain English
    - visualizes selected results with Python

    **Run it from its own folder** so that path works — from the course repository folder:
    `cd week2_multi_table_complex_queries/session03_relational_design_joins`, then `marimo edit notebook_01_relational_joins.py`.
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
    for table in ["customers", "orders", "products"]:
        con.execute(f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT *
            FROM read_csv_auto('{(f"data/{table}.csv")}')
        """)

    show_query("""
    SELECT * 
    FROM customers 
    LIMIT 5;
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 1 — Show all customers.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q1 = mo.sql(
        f"""
        SELECT *
        FROM customers;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query returns the full customers table.
    - It is useful for understanding what customer attributes are available.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 2 — Show all orders.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q2 = mo.sql(
        f"""
        SELECT *
        FROM orders;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query returns the full orders table.
    - It helps students see the order-level structure before joining.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 3 — Count customers by country.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q3 = mo.sql(
        f"""
        SELECT
            country,
            COUNT(*) AS num_customers
        FROM customers
        GROUP BY country
        ORDER BY num_customers DESC;
        """,
        engine=con
    )
    return (df_q3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query groups customers by country.
    - It shows where the customer base is concentrated.
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
    plt.bar(df_q3["country"], df_q3["num_customers"])
    plt.title("Week 2: Customers by Country")
    plt.xlabel("Country")
    plt.ylabel("Number of Customers")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 4 — Count customers by segment.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q4 = mo.sql(
        f"""
        SELECT
            segment,
            COUNT(*) AS num_customers
        FROM customers
        GROUP BY segment
        ORDER BY num_customers DESC;
        """,
        engine=con
    )
    return (df_q4,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This groups customers by business segment.
    - It helps students connect SQL to market segmentation.
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
    plt.bar(df_q4["segment"], df_q4["num_customers"])
    plt.title("Week 2: Customers by Segment")
    plt.xlabel("Segment")
    plt.ylabel("Number of Customers")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 5 — Join customers and orders.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q5 = mo.sql(
        f"""
        SELECT * EXCLUDE (o.customer_id)
        FROM customers c
        JOIN orders o
        ON c.customer_id = o.customer_id;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query combines customer attributes with order records.
    - It introduces the idea that relationships are implemented with matching keys.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 6 — Count orders by country.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q6 = mo.sql(
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
    return (df_q6,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query first joins customers to orders, then groups by country.
    - It shows how relational structure enables richer analysis than single-table queries.
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
    plt.bar(df_q6["country"], df_q6["num_orders"])
    plt.title("Week 2: Orders by Country")
    plt.xlabel("Country")
    plt.ylabel("Number of Orders")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 7 — Count orders by customer.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q7 = mo.sql(
        f"""
        SELECT
            customer_id,
            COUNT(order_id) AS order_count
        FROM orders
        GROUP BY customer_id
        ORDER BY order_count DESC
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query measures purchase frequency per customer.
    - It identifies customers with the largest number of orders.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 8 — Average product price by category.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q8 = mo.sql(
        f"""
        SELECT
            category,
            AVG(price) AS avg_price
        FROM products
        GROUP BY category
        ORDER BY avg_price DESC;
        """,
        engine=con
    )
    return (df_q8,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query summarizes product prices by category.
    - It gives an early example of business-oriented aggregation.
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
    plt.bar(df_q8["category"], df_q8["avg_price"])
    plt.title("Week 2: Average Product Price by Category")
    plt.xlabel("Category")
    plt.ylabel("Average Price")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 9 — Earliest and latest order date.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q9 = mo.sql(
        f"""
        SELECT
            MIN(order_date) AS first_order_date,
            MAX(order_date) AS last_order_date
        FROM orders;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query finds the date range covered by the dataset.
    - It is a common first step in time-based analysis.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 10 — Top 10 customers by number of orders, with country.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q10 = mo.sql(
        f"""
        SELECT
            c.customer_id,
            c.country,
            COUNT(o.order_id) AS order_count
        FROM customers c
        JOIN orders o
        ON c.customer_id = o.customer_id
        GROUP BY
            c.customer_id,
            c.country
        ORDER BY order_count DESC
        LIMIT 10;
        """,
        engine=con
    )
    return (df_q10,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query joins customer details to order counts.
    - It shows how grouping and joining work together.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization
    """)
    return


@app.cell
def _(df_q10, plt):
    plt.figure(figsize=(8,4))
    plt.bar([str(v) for v in df_q10["customer_id"]], df_q10["order_count"])
    plt.title("Week 2: Top 10 Customers by Order Count")
    plt.xlabel("Customer ID")
    plt.ylabel("Order Count")
    plt.tight_layout()
    plt.show()
    return


if __name__ == "__main__":
    app.run()

