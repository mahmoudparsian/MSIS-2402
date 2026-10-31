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
    # Shopify Sales Data — SQL Analysis Notebook

    This notebook queries the `shopify_sales.duckdb` database created in the setup notebook.

    **Prerequisites:** Run `01_data_setup_marimo.py` first to create the database.

    **Structure:**
    - **5 Basic Queries** — Simple SELECT, COUNT, filtering
    - **10 Basic+ Queries** — GROUP BY, ORDER BY, aggregations, CASE
    - **10 Intermediate Queries** — Subqueries, JOINs, date functions, analytics
    - **5 Ranking Function Queries** — WITH (CTEs) and window/ranking functions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup: Connect to Database & Import Plotting
    """)
    return


@app.cell
def _():
    import duckdb
    import pandas as pd
    import warnings
    warnings.filterwarnings('ignore')

    # Import our plotting helper module
    from plot_utils import (
        plot_bar, plot_horizontal_bar, plot_line,
        plot_pie, plot_grouped_bar, plot_heatmap,
        plot_scatter, plot_stacked_bar
    )

    # Connect to the DuckDB database (read-only to prevent accidental changes)
    con = duckdb.connect('shopify_sales.duckdb', read_only=True)

    # Quick check
    row_count = con.execute("SELECT COUNT(*) FROM sales").fetchall()[0][0]
    print(f"Connected to shopify_sales.duckdb — {row_count:,} rows in sales table")

    # Helper: run a query and return a DataFrame
    def q(sql):
        return con.execute(sql).fetchdf()

    return con, plot_bar, plot_grouped_bar, plot_heatmap, plot_horizontal_bar, plot_line, plot_pie, q


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Section 1: Basic Queries (5)

    Simple queries using SELECT, WHERE, LIMIT, COUNT, and basic filtering.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic Query 1: Preview the Data

    **What are we doing?** We retrieve the first 10 rows from the `sales` table to get a quick look at the data structure, column names, and sample values. This is always the first step in any data exploration.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT *
        FROM sales
        LIMIT 10
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic Query 2: Count Total Orders

    **What are we doing?** We count the total number of orders in our dataset. This gives us the scale of the data we're working with. We also count distinct customers and distinct products to understand the breadth of the dataset.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            COUNT(*) AS total_orders,
            COUNT(DISTINCT customer_id) AS unique_customers,
            COUNT(DISTINCT product_id) AS unique_products
        FROM sales
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic Query 3: Orders from the USA

    **What are we doing?** We filter the sales table to show only orders placed by customers in the USA, limited to 10 rows. The `WHERE` clause filters rows based on a condition.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            order_id,
            order_date,
            customer_id,
            product_category,
            revenue,
            customer_country
        FROM sales
        WHERE customer_country = 'USA'
        LIMIT 10
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic Query 4: High-Value Orders (Revenue > $5,000)

    **What are we doing?** We find orders where the total revenue exceeds $5,000, sorted from highest to lowest. This helps identify the most valuable individual transactions.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            order_id,
            order_date,
            product_category,
            quantity,
            product_price,
            discount_percent,
            revenue
        FROM sales
        WHERE revenue > 3000
        ORDER BY revenue DESC
        LIMIT 15
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic Query 5: Distinct Product Categories

    **What are we doing?** We list all unique product categories in the dataset. This helps us understand what types of products are sold and is essential for later grouping analysis.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT DISTINCT product_category
        FROM sales
        ORDER BY product_category
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Section 2: Basic+ Queries (10)

    Queries using GROUP BY, ORDER BY, aggregate functions (SUM, AVG, MIN, MAX), HAVING, CASE, and BETWEEN.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic+ Query 1: Total Revenue by Product Category

    **What are we doing?** We group all orders by product category and calculate the total revenue, total number of orders, and average order value for each. This reveals which categories drive the most revenue.
    """)
    return


@app.cell
def _(con, mo):
    df = mo.sql(
        f"""
        SELECT
            product_category,
            COUNT(*) AS total_orders,
            SUM(revenue) AS total_revenue,
            ROUND(AVG(revenue), 2) AS avg_order_value
        FROM sales
        GROUP BY product_category
        ORDER BY total_revenue DESC
        """,
        engine=con
    )
    return (df,)


