import marimo


__generated_with = "0.23.10"

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    # Jupyter's IPython.display.display() shim, since these
    # notebooks call display() directly for mid-cell output.
    try:
        from IPython.display import display
    except ImportError:
        def display(x):
            print(x)
    return (display,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Sales Data Analysis with DuckDB

    **Dataset:** `sales.csv` — 207 sales records  
    **Columns:** `sale_id`, `sale_date`, `product_id`, `product_category`, `quantity`, `unit_price`, `total_amount`  
    **Categories:** Beauty, Clothing, Computers, Electronics, Home, Office, Sports, Toys  
    **Date range:** 2021 – 2024  

    This notebook:
    1. Loads `sales.csv` into a DuckDB database (`sales_db.duckdb`)
    2. Deduplicates the data
    3. Runs **25 SQL queries** (5 Basic, 10 Basic+, 10 Intermediate) with visualizations

    **Plotting code is decoupled** — all chart functions live in `plot_helpers.py`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup — Imports & Database Creation
    """)
    return


@app.cell
def _():
    import duckdb
    import os

    # Import decoupled plotting helpers
    from plot_helpers import (
        bar_chart, hbar_chart, pie_chart, line_chart,
        grouped_bar_chart, stacked_bar_chart, scatter_plot, histogram
    )
    return bar_chart, duckdb, grouped_bar_chart, hbar_chart, line_chart, os, pie_chart


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Create (or open) the DuckDB database and load `sales.csv`
    """)
    return


@app.cell
def _(duckdb, os):
    # Remove old database if it exists so we start fresh
    if os.path.exists('sales_db.duckdb'):
        os.remove('sales_db.duckdb')

    con = duckdb.connect('sales_db.duckdb')

    # Load CSV into a table called 'sales'
    con.execute("""
        CREATE TABLE sales AS
        SELECT * FROM read_csv_auto('sales.csv');
    """)

    print('Table created.')
    con.execute('SELECT COUNT(*) AS total_rows FROM sales').fetchdf()
    return (con,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Deduplicate — drop full duplicate rows
    """)
    return


@app.cell
def _(con, display):
    # Check for duplicates before dedup
    dup_count = con.execute("""
        SELECT COUNT(*) - COUNT(DISTINCT (sale_id, sale_date, product_id,
               product_category, quantity, unit_price, total_amount))
        AS duplicate_rows
        FROM sales;
    """).fetchdf()
    print('Duplicate rows found:')
    display(dup_count)

    # Deduplicate: keep one copy of each unique row
    con.execute("""
        CREATE OR REPLACE TABLE sales AS
        SELECT DISTINCT *
        FROM sales;
    """)

    final = con.execute('SELECT COUNT(*) AS rows_after_dedup FROM sales').fetchdf()
    print('After deduplication:')
    display(final)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Section 1 — Basic Queries (5)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### B1. Preview the first 10 rows of the sales table
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT *
        FROM sales
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### B2. Count the total number of sales
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT COUNT(*) AS total_sales
        FROM sales;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### B3. List all distinct product categories
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
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
    ### B4. Find the minimum and maximum sale dates
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            MIN(sale_date) AS earliest_sale,
            MAX(sale_date) AS latest_sale
        FROM sales;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### B5. Find the most expensive single unit price
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            sale_id,
            product_category,
            unit_price,
            total_amount
        FROM sales
        ORDER BY unit_price DESC
        LIMIT 5;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Section 2 — Basic+ Queries (10)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP1. Total revenue by product category
    """)
    return


@app.cell
def _(con, mo, sales):
    df = mo.sql(
        f"""
        SELECT
            product_category,
            ROUND(SUM(total_amount), 2) AS total_revenue
        FROM sales
        GROUP BY product_category
        ORDER BY total_revenue DESC;
        """,
        engine=con
    )
    return (df,)


