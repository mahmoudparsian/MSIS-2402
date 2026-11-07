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
    # 📘 Session 2 — HAVING, KPIs & Business Thinking
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
    ## ⚠️ WHERE vs HAVING (Most Important Concept)
    - WHERE → before aggregation
    - HAVING → after aggregation
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
        HAVING revenue > 20000
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🎯 Top Products
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            product,
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
    ## 📊 Visualization: Product Revenue Share
    """)
    return


@app.cell
def _(con, plt):

    df_plot = con.execute('SELECT product, SUM(sales_amount) AS revenue FROM sales GROUP BY product').df()
    plt.figure()
    plt.pie(df_plot['revenue'], labels=df_plot['product'], autopct='%1.1f%%')
    plt.title('Revenue Share by Product')
    plt.show()

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🧠 Business Questions
    1. Which product drives revenue?
    2. Which country underperforms?
    3. Where should we invest?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🧪 Exercise
    1. Countries with avg price > 700
    2. Products with revenue > 30000
    """)
    return


if __name__ == "__main__":
    app.run()