@app.cell
def _(df, plot_bar):
    # Plot: Revenue by Category
    plot_bar(df, 'product_category', 'total_revenue',
             title='Total Revenue by Product Category',
             xlabel='Category', ylabel='Total Revenue',
             rotate_x=45, fmt_currency=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic+ Query 2: Orders by Customer Country

    **What are we doing?** We count how many orders came from each country and calculate each country's share of total revenue. This shows the geographic distribution of sales.
    """)
    return


@app.cell
def _(con, mo):
    df_2 = mo.sql(
        f"""
        SELECT
            customer_country,
            COUNT(*) AS order_count,
            SUM(revenue) AS total_revenue,
            ROUND(AVG(revenue), 2) AS avg_revenue
        FROM sales
        GROUP BY customer_country
        ORDER BY total_revenue DESC
        """,
        engine=con
    )
    return (df_2,)


@app.cell
def _(df_2, plot_pie):
    # Plot: Orders by Country
    plot_pie(df_2, 'customer_country', 'order_count',
             title='Order Distribution by Country')

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic+ Query 3: Revenue by Payment Method

    **What are we doing?** We analyze which payment methods are most popular and which generate the most revenue. This helps understand customer payment preferences.
    """)
    return


@app.cell
def _(con, mo):
    df_3 = mo.sql(
        f"""
        SELECT
            payment_method,
            COUNT(*) AS order_count,
            SUM(revenue) AS total_revenue,
            ROUND(AVG(revenue), 2) AS avg_revenue
        FROM sales
        GROUP BY payment_method
        ORDER BY total_revenue DESC
        """,
        engine=con
    )
    return (df_3,)


@app.cell
def _(df_3, plot_bar):
    # Plot: Revenue by Payment Method
    plot_bar(df_3, 'payment_method', 'total_revenue',
             title='Total Revenue by Payment Method',
             xlabel='Payment Method', ylabel='Revenue',
             fmt_currency=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic+ Query 4: Average Discount by Category

    **What are we doing?** We calculate the average discount percentage offered in each product category. This shows which categories rely more on discounting to drive sales.
    """)
    return


@app.cell
def _(con, mo):
    df_4 = mo.sql(
        f"""
        SELECT
            product_category,
            ROUND(AVG(discount_percent), 2) AS avg_discount_pct,
            ROUND(MIN(discount_percent), 2) AS min_discount,
            ROUND(MAX(discount_percent), 2) AS max_discount
        FROM sales
        GROUP BY product_category
        ORDER BY avg_discount_pct DESC
        """,
        engine=con
    )
    return (df_4,)


@app.cell
def _(df_4, plot_bar):
    # Plot: Average Discount by Category
    plot_bar(df_4, 'product_category', 'avg_discount_pct',
             title='Average Discount % by Product Category',
             xlabel='Category', ylabel='Avg Discount %',
             rotate_x=45)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic+ Query 5: Traffic Source Performance

    **What are we doing?** We analyze how different traffic sources (Paid Ads, Email, Social Media, etc.) contribute to orders and revenue. This is key for marketing ROI decisions.
    """)
    return


@app.cell
def _(con, mo):
    df_5 = mo.sql(
        f"""
        SELECT
            traffic_source,
            COUNT(*) AS order_count,
            SUM(revenue) AS total_revenue,
            ROUND(AVG(revenue), 2) AS avg_revenue,
            ROUND(AVG(rating), 2) AS avg_rating
        FROM sales
        GROUP BY traffic_source
        ORDER BY total_revenue DESC
        """,
        engine=con
    )
    return (df_5,)


