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
    # Session 1 — SQL Foundations with a Single Table

    This notebook uses the **`sales`** table from `data/sales.csv` in this folder.

    ## Learning goals
    - understand how to query a single table
    - practice `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, and `DISTINCT`
    - connect SQL output to simple business questions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # DuckDB Notebook Setup

    These notebooks are designed for **MSIS-2402**.

    Each notebook:
    - connects to DuckDB
    - loads the relevant CSV files
    - presents **10 English business questions**
    - gives the SQL query
    - explains the query in plain English
    - visualizes selected results with Python
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
    sales_path = "data/sales.csv"

    con.execute(f"""
        CREATE OR REPLACE TABLE sales AS
        SELECT *
        FROM read_csv_auto('{sales_path}')
    """)

    show_query("SELECT * FROM sales LIMIT 5;")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data dictionary

    The `sales` table includes:

    - `sale_id`: unique row identifier
    - `sale_date`: date of the sale
    - `product_id`: product identifier
    - `product_category`: product category
    - `quantity`: quantity sold
    - `unit_price`: price per unit
    - `total_amount`: quantity × unit price
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 1 — Show all rows from the sales table.

    ### SQL
    """)
    return


@app.cell
def _(con, mo, sales):
    df_q1 = mo.sql(
        f"""
        SELECT *
        FROM sales
        ORDER BY sale_id;
                """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query returns every row and every column from the `sales` table.
    - It is useful for first inspection, but in practice it can return too much data.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 2 — Show only sale_id, product_id, and total_amount.

    ### SQL
    """)
    return


@app.cell
def _(con, mo, sales):
    df_q2 = mo.sql(
        f"""
        SELECT
            sale_id,
            product_id,
            total_amount
        FROM sales
        ORDER BY sale_id;
                """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query selects only the columns needed for the question.
    - It helps students focus on relevant attributes instead of scanning the whole table.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 3 — Show the first 10 rows.

    ### SQL
    """)
    return


@app.cell
def _(con, mo, sales):
    df_q3 = mo.sql(
        f"""
        SELECT *
        FROM sales
        ORDER BY sale_id
        LIMIT 10;
                """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - `LIMIT 10` restricts the result to 10 rows.
    - `ORDER BY sale_id` makes them the 10 lowest `sale_id`s — without `ORDER BY`,
      SQL does not promise *which* 10 rows you get.
    - This is a common way to preview data safely.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 4 — Show sales where quantity is at least 3.

    ### SQL
    """)
    return


@app.cell
def _(con, mo, sales):
    df_q4 = mo.sql(
        f"""
        SELECT *
        FROM sales
        WHERE quantity >= 3
        ORDER BY sale_id;
                """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - `WHERE` filters rows before they are returned.
    - This query isolates larger-quantity sales.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 5 — Show sales where total_amount is greater than 300.

    ### SQL
    """)
    return


@app.cell
def _(con, mo, sales):
    df_q5 = mo.sql(
        f"""
        SELECT *
        FROM sales
        WHERE total_amount > 300
        ORDER BY sale_id;
                """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query identifies higher-value transactions.
    - It helps students connect SQL conditions with business thresholds.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 6 — List all distinct product categories.

    ### SQL
    """)
    return


@app.cell
def _(con, mo, sales):
    df_q6 = mo.sql(
        f"""
        SELECT DISTINCT product_category
        FROM sales
        ORDER BY product_category;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - `DISTINCT` removes duplicate category values.
    - Sorting the result makes the category list easier to read.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization — Number of rows by product category
    """)
    return


@app.cell
def _(con, plt):
    _df_plot = con.execute("""
        SELECT
            product_category,
            COUNT(*) AS num_rows
        FROM sales
        GROUP BY product_category
        ORDER BY num_rows DESC, product_category
            """).df()

    plt.figure(figsize=(8,4))
    plt.bar(_df_plot["product_category"], _df_plot["num_rows"])
    plt.title("Week 1: Number of Sales Rows by Category")
    plt.xlabel("Product Category")
    plt.ylabel("Number of Rows")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 7 — Show the top 10 sales by total_amount.

    ### SQL
    """)
    return


@app.cell
def _(con, mo, sales):
    df_q7 = mo.sql(
        f"""
        SELECT *
        FROM sales
        ORDER BY total_amount DESC, sale_id
        LIMIT 10;
                """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - `ORDER BY ... DESC` sorts from highest to lowest.
    - Combined with `LIMIT 10`, it returns the largest sales.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization — Top 10 sales by amount
    """)
    return


@app.cell
def _(con, plt):
    _df_plot = con.execute("""
        SELECT
            sale_id,
            total_amount
        FROM sales
        ORDER BY total_amount DESC, sale_id
        LIMIT 10
            """).df()

    plt.figure(figsize=(8,4))
    plt.bar(_df_plot["sale_id"].astype(str), _df_plot["total_amount"])
    plt.title("Week 1: Top 10 Sales by Total Amount")
    plt.xlabel("Sale ID")
    plt.ylabel("Total Amount")
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 8 — Show sales sorted by sale_date.

    ### SQL
    """)
    return


@app.cell
def _(con, mo, sales):
    df_q8 = mo.sql(
        f"""
        SELECT *
        FROM sales
        ORDER BY sale_date, sale_id;
                """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - This query arranges rows chronologically.
    - Sorting by date is useful for understanding time-based patterns.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization — Sales amount over time (first 50 rows after sorting by date)
    """)
    return


@app.cell
def _(con, pd, plt):
    _df_plot = con.execute("""
        SELECT
            sale_date,
            total_amount
        FROM sales
        ORDER BY sale_date, sale_id
        LIMIT 50
            """).df()

    _df_plot["sale_date"] = pd.to_datetime(_df_plot["sale_date"])
    plt.figure(figsize=(8,4))
    plt.plot(_df_plot["sale_date"], _df_plot["total_amount"])
    plt.title("Week 1: Total Amount Over Time (First 50 Rows)")
    plt.xlabel("Sale Date")
    plt.ylabel("Total Amount")
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 9 — Count how many sales rows exist.

    ### SQL
    """)
    return


@app.cell
def _(con, mo, sales):
    df_q9 = mo.sql(
        f"""
        SELECT COUNT(*) AS num_sales
        FROM sales;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - `COUNT(*)` counts all rows in the table.
    - This is often the first summary statistic analysts compute.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 10 — Find the average total_amount by category.

    ### SQL
    """)
    return


@app.cell
def _(con, mo, sales):
    df_q10 = mo.sql(
        f"""
        SELECT
            product_category,
            ROUND(AVG(total_amount), 2) AS avg_total_amount
        FROM sales
        GROUP BY product_category
        ORDER BY avg_total_amount DESC;
                """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explanation

    - `GROUP BY` forms one group per category.
    - `AVG(total_amount)` measures the average sale size inside each category.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization — Average total_amount by category
    """)
    return


@app.cell
def _(con, plt):
    _df_plot = con.execute("""
        SELECT
            product_category,
            ROUND(AVG(total_amount), 2) AS avg_total_amount
        FROM sales
        GROUP BY product_category
        ORDER BY avg_total_amount DESC
            """).df()

    plt.figure(figsize=(8,4))
    plt.bar(_df_plot["product_category"], _df_plot["avg_total_amount"])
    plt.title("Week 1: Average Total Amount by Category")
    plt.xlabel("Product Category")
    plt.ylabel("Average Total Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


if __name__ == "__main__":
    app.run()

