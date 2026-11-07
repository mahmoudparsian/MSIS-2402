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
    # Session 5 — Ranking with Window Functions

    Goes with the deck `slides_02_window_functions_ranking.md` (this folder).

    **Run it from this folder** — from the course repository folder:
    `cd week3_sql_for_analytics/session05_operational_db_window_functions`, then
    `marimo edit notebook_01_ranking.py`.

    **Data:** `data/product_orders.csv` — **200 orders**, one per day from
    2025-01-01 to 2025-07-19, for **4 products** (Laptop, Phone, Tablet, Watch).
    Columns: `order_id`, `order_date`, `product`, `price`, `quantity`,
    `sales_amount` (= `price × quantity`, whole dollars).

    **In this notebook**

    1. `GROUP BY` vs. a window function
    2. `RANK()` after aggregation
    3. `ROW_NUMBER`, `RANK`, and `DENSE_RANK` on a real tie
    4. Top N — with or without the ties
    5. Top N **per group** with `PARTITION BY` (and `QUALIFY`)
    6. Why `WHERE` cannot filter on a rank
    7. The Nth-highest value with `DENSE_RANK`
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


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT *
        FROM sales
        ORDER BY order_id
        LIMIT 5
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. `GROUP BY` vs. a Window Function

    `GROUP BY` **collapses** rows: one row per product.
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            product,
            COUNT(*) AS orders,
            SUM(sales_amount) AS revenue
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
    A **window function** (`... OVER (...)`) computes over a group of rows but
    **keeps every row**. Here each order sits next to its product's total revenue,
    so we can see each order's share:
    `pct_of_product = 100 × sales_amount ÷ product_revenue`, rounded to 2 decimals.

    `PARTITION BY product` means "compute separately for each product".
    The first 6 orders (by `order_id`):
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            order_id,
            product,
            sales_amount,
            SUM(sales_amount) OVER (PARTITION BY product) AS product_revenue,
            ROUND(100.0 * sales_amount / SUM(sales_amount) OVER (PARTITION BY product), 2) AS pct_of_product
        FROM sales
        ORDER BY order_id
        LIMIT 6
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Order 1 (a Tablet, 939) is 2.63% of Tablet's 35,752 revenue. Every one of the
    200 orders is still there — `GROUP BY` could not show this.

    ---
    ## 2. `RANK()` After Aggregation

    A window function can rank the result of an aggregate: `GROUP BY` computes each
    product's total first, then `RANK()` ranks those totals (highest = 1).
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            product,
            SUM(sales_amount) AS revenue,
            RANK() OVER (ORDER BY SUM(sales_amount) DESC) AS rnk
        FROM sales
        GROUP BY product
        ORDER BY rnk, product
        """,
        engine=con
    )
    return


@app.cell
def _(con, plt):
    _df = con.execute("""
        SELECT product, SUM(sales_amount) AS revenue
        FROM sales
        GROUP BY product
        ORDER BY revenue DESC
    """).df()
    _fig, _ax = plt.subplots(figsize=(7, 3.5))
    _ax.bar(_df["product"], _df["revenue"])
    _ax.set_title("Revenue by Product (rank 1 = left)")
    _ax.set_xlabel("Product")
    _ax.set_ylabel("Revenue (dollars)")
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. `ROW_NUMBER`, `RANK`, and `DENSE_RANK` on a Real Tie

    Orders **67** and **70** both have `sales_amount` = **5,610** — tied for 12th
    place. The three functions handle the tie differently. Orders 10th–15th by
    `sales_amount` (highest first):
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        WITH ranked AS (
            SELECT
                order_id,
                product,
                sales_amount,
                ROW_NUMBER() OVER (ORDER BY sales_amount DESC, order_id) AS row_num,
                RANK()       OVER (ORDER BY sales_amount DESC)           AS rnk,
                DENSE_RANK() OVER (ORDER BY sales_amount DESC)           AS dense_rnk
            FROM sales
        )
        SELECT *
        FROM ranked
        WHERE row_num BETWEEN 10 AND 15
        ORDER BY row_num
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    | Function | Orders 67 and 70 (tied) | Next order (142, 5,580) | Rule |
    |---|---|---|---|
    | `ROW_NUMBER` | 12 and 13 | 14 | Always 1, 2, 3, … — **no ties**. The tie-breaker `order_id` decides who gets 12 (order 67) |
    | `RANK` | 12 and 12 | **14** | Ties share a rank, then the next rank **skips** (no 13) |
    | `DENSE_RANK` | 12 and 12 | **13** | Ties share a rank, **no gap** |

    ⚠️ Without `order_id` in `ROW_NUMBER()`'s `ORDER BY`, the database may number
    67 and 70 either way — always add a tie-breaker to `ROW_NUMBER()`.

    ---
    ## 4. Top N — With or Without the Ties

    *"Show the top 12 orders by `sales_amount`."* With `ROW_NUMBER` you get exactly
    **12 rows** — order 70 is cut, although it ties with order 67:
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        WITH ranked AS (
            SELECT
                order_id,
                product,
                sales_amount,
                ROW_NUMBER() OVER (ORDER BY sales_amount DESC, order_id) AS row_num
            FROM sales
        )
        SELECT *
        FROM ranked
        WHERE row_num <= 12
        ORDER BY row_num
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    With `RANK` you get **13 rows** — both tied orders are kept:
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        WITH ranked AS (
            SELECT
                order_id,
                product,
                sales_amount,
                RANK() OVER (ORDER BY sales_amount DESC) AS rnk
            FROM sales
        )
        SELECT *
        FROM ranked
        WHERE rnk <= 12
        ORDER BY rnk, order_id
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Which one when?**

    - Exactly N rows (a page of results, "pick one winner") → `ROW_NUMBER` + a tie-breaker
    - Top N, and nobody tied with the Nth may be left out → `RANK`
    - The Nth-highest **value** → `DENSE_RANK` (section 7)

    ---
    ## 5. Top N per Group — `PARTITION BY`

    *"The 2 largest orders of each product."* `PARTITION BY product` restarts the
    numbering at 1 for every product. Rank inside a CTE, then filter outside it —
    **8 rows** (2 per product):
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        WITH ranked AS (
            SELECT
                product,
                order_id,
                sales_amount,
                ROW_NUMBER() OVER (PARTITION BY product
                                   ORDER BY sales_amount DESC, order_id) AS rn
            FROM sales
        )
        SELECT
            product,
            order_id,
            sales_amount,
            rn
        FROM ranked
        WHERE rn <= 2
        ORDER BY product, rn
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **DuckDB shortcut: `QUALIFY`** filters on a window function directly — no CTE
    needed. Same 8 rows:
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            product,
            order_id,
            sales_amount
        FROM sales
        QUALIFY ROW_NUMBER() OVER (PARTITION BY product
                                   ORDER BY sales_amount DESC, order_id) <= 2
        ORDER BY product, sales_amount DESC
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `QUALIFY` is a DuckDB (and Snowflake, BigQuery) feature — MySQL and PostgreSQL
    don't have it, so the CTE version is the one that works everywhere.

    ---
    ## 6. Why `WHERE` Cannot Filter on a Rank

    `WHERE` runs **before** window functions are computed, so it cannot see a rank.
    The cell below runs the wrong query and prints DuckDB's error:
    """)
    return