@app.cell
def _(df_5, plot_bar):
    # Plot: Revenue by Traffic Source
    plot_bar(df_5, 'traffic_source', 'total_revenue',
             title='Total Revenue by Traffic Source',
             xlabel='Traffic Source', ylabel='Revenue',
             rotate_x=45, fmt_currency=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic+ Query 6: Return Rate by Category

    **What are we doing?** We calculate the return rate (percentage of orders returned) for each product category. High return rates may indicate quality or sizing issues.
    """)
    return


@app.cell
def _(con, mo):
    df_6 = mo.sql(
        f"""
        SELECT
            product_category,
            COUNT(*) AS total_orders,
            SUM(is_returned) AS returned_orders,
            ROUND(100.0 * SUM(is_returned) / COUNT(*), 2) AS return_rate_pct
        FROM sales
        GROUP BY product_category
        ORDER BY return_rate_pct DESC
        """,
        engine=con
    )
    return (df_6,)


@app.cell
def _(df_6, plot_bar):
    # Plot: Return Rate by Category
    plot_bar(df_6, 'product_category', 'return_rate_pct',
             title='Return Rate (%) by Product Category',
             xlabel='Category', ylabel='Return Rate %',
             rotate_x=45)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic+ Query 7: Revenue Buckets Using CASE

    **What are we doing?** We use a `CASE` expression to classify each order into revenue buckets (Low, Medium, High, Premium). This helps understand the distribution of order sizes.
    """)
    return


@app.cell
def _(con, mo):
    df_7 = mo.sql(
        f"""
        SELECT
            CASE WHEN revenue < 200 THEN '1. Low (<$200)' WHEN revenue < 1000 THEN '2. Medium ($200-$999)' WHEN revenue < 3000 THEN '3. High ($1K-$2,999)' ELSE '4. Premium ($3K+)' END AS revenue_bucket,
            COUNT(*) AS order_count,
            ROUND(AVG(revenue), 2) AS avg_revenue,
            SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY revenue_bucket
        ORDER BY revenue_bucket
        """,
        engine=con
    )
    return (df_7,)


@app.cell
def _(df_7, plot_bar):
    # Plot: Order Count by Revenue Bucket
    plot_bar(df_7, 'revenue_bucket', 'order_count',
             title='Number of Orders by Revenue Bucket',
             xlabel='Revenue Bucket', ylabel='Order Count')

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic+ Query 8: Top 10 Customers by Total Spending

    **What are we doing?** We identify the top 10 customers who have spent the most in total across all their orders. These are the most valuable customers (VIPs).
    """)
    return


@app.cell
def _(con, mo):
    df_8 = mo.sql(
        f"""
        SELECT
            customer_id,
            COUNT(*) AS total_orders,
            SUM(revenue) AS total_spent,
            ROUND(AVG(revenue), 2) AS avg_order_value
        FROM sales
        GROUP BY customer_id
        ORDER BY total_spent DESC
        LIMIT 10
        """,
        engine=con
    )
    return (df_8,)


@app.cell
def _(df_8, plot_bar):
    # Plot: Top 10 Customers
    plot_bar(df_8, 'customer_id', 'total_spent',
             title='Top 10 Customers by Total Spending',
             xlabel='Customer ID', ylabel='Total Spent',
             fmt_currency=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic+ Query 9: Categories with Average Revenue Above $1,000 (HAVING)

    **What are we doing?** We use `HAVING` to filter groups after aggregation. Unlike `WHERE` (which filters individual rows), `HAVING` filters groups based on aggregate values. Here we find categories whose average order revenue exceeds $1,000.
    """)
    return


@app.cell
def _(con, mo):
    df_9 = mo.sql(
        f"""
        SELECT
            product_category,
            COUNT(*) AS order_count,
            ROUND(AVG(revenue), 2) AS avg_revenue,
            SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY product_category
        HAVING AVG(revenue) > 800
        ORDER BY avg_revenue DESC
        """,
        engine=con
    )
    return (df_9,)


