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
    # Notebook 2: Citi Bike SQL Analysis with DuckDB

    This notebook runs **30 SQL queries** against the `citibike.duckdb` database built in Notebook 1.

    | Section | Count | Concepts |
    |---------|-------|----------|
    | Basic Queries | 5 | SELECT, WHERE, ORDER BY, LIMIT, COUNT, DISTINCT |
    | Basic+ Queries | 10 | GROUP BY, aggregate functions, HAVING, BETWEEN, LIKE, CASE |
    | Intermediate Queries | 10 | Subqueries, JOINs, window functions, time analytics, CTEs |
    | Ranking Queries | 5 | WITH (CTEs), ROW_NUMBER, RANK, DENSE_RANK, NTILE, PERCENT_RANK |

    Each query cell includes:
    1. **Explanation** of what we're doing and why
    2. **SQL query** (nicely formatted)
    3. **Result** displayed as a table
    4. **Plot** when appropriate (in a separate cell, powered by `plot_helpers.py`)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup
    """)
    return


@app.cell
def _():
    import duckdb
    from plot_helpers import plot_age_group_duration, plot_cumulative_rides, plot_duration_distribution, plot_mom_growth, plot_monthly_trend_by_year, plot_most_used_bikes, plot_net_inflow, plot_peak_hours_per_day, plot_quartile_summary, plot_rides_per_day_of_week, plot_rides_per_gender, plot_rides_per_hour, plot_rides_per_month, plot_rides_per_user_type, plot_rides_per_year, plot_round_trip_vs_one_way, plot_top_end_stations, plot_top_routes, plot_top_start_stations, plot_top_stations_per_year, plot_weekday_vs_weekend
    # Connect to the database built in Notebook 1
    con = duckdb.connect('citibike.duckdb', read_only=True)

    # Quick check
    count = con.execute("SELECT COUNT(*) FROM rides").fetchall()[0][0]
    print(f'Connected to citibike.duckdb — {count:,} rides available')
    return con, plot_age_group_duration, plot_cumulative_rides, plot_duration_distribution, plot_mom_growth, plot_monthly_trend_by_year, plot_most_used_bikes, plot_net_inflow, plot_peak_hours_per_day, plot_quartile_summary, plot_rides_per_day_of_week, plot_rides_per_gender, plot_rides_per_hour, plot_rides_per_month, plot_rides_per_user_type, plot_rides_per_year, plot_round_trip_vs_one_way, plot_top_end_stations, plot_top_routes, plot_top_start_stations, plot_top_stations_per_year, plot_weekday_vs_weekend


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---
    # PART 1: Basic Queries (5)

    These queries introduce the fundamental SQL building blocks:  
    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `COUNT`, and `DISTINCT`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q1. Preview the First 10 Rides

    **What are we doing?**  
    We use `SELECT *` with `LIMIT` to peek at the data. This is always the first thing  
    you should do with a new table — get a feel for what the columns look like.

    **SQL concepts:** `SELECT`, `LIMIT`
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT *
        FROM rides
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q2. Count the Total Number of Rides

    **What are we doing?**  
    We use `COUNT(*)` to get the total number of rows in the table.  
    This tells us the overall size of our dataset.

    **SQL concepts:** `COUNT` aggregate function
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT COUNT(*) AS total_rides
        FROM rides;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q3. How Many Unique Bikes Are in the Fleet?

    **What are we doing?**  
    We use `COUNT(DISTINCT bike_id)` to find how many different bikes appear in the data.  
    This is different from `COUNT(*)` because the same bike can make thousands of trips.

    **SQL concepts:** `COUNT`, `DISTINCT`
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            COUNT(DISTINCT bike_id) AS unique_bikes,
            COUNT(DISTINCT start_station_id) AS unique_start_stations,
            COUNT(DISTINCT end_station_id) AS unique_end_stations
        FROM rides;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q4. Find the 10 Longest Rides by Duration

    **What are we doing?**  
    We sort all rides by `trip_duration_min` in descending order and take the top 10.  
    This is a classic **Top-N** query pattern.

    **SQL concepts:** `ORDER BY ... DESC`, `LIMIT`
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            bike_id,
            start_station_name,
            end_station_name,
            trip_duration_min,
            start_time
        FROM rides
        ORDER BY trip_duration_min DESC
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q5. Filter: Rides by Female Subscribers Only

    **What are we doing?**  
    We use `WHERE` with two conditions joined by `AND` to filter for  
    female riders who are subscribers. This shows how to combine filters.

    **SQL concepts:** `WHERE`, `AND`, multiple conditions
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            start_station_name,
            end_station_name,
            trip_duration_min,
            rider_age,
            start_time
        FROM rides
        WHERE
            gender = 'female'
            AND user_type = 'Subscriber'
        ORDER BY trip_duration_min DESC
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---
    # PART 2: Basic+ Queries (10)

    These queries build on the basics and introduce **aggregation**, **grouping**,  
    and **filtering on groups**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q6. Rides per User Type (Subscriber vs Customer)

    **What are we doing?**  
    We group rides by `user_type` and count how many rides each type took.  
    `GROUP BY` collapses all rows with the same user_type into one summary row.

    **SQL concepts:** `GROUP BY`, `COUNT`
    """)
    return