@app.cell
def _(bar_chart, df):
    bar_chart(
        df['product_category'], df['total_revenue'],
        title='Total Revenue by Product Category',
        xlabel='Category', ylabel='Revenue ($)',
        dollar=True, rotate_labels=30
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP2. Number of sales per product category
    """)
    return


@app.cell
def _(con, mo, sales):
    df_2 = mo.sql(
        f"""
        SELECT
            product_category,
            COUNT(*) AS num_sales
        FROM sales
        GROUP BY product_category
        ORDER BY num_sales DESC;
        """,
        engine=con
    )
    return (df_2,)


@app.cell
def _(df_2, pie_chart):
    pie_chart(
        df_2['product_category'], df_2['num_sales'],
        title='Sales Distribution by Category'
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP3. Average unit price per category
    """)
    return


@app.cell
def _(con, mo, sales):
    df_3 = mo.sql(
        f"""
        SELECT
            product_category,
            ROUND(AVG(unit_price), 2) AS avg_unit_price
        FROM sales
        GROUP BY product_category
        ORDER BY avg_unit_price DESC;
        """,
        engine=con
    )
    return (df_3,)


@app.cell
def _(bar_chart, df_3):
    bar_chart(
        df_3['product_category'], df_3['avg_unit_price'],
        title='Average Unit Price by Category',
        xlabel='Category', ylabel='Avg Unit Price ($)',
        dollar=True, rotate_labels=30
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP4. Total quantity sold per category
    """)
    return


@app.cell
def _(con, mo, sales):
    df_4 = mo.sql(
        f"""
        SELECT
            product_category,
            SUM(quantity) AS total_qty
        FROM sales
        GROUP BY product_category
        ORDER BY total_qty DESC;
        """,
        engine=con
    )
    return (df_4,)


@app.cell
def _(bar_chart, df_4):
    bar_chart(
        df_4['product_category'], df_4['total_qty'],
        title='Total Quantity Sold by Category',
        xlabel='Category', ylabel='Quantity'
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP5. Sales with total_amount > $1,000
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            sale_id,
            sale_date,
            product_category,
            quantity,
            unit_price,
            total_amount
        FROM sales
        WHERE total_amount > 1000
        ORDER BY total_amount DESC;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP6. Average total amount per category
    """)
    return


@app.cell
def _(con, mo, sales):
    df_5 = mo.sql(
        f"""
        SELECT
            product_category,
            ROUND(AVG(total_amount), 2) AS avg_total
        FROM sales
        GROUP BY product_category
        ORDER BY avg_total DESC;
        """,
        engine=con
    )
    return (df_5,)


@app.cell
def _(df_5, hbar_chart):
    hbar_chart(
        df_5['product_category'], df_5['avg_total'],
        title='Average Order Value by Category',
        xlabel='Avg Total ($)', dollar=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP7. Number of sales per year
    """)
    return


@app.cell
def _(con, mo, sales):
    df_6 = mo.sql(
        f"""
        SELECT
            YEAR(sale_date) AS sale_year,
            COUNT(*) AS num_sales
        FROM sales
        GROUP BY sale_year
        ORDER BY sale_year;
        """,
        engine=con
    )
    if hasattr(df_6, "to_pandas"):
        df_6 = df_6.to_pandas()
    return (df_6,)


@app.cell
def _(bar_chart, df_6):
    bar_chart(
        df_6['sale_year'].astype(str), df_6['num_sales'],
        title='Number of Sales per Year',
        xlabel='Year', ylabel='Sales Count'
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP8. Top 10 highest-value individual sales
    """)
    return


@app.cell
def _(con, mo, sales):
    df_7 = mo.sql(
        f"""
        SELECT
            sale_id,
            sale_date,
            product_category,
            quantity,
            unit_price,
            total_amount
        FROM sales
        ORDER BY total_amount DESC
        LIMIT 10;
        """,
        engine=con
    )
    if hasattr(df_7, "to_pandas"):
        df_7 = df_7.to_pandas()
    return (df_7,)