@app.cell
def _(df_9, plot_bar):
    # Plot: Categories with High Average Revenue
    plot_bar(df_9, 'product_category', 'avg_revenue',
             title='Categories with Avg Revenue > $800',
             xlabel='Category', ylabel='Avg Revenue',
             rotate_x=45, fmt_currency=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic+ Query 10: Shipping Cost Analysis by Country

    **What are we doing?** We calculate the average, minimum, and maximum shipping costs for each country. This reveals geographic cost differences in fulfillment.
    """)
    return


@app.cell
def _(con, mo):
    df_10 = mo.sql(
        f"""
        SELECT
            customer_country,
            COUNT(*) AS order_count,
            ROUND(AVG(shipping_cost), 2) AS avg_shipping,
            ROUND(MIN(shipping_cost), 2) AS min_shipping,
            ROUND(MAX(shipping_cost), 2) AS max_shipping,
            ROUND(SUM(shipping_cost), 2) AS total_shipping
        FROM sales
        GROUP BY customer_country
        ORDER BY avg_shipping DESC
        """,
        engine=con
    )
    return (df_10,)


@app.cell
def _(df_10, plot_bar):
    # Plot: Average Shipping Cost by Country
    plot_bar(df_10, 'customer_country', 'avg_shipping',
             title='Average Shipping Cost by Country',
             xlabel='Country', ylabel='Avg Shipping Cost ($)',
             fmt_currency=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Section 3: Intermediate Queries (10)

    Queries using date functions, subqueries, multi-level aggregations, correlation analysis, and more complex analytics.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Intermediate Query 1: Monthly Revenue Trend

    **What are we doing?** We extract the year and month from `order_date` and calculate the total revenue and order count for each month. This time-series view reveals seasonal patterns and growth trends.
    """)
    return


@app.cell
def _(q):
    _sql = """
    SELECT EXTRACT(YEAR FROM order_date)  AS year,
           EXTRACT(MONTH FROM order_date) AS month,
           COUNT(*)                       AS order_count,
           ROUND(SUM(revenue), 2)         AS monthly_revenue
    FROM   sales
    GROUP BY year, month
    ORDER BY year, month
    """

    df_11 = q(_sql)
    df_11['period'] = df_11['year'].astype(int).astype(str) + '-' + df_11['month'].astype(int).astype(str).str.zfill(2)
    df_11

    return (df_11,)


@app.cell
def _(df_11, plot_line):
    # Plot: Monthly Revenue Trend
    plot_line(df_11, 'period', 'monthly_revenue',
              title='Monthly Revenue Trend',
              xlabel='Month', ylabel='Revenue',
              fmt_currency=True, figsize=(14, 6))

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Intermediate Query 2: Year-over-Year Revenue Comparison

    **What are we doing?** We compare total revenue across years to measure business growth. This high-level view shows whether the business is growing, stable, or declining.
    """)
    return


@app.cell
def _(con, mo):
    df_12 = mo.sql(
        f"""
        SELECT
            EXTRACT(YEAR FROM order_date) AS year,
            COUNT(*) AS total_orders,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(AVG(revenue), 2) AS avg_order_value,
            ROUND(SUM(profit), 2) AS total_profit
        FROM sales
        GROUP BY year
        ORDER BY year
        """,
        engine=con
    )
    return (df_12,)


@app.cell
def _(df_12, plot_grouped_bar):
    # Plot: Year-over-Year Revenue
    plot_grouped_bar(df_12, 'year', ['total_revenue', 'total_profit'],
                     title='Year-over-Year: Revenue vs. Profit',
                     xlabel='Year', ylabel='Amount ($)',
                     fmt_currency=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Intermediate Query 3: Category Revenue by Country (Cross-Tab)

    **What are we doing?** We create a cross-tabulation showing revenue broken down by both category and country. This reveals which categories perform best in which markets — essential for localized marketing.
    """)
    return


@app.cell
def _(q):
    _sql = """
    SELECT product_category,
           customer_country,
           COUNT(*)               AS orders,
           ROUND(SUM(revenue), 2) AS total_revenue
    FROM   sales
    GROUP BY product_category, customer_country
    ORDER BY product_category, total_revenue DESC
    """

    _df = q(_sql)
    pivot = _df.pivot_table(index='product_category', columns='customer_country',
                           values='total_revenue', fill_value=0)
    pivot

    return (pivot,)