@app.cell
def _(con, mo):
    df = mo.sql(
        f"""
        SELECT
            user_type,
            COUNT(*) AS ride_count,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min
        FROM rides
        GROUP BY user_type
        ORDER BY ride_count DESC;
        """,
        engine=con
    )
    return (df,)


@app.cell
def _(df, plot_rides_per_user_type):
    plot_rides_per_user_type(df)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q7. Rides per Gender

    **What are we doing?**  
    We group by `gender` and compute the count and average duration for each group.  
    This lets us see how ride patterns differ across genders.

    **SQL concepts:** `GROUP BY`, `COUNT`, `AVG`, `ROUND`
    """)
    return


@app.cell
def _(con, mo):
    df_2 = mo.sql(
        f"""
        SELECT
            gender,
            COUNT(*) AS ride_count,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min,
            ROUND(AVG(distance_km), 3) AS avg_distance_km
        FROM rides
        GROUP BY gender
        ORDER BY ride_count DESC;
        """,
        engine=con
    )
    return (df_2,)


@app.cell
def _(df_2, plot_rides_per_gender):
    plot_rides_per_gender(df_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q8. Total Rides per Year

    **What are we doing?**  
    We group by `start_year` to see how ridership changed over the years.  
    This is a fundamental **time-series aggregation**.

    **SQL concepts:** `GROUP BY`, `ORDER BY`
    """)
    return


@app.cell
def _(con, mo):
    df_3 = mo.sql(
        f"""
        SELECT
            start_year,
            COUNT(*) AS ride_count,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min
        FROM rides
        GROUP BY start_year
        ORDER BY start_year;
        """,
        engine=con
    )
    return (df_3,)


@app.cell
def _(df_3, plot_rides_per_year):
    plot_rides_per_year(df_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q9. Rides per Month (All Years Combined)

    **What are we doing?**  
    By grouping on `start_month` we can see **seasonal patterns** — which months  
    are busiest for Citi Bike? We expect summer months to dominate.

    **SQL concepts:** `GROUP BY`, aggregate functions, seasonality analysis
    """)
    return


@app.cell
def _(con, mo):
    df_4 = mo.sql(
        f"""
        SELECT
            start_month,
            COUNT(*) AS ride_count,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min
        FROM rides
        GROUP BY start_month
        ORDER BY start_month;
        """,
        engine=con
    )
    return (df_4,)


@app.cell
def _(df_4, plot_rides_per_month):
    plot_rides_per_month(df_4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q10. Rides per Hour of Day

    **What are we doing?**  
    Grouping by `start_hour` reveals the **daily rhythm** of bike usage —  
    morning commute, afternoon, and evening peaks.

    **SQL concepts:** `GROUP BY`, time-based grouping
    """)
    return


