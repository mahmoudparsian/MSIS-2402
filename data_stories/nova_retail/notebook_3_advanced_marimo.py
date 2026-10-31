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
    # Notebook 3 — Advanced SQL Queries (Nova Retail)

    This notebook introduces **advanced SQL techniques** for analytical workloads.

    **Topics covered:** Window functions (ROW_NUMBER, RANK, DENSE_RANK, LAG, SUM OVER),
    Common Table Expressions (CTEs / WITH), Top-N per group, time-based analytics,
    ranking queries, and DuckDB MACROs.

    **Structure:** 5 intermediate queries + 10 intermediate+/advanced queries + 2 MACROs.
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

    sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
    from plot_helpers import (
        plot_bar, plot_hbar, plot_line, plot_pie,
        plot_grouped_bar, plot_stacked_bar, plot_multi_line, plot_scatter
    )

    con = duckdb.connect("nova_db.duckdb", read_only=True)
    print("Connected to nova_db.duckdb (read-only)")
    return con, plot_bar, plot_grouped_bar, plot_hbar, plot_line, plot_multi_line, plot_pie, plot_stacked_bar


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
    ## Part A — Intermediate Queries (5 queries)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q1 — Year-over-Year Revenue Growth  
    **Concept:** CTE + `LAG()` window function  
    We compute yearly revenue with a CTE, then use `LAG` to look at the previous year's value
    and calculate the growth percentage.
    """)
    return


@app.cell
def _(con, mo):
    df = mo.sql(
        f"""
        WITH yearly_rev AS (SELECT EXTRACT(YEAR FROM o.order_date) AS order_year, ROUND(SUM(oi.sales_amount), 2) AS revenue FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY order_year)
        SELECT
            order_year,
            revenue,
            LAG(revenue) OVER(ORDER BY order_year) AS prev_year_revenue,
            ROUND(100.0 * (revenue - LAG(revenue) OVER(ORDER BY order_year)) / LAG(revenue) OVER(ORDER BY order_year), 1) AS yoy_growth_pct
        FROM yearly_rev
        ORDER BY order_year;
        """,
        engine=con
    )
    return (df,)


@app.cell
def _(df, plot_bar):
    plot_bar(df, "order_year", "revenue",
            title="Yearly Revenue with YoY Growth",
            xlabel="Year", ylabel="Revenue ($)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q2 — Monthly Revenue Trend with Running Total  
    **Concept:** `SUM() OVER (ORDER BY …)` — cumulative window function  
    We compute monthly revenue, then add a running total that accumulates month by month.
    """)
    return


@app.cell
def _(con, mo):
    df_2 = mo.sql(
        f"""
        WITH monthly AS (SELECT STRFTIME(o.order_date, '%Y-%m') AS year_month, ROUND(SUM(oi.sales_amount), 2) AS monthly_revenue FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY year_month)
        SELECT
            year_month,
            monthly_revenue,
            ROUND(SUM(monthly_revenue) OVER(ORDER BY year_month), 2) AS running_total
        FROM monthly
        ORDER BY year_month;
        """,
        engine=con
    )
    return (df_2,)