@app.cell
def _(pivot, plot_heatmap):
    # Plot: Heatmap of Category × Country Revenue
    plot_heatmap(pivot,
                 title='Revenue Heatmap: Category × Country',
                 fmt=',.0f', figsize=(12, 8))

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Intermediate Query 4: Discount Impact on Revenue

    **What are we doing?** We group orders by discount percentage to see how discounting affects average revenue and return rates. Do heavier discounts drive more volume? Do they increase returns?
    """)
    return


@app.cell
def _(con, mo):
    df_13 = mo.sql(
        f"""
        SELECT
            discount_percent,
            COUNT(*) AS order_count,
            ROUND(AVG(revenue), 2) AS avg_revenue,
            ROUND(AVG(quantity), 2) AS avg_quantity,
            ROUND(100.0 * SUM(is_returned) / COUNT(*), 2) AS return_rate_pct
        FROM sales
        GROUP BY discount_percent
        ORDER BY discount_percent
        """,
        engine=con
    )
    return (df_13,)


@app.cell
def _(df_13, plot_line):
    # Plot: Avg Revenue vs. Discount
    plot_line(df_13, 'discount_percent', 'avg_revenue',
              title='Average Revenue by Discount Percentage',
              xlabel='Discount %', ylabel='Avg Revenue ($)',
              fmt_currency=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Intermediate Query 5: Repeat vs. One-Time Customers

    **What are we doing?** We identify which customers placed more than one order (repeat buyers) vs. those who only bought once. Repeat customer rate is a key loyalty metric.
    """)
    return


@app.cell
def _(con, mo):
    df_14 = mo.sql(
        f"""
        WITH customer_orders AS (SELECT customer_id, COUNT(*) AS order_count FROM sales GROUP BY customer_id)
        SELECT
            CASE WHEN order_count = 1 THEN 'One-Time' WHEN order_count BETWEEN 2 AND 3 THEN '2-3 Orders' WHEN order_count BETWEEN 4 AND 5 THEN '4-5 Orders' ELSE '6+ Orders' END AS customer_segment,
            COUNT(*) AS num_customers,
            SUM(order_count) AS total_orders
        FROM customer_orders
        GROUP BY customer_segment
        ORDER BY customer_segment
        """,
        engine=con
    )
    return (df_14,)


@app.cell
def _(df_14, plot_pie):
    # Plot: Customer Segments
    plot_pie(df_14, 'customer_segment', 'num_customers',
             title='Customer Segments by Order Frequency')

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Intermediate Query 6: Day-of-Week Sales Pattern

    **What are we doing?** We extract the day of the week from `order_date` to see if there are patterns — do people buy more on weekends or weekdays? We use DuckDB's `dayname()` function.
    """)
    return


@app.cell
def _(con, mo):
    df_15 = mo.sql(
        f"""
        SELECT
            dayname(order_date) AS day_of_week,
            EXTRACT(DOW FROM order_date) AS day_num,
            COUNT(*) AS order_count,
            ROUND(SUM(revenue), 2) AS total_revenue
        FROM sales
        GROUP BY
            day_of_week,
            day_num
        ORDER BY day_num
        """,
        engine=con
    )
    return (df_15,)


@app.cell
def _(df_15, plot_bar):
    # Plot: Orders by Day of Week
    plot_bar(df_15, 'day_of_week', 'order_count',
             title='Order Count by Day of the Week',
             xlabel='Day', ylabel='Orders')

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Intermediate Query 7: Profit Margin by Category

    **What are we doing?** We calculate the profit margin (profit as a percentage of revenue) for each product category. This shows which categories are most profitable, not just highest revenue.
    """)
    return


@app.cell
def _(con, mo):
    df_16 = mo.sql(
        f"""
        SELECT
            product_category,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(SUM(profit), 2) AS total_profit,
            ROUND(100.0 * SUM(profit) / NULLIF(SUM(revenue), 0), 2) AS profit_margin_pct
        FROM sales
        GROUP BY product_category
        ORDER BY profit_margin_pct DESC
        """,
        engine=con
    )
    return (df_16,)