@app.cell
def _(con, mo):
    df_5 = mo.sql(
        f"""
        SELECT
            start_hour,
            COUNT(*) AS ride_count
        FROM rides
        GROUP BY start_hour
        ORDER BY start_hour;
        """,
        engine=con
    )
    return (df_5,)


@app.cell
def _(df_5, plot_rides_per_hour):
    plot_rides_per_hour(df_5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q11. Rides per Day of Week

    **What are we doing?**  
    Grouping by `start_day_of_week` tells us whether weekdays or weekends are busier.  
    For a commuter-heavy system like Citi Bike, we expect weekdays to have more rides.

    **SQL concepts:** `GROUP BY`, `CASE` (for ordering days logically)
    """)
    return


@app.cell
def _(con, mo):
    df_6 = mo.sql(
        f"""
        SELECT
            start_day_of_week,
            COUNT(*) AS ride_count,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min
        FROM rides
        GROUP BY start_day_of_week
        ORDER BY CASE start_day_of_week WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7 END;
        """,
        engine=con
    )
    return (df_6,)


@app.cell
def _(df_6, plot_rides_per_day_of_week):
    plot_rides_per_day_of_week(df_6)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q12. Top 10 Most Popular Start Stations

    **What are we doing?**  
    We find the stations where the most rides **begin**. This is a classic  
    Top-N + GROUP BY pattern. Useful for understanding demand hotspots.

    **SQL concepts:** `GROUP BY`, `ORDER BY ... DESC`, `LIMIT` (Top-N)
    """)
    return


@app.cell
def _(con, mo):
    df_7 = mo.sql(
        f"""
        SELECT
            start_station_name,
            COUNT(*) AS ride_count
        FROM rides
        GROUP BY start_station_name
        ORDER BY ride_count DESC
        LIMIT 10;
        """,
        engine=con
    )
    return (df_7,)


@app.cell
def _(df_7, plot_top_start_stations):
    plot_top_start_stations(df_7)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q13. Top 10 Most Popular Destinations (End Stations)

    **What are we doing?**  
    Same pattern as Q12 but for **end stations** — where do riders go?  
    Comparing start vs. end popularity reveals flow imbalances.

    **SQL concepts:** `GROUP BY`, Top-N, popular destinations
    """)
    return


@app.cell
def _(con, mo):
    df_8 = mo.sql(
        f"""
        SELECT
            end_station_name,
            COUNT(*) AS ride_count
        FROM rides
        GROUP BY end_station_name
        ORDER BY ride_count DESC
        LIMIT 10;
        """,
        engine=con
    )
    return (df_8,)


@app.cell
def _(df_8, plot_top_end_stations):
    plot_top_end_stations(df_8)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q14. Stations with More Than 5,000 Rides (HAVING)

    **What are we doing?**  
    We use `HAVING` to filter **after** grouping. `WHERE` filters individual rows,  
    but `HAVING` filters groups. Here we keep only high-traffic stations.

    **SQL concepts:** `WHERE` vs `HAVING` — a critical distinction!
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            start_station_name,
            COUNT(*) AS ride_count,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min
        FROM rides
        GROUP BY start_station_name
        HAVING COUNT(*) > 5000
        ORDER BY ride_count DESC;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q15. Average Duration by Age Group (CASE + GROUP BY)

    **What are we doing?**  
    We create age brackets using a `CASE` expression and then compute  
    average ride stats per bracket. This combines transformation with aggregation.

    **SQL concepts:** `CASE WHEN`, `GROUP BY`, derived categories
    """)
    return


