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
    # Session 5 — Trends and Segmentation

    Goes with the deck `slides_02_window_functions_ranking.md` (this folder), from
    "Running Totals" to "Combine Everything".

    **Run it from this folder** — from the course repository folder:
    `cd week3_sql_for_analytics/session05_operational_db_window_functions`, then
    `marimo edit notebook_02_trends_segmentation.py`.

    **Data:** `data/product_orders.csv` — **200 orders**, one per day from
    2025-01-01 to 2025-07-19, for **4 products**. Columns: `order_id`,
    `order_date`, `product`, `price`, `quantity`, `sales_amount` (whole dollars).
    Total revenue: **396,373**.

    **In this notebook**

    1. A running total, step by step
    2. The running total of real revenue — and its chart
    3. Monthly revenue and cumulative revenue
    4. A running total per product (`PARTITION BY`)
    5. Segmenting products with `CASE`
    6. Rank, share, and segment in one query
    7. Segmenting orders by size
    8. Try it yourself
    """)
    return


@app.cell
def _():
    import duckdb
    import matplotlib.pyplot as plt

    con = duckdb.connect()
    print("DuckDB version:", duckdb.__version__)
    return con, plt


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        CREATE OR REPLACE TABLE sales AS
        SELECT *
        FROM read_csv_auto('data/product_orders.csv')
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. A Running Total, Step by Step

    `SUM(...) OVER (ORDER BY ...)` adds up every row **up to and including** the
    current one. Three days of made-up revenue (an inline `VALUES` table):
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        WITH daily_sales AS (
            SELECT *
            FROM (VALUES
                (DATE '2024-01-01', 100.00),
                (DATE '2024-01-02', 250.00),
                (DATE '2024-01-03', 150.00)
            ) AS t(sale_date, revenue)
        )
        SELECT
            sale_date,
            revenue,
            SUM(revenue) OVER (ORDER BY sale_date) AS running_total
        FROM daily_sales
        ORDER BY sale_date
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    | sale_date | how `running_total` is computed |
    |---|---|
    | 2024-01-01 | 100 (first row) |
    | 2024-01-02 | 100 + 250 = 350 |
    | 2024-01-03 | 350 + 150 = 500 |

    ---
    ## 2. The Running Total of Real Revenue

    Same idea on the 200 orders (one per day, so `order_date` alone gives a clear
    order). The first rows are 939, then 939 + 218 = 1,157, then 3,553, …
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            order_date,
            sales_amount,
            SUM(sales_amount) OVER (ORDER BY order_date) AS running_total
        FROM sales
        ORDER BY order_date
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Self-check:** the last row (2025-07-19) shows **396,373** — the same number
    as the total revenue below, because by the last day every order has been added.
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT SUM(sales_amount) AS total_revenue
        FROM sales
        """,
        engine=con
    )
    return


@app.cell
def _(con, plt):
    _df = con.execute("""
        SELECT order_date,
               SUM(sales_amount) OVER (ORDER BY order_date) AS running_total
        FROM sales
        ORDER BY order_date
    """).df()
    _fig, _ax = plt.subplots(figsize=(8, 3.5))
    _ax.plot(_df["order_date"], _df["running_total"])
    _ax.set_title("Running Total of Revenue, 2025-01-01 to 2025-07-19")
    _ax.set_xlabel("Order date")
    _ax.set_ylabel("Revenue so far (dollars)")
    _fig.autofmt_xdate()
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A steady upward line means steady sales; a steeper stretch means a stronger
    period. `GROUP BY` gives a **snapshot** (one number per group); a window
    function gives a **trend** (one number per row, building on the rows before it).

    ---
    ## 3. Monthly Revenue and Cumulative Revenue

    First `GROUP BY` the month (`strftime(order_date, '%Y-%m')`, from Session 2),
    then run a window function over those monthly totals:
    `SUM(SUM(sales_amount)) OVER (ORDER BY month)` — the inner `SUM` is the
    month's revenue, the outer `SUM ... OVER` adds the months up.
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            strftime(order_date, '%Y-%m') AS month,
            COUNT(*) AS orders,
            SUM(sales_amount) AS revenue,
            SUM(SUM(sales_amount)) OVER (ORDER BY strftime(order_date, '%Y-%m')) AS cumulative_revenue
        FROM sales
        GROUP BY strftime(order_date, '%Y-%m')
        ORDER BY month
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Read it carefully:** March is the strongest month (81,222). July looks weak
    (27,893), but it has only **19 days** of data (2025-07-01 to 2025-07-19), not a
    full month — compare months with the same number of days before calling it a
    decline.
    """)
    return


@app.cell
def _(con, plt):
    _df = con.execute("""
        SELECT strftime(order_date, '%Y-%m') AS month,
               SUM(sales_amount) AS revenue
        FROM sales
        GROUP BY strftime(order_date, '%Y-%m')
        ORDER BY month
    """).df()
    _fig, _ax = plt.subplots(figsize=(8, 3.5))
    _ax.bar(_df["month"], _df["revenue"])
    _ax.set_title("Revenue by Month (2025-07 = 19 days only)")
    _ax.set_xlabel("Month")
    _ax.set_ylabel("Revenue (dollars)")
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. A Running Total per Product — `PARTITION BY`

    `PARTITION BY product` keeps a **separate** running total for each product —
    it restarts at the product's first order. All 200 rows, by product and date:
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            product,
            order_date,
            sales_amount,
            SUM(sales_amount) OVER (PARTITION BY product ORDER BY order_date) AS product_running_total
        FROM sales
        ORDER BY product, order_date
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Self-check:** each product's **last** running total equals its total revenue
    (Laptop 216,940 · Phone 113,860 · Tablet 35,752 · Watch 29,821). `QUALIFY`
    (from `notebook_01_ranking.py`) keeps just that last row per product:
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            product,
            order_date AS last_order_date,
            SUM(sales_amount) OVER (PARTITION BY product ORDER BY order_date) AS product_running_total
        FROM sales
        QUALIFY ROW_NUMBER() OVER (PARTITION BY product ORDER BY order_date DESC) = 1
        ORDER BY product
        """,
        engine=con
    )
    return