@app.cell
def _(df_16, plot_bar):
    # Plot: Profit Margin by Category
    plot_bar(df_16, 'product_category', 'profit_margin_pct',
             title='Profit Margin (%) by Product Category',
             xlabel='Category', ylabel='Profit Margin %',
             rotate_x=45)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Intermediate Query 8: Average Rating by Category and Return Status

    **What are we doing?** We compare the average customer rating for returned vs. non-returned orders within each category. This helps determine if low ratings correlate with returns.
    """)
    return


@app.cell
def _(con, mo):
    df_17 = mo.sql(
        f"""
        SELECT
            product_category,
            CASE WHEN is_returned = 1 THEN 'Returned' ELSE 'Not Returned' END AS return_status,
            COUNT(*) AS order_count,
            ROUND(AVG(rating), 2) AS avg_rating
        FROM sales
        GROUP BY
            product_category,
            return_status
        ORDER BY
            product_category,
            return_status
        """,
        engine=con
    )
    if hasattr(df_17, "to_pandas"):
        df_17 = df_17.to_pandas()
    return (df_17,)


@app.cell
def _(df_17, plot_grouped_bar):
    # Plot: Grouped bar — avg rating by category and return status
    _pivot = df_17.pivot_table(index='product_category', columns='return_status',
                           values='avg_rating', fill_value=0)
    plot_grouped_bar(_pivot.reset_index(), 'product_category',
                     list(_pivot.columns),
                     title='Avg Rating: Returned vs. Not Returned by Category',
                     xlabel='Category', ylabel='Average Rating',
                     figsize=(12, 6))

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Intermediate Query 9: Revenue Contribution — Top 20% of Products (Pareto)

    **What are we doing?** We apply the Pareto principle (80/20 rule) to find which products generate the majority of revenue. We rank products by revenue and identify the top 20%.
    """)
    return


@app.cell
def _(con, mo):
    df_18 = mo.sql(
        f"""
        WITH product_revenue AS (SELECT product_id, product_category, SUM(revenue) AS total_revenue FROM sales GROUP BY product_id, product_category), ranked AS (SELECT *, ROW_NUMBER() OVER(ORDER BY total_revenue DESC) AS rank, COUNT(*) OVER() AS total_products FROM product_revenue)
        SELECT
            rank,
            product_id,
            product_category,
            ROUND(total_revenue, 2) AS total_revenue,
            total_products
        FROM ranked
        WHERE rank <= CEIL(total_products * 0.2)
        ORDER BY rank
        LIMIT 20
        """,
        engine=con
    )
    return (df_18,)


@app.cell
def _(df_18, plot_horizontal_bar):
    # Plot: Top 20 Products by Revenue
    plot_horizontal_bar(df_18.head(20), 'total_revenue', 'product_id',
                        title='Top 20 Products by Revenue (Pareto Analysis)',
                        xlabel='Total Revenue', ylabel='Product ID',
                        fmt_currency=True, figsize=(10, 8))

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Intermediate Query 10: Quarterly Sales Summary

    **What are we doing?** We aggregate sales by quarter to see broader seasonal trends. Quarterly views smooth out monthly noise and are commonly used in business reporting.
    """)
    return


@app.cell
def _(q):
    _sql = """
    SELECT EXTRACT(YEAR FROM order_date)    AS year,
           EXTRACT(QUARTER FROM order_date) AS quarter,
           COUNT(*)                         AS order_count,
           ROUND(SUM(revenue), 2)          AS total_revenue,
           ROUND(SUM(profit), 2)           AS total_profit,
           ROUND(AVG(discount_percent), 2) AS avg_discount
    FROM   sales
    GROUP BY year, quarter
    ORDER BY year, quarter
    """

    df_19 = q(_sql)
    df_19['period'] = df_19['year'].astype(int).astype(str) + '-Q' + df_19['quarter'].astype(int).astype(str)
    df_19

    return (df_19,)


@app.cell
def _(df_19, plot_line):
    # Plot: Quarterly Revenue
    plot_line(df_19, 'period', 'total_revenue',
              title='Quarterly Revenue Trend',
              xlabel='Quarter', ylabel='Revenue',
              fmt_currency=True, figsize=(14, 6))

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Section 4: Ranking Function Queries (5)

    Advanced queries using Common Table Expressions (WITH / CTEs) combined with window/ranking functions: `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `NTILE()`, and `PERCENT_RANK()`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ranking Query 1: Top 3 Products per Category by Revenue (ROW_NUMBER)

    **What are we doing?** We use a CTE with `ROW_NUMBER()` to rank products within each category by total revenue, then select only the top 3 per category. This is a classic "Top-N per group" pattern.

    **Key Concept — ROW_NUMBER():** Assigns a unique sequential number to each row within a partition. Ties get different numbers (arbitrary tiebreak).
    """)
    return