@app.cell
def _(con, mo):
    df_9 = mo.sql(
        f"""
        SELECT
            CASE WHEN rider_age < 20 THEN 'Under 20' WHEN rider_age BETWEEN 20 AND 29 THEN '20-29' WHEN rider_age BETWEEN 30 AND 39 THEN '30-39' WHEN rider_age BETWEEN 40 AND 49 THEN '40-49' WHEN rider_age BETWEEN 50 AND 59 THEN '50-59' WHEN rider_age >= 60 THEN '60+' ELSE 'Unknown' END AS age_group,
            COUNT(*) AS ride_count,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min,
            ROUND(AVG(distance_km), 3) AS avg_distance_km
        FROM rides
        WHERE rider_age IS NOT NULL
        GROUP BY age_group
        ORDER BY CASE age_group WHEN 'Under 20' THEN 1 WHEN '20-29' THEN 2 WHEN '30-39' THEN 3 WHEN '40-49' THEN 4 WHEN '50-59' THEN 5 WHEN '60+' THEN 6 END;
        """,
        engine=con
    )
    return (df_9,)


@app.cell
def _(df_9, plot_age_group_duration):
    plot_age_group_duration(df_9)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---
    # PART 3: Intermediate Queries (10)

    These queries explore **subqueries**, **window functions**, **time-based analytics**,  
    and **Common Table Expressions (CTEs)**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q16. Top 10 Most Popular Routes (Start -> End Pairs)

    **What are we doing?**  
    We group by BOTH start and end station to find the most popular **routes**.  
    This is more informative than looking at stations in isolation.

    **SQL concepts:** Multi-column `GROUP BY`, string concatenation
    """)
    return


@app.cell
def _(con, mo):
    df_10 = mo.sql(
        f"""
        SELECT
            start_station_name || ' -> ' || end_station_name AS route,
            COUNT(*) AS ride_count,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min,
            ROUND(AVG(distance_km), 3) AS avg_distance_km
        FROM rides
        GROUP BY
            start_station_name,
            end_station_name
        ORDER BY ride_count DESC
        LIMIT 10;
        """,
        engine=con
    )
    return (df_10,)


@app.cell
def _(df_10, plot_top_routes):
    plot_top_routes(df_10)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q17. Round-Trip Rides (Same Start and End Station)

    **What are we doing?**  
    We filter for rides where the start and end station are the same — these are  
    likely leisure/recreational rides. We compare their stats against one-way rides.

    **SQL concepts:** `WHERE` with column comparison, `CASE`, conditional aggregation
    """)
    return


@app.cell
def _(con, mo):
    df_11 = mo.sql(
        f"""
        SELECT
            CASE WHEN start_station_id = end_station_id THEN 'Round Trip' ELSE 'One Way' END AS trip_type,
            COUNT(*) AS ride_count,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS pct_of_total
        FROM rides
        GROUP BY trip_type;
        """,
        engine=con
    )
    return (df_11,)


@app.cell
def _(df_11, plot_round_trip_vs_one_way):
    plot_round_trip_vs_one_way(df_11)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q18. Monthly Trend by Year (Year-over-Year Comparison)

    **What are we doing?**  
    We group by both `start_year` and `start_month` to create a time series  
    that shows monthly trends across different years.

    **SQL concepts:** Multi-level `GROUP BY`, time-series analysis
    """)
    return


@app.cell
def _(con, mo):
    df_12 = mo.sql(
        f"""
        SELECT
            start_year,
            start_month,
            COUNT(*) AS ride_count
        FROM rides
        GROUP BY
            start_year,
            start_month
        ORDER BY
            start_year,
            start_month;
        """,
        engine=con
    )
    return (df_12,)


@app.cell
def _(df_12, plot_monthly_trend_by_year):
    plot_monthly_trend_by_year(df_12)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q19. Weekday vs Weekend Riding Patterns by Hour

    **What are we doing?**  
    We split the data into weekday and weekend groups, then compute hourly ride counts  
    for each. This reveals the commute pattern (weekdays) vs. leisure pattern (weekends).

    **SQL concepts:** `CASE WHEN` for categorization, `GROUP BY` with derived columns
    """)
    return