@app.cell
def _(con):
    _wrong = """
        SELECT order_id,
               sales_amount,
               RANK() OVER (ORDER BY sales_amount DESC) AS rnk
        FROM sales
        WHERE rnk <= 3
    """
    try:
        con.execute(_wrong).fetchall()
    except Exception as _e:
        print(type(_e).__name__ + ":", _e)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Fix:** rank in a CTE and filter outside it (section 4), or use `QUALIFY`
    (section 5).

    ---
    ## 7. The Nth-Highest Value — `DENSE_RANK`

    *"Which order has the 13th-highest `sales_amount`, counting tied amounts once?"*
    `DENSE_RANK` counts **distinct values**, so level 13 is the amount right after
    the tied 5,610 — order 142 (5,580):
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        WITH ranked AS (
            SELECT
                order_id,
                sales_amount,
                DENSE_RANK() OVER (ORDER BY sales_amount DESC) AS amount_level
            FROM sales
        )
        SELECT
            order_id,
            sales_amount
        FROM ranked
        WHERE amount_level = 13
        ORDER BY order_id
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    With `RANK` instead, `= 13` returns **no rows** — after the tie at 12, `RANK`
    jumps straight to 14:
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        WITH ranked AS (
            SELECT
                order_id,
                sales_amount,
                RANK() OVER (ORDER BY sales_amount DESC) AS rnk
            FROM sales
        )
        SELECT
            order_id,
            sales_amount
        FROM ranked
        WHERE rnk = 13
        ORDER BY order_id
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 8. Try It Yourself

    Write each query in the cell below (replace the starter query). Use the
    `sales` table; break ties as stated.

    1. **The 5 largest orders.** Columns `order_id`, `product`, `sales_amount`;
       sort by `sales_amount` descending, ties by `order_id`; limit 5.
       *Self-check:* 5 rows, all Laptops.
    2. **The smallest order of each product.** Columns `product`, `order_id`,
       `sales_amount`; use `ROW_NUMBER()` with `PARTITION BY product`, ordered by
       `sales_amount` ascending, ties by `order_id`; sort by `product`.
       *Self-check:* 4 rows.
    3. **Rank products by number of orders.** Columns `product`, `orders`
       (`COUNT(*)`), and the ranks `rnk` (`RANK`) and `dense_rnk` (`DENSE_RANK`),
       highest count = 1; sort by `rnk`, then `product`.
       *Self-check:* 4 rows. Two products tie — which ranks does each function
       give the product after them?
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        -- Your query here
        SELECT *
        FROM sales
        ORDER BY order_id
        LIMIT 5
        """,
        engine=con
    )
    return


if __name__ == "__main__":
    app.run()
