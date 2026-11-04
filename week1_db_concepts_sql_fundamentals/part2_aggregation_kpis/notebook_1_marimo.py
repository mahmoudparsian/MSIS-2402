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
    # 📘 Week 1, Part 2 — Aggregation & KPIs (Lecture Quality)

    ## 🎯 Goal
    Move from raw data → business metrics
    """)
    return


@app.cell
def _():
    import duckdb, pandas as pd
    import matplotlib.pyplot as plt
    plt.rcParams['font.family']='DejaVu Sans'

    con = duckdb.connect()
    df = pd.read_csv('./data/sales_dataset.csv')
    con.register('sales', df)
    df.head()
    return con, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🧠 Why Aggregation?
    Businesses care about **totals, averages, trends** — not raw rows.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## COUNT vs SUM vs AVG
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT COUNT(*) AS total_transactions
        FROM sales
        """,
        engine=con
    )
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
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT AVG(price) AS avg_price
        FROM sales
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🎯 GROUP BY (CRITICAL)
    Without GROUP BY → single number
    With GROUP BY → segmented insights
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            country,
            SUM(sales_amount) AS revenue
        FROM sales
        GROUP BY country
        ORDER BY revenue DESC
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📊 Visualization: Revenue by Country
    """)
    return


@app.cell
def _(con, plt):

    df_plot = con.execute('SELECT country, SUM(sales_amount) AS revenue FROM sales GROUP BY country').df()
    plt.figure()
    plt.bar(df_plot['country'], df_plot['revenue'])
    plt.title('Revenue by Country')
    plt.xlabel('Country')
    plt.ylabel('Revenue')
    plt.show()

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🧪 In-Class Exercise
    1. Revenue by product
    2. Avg quantity by country
    3. Count transactions per product
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 🧹📅 Text and Date Functions

    Slides: `lecture_slides_text_and_date_functions.md` (this folder).

    Two small tables:

    * `signups` — six sign-ups typed by hand (messy on purpose)
    * `sales_history` — the 200 dated sales from Session 1
      (`../part1_single_table_sql/data/sales.csv`, 2021-01-03 to 2024-12-28)
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        CREATE OR REPLACE TABLE signups AS
        SELECT * FROM (VALUES
            (1, '  Maria ', 'Garcia', 'San Jose'),
            (2, 'JAMES',    'lee',    'san jose'),
            (3, 'Aisha',    'Khan ',  ' San Jose '),
            (4, 'tom',      'NGUYEN', 'SAN JOSE'),
            (5, 'Li',       'Wei',    'Austin'),
            (6, 'Sara',     'Cohen',  'austin ')
        ) AS t(signup_id, first_name, last_name, city)
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        CREATE OR REPLACE TABLE sales_history AS
        SELECT * FROM read_csv_auto('../part1_single_table_sql/data/sales.csv')
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Problem: Messy Text Splits Your Groups

    How many sign-ups per city? There are only **2** cities — count the groups.
    """)
    return


@app.cell
def _(con, mo, signups):
    _df = mo.sql(
        f"""
        SELECT city, COUNT(*) AS signups
        FROM signups
        GROUP BY city
        ORDER BY signups DESC, city
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Fix: `LOWER(TRIM(city))` Before You Group

    `TRIM` removes the spaces at the start and end; `LOWER` makes every
    letter lowercase. Expect **2 rows**: san jose 4, austin 2.
    """)
    return


@app.cell
def _(con, mo, signups):
    _df = mo.sql(
        f"""
        SELECT LOWER(TRIM(city)) AS clean_city,
               COUNT(*)          AS signups
        FROM signups
        GROUP BY clean_city
        ORDER BY signups DESC, clean_city
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## `||` — Join Text Together
    """)
    return


@app.cell
def _(con, mo, signups):
    _df = mo.sql(
        f"""
        SELECT signup_id,
               TRIM(first_name) || ' ' || UPPER(TRIM(last_name)) AS full_name
        FROM signups
        ORDER BY signup_id
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📊 Revenue per Year — `YEAR()`

    `sale_date` is a real `DATE`, so `YEAR(sale_date)` works directly.
    """)
    return


@app.cell
def _(con, mo, sales_history):
    _df = mo.sql(
        f"""
        SELECT YEAR(sale_date)             AS sale_year,
               COUNT(*)                    AS sales,
               ROUND(SUM(total_amount), 2) AS revenue
        FROM sales_history
        GROUP BY sale_year
        ORDER BY sale_year
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📈 Monthly Trend — `DATE_TRUNC` + `strftime`

    `DATE_TRUNC('month', d)` groups by the **real month** (it keeps the year);
    `strftime(..., '%Y-%m')` shows it as `'2024-01'`.
    Dates you type are written as `DATE 'YYYY-MM-DD'`.
    """)
    return


@app.cell
def _(con, mo, sales_history):
    _df = mo.sql(
        f"""
        SELECT strftime(DATE_TRUNC('month', sale_date), '%Y-%m') AS sale_month,
               COUNT(*)                    AS sales,
               ROUND(SUM(total_amount), 2) AS revenue
        FROM sales_history
        WHERE sale_date >= DATE '2024-01-01'
          AND sale_date <  DATE '2024-07-01'
        GROUP BY sale_month
        ORDER BY sale_month
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ⏱️ Days Ago — `date_diff('day', start, end)`

    Days from each sale to the end of 2024 (recency). Order: **start, end**.
    """)
    return


@app.cell
def _(con, mo, sales_history):
    _df = mo.sql(
        f"""
        SELECT sale_id,
               sale_date,
               date_diff('day', sale_date, DATE '2024-12-31') AS days_ago
        FROM sales_history
        ORDER BY sale_date DESC, sale_id
        LIMIT 5
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🗓️ The Last 90 Days — `INTERVAL`
    """)
    return


@app.cell
def _(con, mo, sales_history):
    _df = mo.sql(
        f"""
        SELECT COUNT(*)                    AS sales,
               ROUND(SUM(total_amount), 2) AS revenue
        FROM sales_history
        WHERE sale_date > DATE '2024-12-31' - INTERVAL 90 DAY
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🧪 Try It

    1. Monthly revenue for **2023**: columns `sale_month` (`'YYYY-MM'`),
       `sales`, `revenue` (`ROUND(..., 2)`); sort by `sale_month`.
       Self-check: **11 rows**. One month of 2023 is missing — which one, and why?
    2. Every sale in the **last 30 days of 2024**
       (`sale_date > DATE '2024-12-31' - INTERVAL 30 DAY`): columns `sale_id`,
       `sale_date`, `days_ago` (days from `sale_date` to `DATE '2024-12-31'`);
       sort by `days_ago`, then `sale_id`. Self-check: **6 rows**.

    Need another function? Look it up:
    [text](https://duckdb.org/docs/stable/sql/functions/text) ·
    [date](https://duckdb.org/docs/stable/sql/functions/date) ·
    [`strftime` patterns](https://duckdb.org/docs/stable/sql/functions/dateformat)
    """)
    return


if __name__ == "__main__":
    app.run()