@app.cell
def _(df_7, hbar_chart):
    hbar_chart(
        df_7['sale_id'].astype(str) + ' (' + df_7['product_category'] + ')',
        df_7['total_amount'],
        title='Top 10 Highest-Value Sales',
        xlabel='Total Amount ($)', dollar=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP9. Min, Max, and Average quantity per category
    """)
    return


@app.cell
def _(con, mo, sales):
    df_8 = mo.sql(
        f"""
        SELECT
            product_category,
            MIN(quantity) AS min_qty,
            MAX(quantity) AS max_qty,
            ROUND(AVG(quantity), 1) AS avg_qty
        FROM sales
        GROUP BY product_category
        ORDER BY product_category;
        """,
        engine=con
    )
    return (df_8,)


@app.cell
def _(df_8, grouped_bar_chart):
    grouped_bar_chart(
        list(df_8['product_category']),
        {'Min Qty': list(df_8['min_qty']),
         'Avg Qty': list(df_8['avg_qty']),
         'Max Qty': list(df_8['max_qty'])},
        title='Quantity Stats by Category',
        xlabel='Category', ylabel='Quantity'
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP10. Revenue by year
    """)
    return


@app.cell
def _(con, mo, sales):
    df_9 = mo.sql(
        f"""
        SELECT
            YEAR(sale_date) AS sale_year,
            ROUND(SUM(total_amount), 2) AS total_revenue
        FROM sales
        GROUP BY sale_year
        ORDER BY sale_year;
        """,
        engine=con
    )
    if hasattr(df_9, "to_pandas"):
        df_9 = df_9.to_pandas()
    return (df_9,)


@app.cell
def _(df_9, line_chart):
    line_chart(
        df_9['sale_year'].astype(str), df_9['total_revenue'],
        title='Total Revenue by Year',
        xlabel='Year', ylabel='Revenue ($)',
        dollar=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Section 3 — Intermediate Queries (10)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I1. Monthly revenue trend (all years combined)
    """)
    return


@app.cell
def _(con, mo, sales):
    df_10 = mo.sql(
        f"""
        SELECT
            MONTH(sale_date) AS sale_month,
            MONTHNAME(sale_date) AS month_name,
            ROUND(SUM(total_amount), 2) AS monthly_revenue
        FROM sales
        GROUP BY
            sale_month,
            month_name
        ORDER BY sale_month;
        """,
        engine=con
    )
    return (df_10,)


@app.cell
def _(df_10, line_chart):
    line_chart(
        df_10['month_name'], df_10['monthly_revenue'],
        title='Monthly Revenue (All Years Combined)',
        xlabel='Month', ylabel='Revenue ($)',
        dollar=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I2. Year-over-year revenue by category
    """)
    return


@app.cell
def _(con, mo, sales):
    df_11 = mo.sql(
        f"""
        SELECT
            YEAR(sale_date) AS sale_year,
            product_category,
            ROUND(SUM(total_amount), 2) AS revenue
        FROM sales
        GROUP BY
            sale_year,
            product_category
        ORDER BY
            sale_year,
            product_category;
        """,
        engine=con
    )
    if hasattr(df_11, "to_pandas"):
        df_11 = df_11.to_pandas()
    return (df_11,)


