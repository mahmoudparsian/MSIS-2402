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
    # Notebook 1 — Basic SQL Queries (Nova Retail)

    This notebook covers **fundamental SQL concepts** using the Nova Retail DuckDB database.

    **Topics covered:** SELECT, WHERE, ORDER BY, LIMIT, COUNT, SUM, AVG, MIN, MAX,
    DISTINCT, LIKE, BETWEEN, IN, IS NULL, basic GROUP BY, and simple aggregations.

    **Structure:** 5 basic queries + 10 basic+ queries.  
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

    # make sure plot_helpers is importable
    sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
    from plot_helpers import (
        plot_bar, plot_hbar, plot_line, plot_pie,
        plot_grouped_bar, plot_stacked_bar
    )

    # open database in READ-ONLY mode
    con = duckdb.connect("nova_db.duckdb", read_only=True)
    print("Connected to nova_db.duckdb (read-only)")
    print("Tables:", con.execute("SHOW TABLES").fetchdf().to_string(index=False))
    return con, plot_bar, plot_hbar, plot_line, plot_pie


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
    ## Part A — Basic Queries (5 queries)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q1 — Preview the Customers Table
    **Concept:** `SELECT` with `LIMIT`  
    We start by peeking at the first 10 rows of the `customers` table to understand its structure.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT *
        FROM customers
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q2 — Count the Total Number of Orders
    **Concept:** `COUNT(*)` aggregate  
    A single-value query that tells us the total volume of orders in the database.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT COUNT(*) AS total_orders
        FROM orders;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q3 — List All Distinct Product Categories
    **Concept:** `SELECT DISTINCT`  
    Returns the unique set of product categories available in the catalogue.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT DISTINCT category
        FROM products
        ORDER BY category;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q4 — Find the Most Expensive Product
    **Concept:** `ORDER BY … DESC` with `LIMIT 1`  
    Retrieves the single product with the highest price.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            product_id,
            category,
            price
        FROM products
        ORDER BY price DESC
        LIMIT 1;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q5 — Customers Who Signed Up in 2024
    **Concept:** `WHERE` with `BETWEEN` on dates  
    Filters customers whose `signup_date` falls within the year 2024.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            customer_id,
            gender,
            country,
            customer_segment,
            signup_date
        FROM customers
        WHERE signup_date BETWEEN '2024-01-01' AND '2024-12-31'
        ORDER BY signup_date
        LIMIT 15;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part B — Basic+ Queries (10 queries)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q6 — Total Revenue Across All Orders
    **Concept:** `SUM()` aggregate  
    Computes the grand total of `sales_amount` across all order items.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT ROUND(SUM(sales_amount), 2) AS total_revenue
        FROM order_items;
                """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q7 — Number of Customers per Country
    **Concept:** `GROUP BY` + `COUNT`  
    Groups customers by their country and counts how many are in each.
    This is one of the most fundamental GROUP BY patterns.
    """)
    return


@app.cell
def _(con, mo):
    df = mo.sql(
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
    return (df,)


@app.cell
def _(df, plot_bar):
    plot_bar(df, "country", "num_customers",
            title="Number of Customers per Country",
            xlabel="Country", ylabel="Customers")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q8 — Average Product Price by Category
    **Concept:** `GROUP BY` + `AVG`  
    Shows the average price for each product category — useful for understanding the price tier of each category.
    """)
    return


@app.cell
def _(con, mo):
    df_2 = mo.sql(
        f"""
        SELECT
            category,
            ROUND(AVG(price), 2) AS avg_price
        FROM products
        GROUP BY category
        ORDER BY avg_price DESC;
        """,
        engine=con
    )
    return (df_2,)


@app.cell
def _(df_2, plot_hbar):
    plot_hbar(df_2, "category", "avg_price",
             title="Average Product Price by Category",
             xlabel="Average Price ($)", ylabel="Category")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q9 — Orders Placed Each Year  (Derived Column: order_year)
    **Concept:** `EXTRACT(YEAR …)` derived column + `GROUP BY`  
    We create a derived column `order_year` directly in the SQL using `EXTRACT`, then count orders per year.
    """)
    return