@app.cell
def _(con, mo):
    df_13 = mo.sql(
        f"""
        SELECT
            start_hour,
            CASE WHEN start_day_of_week IN ('Saturday', 'Sunday') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
            COUNT(*) AS ride_count
        FROM rides
        GROUP BY
            start_hour,
            day_type
        ORDER BY
            day_type,
            start_hour;
        """,
        engine=con
    )
    return (df_13,)


@app.cell
def _(df_13, plot_weekday_vs_weekend):
    plot_weekday_vs_weekend(df_13)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q20. Running Total of Rides per Month (Window Function)

    **What are we doing?**  
    We use `SUM() OVER (ORDER BY ...)` to compute a **cumulative (running) total**.  
    This window function adds up ride counts month-by-month without collapsing rows.

    **SQL concepts:** Window function `SUM() OVER()`, running totals
    """)
    return


@app.cell
def _(con, mo):
    df_14 = mo.sql(
        f"""
        WITH monthly AS (SELECT start_year, start_month, COUNT(*) AS monthly_rides FROM rides GROUP BY start_year, start_month)
        SELECT
            start_year,
            start_month,
            monthly_rides,
            SUM(monthly_rides) OVER(ORDER BY start_year, start_month) AS cumulative_rides
        FROM monthly
        ORDER BY
            start_year,
            start_month;
        """,
        engine=con
    )
    return (df_14,)


@app.cell
def _(df_14, plot_cumulative_rides):
    plot_cumulative_rides(df_14)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q21. Month-over-Month Growth Rate (LAG Window Function)

    **What are we doing?**  
    We use `LAG()` to access the **previous month's** ride count and compute  
    the percentage change. This is essential for trend analysis.

    **SQL concepts:** `LAG() OVER()`, percentage calculations, CTEs
    """)
    return


@app.cell
def _(con, mo):
    df_15 = mo.sql(
        f"""
        WITH monthly AS (SELECT start_year, start_month, COUNT(*) AS rides FROM rides GROUP BY start_year, start_month)
        SELECT
            start_year,
            start_month,
            rides,
            LAG(rides) OVER(ORDER BY start_year, start_month) AS prev_month_rides,
            ROUND(100.0 * (rides - LAG(rides) OVER(ORDER BY start_year, start_month)) / LAG(rides) OVER(ORDER BY start_year, start_month), 2) AS pct_change
        FROM monthly
        ORDER BY
            start_year,
            start_month;
        """,
        engine=con
    )
    return (df_15,)


@app.cell
def _(df_15, plot_mom_growth):
    plot_mom_growth(df_15)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q22. Busiest Stations by Average Rides per Day

    **What are we doing?**  
    Raw ride counts can be misleading if a station only operated part of the period.  
    Here we compute the **average rides per active day** for each station using a subquery.

    **SQL concepts:** Subquery in FROM clause, `COUNT(DISTINCT)`, derived metrics
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            start_station_name,
            COUNT(*) AS total_rides,
            COUNT(DISTINCT CAST(start_time AS DATE)) AS active_days,
            ROUND(1.0 * COUNT(*) / COUNT(DISTINCT CAST(start_time AS DATE)), 2) AS avg_rides_per_day
        FROM rides
        GROUP BY start_station_name
        HAVING COUNT(DISTINCT CAST(start_time AS DATE)) > 30
        ORDER BY avg_rides_per_day DESC
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q23. Duration Distribution: Short, Medium, Long Rides

    **What are we doing?**  
    We bucket rides into duration categories and compute the distribution.  
    This reveals the typical ride length profile of the system.

    **SQL concepts:** `CASE WHEN` bucketing, percentage calculation with window function
    """)
    return


@app.cell
def _(con, mo):
    df_16 = mo.sql(
        f"""
        SELECT
            CASE WHEN trip_duration_min < 5 THEN '1. Under 5 min' WHEN trip_duration_min < 10 THEN '2. 5-10 min' WHEN trip_duration_min < 15 THEN '3. 10-15 min' WHEN trip_duration_min < 30 THEN '4. 15-30 min' WHEN trip_duration_min < 60 THEN '5. 30-60 min' ELSE '6. 60+ min' END AS duration_bucket,
            COUNT(*) AS ride_count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS pct
        FROM rides
        GROUP BY duration_bucket
        ORDER BY duration_bucket;
        """,
        engine=con
    )
    return (df_16,)


@app.cell
def _(df_16, plot_duration_distribution):
    plot_duration_distribution(df_16)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q24. Stations Where Bikes Accumulate (Net Inflow)

    **What are we doing?**  
    We compute the **net flow** for each station: (arrivals - departures).  
    Positive = bikes pile up there. Negative = bikes leave faster than they arrive.  
    This uses a CTE with two subqueries.

    **SQL concepts:** CTE (`WITH`), `FULL OUTER JOIN`, `COALESCE`, net flow analysis
    """)
    return