@app.cell
def _(df_11, grouped_bar_chart):
    # Pivot for grouped bar chart
    _pivot = df_11.pivot(index='product_category', columns='sale_year', values='revenue').fillna(0)
    _series = {str(col): list(_pivot[col]) for col in _pivot.columns}

    grouped_bar_chart(
        list(_pivot.index), _series,
        title='Revenue by Category and Year',
        xlabel='Category', ylabel='Revenue ($)',
        dollar=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I3. Running total of revenue over time (cumulative)
    """)
    return


@app.cell
def _(con, mo, sales):
    df_12 = mo.sql(
        f"""
        SELECT
            sale_date,
            total_amount,
            SUM(total_amount) OVER(ORDER BY sale_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue
        FROM sales
        ORDER BY sale_date;
        """,
        engine=con
    )
    if hasattr(df_12, "to_pandas"):
        df_12 = df_12.to_pandas()
    return (df_12,)


@app.cell
def _(df_12, line_chart):
    line_chart(
        df_12['sale_date'].astype(str), df_12['cumulative_revenue'],
        title='Cumulative Revenue Over Time',
        xlabel='Date', ylabel='Cumulative Revenue ($)',
        dollar=True, marker=''
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I4. Rank categories by total revenue using RANK()
    """)
    return


@app.cell
def _(con, mo, sales):
    df_13 = mo.sql(
        f"""
        SELECT
            product_category,
            ROUND(SUM(total_amount), 2) AS total_revenue,
            RANK() OVER(ORDER BY SUM(total_amount) DESC) AS revenue_rank
        FROM sales
        GROUP BY product_category
        ORDER BY revenue_rank;
        """,
        engine=con
    )
    return (df_13,)


@app.cell
def _(bar_chart, df_13):
    bar_chart(
        df_13['product_category'], df_13['total_revenue'],
        title='Category Revenue Ranking',
        xlabel='Category (ranked)', ylabel='Total Revenue ($)',
        dollar=True, rotate_labels=30
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I5. Percentage of total revenue contributed by each category
    """)
    return


@app.cell
def _(con, mo, sales):
    df_14 = mo.sql(
        f"""
        SELECT
            product_category,
            ROUND(SUM(total_amount), 2) AS category_revenue,
            ROUND(100.0 * SUM(total_amount) / (SELECT SUM(total_amount) FROM sales), 2) AS pct_of_total
        FROM sales
        GROUP BY product_category
        ORDER BY pct_of_total DESC;
        """,
        engine=con
    )
    return (df_14,)


@app.cell
def _(df_14, pie_chart):
    pie_chart(
        df_14['product_category'], df_14['category_revenue'],
        title='Revenue Share by Category'
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I6. Quarterly revenue trend
    """)
    return


@app.cell
def _(con, mo, sales):
    df_15 = mo.sql(
        f"""
        SELECT
            YEAR(sale_date) AS yr,
            QUARTER(sale_date) AS qtr,
            CONCAT(YEAR(sale_date), '-Q', QUARTER(sale_date)) AS year_quarter,
            ROUND(SUM(total_amount), 2) AS quarterly_revenue
        FROM sales
        GROUP BY
            yr,
            qtr,
            year_quarter
        ORDER BY
            yr,
            qtr;
        """,
        engine=con
    )
    return (df_15,)


@app.cell
def _(df_15, line_chart):
    line_chart(
        df_15['year_quarter'], df_15['quarterly_revenue'],
        title='Quarterly Revenue Trend',
        xlabel='Quarter', ylabel='Revenue ($)',
        dollar=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I7. Distribution of total_amount (histogram analysis via SQL buckets)
    """)
    return


@app.cell
def _(con, mo, sales):
    df_16 = mo.sql(
        f"""
        SELECT
            CASE WHEN total_amount < 100 THEN '0-99' WHEN total_amount < 300 THEN '100-299' WHEN total_amount < 500 THEN '300-499' WHEN total_amount < 750 THEN '500-749' WHEN total_amount < 1000 THEN '750-999' WHEN total_amount < 1500 THEN '1000-1499' ELSE '1500+' END AS amount_bucket,
            COUNT(*) AS num_sales
        FROM sales
        GROUP BY amount_bucket
        ORDER BY MIN(total_amount);
        """,
        engine=con
    )
    return (df_16,)


@app.cell
def _(bar_chart, df_16):
    bar_chart(
        df_16['amount_bucket'], df_16['num_sales'],
        title='Distribution of Sale Amounts',
        xlabel='Amount Bucket ($)', ylabel='Number of Sales'
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I8. Top category per year (using a CTE + window function)
    """)
    return


@app.cell
def _(con, mo, sales):
    df_17 = mo.sql(
        f"""
        WITH ranked AS (SELECT YEAR(sale_date) AS sale_year, product_category, ROUND(SUM(total_amount), 2) AS revenue, ROW_NUMBER() OVER(PARTITION BY YEAR(sale_date) ORDER BY SUM(total_amount) DESC) AS rn FROM sales GROUP BY sale_year, product_category)
        SELECT
            sale_year,
            product_category,
            revenue
        FROM ranked
        WHERE rn = 1
        ORDER BY sale_year;
        """,
        engine=con
    )
    if hasattr(df_17, "to_pandas"):
        df_17 = df_17.to_pandas()
    return (df_17,)


@app.cell
def _(bar_chart, df_17):
    bar_chart(
        df_17['sale_year'].astype(str) + '\n' + df_17['product_category'],
        df_17['revenue'],
        title='Top Revenue Category per Year',
        xlabel='Year / Category', ylabel='Revenue ($)',
        dollar=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I9. Average order value vs number of orders per category (scatter analysis)
    """)
    return


@app.cell
def _(con, mo, sales):
    df_18 = mo.sql(
        f"""
        SELECT
            product_category,
            COUNT(*) AS num_orders,
            ROUND(AVG(total_amount), 2) AS avg_order_value
        FROM sales
        GROUP BY product_category;
        """,
        engine=con
    )
    if hasattr(df_18, "to_pandas"):
        df_18 = df_18.to_pandas()
    return (df_18,)


@app.cell
def _(df_18):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df_18['num_orders'], df_18['avg_order_value'],
               s=150, color='#4C72B0', edgecolors='white', zorder=5)
    for _, row in df_18.iterrows():
        ax.annotate(row['product_category'],
                    (row['num_orders'], row['avg_order_value']),
                    textcoords='offset points', xytext=(8, 5), fontsize=10)
    ax.set_title('Avg Order Value vs Number of Orders', fontweight='bold')
    ax.set_xlabel('Number of Orders')
    ax.set_ylabel('Avg Order Value ($)')
    ax.grid(alpha=0.3)
    ax.spines[['top','right']].set_visible(False)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I10. Year-over-year growth rate (%) by category
    """)
    return


@app.cell
def _(con, mo, sales):
    df_19 = mo.sql(
        f"""
        WITH yearly AS (SELECT YEAR(sale_date) AS yr, product_category, ROUND(SUM(total_amount), 2) AS revenue FROM sales GROUP BY yr, product_category)
        SELECT
            a.yr AS year,
            a.product_category,
            a.revenue AS current_rev,
            b.revenue AS prev_rev,
            ROUND(100.0 * (a.revenue - b.revenue) / b.revenue, 1) AS yoy_growth_pct
        FROM yearly a
        JOIN yearly b
        ON
            a.product_category = b.product_category
            AND a.yr = b.yr + 1
        ORDER BY
            a.product_category,
            a.yr;
        """,
        engine=con
    )
    if hasattr(df_19, "to_pandas"):
        df_19 = df_19.to_pandas()
    return (df_19,)


@app.cell
def _(df_19, grouped_bar_chart):
    # Pivot for grouped bar chart
    _pivot = df_19.pivot(index='product_category', columns='year', values='yoy_growth_pct').fillna(0)
    _series = {str(col): list(_pivot[col]) for col in _pivot.columns}

    grouped_bar_chart(
        list(_pivot.index), _series,
        title='Year-over-Year Revenue Growth (%) by Category',
        xlabel='Category', ylabel='Growth (%)'
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Closing Connection
    """)
    return


@app.cell
def _(con):
    con.close()
    print('Connection closed. Database saved as sales_db.duckdb')
    return


if __name__ == "__main__":
    app.run()