@app.cell
def _(df_2, plot_line):
    plot_line(df_2, "year_month", "running_total",
             title="Cumulative Revenue Over Time",
             xlabel="Month", ylabel="Running Total ($)",
             figsize=(12, 4))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q3 — Top 3 Products per Category by Revenue  
    **Concept:** `ROW_NUMBER() OVER (PARTITION BY … ORDER BY …)` + CTE for Top-N per group  
    We rank products within each category and keep only the top 3.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        WITH ranked AS (SELECT oi.product_id, p.category, ROUND(p.price, 2) AS unit_price, ROUND(SUM(oi.sales_amount), 2) AS product_revenue, ROW_NUMBER() OVER(PARTITION BY p.category ORDER BY SUM(oi.sales_amount) DESC) AS rn FROM order_items oi JOIN products p ON oi.product_id = p.product_id GROUP BY oi.product_id, p.category, p.price)
        SELECT
            product_id,
            category,
            unit_price,
            product_revenue,
            rn
        FROM ranked
        WHERE rn <= 3
        ORDER BY
            category,
            rn;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q4 — Customer Order Frequency Distribution  
    **Concept:** CTE + `GROUP BY` on derived frequency  
    First we count orders per customer, then group by that count to see the distribution:
    how many customers placed exactly 1 order, 2 orders, etc.
    """)
    return


@app.cell
def _(con, mo):
    df_3 = mo.sql(
        f"""
        WITH cust_orders AS (SELECT customer_id, COUNT(*) AS num_orders FROM orders GROUP BY customer_id)
        SELECT
            num_orders,
            COUNT(*) AS num_customers
        FROM cust_orders
        GROUP BY num_orders
        ORDER BY num_orders;
        """,
        engine=con
    )
    return (df_3,)


@app.cell
def _(df_3, plot_bar):
    plot_bar(df_3, "num_orders", "num_customers",
            title="Customer Order Frequency Distribution",
            xlabel="Number of Orders", ylabel="Number of Customers",
            figsize=(10, 4))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q5 — Revenue by Country and Category  
    **Concept:** Multi-dimensional aggregation across 3 tables  
    A cross-tab view showing revenue broken down by both country and product category.
    """)
    return


@app.cell
def _(con, mo):
    df_4 = mo.sql(
        f"""
        SELECT
            c.country,
            oi.category,
            ROUND(SUM(oi.sales_amount), 2) AS revenue
        FROM order_items oi
        JOIN orders o
        ON oi.order_id = o.order_id
        JOIN customers c
        ON o.customer_id = c.customer_id
        GROUP BY
            c.country,
            oi.category
        ORDER BY
            c.country,
            revenue DESC;
        """,
        engine=con
    )
    if hasattr(df_4, "to_pandas"):
        df_4 = df_4.to_pandas()
    return (df_4,)


@app.cell
def _(df_4, plot_stacked_bar):
    # Pivot for stacked bar
    pivot = df_4.pivot_table(index="country", columns="category", values="revenue", fill_value=0)
    plot_stacked_bar(pivot,
        title="Revenue by Country and Category",
        xlabel="Country", ylabel="Revenue ($)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part B — Intermediate+ / Advanced Queries (10 queries)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q6 — RANK vs DENSE_RANK: Top Revenue Categories  
    **Concept:** `RANK()` and `DENSE_RANK()` window functions  
    We demonstrate the difference between RANK (gaps after ties) and DENSE_RANK (no gaps).
    Both rank categories by total revenue.
    """)
    return


@app.cell
def _(con, mo):
    df_5 = mo.sql(
        f"""
        WITH cat_rev AS (SELECT category, ROUND(SUM(sales_amount), 2) AS total_revenue FROM order_items GROUP BY category)
        SELECT
            category,
            total_revenue,
            RANK() OVER(ORDER BY total_revenue DESC) AS rank_val,
            DENSE_RANK() OVER(ORDER BY total_revenue DESC) AS dense_rank_val
        FROM cat_rev
        ORDER BY total_revenue DESC;
        """,
        engine=con
    )
    return (df_5,)


@app.cell
def _(df_5, plot_hbar):
    plot_hbar(df_5, "category", "total_revenue",
             title="Category Revenue Ranking",
             xlabel="Revenue ($)", ylabel="Category")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q7 — Customer Spending Quartiles Using NTILE  
    **Concept:** `NTILE(4)` window function — divides into equal-sized buckets  
    We split customers into 4 spending quartiles and show summary stats for each.
    """)
    return


@app.cell
def _(con, mo):
    df_6 = mo.sql(
        f"""
        WITH cust_spend AS (SELECT o.customer_id, ROUND(SUM(oi.sales_amount), 2) AS total_spent FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.customer_id), quartiled AS (SELECT *, NTILE(4) OVER(ORDER BY total_spent) AS spending_quartile FROM cust_spend)
        SELECT
            spending_quartile,
            COUNT(*) AS num_customers,
            ROUND(MIN(total_spent), 2) AS min_spent,
            ROUND(AVG(total_spent), 2) AS avg_spent,
            ROUND(MAX(total_spent), 2) AS max_spent
        FROM quartiled
        GROUP BY spending_quartile
        ORDER BY spending_quartile;
        """,
        engine=con
    )
    return (df_6,)