@app.cell
def _(con, mo):
    df_17 = mo.sql(
        f"""
        WITH departures AS (SELECT start_station_name AS station, COUNT(*) AS depart_count FROM rides GROUP BY start_station_name), arrivals AS (SELECT end_station_name AS station, COUNT(*) AS arrive_count FROM rides GROUP BY end_station_name)
        SELECT
            COALESCE(d.station, a.station) AS station,
            COALESCE(a.arrive_count, 0) AS arrivals,
            COALESCE(d.depart_count, 0) AS departures,
            COALESCE(a.arrive_count, 0) - COALESCE(d.depart_count, 0) AS net_inflow
        FROM departures d
        FULL OUTER JOIN arrivals a
        ON d.station = a.station
        ORDER BY ABS(net_inflow) DESC
        LIMIT 15;
        """,
        engine=con
    )
    return (df_17,)


@app.cell
def _(df_17, plot_net_inflow):
    plot_net_inflow(df_17)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q25. Most Used Bikes (Which Bikes Work the Hardest?)

    **What are we doing?**  
    We find the bikes with the most total rides and the most total distance traveled.  
    This identifies the "workhorses" of the fleet.

    Only about 1% of rides in this dataset record a bike ID (the rest are `NULL`),
    so we filter with `WHERE bike_id IS NOT NULL`. Without it, all the `NULL`s
    form one group of about 990,000 rides and top the list as if they were one bike.

    **SQL concepts:** `WHERE ... IS NOT NULL`, `GROUP BY`, multiple aggregations, `SUM`, fleet analysis
    """)
    return


@app.cell
def _(con, mo):
    df_18 = mo.sql(
        f"""
        SELECT
            bike_id,
            COUNT(*) AS total_rides,
            ROUND(SUM(trip_duration_min), 1) AS total_minutes,
            ROUND(SUM(distance_km), 2) AS total_distance_km,
            COUNT(DISTINCT start_station_id) AS stations_visited
        FROM rides
        WHERE bike_id IS NOT NULL
        GROUP BY bike_id
        ORDER BY total_rides DESC
        LIMIT 15;
        """,
        engine=con
    )
    return (df_18,)


@app.cell
def _(df_18, plot_most_used_bikes):
    plot_most_used_bikes(df_18)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---
    # PART 4: Ranking Queries with CTEs (5)

    These queries demonstrate **WITH (Common Table Expressions)** combined with  
    **ranking functions**: `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, and `PERCENT_RANK`.  
    These are powerful tools for Top-N analysis, percentile calculations, and tiered grouping.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q26. Top 3 Stations per Year (ROW_NUMBER)

    **What are we doing?**  
    For **each year**, we want the top 3 busiest start stations. We can't do this  
    with a simple `ORDER BY` + `LIMIT` because the ranking needs to restart for each year.  
    This is where `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` shines.

    **SQL concepts:**  
    - `WITH` (CTE) to pre-compute station counts  
    - `ROW_NUMBER()` window function  
    - `PARTITION BY` to rank within each year  
    - Filtering on a window function result
    """)
    return


