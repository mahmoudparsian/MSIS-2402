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
    # Session 5 — Trends & Segmentation
    """)
    return


@app.cell
def _():
    import duckdb, pandas as pd
    import matplotlib.pyplot as plt
    con=duckdb.connect()
    df=pd.read_csv('./data/product_orders.csv')
    con.register('sales', df)
    return con, plt


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            order_date,
            SUM(sales_amount) OVER(ORDER BY order_date) AS running_total
        FROM sales
        """,
        engine=con
    )
    return


@app.cell
def _(con, plt):
    df_plot = con.execute('SELECT order_date, SUM(sales_amount) OVER (ORDER BY order_date) AS running_total FROM sales').df()
    plt.figure()
    plt.plot(df_plot['order_date'], df_plot['running_total'])
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            product,
            SUM(sales_amount) AS revenue,
            CASE WHEN SUM(sales_amount) >50000 THEN 'High' WHEN SUM(sales_amount) >20000 THEN 'Medium' ELSE 'Low' END AS segment
        FROM sales
        GROUP BY product
        """,
        engine=con
    )
    return


if __name__ == "__main__":
    app.run()