@app.cell
def _(con, plt):
    _df = con.execute("""
        SELECT product,
               order_date,
               SUM(sales_amount) OVER (PARTITION BY product ORDER BY order_date) AS product_running_total
        FROM sales
        ORDER BY product, order_date
    """).df()
    _fig, _ax = plt.subplots(figsize=(8, 3.5))
    for _product, _rows in _df.groupby("product"):
        _ax.plot(_rows["order_date"], _rows["product_running_total"], label=_product)
    _ax.set_title("Running Total of Revenue per Product")
    _ax.set_xlabel("Order date")
    _ax.set_ylabel("Revenue so far (dollars)")
    _ax.legend()
    _fig.autofmt_xdate()
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5. Segmenting Products with `CASE`

    A **segment** is a business label computed from a number. The tiers here, by a
    product's total revenue:

    | Segment | Rule |
    |---|---|
    | High | revenue > 50,000 |
    | Medium | 20,000 < revenue ≤ 50,000 |
    | Low | revenue ≤ 20,000 |

    `CASE` checks the `WHEN`s from the top and stops at the first true one — so the
    Medium line only sees products that were not already High.
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            product,
            SUM(sales_amount) AS revenue,
            CASE
                WHEN SUM(sales_amount) > 50000 THEN 'High'
                WHEN SUM(sales_amount) > 20000 THEN 'Medium'
                ELSE 'Low'
            END AS segment
        FROM sales
        GROUP BY product
        ORDER BY revenue DESC
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    No product is Low with these thresholds — thresholds are a business decision,
    and changing them changes the answer.

    ---
    ## 6. Rank, Share, and Segment in One Query

    `RANK()`, a share of the total, and the `CASE` label side by side:

    - `pct_of_total = 100 × product revenue ÷ total revenue (396,373)`, rounded to
      1 decimal. `SUM(SUM(sales_amount)) OVER ()` is the total revenue: an empty
      `OVER ()` means "over all rows of the result".
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            product,
            SUM(sales_amount) AS revenue,
            RANK() OVER (ORDER BY SUM(sales_amount) DESC) AS rnk,
            ROUND(100.0 * SUM(sales_amount) / SUM(SUM(sales_amount)) OVER (), 1) AS pct_of_total,
            CASE
                WHEN SUM(sales_amount) > 50000 THEN 'High'
                WHEN SUM(sales_amount) > 20000 THEN 'Medium'
                ELSE 'Low'
            END AS segment
        FROM sales
        GROUP BY product
        ORDER BY rnk, product
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Insight:** Laptops alone bring in 54.7% of revenue; Laptop and Phone together
    83.5% (330,800 of 396,373).

    ---
    ## 7. Segmenting Orders by Size

    The same `CASE` idea on single orders (`sales_amount` runs from 185 to 6,295):

    | Order size | Rule |
    |---|---|
    | Large | `sales_amount` ≥ 2,000 |
    | Medium | 500 ≤ `sales_amount` < 2,000 |
    | Small | `sales_amount` < 500 |

    `pct_of_revenue = 100 × the size group's revenue ÷ 396,373`, rounded to 1 decimal.
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            CASE
                WHEN sales_amount >= 2000 THEN 'Large'
                WHEN sales_amount >= 500 THEN 'Medium'
                ELSE 'Small'
            END AS order_size,
            COUNT(*) AS orders,
            SUM(sales_amount) AS revenue,
            ROUND(100.0 * SUM(sales_amount) / SUM(SUM(sales_amount)) OVER (), 1) AS pct_of_revenue
        FROM sales
        GROUP BY order_size
        ORDER BY revenue DESC
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Insight:** the 79 Large orders (39.5% of the 200 orders) bring in 75.4% of revenue; the
    33 Small orders bring in only 2.7%.

    ---
    ## 8. Try It Yourself

    Write each query in the cell below (replace the starter query).

    1. **Running count of orders.** Columns `order_date`, `orders_so_far`
       (`COUNT(*) OVER (ORDER BY order_date)`); sort by `order_date`.
       *Self-check:* 200 rows; the last row shows 200.
    2. **Monthly revenue per product, with a running total per product.** Columns
       `product`, `month` (`strftime(order_date, '%Y-%m')`), `revenue`, and
       `product_cumulative_revenue` (`SUM(SUM(sales_amount)) OVER (PARTITION BY
       product ORDER BY month)`); group by product and month; sort by `product`,
       then `month`. *Self-check:* 28 rows (4 products × 7 months).
    3. **Your own segments.** Change the product thresholds in section 5 so that
       exactly one product is High, one Medium, and two Low. Which thresholds did
       you choose?
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        -- Your query here
        SELECT *
        FROM sales
        ORDER BY order_date
        LIMIT 5
        """,
        engine=con
    )
    return


if __name__ == "__main__":
    app.run()