@app.cell
def _(con, mo):
    df_19 = mo.sql(
        f"""
        WITH station_yearly AS (SELECT start_year, start_station_name, COUNT(*) AS ride_count FROM rides GROUP BY start_year, start_station_name), ranked AS (SELECT start_year, start_station_name, ride_count, ROW_NUMBER() OVER(PARTITION BY start_year ORDER BY ride_count DESC) AS rn FROM station_yearly)
        SELECT
            start_year,
            rn AS rank,
            start_station_name,
            ride_count
        FROM ranked
        WHERE rn <= 3
        ORDER BY
            start_year,
            rn;
        """,
        engine=con
    )
    return (df_19,)


@app.cell
def _(df_19, plot_top_stations_per_year):
    plot_top_stations_per_year(df_19)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q27. Station Popularity Tiers (RANK + DENSE_RANK)

    **What are we doing?**  
    We rank all stations by total ride count using both `RANK()` and `DENSE_RANK()`.  
    The difference: `RANK()` leaves gaps after ties (1, 2, 2, **4**),  
    while `DENSE_RANK()` does not (1, 2, 2, **3**). Understanding this distinction  
    is critical for SQL interviews and real analytics.

    **SQL concepts:**  
    - `WITH` (CTE) for clean aggregation  
    - `RANK()` vs `DENSE_RANK()` comparison  
    - Understanding tie-handling in ranking
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        WITH station_counts AS (SELECT start_station_name, COUNT(*) AS ride_count FROM rides GROUP BY start_station_name)
        SELECT
            start_station_name,
            ride_count,
            RANK() OVER(ORDER BY ride_count DESC) AS rank_position,
            DENSE_RANK() OVER(ORDER BY ride_count DESC) AS dense_rank_position
        FROM station_counts
        ORDER BY rank_position
        LIMIT 20;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q28. Station Quartiles by Ride Volume (NTILE)

    **What are we doing?**  
    `NTILE(4)` divides all stations into **4 equal-sized groups** (quartiles) based on  
    ride count. Quartile 1 = busiest 25% of stations, Quartile 4 = quietest 25%.  
    This is useful for tiered analysis ("What do our top-tier stations look like?").

    **SQL concepts:**  
    - `WITH` (CTE)  
    - `NTILE()` window function for bucketing  
    - Aggregation on top of window function results
    """)
    return


@app.cell
def _(con, mo):
    df_20 = mo.sql(
        f"""
        WITH station_counts AS (SELECT start_station_name, COUNT(*) AS ride_count FROM rides GROUP BY start_station_name), quartiled AS (SELECT start_station_name, ride_count, NTILE(4) OVER(ORDER BY ride_count DESC) AS quartile FROM station_counts)
        SELECT
            quartile,
            COUNT(*) AS num_stations,
            SUM(ride_count) AS total_rides,
            MIN(ride_count) AS min_rides,
            MAX(ride_count) AS max_rides,
            ROUND(AVG(ride_count), 0) AS avg_rides
        FROM quartiled
        GROUP BY quartile
        ORDER BY quartile;
        """,
        engine=con
    )
    return (df_20,)


@app.cell
def _(df_20, plot_quartile_summary):
    plot_quartile_summary(df_20)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q29. Percentile Rank of Each Station (PERCENT_RANK)

    **What are we doing?**  
    `PERCENT_RANK()` gives each station a value between 0 and 1 indicating  
    its relative position. 0.95 means "busier than 95% of all stations."  
    This is useful for identifying which stations are in the top 10%, top 5%, etc.

    **SQL concepts:**  
    - `WITH` (CTE)  
    - `PERCENT_RANK()` window function  
    - Filtering for specific percentile thresholds
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        WITH station_counts AS (SELECT start_station_name, COUNT(*) AS ride_count FROM rides GROUP BY start_station_name), pct_ranked AS (SELECT start_station_name, ride_count, ROUND(PERCENT_RANK() OVER(ORDER BY ride_count ASC), 4) AS pct_rank FROM station_counts)
        SELECT
            start_station_name,
            ride_count,
            pct_rank,
            CASE WHEN pct_rank >= 0.95 THEN 'Top 5%' WHEN pct_rank >= 0.90 THEN 'Top 10%' WHEN pct_rank >= 0.75 THEN 'Top 25%' ELSE 'Bottom 75%' END AS tier
        FROM pct_ranked
        WHERE pct_rank >= 0.90
        ORDER BY pct_rank DESC;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q30. Peak Hour Ranking per Day of Week (ROW_NUMBER + PARTITION BY)

    **What are we doing?**  
    For each day of the week, we find the **top 3 busiest hours**. This combines  
    two levels of grouping with a partitioned ranking — one of the most common  
    patterns in SQL analytics.

    **SQL concepts:**  
    - `WITH` (CTE) for multi-step logic  
    - `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`  
    - Combining `GROUP BY` with window functions  
    - Filtering on rank to get Top-N per group
    """)
    return


