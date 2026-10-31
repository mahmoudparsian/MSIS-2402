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
    # Week 3, Part 1 — Ranking
    """)
    return


@app.cell
def _():
    import duckdb, pandas as pd
    con=duckdb.connect()
    df=pd.read_csv('./data/week4_sales.csv')
    con.register('sales', df)
    return (con,)


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            product,
            SUM(sales_amount) AS revenue,
            RANK() OVER(ORDER BY SUM(sales_amount) DESC) AS rank
        FROM sales
        GROUP BY product
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            *,
            ROW_NUMBER() OVER(ORDER BY sales_amount DESC) AS rn
        FROM sales
        """,
        engine=con
    )
    return


if __name__ == "__main__":
    app.run()