@app.cell
def _(df_6, plot_bar):
    plot_bar(df_6, "spending_quartile", "avg_spent",
            title="Average Spending by Customer Quartile",
            xlabel="Quartile (1=Lowest, 4=Highest)", ylabel="Avg Spent ($)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q8 — Month-over-Month Revenue Change  
    **Concept:** `LAG()` for time-series comparison  
    We compute each month's revenue and the absolute/percentage change from the prior month.
    """)
    return


@app.cell
def _(con, mo):
    df_7 = mo.sql(
        f"""
        WITH monthly AS (SELECT STRFTIME(o.order_date, '%Y-%m') AS year_month, ROUND(SUM(oi.sales_amount), 2) AS revenue FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY year_month)
        SELECT
            year_month,
            revenue,
            LAG(revenue) OVER(ORDER BY year_month) AS prev_month,
            ROUND(revenue - LAG(revenue) OVER(ORDER BY year_month), 2) AS mom_change,
            ROUND(100.0 * (revenue - LAG(revenue) OVER(ORDER BY year_month)) / LAG(revenue) OVER(ORDER BY year_month), 1) AS mom_pct
        FROM monthly
        ORDER BY year_month;
        """,
        engine=con
    )
    if hasattr(df_7, "to_pandas"):
        df_7 = df_7.to_pandas()
    return (df_7,)


@app.cell
def _(df_7, plot_line):
    # Plot only MoM % change (skip first row which is NULL)
    df_plot = df_7.dropna(subset=["mom_pct"])
    plot_line(df_plot, "year_month", "mom_pct",
             title="Month-over-Month Revenue Growth (%)",
             xlabel="Month", ylabel="MoM Change (%)",
             figsize=(12, 4))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q9 — Top 3 Customers per Segment by Spending (Ranking + CTE)  
    **Concept:** `WITH` subquery + `ROW_NUMBER() OVER (PARTITION BY …)` — ranking within groups  
    We rank customers by total spending within each segment and keep only the top 3.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        WITH customer_spend AS (SELECT c.customer_id, c.customer_segment, c.country, ROUND(SUM(oi.sales_amount), 2) AS total_spent, ROW_NUMBER() OVER(PARTITION BY c.customer_segment ORDER BY SUM(oi.sales_amount) DESC) AS rn FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id GROUP BY c.customer_id, c.customer_segment, c.country)
        SELECT
            customer_id,
            customer_segment,
            country,
            total_spent,
            rn AS rank_in_segment
        FROM customer_spend
        WHERE rn <= 3
        ORDER BY
            customer_segment,
            rn;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q10 — 3-Month Moving Average of Revenue  
    **Concept:** `AVG() OVER (… ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` — sliding window  
    A moving average smooths out noise in monthly data and reveals the underlying trend.
    """)
    return


@app.cell
def _(con, mo):
    df_8 = mo.sql(
        f"""
        WITH monthly AS (SELECT STRFTIME(o.order_date, '%Y-%m') AS year_month, ROUND(SUM(oi.sales_amount), 2) AS revenue FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY year_month)
        SELECT
            year_month,
            revenue,
            ROUND(AVG(revenue) OVER(ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg_3m
        FROM monthly
        ORDER BY year_month;
        """,
        engine=con
    )
    if hasattr(df_8, "to_pandas"):
        df_8 = df_8.to_pandas()
    return (df_8,)