@app.cell
def _(con, mo):
    df_20 = mo.sql(
        f"""
        WITH product_category_revenue AS (SELECT product_category, product_id, SUM(revenue) AS total_revenue, COUNT(*) AS order_count, ROW_NUMBER() OVER(PARTITION BY product_category ORDER BY SUM(revenue) DESC) AS rn FROM sales GROUP BY product_category, product_id)
        SELECT
            product_category,
            product_id,
            ROUND(total_revenue, 2) AS total_revenue,
            order_count,
            rn AS rank_in_category
        FROM product_category_revenue
        WHERE rn <= 3
        ORDER BY
            product_category,
            rn
        """,
        engine=con
    )
    return (df_20,)


@app.cell
def _(df_20, plot_horizontal_bar):
    # Plot: Top 3 Products per Category
    plot_horizontal_bar(df_20, 'total_revenue', 'product_id',
                        title='Top 3 Products per Category by Revenue',
                        xlabel='Total Revenue', ylabel='Product ID',
                        fmt_currency=True, figsize=(10, 10))

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ranking Query 2: Country Revenue Ranking with RANK and DENSE_RANK

    **What are we doing?** We compare `RANK()` and `DENSE_RANK()` side by side on country-level revenue.

    **Key Concepts:**
    - **RANK():** If two rows tie, both get the same rank and the next rank is skipped (e.g., 1, 2, 2, 4).
    - **DENSE_RANK():** If two rows tie, both get the same rank but the next rank is NOT skipped (e.g., 1, 2, 2, 3).
    """)
    return


@app.cell
def _(con, mo):
    df_21 = mo.sql(
        f"""
        WITH country_stats AS (SELECT customer_country, COUNT(*) AS total_orders, SUM(revenue) AS total_revenue, AVG(revenue) AS avg_order_value FROM sales GROUP BY customer_country)
        SELECT
            customer_country,
            total_orders,
            ROUND(total_revenue, 2) AS total_revenue,
            ROUND(avg_order_value, 2) AS avg_order_value,
            RANK() OVER(ORDER BY total_revenue DESC) AS rank_val,
            DENSE_RANK() OVER(ORDER BY total_revenue DESC) AS dense_rank_val
        FROM country_stats
        ORDER BY rank_val
        """,
        engine=con
    )
    return (df_21,)


@app.cell
def _(df_21, plot_bar):
    # Plot: Country Revenue Ranking
    plot_bar(df_21, 'customer_country', 'total_revenue',
             title='Country Revenue Ranking (RANK vs DENSE_RANK)',
             xlabel='Country', ylabel='Total Revenue',
             fmt_currency=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ranking Query 3: Customer Spending Quartiles (NTILE)

    **What are we doing?** We use `NTILE(4)` to divide all customers into 4 equal quartiles based on total spending. Quartile 1 = top 25% spenders, Quartile 4 = bottom 25%. This is useful for customer segmentation.

    **Key Concept — NTILE(n):** Distributes rows into `n` roughly equal-sized buckets. Useful for percentile-based segmentation.
    """)
    return


@app.cell
def _(con, mo):
    df_22 = mo.sql(
        f"""
        WITH customer_spending AS (SELECT customer_id, SUM(revenue) AS total_spent, COUNT(*) AS order_count, NTILE(4) OVER(ORDER BY SUM(revenue) DESC) AS spending_quartile FROM sales GROUP BY customer_id)
        SELECT
            spending_quartile,
            COUNT(*) AS num_customers,
            ROUND(MIN(total_spent), 2) AS min_spent,
            ROUND(AVG(total_spent), 2) AS avg_spent,
            ROUND(MAX(total_spent), 2) AS max_spent,
            ROUND(SUM(total_spent), 2) AS quartile_total
        FROM customer_spending
        GROUP BY spending_quartile
        ORDER BY spending_quartile
        """,
        engine=con
    )
    return (df_22,)