@app.cell
def _(con, mo):
    df_21 = mo.sql(
        f"""
        WITH hourly_by_day AS (SELECT start_day_of_week, start_hour, COUNT(*) AS ride_count FROM rides GROUP BY start_day_of_week, start_hour), ranked AS (SELECT start_day_of_week, start_hour, ride_count, ROW_NUMBER() OVER(PARTITION BY start_day_of_week ORDER BY ride_count DESC) AS hour_rank FROM hourly_by_day)
        SELECT
            start_day_of_week AS day,
            hour_rank AS rank,
            start_hour AS peak_hour,
            ride_count
        FROM ranked
        WHERE hour_rank <= 3
        ORDER BY
            CASE start_day_of_week WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7 END,
            hour_rank;
        """,
        engine=con
    )
    return (df_21,)


@app.cell
def _(df_21, plot_peak_hours_per_day):
    plot_peak_hours_per_day(df_21)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary of SQL Concepts Covered

    | Concept | Queries |
    |---------|--------|
    | SELECT, LIMIT | Q1, Q4, Q5 |
    | COUNT, DISTINCT | Q2, Q3 |
    | WHERE (filtering) | Q5, Q17 |
    | GROUP BY | Q6-Q15 |
    | ORDER BY (ASC/DESC) | Q4, Q12, Q13 |
    | HAVING (filter on groups) | Q14, Q22 |
    | CASE WHEN | Q11, Q15, Q17, Q19, Q23 |
    | Aggregates (AVG, SUM, MIN, MAX) | Q6-Q15, Q22, Q25 |
    | String concatenation | Q16 |
    | CTE (WITH clause) | Q20, Q21, Q24, Q26-Q30 |
    | Window: SUM() OVER | Q17, Q20, Q23 |
    | Window: LAG() OVER | Q21 |
    | Window: ROW_NUMBER() | Q26, Q30 |
    | Window: RANK / DENSE_RANK | Q27 |
    | Window: NTILE | Q28 |
    | Window: PERCENT_RANK | Q29 |
    | PARTITION BY | Q26, Q30 |
    | FULL OUTER JOIN | Q24 |
    | Time-based analytics | Q8-Q10, Q18-Q21, Q30 |
    | Top-N queries | Q4, Q12, Q13, Q26, Q30 |
    | Popular destinations | Q13, Q16 |
    """)
    return


@app.cell
def _():
    # Close the connection
    # con.close()
    print('Done! Connection closed.')
    return


if __name__ == "__main__":
    app.run()