@app.cell
def _(df_8):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df_8["year_month"].astype(str), df_8["revenue"],
            marker=".", color="#4C72B0", linewidth=1, alpha=0.5, label="Monthly Revenue")
    ax.plot(df_8["year_month"].astype(str), df_8["moving_avg_3m"],
            marker="o", color="#DD8452", linewidth=2, markersize=3, label="3-Month Moving Avg")
    ax.legend()
    ax.set_title("Monthly Revenue vs 3-Month Moving Average", fontsize=13, fontweight="bold")
    ax.set_xlabel("Month"); ax.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45, ha="right")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    plt.tight_layout(); plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q11 — Signup Cohort Analysis: Orders per Cohort Year  
    **Concept:** Time-based analytics + multi-table CTE  
    We group customers by their signup year (cohort) and measure how many orders
    each cohort placed in each calendar year.
    """)
    return


@app.cell
def _(con, mo):
    df_9 = mo.sql(
        f"""
        WITH cohort AS (SELECT customer_id, EXTRACT(YEAR FROM signup_date) AS cohort_year FROM customers)
        SELECT
            co.cohort_year,
            EXTRACT(YEAR FROM o.order_date) AS order_year,
            COUNT(*) AS num_orders
        FROM cohort co
        JOIN orders o
        ON co.customer_id = o.customer_id
        GROUP BY
            co.cohort_year,
            order_year
        ORDER BY
            co.cohort_year,
            order_year;
        """,
        engine=con
    )
    return (df_9,)


@app.cell
def _(df_9, plot_multi_line):
    plot_multi_line(df_9, "order_year", "num_orders", "cohort_year",
                   title="Orders by Signup Cohort Year",
                   xlabel="Order Year", ylabel="Number of Orders")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q12 — Category Revenue as Percent of Total (Window Function)  
    **Concept:** `SUM() OVER ()` — window without PARTITION (grand total)  
    We compute each category's share of total revenue using a window function —
    no subquery needed.
    """)
    return


@app.cell
def _(con, mo):
    df_10 = mo.sql(
        f"""
        SELECT
            category,
            ROUND(SUM(sales_amount), 2) AS cat_revenue,
            ROUND(SUM(sales_amount) / SUM(SUM(sales_amount)) OVER() * 100, 1) AS pct_of_total
        FROM order_items
        GROUP BY category
        ORDER BY cat_revenue DESC;
        """,
        engine=con
    )
    return (df_10,)