@app.cell
def _(df_22, plot_bar):
    # Plot: Quartile Spending Distribution
    plot_bar(df_22, 'spending_quartile', 'quartile_total',
             title='Total Spending by Customer Quartile (NTILE)',
             xlabel='Quartile (1=Top, 4=Bottom)', ylabel='Total Spending',
             fmt_currency=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ranking Query 4: Running Total of Monthly Revenue (Cumulative SUM)

    **What are we doing?** We compute a **running (cumulative) total** of monthly revenue using `SUM() OVER (ORDER BY ...)`. This shows how revenue accumulates over time — useful for tracking progress toward annual targets.

    **Key Concept — Window Frame:** `SUM(revenue) OVER (ORDER BY month)` creates a running total from the first row to the current row (default frame: `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`).
    """)
    return


@app.cell
def _(q):
    _sql = """
    WITH monthly AS (
        SELECT DATE_TRUNC('month', order_date) AS month,
               SUM(revenue)                    AS monthly_revenue,
               SUM(profit)                     AS monthly_profit
        FROM   sales
        GROUP BY month
    )
    SELECT month,
           ROUND(monthly_revenue, 2)  AS monthly_revenue,
           ROUND(SUM(monthly_revenue) OVER (
               ORDER BY month
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ), 2)                       AS cumulative_revenue,
           ROUND(monthly_profit, 2)   AS monthly_profit,
           ROUND(SUM(monthly_profit) OVER (
               ORDER BY month
           ), 2)                       AS cumulative_profit
    FROM   monthly
    ORDER BY month
    """

    df_23 = q(_sql)
    df_23['month'] = df_23['month'].astype(str).str[:7]
    df_23

    return (df_23,)


@app.cell
def _(df_23, plot_line):
    # Plot: Cumulative Revenue Over Time
    plot_line(df_23, 'month', ['monthly_revenue', 'cumulative_revenue'],
              title='Monthly vs. Cumulative Revenue',
              xlabel='Month', ylabel='Revenue ($)',
              fmt_currency=True, figsize=(14, 6))

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Ranking Query 5: Percent Rank of Products by Profit (PERCENT_RANK)

    **What are we doing?** We use `PERCENT_RANK()` to calculate each product's relative position in terms of total profit. A percent rank of 0.95 means the product is more profitable than 95% of all products.

    **Key Concept — PERCENT_RANK():** Returns a value between 0 and 1 representing the relative standing of a row: `(rank - 1) / (total_rows - 1)`.
    """)
    return


@app.cell
def _(con, mo):
    df_24 = mo.sql(
        f"""
        WITH product_profit AS (SELECT product_id, product_category, SUM(profit) AS total_profit, SUM(revenue) AS total_revenue, COUNT(*) AS order_count, PERCENT_RANK() OVER(ORDER BY SUM(profit)) AS pct_rank FROM sales GROUP BY product_id, product_category)
        SELECT
            product_id,
            product_category,
            ROUND(total_profit, 2) AS total_profit,
            ROUND(total_revenue, 2) AS total_revenue,
            order_count,
            ROUND(pct_rank, 4) AS percentile_rank
        FROM product_profit
        WHERE pct_rank >= 0.95
        ORDER BY pct_rank DESC
        LIMIT 15
        """,
        engine=con
    )
    return (df_24,)


@app.cell
def _(df_24, plot_horizontal_bar):
    # Plot: Top Percentile Products
    plot_horizontal_bar(df_24, 'total_profit', 'product_id',
                        title='Top 5% Products by Profit (PERCENT_RANK >= 0.95)',
                        xlabel='Total Profit', ylabel='Product ID',
                        fmt_currency=True, figsize=(10, 8))

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Closing: Disconnect
    """)
    return


@app.cell
def _(con):
    # Close the database connection
    con.close()
    print("Database connection closed. Analysis complete!")

    return


if __name__ == "__main__":
    app.run()

