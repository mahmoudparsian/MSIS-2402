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


if __name__ == "__main__":
    app.run()