@app.cell
def _(df_10, plot_pie):
    plot_pie(df_10, "category", "cat_revenue",
            title="Revenue Share by Category")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q13 — First and Last Order per Customer  
    **Concept:** `FIRST_VALUE()` and `LAST_VALUE()` window functions  
    For each customer we find the date and amount of their very first and very last orders.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        WITH order_detail AS (SELECT o.customer_id, o.order_date, ROUND(SUM(oi.sales_amount), 2) AS order_total FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.customer_id, o.order_id, o.order_date), windowed AS (SELECT customer_id, FIRST_VALUE(order_date) OVER w AS first_order_date, FIRST_VALUE(order_total) OVER w AS first_order_amount, LAST_VALUE(order_date) OVER(PARTITION BY customer_id ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_order_date, LAST_VALUE(order_total) OVER(PARTITION BY customer_id ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_order_amount FROM order_detail WINDOW w AS (PARTITION BY customer_id ORDER BY order_date))
        SELECT DISTINCT
            customer_id,
            first_order_date,
            first_order_amount,
            last_order_date,
            last_order_amount
        FROM windowed
        ORDER BY customer_id
        LIMIT 15;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q14 — Average Days Between Consecutive Orders per Customer  
    **Concept:** `LAG()` for gap analysis  
    Using LAG to compute the gap (in days) between consecutive orders for each customer,
    then averaging those gaps.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        WITH ordered AS (SELECT customer_id, order_date, LAG(order_date) OVER(PARTITION BY customer_id ORDER BY order_date) AS prev_order_date FROM orders), gaps AS (SELECT customer_id, DATEDIFF('day', prev_order_date, order_date) AS days_between FROM ordered WHERE prev_order_date IS NOT NULL)
        SELECT
            customer_id,
            COUNT(*) AS num_gaps,
            ROUND(AVG(days_between), 1) AS avg_days_between,
            MIN(days_between) AS min_gap,
            MAX(days_between) AS max_gap
        FROM gaps
        GROUP BY customer_id
        ORDER BY avg_days_between
        LIMIT 15;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q15 — Country + Segment Revenue Ranking  
    **Concept:** Multiple CTEs + `DENSE_RANK` — complex ranking  
    We rank every (country, segment) combination by revenue and identify the top performer
    in each country.
    """)
    return


@app.cell
def _(con, mo):
    df_11 = mo.sql(
        f"""
        WITH segment_rev AS (SELECT c.country, c.customer_segment, ROUND(SUM(oi.sales_amount), 2) AS segment_revenue FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id GROUP BY c.country, c.customer_segment), ranked AS (SELECT *, DENSE_RANK() OVER(PARTITION BY country ORDER BY segment_revenue DESC) AS segment_rank FROM segment_rev)
        SELECT
            country,
            customer_segment,
            segment_revenue,
            segment_rank
        FROM ranked
        WHERE segment_rank <= 3
        ORDER BY
            country,
            segment_rank;
        """,
        engine=con
    )
    return (df_11,)


@app.cell
def _(df_11, plot_grouped_bar):
    plot_grouped_bar(df_11, "country", "segment_revenue", "customer_segment",
                     title="Top 3 Segments by Revenue per Country",
                     xlabel="Country", ylabel="Revenue ($)", rotate_x=30)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## DuckDB MACROs

    DuckDB supports **MACROs** — reusable SQL functions stored in the database.
    They simplify repetitive queries and promote consistency.

    > **Note:** Since we opened the database in read-only mode, we create these macros
    > as temporary (`TEMP`) macros that live for the duration of this session.
    > In a read-write connection you could omit `TEMP` to persist them.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### MACRO 1 — `customer_lifetime_value(cid)`
    **Justification:** Computing a customer's total lifetime spending is a very common
    analytical operation. Wrapping it in a macro means any analyst can call
    `customer_lifetime_value(42)` instead of writing a multi-table join every time.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        CREATE OR REPLACE TEMP MACRO customer_lifetime_value(cid) AS (SELECT ROUND(COALESCE(SUM(oi.sales_amount), 0), 2) FROM orders o JOIN order_items oi ON o.order_id = oi.order_id WHERE o.customer_id = cid);
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    df_12 = mo.sql(
        f"""
        SELECT
            customer_id,
            customer_lifetime_value(customer_id) AS lifetime_value
        FROM customers
        WHERE customer_id <= 10
        ORDER BY customer_id;
        """,
        engine=con
    )
    return (df_12,)


@app.cell
def _(df_12, plot_bar):
    plot_bar(df_12, "customer_id", "lifetime_value",
            title="Lifetime Value — Customers 1-10",
            xlabel="Customer ID", ylabel="Lifetime Value ($)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### MACRO 2 — `category_revenue_in_year(cat, yr)`
    **Justification:** Analysts frequently need to pull revenue for a specific category
    in a specific year. This macro encapsulates the date filtering and aggregation
    so the call becomes a simple two-argument function.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        CREATE OR REPLACE TEMP MACRO category_revenue_in_year(cat, yr) AS (SELECT ROUND(COALESCE(SUM(oi.sales_amount), 0), 2) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE oi.category = cat AND EXTRACT(YEAR FROM o.order_date) = yr);
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    df_13 = mo.sql(
        f"""
        SELECT
            2021 AS year,
            category_revenue_in_year('Electronics', 2021) AS revenue
        UNION ALL
        SELECT
            2022,
            category_revenue_in_year('Electronics', 2022)
        UNION ALL
        SELECT
            2023,
            category_revenue_in_year('Electronics', 2023)
        UNION ALL
        SELECT
            2024,
            category_revenue_in_year('Electronics', 2024);
        """,
        engine=con
    )
    return (df_13,)


@app.cell
def _(df_13, plot_bar):
    plot_bar(df_13, "year", "revenue",
            title="Electronics Revenue by Year (via MACRO)",
            xlabel="Year", ylabel="Revenue ($)")
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