@app.cell
def _(con, mo):
    df_3 = mo.sql(
        f"""
        SELECT
            EXTRACT(YEAR FROM order_date) AS order_year,
            COUNT(*) AS num_orders
        FROM orders
        GROUP BY order_year
        ORDER BY order_year;
        """,
        engine=con
    )
    return (df_3,)


@app.cell
def _(df_3, plot_bar):
    plot_bar(df_3, "order_year", "num_orders",
            title="Number of Orders per Year",
            xlabel="Year", ylabel="Orders")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q10 — Revenue by Product Category
    **Concept:** `GROUP BY` + `SUM`  
    Sums `sales_amount` by category to find out which product lines generate the most revenue.
    """)
    return


@app.cell
def _(con, mo):
    df_4 = mo.sql(
        f"""
        SELECT
            category,
            ROUND(SUM(sales_amount), 2) AS total_revenue
        FROM order_items
        GROUP BY category
        ORDER BY total_revenue DESC;
        """,
        engine=con
    )
    return (df_4,)


@app.cell
def _(df_4, plot_pie):
    plot_pie(df_4, "category", "total_revenue",
            title="Revenue Share by Product Category")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q11 — Top 5 Customers by Total Spending
    **Concept:** `GROUP BY` + `SUM` + `ORDER BY … DESC LIMIT`  
    Identifies the five biggest spenders by summing their order-item sales.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            oi.order_id,
            o.customer_id,
            ROUND(SUM(oi.sales_amount), 2) AS total_spent
        FROM order_items oi
        JOIN orders o
        ON oi.order_id = o.order_id
        GROUP BY
            oi.order_id,
            o.customer_id
        ORDER BY total_spent DESC
        LIMIT 5;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q12 — Customer Segment Distribution
    **Concept:** `GROUP BY` + `COUNT` on a categorical column  
    Counts how many customers fall into each segment (Consumer, Corporate, VIP, Small Business).
    """)
    return


@app.cell
def _(con, mo):
    df_5 = mo.sql(
        f"""
        SELECT
            customer_segment,
            COUNT(*) AS num_customers
        FROM customers
        GROUP BY customer_segment
        ORDER BY num_customers DESC;
        """,
        engine=con
    )
    return (df_5,)


@app.cell
def _(df_5, plot_pie):
    plot_pie(df_5, "customer_segment", "num_customers",
            title="Customer Segment Distribution")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q13 — Monthly Order Volume for 2024
    **Concept:** `EXTRACT(MONTH …)` derived column + `WHERE` year filter  
    Computes the number of orders placed each month during 2024.
    """)
    return


@app.cell
def _(con, mo):
    df_6 = mo.sql(
        f"""
        SELECT
            EXTRACT(MONTH FROM order_date) AS order_month,
            COUNT(*) AS num_orders
        FROM orders
        WHERE EXTRACT(YEAR FROM order_date) = 2024
        GROUP BY order_month
        ORDER BY order_month;
        """,
        engine=con
    )
    return (df_6,)


@app.cell
def _(df_6, plot_line):
    plot_line(df_6, "order_month", "num_orders",
             title="Monthly Order Volume in 2024",
             xlabel="Month", ylabel="Orders")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q14 — Products in the Electronics Category Priced Above `$300`

    **Concept:** 

    ```
    `WHERE` with compound conditions (`AND`)  
    Filters the product catalog for Electronics 
    items above the $300 price point.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            product_id,
            category,
            price
        FROM products
        WHERE
            category = 'Electronics'
            AND price > 300
        ORDER BY price DESC
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q15 — Gender Breakdown of Customers
    **Concept:** `GROUP BY` + percentage calculation  
    Counts customers by gender and computes each group's share as a percentage.
    """)
    return


@app.cell
def _(con, mo):
    df_7 = mo.sql(
        f"""
        SELECT
            gender,
            COUNT(*) AS num_customers,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct
        FROM customers
        GROUP BY gender
        ORDER BY num_customers DESC;
        """,
        engine=con
    )
    return (df_7,)


@app.cell
def _(df_7, plot_bar):
    plot_bar(df_7, "gender", "num_customers",
            title="Customer Gender Distribution",
            xlabel="Gender", ylabel="Customers")
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

