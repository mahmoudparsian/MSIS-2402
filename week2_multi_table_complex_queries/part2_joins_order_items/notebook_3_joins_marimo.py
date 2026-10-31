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
    # Week 2 — Transaction Analytics

    This notebook focuses on the transaction-level schema:

    - `customers`
    - `orders`
    - `order_items`
    - `products`

    ## Learning goals
    - understand why `order_items` exists
    - perform multi-table joins
    - calculate revenue and quantity metrics
    - analyze categories, products, and customers
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

    def find_path(candidates):
        for p in candidates:
            p = Path(p)
            if p.exists():
                return p
        raise FileNotFoundError("Could not find any of these paths: " + ", ".join(map(str, candidates)))

    def show_query(sql: str):
        print(sql)
        return con.execute(sql).df()

    print("DuckDB version:", duckdb.__version__)
    return con, find_path, plt, show_query


@app.cell
def _(con, find_path, show_query):
    oltp_dir = find_path([
        "datasets/oltp_database",
        "../datasets/oltp_database",
        "../../datasets/oltp_database",
        "datasets_2026/oltp_database",
        "../datasets_2026/oltp_database",
        "../../datasets_2026/oltp_database",
    ])

    for table in ["customers", "orders", "order_items", "products"]:
        con.execute(f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT *
            FROM read_csv_auto('{(oltp_dir / f"{table}.csv").as_posix()}')
        """)

    show_query("SELECT * FROM order_items LIMIT 5;")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 1 — Show all order_items.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q1 = mo.sql(
        f"""
        SELECT *
        FROM order_items;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query returns the line-item table that sits at the center of transaction analysis.
    - Each row represents one product inside one order.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 2 — Join orders and order_items.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q2 = mo.sql(
        f"""
        SELECT * EXCLUDE (oi.order_id)
        FROM orders o
        JOIN order_items oi
        ON o.order_id = oi.order_id;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query combines order-level information with item-level information.
    - It helps students see how one order can expand into multiple rows after a join.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 3 — Join order_items and products.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q3 = mo.sql(
        f"""
        SELECT * EXCLUDE (p.product_id, p.category, p.price)
        FROM order_items oi
        JOIN products p
        ON oi.product_id = p.product_id;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query connects sold items to product metadata.
    - It makes category-level analysis possible.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 4 — Revenue by category.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q4 = mo.sql(
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
    return (df_q4,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query groups revenue by product category.
    - It is one of the most important retail analytics patterns.
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
    plt.bar(df_q4["category"], df_q4["revenue"])
    plt.title("Week 2: Revenue by Category")
    plt.xlabel("Category")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 5 — Total revenue.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q5 = mo.sql(
        f"""
        SELECT SUM(sales_amount) AS total_revenue
        FROM order_items;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query sums sales_amount across all order items.
    - It gives a quick picture of total sales volume in the dataset.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 6 — Average sales amount per order item.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q6 = mo.sql(
        f"""
        SELECT AVG(sales_amount) AS avg_sales_amount
        FROM order_items;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query computes the average value of a line item.
    - It helps students distinguish between totals and averages.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 7 — Top 10 products by revenue.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q7 = mo.sql(
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
    if hasattr(df_q7, "to_pandas"):
        df_q7 = df_q7.to_pandas()
    return (df_q7,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query aggregates revenue at the product level.
    - It identifies the strongest products in the dataset.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization
    """)
    return


@app.cell
def _(df_q7, plt):
    plt.figure(figsize=(8,4))
    plt.bar(df_q7["product_id"].astype(str), df_q7["revenue"])
    plt.title("Week 2: Top 10 Products by Revenue")
    plt.xlabel("Product ID")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 8 — Orders per customer.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q8 = mo.sql(
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
    if hasattr(df_q8, "to_pandas"):
        df_q8 = df_q8.to_pandas()
    return (df_q8,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query measures customer activity frequency.
    - It is useful for identifying loyal or highly active customers.
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
    plt.bar(df_q8["customer_id"].astype(str), df_q8["order_count"])
    plt.title("Week 2: Top 10 Customers by Order Count")
    plt.xlabel("Customer ID")
    plt.ylabel("Order Count")
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 9 — Revenue by country.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q9 = mo.sql(
        f"""
        SELECT
            c.country,
            SUM(oi.sales_amount) AS revenue
        FROM customers c
        JOIN orders o
        ON c.customer_id = o.customer_id
        JOIN order_items oi
        ON o.order_id = oi.order_id
        GROUP BY c.country
        ORDER BY revenue DESC;
        """,
        engine=con
    )
    return (df_q9,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query combines customers, orders, and order_items.
    - It shows how geography relates to revenue.
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
    plt.bar(df_q9["country"], df_q9["revenue"])
    plt.title("Week 2: Revenue by Country")
    plt.xlabel("Country")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 10 — Units sold by category.

    ### SQL
    """)
    return


@app.cell
def _(con, mo):
    df_q10 = mo.sql(
        f"""
        SELECT
            p.category,
            SUM(oi.quantity) AS units_sold
        FROM order_items oi
        JOIN products p
        ON oi.product_id = p.product_id
        GROUP BY p.category
        ORDER BY units_sold DESC;
        """,
        engine=con
    )
    return (df_q10,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query focuses on quantity rather than revenue.
    - It helps students compare demand volume with sales value.
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
    plt.bar(df_q10["category"], df_q10["units_sold"])
    plt.title("Week 2: Units Sold by Category")
    plt.xlabel("Category")
    plt.ylabel("Units Sold")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


if __name__ == "__main__":
    app.run()

