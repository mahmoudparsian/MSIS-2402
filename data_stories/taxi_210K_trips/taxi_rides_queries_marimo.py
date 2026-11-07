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
    # NYC Taxi Rides — SQL Data Story

    ## MSIS-2402 — Database Management Systems: Fundamentals of SQL

    This notebook uses **DuckDB** to explore 210,035
    NYC yellow-taxi trips from **January 1, 2015, 00:00–14:59** —
    the first 15 hours of New Year's Day.

    Each section introduces a SQL concept, shows the
    query, displays the result, and (where helpful)
    plots it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 0 — Environment Setup
    """)
    return


@app.cell
def _():
    # Install required packages (run once)
    # !pip install "duckdb>=2.0" matplotlib numpy
    return


@app.cell
def _():
    import duckdb
    import pandas as pd
    import os

    # so plots appear inline
    # %matplotlib inline

    # import our decoupled plotting module
    from plot_helpers import (
        plot_bar, plot_horizontal_bar, plot_line, plot_multi_line,
        plot_histogram, plot_pie, plot_grouped_bar, plot_scatter,
        plot_stacked_bar,
    )

    print("All imports successful ✓")
    return duckdb, os, plot_bar, plot_grouped_bar, plot_horizontal_bar, plot_line, plot_multi_line, plot_pie, plot_scatter


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1 — Load CSV into DuckDB

    We read `taxi.csv` into an in‑process DuckDB database file (`taxi_rides.duckdb`).

    Steps:

    1. Create (or connect to) the database file.

    2. Import the CSV into a table called **`rides`**.

    3. Rename the columns to clean **snake_case** names.

    4. Parse the datetime strings into proper `TIMESTAMP` columns.

    5. Add four **derived columns** that will be useful for analytics:   

    - `trip_duration_minutes` — how long the trip took   
    - `tip_percentage` — tip as a fraction of fare   
    - `hour_of_day` — the hour when the trip started (0–23)   
    - `day_of_week` — day name (Monday … Sunday; in this data every ride is on a Thursday)
    """)
    return


@app.cell
def _(duckdb, os):
    # ── 1a  Create / connect to the DuckDB file ──────────────────────────────────
    DB_PATH = "taxi_rides.duckdb"

    # Remove old DB so we start fresh each time this cell runs
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    con = duckdb.connect(DB_PATH)
    print(f"Connected to {DB_PATH}")
    return (con,)


@app.cell
def _(con):
    # ── 1b  Import CSV into a raw staging table ──────────────────────────────────
    con.execute("""
        CREATE OR REPLACE TABLE rides_raw AS
        SELECT * FROM read_csv_auto('taxi.csv', header=True,
                                    timestampformat = '%m/%d/%y %H:%M');
    """)
    _count = con.execute("SELECT COUNT(*) FROM rides_raw").fetchall()[0][0]
    print(f"Imported {_count:,} rows into rides_raw")
    return


@app.cell
def _(con):
    # ── 1c  Rename columns, parse dates, add derived columns ──────────────────────
    #
    # NOTE: the CSV writes dates as month/day/2-digit-year (e.g. 1/1/15 0:11).
    # Without timestampformat in step 1b, DuckDB guesses wrong and reads them as
    # year 1. With it, the datetime columns are proper TIMESTAMPs we can use directly.
    con.execute("""
        CREATE OR REPLACE TABLE rides AS
        SELECT
            -- renamed columns
            VENDORID                          AS vendor_id,
            TPEP_PICKUP_DATETIME              AS pickup_datetime,
            TPEP_DROPOFF_DATETIME             AS dropoff_datetime,
            PASSENGER_COUNT                   AS passenger_count,
            TRIP_DISTANCE                     AS trip_distance,
            RATECODEID                        AS rate_code_id,
            STORE_AND_FWD_FLAG                AS store_and_fwd_flag,
            PULOCATIONID                      AS pickup_location_id,
            DOLOCATIONID                      AS drop_location_id,
            PAYMENT_TYPE                      AS payment_type,
            FARE_AMOUNT                       AS fare_amount,
            EXTRA                             AS extra,
            MTA_TAX                           AS mta_tax,
            TIP_AMOUNT                        AS tip_amount,
            TOLLS_AMOUNT                      AS tolls_amount,
            IMPROVEMENT_SURCHARGE             AS improvement_surcharge,
            TOTAL_AMOUNT                      AS total_amount,

            -- derived columns
            DATEDIFF('minute',
                     TPEP_PICKUP_DATETIME,
                     TPEP_DROPOFF_DATETIME
            )                                 AS trip_duration_minutes,

            CASE WHEN FARE_AMOUNT > 0
                 THEN ROUND(TIP_AMOUNT / FARE_AMOUNT * 100, 2)
                 ELSE 0
            END                               AS tip_percentage,

            EXTRACT(HOUR FROM TPEP_PICKUP_DATETIME)  AS hour_of_day,

            DAYNAME(TPEP_PICKUP_DATETIME)             AS day_of_week

        FROM rides_raw;
    """)

    # Drop the raw staging table
    con.execute("DROP TABLE rides_raw;")

    _count = con.execute("SELECT COUNT(*) FROM rides").fetchall()[0][0]
    print(f"Table 'rides' created with {_count:,} rows and derived columns ✓")
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        DESCRIBE rides
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo, rides):
    _df = mo.sql(
        f"""
        SELECT *
        FROM rides
        LIMIT 5
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2 — Basic Queries

    These queries use the fundamental SQL building
    blocks: `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`,
    and simple aggregates like `COUNT`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### B1 — How many total rides are in the dataset?

    The simplest aggregate: `COUNT(*)` returns the total number of rows.
    """)
    return


@app.cell
def _(con, mo, rides):
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
    ### B2 — What are the 10 longest trips by distance?

    `ORDER BY … DESC` with `LIMIT` gives us a Top‑N
    query — one of the most common patterns in SQL.
    """)
    return


@app.cell
def _(con, mo, rides):
    df = mo.sql(
        f"""
        SELECT
            pickup_datetime,
            dropoff_datetime,
            trip_distance,
            fare_amount,
            total_amount
        FROM rides
        ORDER BY trip_distance DESC
        LIMIT 10;
        """,
        engine=con
    )
    if hasattr(df, "to_pandas"):
        df = df.to_pandas()
    return (df,)


@app.cell
def _(df, plot_bar):
    plot_bar(
        labels=[f"Trip {i+1}" for i in range(len(df))],
        values=df["trip_distance"].tolist(),
        title="Top 10 Longest Trips by Distance",
        xlabel="Trip Rank", ylabel="Distance (miles)"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### B3 — How many rides had exactly 1 passenger?

    A `WHERE` filter narrows the dataset before the aggregate runs.
    """)
    return


@app.cell
def _(con, mo, rides):
    _df = mo.sql(
        f"""
        SELECT COUNT(*) AS solo_rides
        FROM rides
        WHERE passenger_count = 1;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### B4 — What are the minimum, maximum, and average fare amounts?

    Multiple aggregate functions in one SELECT —
    SQL can compute several summaries in a single pass.
    """)
    return


@app.cell
def _(con, mo, rides):
    _df = mo.sql(
        f"""
        SELECT
            MIN(fare_amount) AS min_fare,
            MAX(fare_amount) AS max_fare,
            ROUND(AVG(fare_amount), 2) AS avg_fare
        FROM rides;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### B5 — Show 10 sample rides that cost more than $50

    Combining `WHERE` with `LIMIT` lets us inspect a
    filtered subset without flooding the screen.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_2 = mo.sql(
        f"""
        SELECT
            pickup_datetime,
            trip_distance,
            fare_amount,
            tip_amount,
            total_amount
        FROM rides
        WHERE total_amount > 50
        ORDER BY total_amount DESC
        LIMIT 10;
        """,
        engine=con
    )
    if hasattr(df_2, "to_pandas"):
        df_2 = df_2.to_pandas()
    return (df_2,)


@app.cell
def _(df_2, plot_bar):
    plot_bar(
        labels=[str(t)[:16] for t in df_2["pickup_datetime"]],
        values=df_2["total_amount"].tolist(),
        title="10 Sample Rides Over $50",
        xlabel="Pickup Time", ylabel="Total Amount ($)",
        rotate_x=45, fmt_currency=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3 — Basic+ Queries

    These queries introduce `GROUP BY`, aggregate functions on groups, `HAVING`, `DISTINCT`, `BETWEEN`, `IN`, and `CASE`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP1 — Total rides per passenger count

    `GROUP BY` splits the table into groups;

    `COUNT(*)` counts each group.
    This shows the distribution of passengers per ride.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_3 = mo.sql(
        f"""
        SELECT
            passenger_count,
            COUNT(*) AS num_rides
        FROM rides
        GROUP BY passenger_count
        ORDER BY passenger_count;
        """,
        engine=con
    )
    if hasattr(df_3, "to_pandas"):
        df_3 = df_3.to_pandas()
    return (df_3,)


@app.cell
def _(df_3, plot_bar):
    plot_bar(
        labels=df_3["passenger_count"].astype(str).tolist(),
        values=df_3["num_rides"].tolist(),
        title="Rides by Passenger Count",
        xlabel="Passengers", ylabel="Number of Rides"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP2 — Average fare by payment type

    Payment type is coded as integers

    1=Credit Card,
    2=Cash,
    3=No Charge,
    4=Dispute,
    5=Unknown,
    6=Voided

    We use `CASE` inside the `GROUP BY` to give them readable labels.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_4 = mo.sql(
        f"""
        SELECT
            CASE payment_type WHEN 1 THEN 'Credit Card' WHEN 2 THEN 'Cash' WHEN 3 THEN 'No Charge' WHEN 4 THEN 'Dispute' WHEN 5 THEN 'Unknown' WHEN 6 THEN 'Voided' ELSE 'Other' END AS payment_method,
            COUNT(*) AS num_rides,
            ROUND(AVG(fare_amount), 2) AS avg_fare
        FROM rides
        GROUP BY payment_type
        ORDER BY num_rides DESC;
        """,
        engine=con
    )
    if hasattr(df_4, "to_pandas"):
        df_4 = df_4.to_pandas()
    return (df_4,)


@app.cell
def _(df_4, plot_bar):
    plot_bar(
        labels=df_4["payment_method"].tolist(),
        values=df_4["avg_fare"].tolist(),
        title="Average Fare by Payment Method",
        xlabel="Payment Method", ylabel="Avg Fare ($)",
        fmt_currency=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP3 — Average trip distance per vendor

    Two vendor IDs are present:

    1 = Creative Mobile Technologies,
    2 = VeriFone Inc.

    `GROUP BY vendor_id` compares them.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_5 = mo.sql(
        f"""
        SELECT
            vendor_id,
            COUNT(*) AS num_rides,
            ROUND(AVG(trip_distance), 2) AS avg_distance,
            ROUND(AVG(fare_amount), 2) AS avg_fare
        FROM rides
        GROUP BY vendor_id
        ORDER BY vendor_id;
        """,
        engine=con
    )
    if hasattr(df_5, "to_pandas"):
        df_5 = df_5.to_pandas()
    return (df_5,)


@app.cell
def _(df_5, plot_grouped_bar):
    plot_grouped_bar(
        labels=[f"Vendor {v}" for v in df_5["vendor_id"]],
        group_dict={
            "Avg Distance (mi)": df_5["avg_distance"].tolist(),
            "Avg Fare ($)": df_5["avg_fare"].tolist(),
        },
        title="Vendor Comparison",
        ylabel="Value"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP4 — Rides by part of the day

    All 210,035 rides are from **one day** (January 1, 2015, 00:00–14:59), so we group
    by *time of day* instead of day of the week. A `CASE` expression turns each
    `hour_of_day` into a label, and `GROUP BY` counts the rides in each part:

    | Part of the day | Hours |
    |---|---|
    | Night | 0–5 |
    | Morning | 6–11 |
    | Early afternoon | 12–14 (the data ends at 14:59) |

    `first_hour` (`MIN(hour_of_day)`) is there only to sort the parts in time order.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_6 = mo.sql(
        f"""
        SELECT
            CASE
                WHEN hour_of_day < 6  THEN 'Night (0-5)'
                WHEN hour_of_day < 12 THEN 'Morning (6-11)'
                ELSE 'Early afternoon (12-14)'
            END AS part_of_day,
            MIN(hour_of_day) AS first_hour,
            COUNT(*) AS num_rides,
            ROUND(AVG(total_amount), 2) AS avg_total_amount
        FROM rides
        GROUP BY part_of_day
        ORDER BY first_hour;
        """,
        engine=con
    )
    if hasattr(df_6, "to_pandas"):
        df_6 = df_6.to_pandas()
    return (df_6,)


@app.cell
def _(df_6, plot_bar):
    plot_bar(
        labels=df_6["part_of_day"].tolist(),
        values=df_6["num_rides"].tolist(),
        title="Rides by Part of the Day (January 1, 2015)",
        xlabel="Part of the day", ylabel="Number of Rides"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Reading it:** more than half of all rides (117,868 of 210,035) happen between
    midnight and 6 am — New Year's Eve crowds going home.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP5 — Pickup locations with more than 2,000 rides 

    *(WHERE vs HAVING)*

    `WHERE` filters **rows before** grouping;
    `HAVING` filters **groups after** aggregation.

    Here we need `HAVING` because we want to keep only
    locations whose *count* exceeds a threshold.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_7 = mo.sql(
        f"""
        SELECT
            pickup_location_id,
            COUNT(*) AS num_rides
        FROM rides
        GROUP BY pickup_location_id
        HAVING COUNT(*) > 2000
        ORDER BY num_rides DESC;
        """,
        engine=con
    )
    if hasattr(df_7, "to_pandas"):
        df_7 = df_7.to_pandas()
    return (df_7,)


@app.cell
def _(df_7, plot_horizontal_bar):
    plot_horizontal_bar(
        labels=df_7["pickup_location_id"].astype(str).tolist(),
        values=df_7["num_rides"].tolist(),
        title="Busiest Pickup Locations (>2,000 rides)",
        xlabel="Number of Rides", ylabel="Location ID"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP6 — How many distinct pickup locations exist?

    `COUNT(DISTINCT …)` counts unique values — useful for understanding cardinality.
    """)
    return


@app.cell
def _(con, mo, rides):
    _df = mo.sql(
        f"""
        SELECT
            COUNT(DISTINCT pickup_location_id) AS unique_pickup_locs,
            COUNT(DISTINCT drop_location_id) AS unique_dropoff_locs
        FROM rides;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP7 — Rides with fares between `$10` and `$20`

    `BETWEEN` is syntactic sugar for `>= AND <=`. Clean and readable.
    """)
    return


@app.cell
def _(con, mo, rides):
    _df = mo.sql(
        f"""
        SELECT COUNT(*) AS rides_10_to_20
        FROM rides
        WHERE fare_amount BETWEEN 10 AND 20;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP8 — Average tip percentage by passenger count

    Combines our derived `tip_percentage`
    column with `GROUP BY` and `HAVING` to
    exclude groups with very few rides.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_8 = mo.sql(
        f"""
        SELECT
            passenger_count,
            COUNT(*) AS num_rides,
            ROUND(AVG(tip_percentage), 2) AS avg_tip_pct
        FROM rides
        WHERE passenger_count BETWEEN 1 AND 6
        GROUP BY passenger_count
        HAVING COUNT(*) > 100
        ORDER BY passenger_count;
        """,
        engine=con
    )
    if hasattr(df_8, "to_pandas"):
        df_8 = df_8.to_pandas()
    return (df_8,)


@app.cell
def _(df_8, plot_bar):
    plot_bar(
        labels=df_8["passenger_count"].astype(str).tolist(),
        values=df_8["avg_tip_pct"].tolist(),
        title="Average Tip % by Passenger Count",
        xlabel="Passengers", ylabel="Avg Tip %"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP9 — Rides paid with credit card vs. cash 

    (using IN)`IN (…)` is a concise alternative to multiple `OR` conditions.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_9 = mo.sql(
        f"""
        SELECT
            CASE payment_type WHEN 1 THEN 'Credit Card' WHEN 2 THEN 'Cash' END AS method,
            COUNT(*) AS num_rides,
            ROUND(SUM(total_amount), 2) AS total_revenue
        FROM rides
        WHERE payment_type IN (1, 2)
        GROUP BY payment_type
        ORDER BY num_rides DESC;
        """,
        engine=con
    )
    if hasattr(df_9, "to_pandas"):
        df_9 = df_9.to_pandas()
    return (df_9,)


@app.cell
def _(df_9, plot_pie):
    plot_pie(
        labels=df_9["method"].tolist(),
        values=df_9["num_rides"].tolist(),
        title="Credit Card vs Cash Rides"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### BP10 — Categorize trips by distance (Short / Medium / Long)

    `CASE` expressions create computed categories
    on the fly — like adding a virtual column.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_10 = mo.sql(
        f"""
        SELECT
            CASE WHEN trip_distance < 2 THEN 'Short (<2 mi)' WHEN trip_distance < 10 THEN 'Medium (2–10 mi)' ELSE 'Long (10+ mi)' END AS distance_category,
            COUNT(*) AS num_rides,
            ROUND(AVG(fare_amount), 2) AS avg_fare
        FROM rides
        GROUP BY distance_category
        ORDER BY avg_fare;
        """,
        engine=con
    )
    if hasattr(df_10, "to_pandas"):
        df_10 = df_10.to_pandas()
    return (df_10,)


@app.cell
def _(df_10, plot_bar):
    plot_bar(
        labels=df_10["distance_category"].tolist(),
        values=df_10["num_rides"].tolist(),
        title="Rides by Distance Category",
        xlabel="Category", ylabel="Number of Rides"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4 — Intermediate Queries

    Window functions, subqueries, time‑based analytics, correlated filters, and more.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I1 — Hourly ride volume (time‑based analytics)

    Using `hour_of_day` to see when New Yorkers ride the most.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_11 = mo.sql(
        f"""
        SELECT
            hour_of_day,
            COUNT(*) AS num_rides
        FROM rides
        GROUP BY hour_of_day
        ORDER BY hour_of_day;
        """,
        engine=con
    )
    if hasattr(df_11, "to_pandas"):
        df_11 = df_11.to_pandas()
    return (df_11,)


@app.cell
def _(df_11, plot_line):
    plot_line(
        x=df_11["hour_of_day"].tolist(),
        y=df_11["num_rides"].tolist(),
        title="Ride Volume by Hour of Day",
        xlabel="Hour (0–23)", ylabel="Number of Rides"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I2 — Running total of rides per hour 

    *(window function: SUM … OVER)*

    A **window function**
    computes a value across a set of rows related to the
    current row — without collapsing the result.

    Here, `SUM(num_rides) OVER (ORDER BY hour_of_day)`
    produces a cumulative (running) total.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_12 = mo.sql(
        f"""
        SELECT
            hour_of_day,
            COUNT(*) AS num_rides,
            SUM(COUNT(*)) OVER(ORDER BY hour_of_day) AS running_total
        FROM rides
        GROUP BY hour_of_day
        ORDER BY hour_of_day;
        """,
        engine=con
    )
    if hasattr(df_12, "to_pandas"):
        df_12 = df_12.to_pandas()
    return (df_12,)


@app.cell
def _(df_12, plot_multi_line):
    plot_multi_line(
        x=df_12["hour_of_day"].tolist(),
        y_dict={
            "Rides This Hour": df_12["num_rides"].tolist(),
            "Running Total": df_12["running_total"].tolist(),
        },
        title="Hourly Rides with Running Total",
        xlabel="Hour of Day", ylabel="Count"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I3 — Trip distance distribution 

    *(histogram via SQL buckets)*

    We can create
    histogram buckets in SQL with `FLOOR(trip_distance)`
    and then plot the distribution.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_13 = mo.sql(
        f"""
        SELECT
            FLOOR(trip_distance) AS distance_bucket,
            COUNT(*) AS num_rides
        FROM rides
        WHERE trip_distance BETWEEN 0 AND 20
        GROUP BY distance_bucket
        ORDER BY distance_bucket;
        """,
        engine=con
    )
    if hasattr(df_13, "to_pandas"):
        df_13 = df_13.to_pandas()
    return (df_13,)


@app.cell
def _(df_13, plot_bar):
    plot_bar(
        labels=df_13["distance_bucket"].astype(int).astype(str).tolist(),
        values=df_13["num_rides"].tolist(),
        title="Trip Distance Distribution (0–20 miles)",
        xlabel="Distance (miles, floored)", ylabel="Number of Rides"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I4 — Average fare per mile by hour of day

    Dividing fare by distance gives a
    "price per mile" metric. We exclude
    very short trips (< 0.5 mi) to
    avoid division noise.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_14 = mo.sql(
        f"""
        SELECT
            hour_of_day,
            ROUND(AVG(fare_amount / trip_distance), 2) AS avg_fare_per_mile
        FROM rides
        WHERE trip_distance >= 0.5
        GROUP BY hour_of_day
        ORDER BY hour_of_day;
        """,
        engine=con
    )
    if hasattr(df_14, "to_pandas"):
        df_14 = df_14.to_pandas()
    return (df_14,)


@app.cell
def _(df_14, plot_line):
    plot_line(
        x=df_14["hour_of_day"].tolist(),
        y=df_14["avg_fare_per_mile"].tolist(),
        title="Average Fare per Mile by Hour",
        xlabel="Hour of Day", ylabel="$/mile"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I5 — Top 5 busiest pickup → drop‑off routes

    Combining two `GROUP BY` columns reveals
    popular origin–destination pairs.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_15 = mo.sql(
        f"""
        SELECT
            pickup_location_id,
            drop_location_id,
            COUNT(*) AS num_rides,
            ROUND(AVG(trip_distance), 2) AS avg_distance,
            ROUND(AVG(total_amount), 2) AS avg_total
        FROM rides
        GROUP BY
            pickup_location_id,
            drop_location_id
        ORDER BY num_rides DESC
        LIMIT 5;
        """,
        engine=con
    )
    if hasattr(df_15, "to_pandas"):
        df_15 = df_15.to_pandas()
    return (df_15,)


@app.cell
def _(df_15, plot_horizontal_bar):
    plot_horizontal_bar(
        labels=[f"{r.pickup_location_id} → {r.drop_location_id}" for _, r in df_15.iterrows()],
        values=df_15["num_rides"].tolist(),
        title="Top 5 Busiest Routes",
        xlabel="Number of Rides", ylabel="Route (Pickup → Dropoff)"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I6 — Percentage of rides per payment type 

    *(window function: ratio)*

    `COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()`
    computes each group's share of the grand total
    — a window aggregate over the entire result set.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_16 = mo.sql(
        f"""
        SELECT
            CASE payment_type WHEN 1 THEN 'Credit Card' WHEN 2 THEN 'Cash' WHEN 3 THEN 'No Charge' WHEN 4 THEN 'Dispute' ELSE 'Other' END AS payment_method,
            COUNT(*) AS num_rides,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct_of_total
        FROM rides
        GROUP BY payment_type
        ORDER BY num_rides DESC;
        """,
        engine=con
    )
    if hasattr(df_16, "to_pandas"):
        df_16 = df_16.to_pandas()
    return (df_16,)


@app.cell
def _(df_16, plot_pie):
    plot_pie(
        labels=df_16["payment_method"].tolist(),
        values=df_16["num_rides"].tolist(),
        title="Ride Share by Payment Method"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I7 — Trips where the tip exceeded the fare 

    *(subquery filter)*

    A subquery in the `WHERE`
    clause identifies unusual rides where passengers
    tipped more than the fare itself.
    """)
    return


@app.cell
def _(con, mo, rides):
    _df = mo.sql(
        f"""
        SELECT
            pickup_datetime,
            trip_distance,
            fare_amount,
            tip_amount,
            tip_percentage
        FROM rides
        WHERE
            tip_amount > fare_amount
            AND fare_amount > 0
        ORDER BY tip_percentage DESC
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I8 — Hour-by-hour average duration and distance 

    *(multi-metric time series)*

    Grouping by `hour_of_day`
    and computing several averages gives a rich picture
    of how trips differ throughout the day.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_17 = mo.sql(
        f"""
        SELECT
            hour_of_day,
            ROUND(AVG(trip_duration_minutes), 2) AS avg_duration,
            ROUND(AVG(trip_distance), 2) AS avg_distance,
            ROUND(AVG(total_amount), 2) AS avg_total
        FROM rides
        WHERE trip_duration_minutes > 0
        GROUP BY hour_of_day
        ORDER BY hour_of_day;
        """,
        engine=con
    )
    if hasattr(df_17, "to_pandas"):
        df_17 = df_17.to_pandas()
    return (df_17,)


@app.cell
def _(df_17, plot_multi_line):
    plot_multi_line(
        x=df_17["hour_of_day"].tolist(),
        y_dict={
            "Avg Duration (min)": df_17["avg_duration"].tolist(),
            "Avg Distance (mi)": df_17["avg_distance"].tolist(),
        },
        title="Trip Duration & Distance by Hour",
        xlabel="Hour of Day", ylabel="Value"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I9 — Fare vs. distance scatter 

    *(do fares follow distance?)*

    This query extracts a sample of 5,000 rides
    so we can plot fare vs. distance and visually
    check the relationship.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_18 = mo.sql(
        f"""
        SELECT
            trip_distance,
            fare_amount
        FROM rides
        WHERE
            trip_distance BETWEEN 0.5 AND 30
            AND fare_amount BETWEEN 2.5 AND 200 USING SAMPLE 5000;
        """,
        engine=con
    )
    if hasattr(df_18, "to_pandas"):
        df_18 = df_18.to_pandas()
    return (df_18,)


@app.cell
def _(df_18, plot_scatter):
    plot_scatter(
        x=df_18["trip_distance"].tolist(),
        y=df_18["fare_amount"].tolist(),
        title="Fare vs. Trip Distance (5,000 sample)",
        xlabel="Distance (miles)", ylabel="Fare ($)"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### I10 — Pickup location × hour heatmap

    **Two-dimensional `GROUP BY`:** grouping by **two** columns — `pickup_location_id`
    and `hour_of_day` — gives one count per (location, hour) pair, a matrix we pivot in
    pandas and draw as a heatmap. To keep it readable we take only the **8 busiest pickup
    locations** (a CTE ranks them by number of rides; ties broken by `pickup_location_id`).
    """)
    return


@app.cell
def _(con):
    _df = con.execute("""
        WITH top_locations AS (
            SELECT pickup_location_id
            FROM rides
            GROUP BY pickup_location_id
            ORDER BY COUNT(*) DESC, pickup_location_id
            LIMIT 8
        )
        SELECT pickup_location_id,
               hour_of_day,
               COUNT(*) AS num_rides
        FROM rides
        WHERE pickup_location_id IN (SELECT pickup_location_id FROM top_locations)
        GROUP BY pickup_location_id, hour_of_day
        ORDER BY pickup_location_id, hour_of_day;
    """).df()

    # Pivot for heatmap: one row per location (busiest first), one column per hour
    import matplotlib.pyplot as plt
    pivot = _df.pivot(index="pickup_location_id", columns="hour_of_day", values="num_rides").fillna(0)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(12, 5))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([f"Location {i}" for i in pivot.index])
    ax.set_xlabel("Hour of Day (January 1, 2015)")
    ax.set_ylabel("Pickup location")
    ax.set_title("Ride Volume: 8 Busiest Pickup Locations × Hour of Day", fontweight="bold")
    plt.colorbar(im, ax=ax, label="Number of Rides")
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Reading it:** the 8 busiest locations are all in Manhattan; location 79 (East
    Village, in NYC's official taxi-zone list) is the busiest, with 9,074 pickups. Most
    of the color sits in the early-morning hours.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5 — Ranking Function Queries (CTEs + Window Rankings)

    These queries use **Common Table Expressions** (`WITH`)
    and ranking window functions:`ROW_NUMBER()`, `RANK()`,
    `DENSE_RANK()`, `NTILE()`, and `PERCENT_RANK()`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### R1 — Top 3 pickup locations by ride volume 

    *(ROW_NUMBER)*

    `ROW_NUMBER()` assigns a unique sequential integer
    to each row within a partition. We use a CTE (`WITH`)
    to first compute counts, then filter to the top 3.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_19 = mo.sql(
        f"""
        WITH location_counts AS (SELECT pickup_location_id, COUNT(*) AS num_rides, ROW_NUMBER() OVER(ORDER BY COUNT(*) DESC) AS rn FROM rides GROUP BY pickup_location_id)
        SELECT
            pickup_location_id,
            num_rides,
            rn
        FROM location_counts
        WHERE rn <= 3;
        """,
        engine=con
    )
    if hasattr(df_19, "to_pandas"):
        df_19 = df_19.to_pandas()
    return (df_19,)


@app.cell
def _(df_19, plot_bar):
    plot_bar(
        labels=df_19["pickup_location_id"].astype(str).tolist(),
        values=df_19["num_rides"].tolist(),
        title="Top 3 Pickup Locations (ROW_NUMBER)",
        xlabel="Location ID", ylabel="Number of Rides"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### R2 — Rank hours by average fare with ties 

    *(RANK vs DENSE_RANK)*

    `RANK()` leaves gaps after ties;
    `DENSE_RANK()` does not.

    This query shows both side‑by‑side so students can compare.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_20 = mo.sql(
        f"""
        WITH hourly_fares AS (SELECT hour_of_day, ROUND(AVG(fare_amount), 2) AS avg_fare FROM rides GROUP BY hour_of_day)
        SELECT
            hour_of_day,
            avg_fare,
            RANK() OVER(ORDER BY avg_fare DESC) AS fare_rank,
            DENSE_RANK() OVER(ORDER BY avg_fare DESC) AS fare_dense_rank
        FROM hourly_fares
        ORDER BY fare_rank
        LIMIT 10;
        """,
        engine=con
    )
    if hasattr(df_20, "to_pandas"):
        df_20 = df_20.to_pandas()
    return (df_20,)


@app.cell
def _(df_20, plot_bar):
    plot_bar(
        labels=df_20["hour_of_day"].astype(str).tolist(),
        values=df_20["avg_fare"].tolist(),
        title="Top 10 Hours by Average Fare (Ranked)",
        xlabel="Hour of Day", ylabel="Avg Fare ($)",
        fmt_currency=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### R3 — Divide trips into 4 fare quartiles 

    *(NTILE)*

    `NTILE(4)` splits the ordered data into 4 roughly
    equal groups — quartiles. We then summarize each quartile.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_21 = mo.sql(
        f"""
        WITH quartiled AS (SELECT fare_amount, trip_distance, tip_percentage, NTILE(4) OVER(ORDER BY fare_amount) AS fare_quartile FROM rides WHERE fare_amount > 0)
        SELECT
            fare_quartile,
            COUNT(*) AS num_rides,
            ROUND(MIN(fare_amount), 2) AS min_fare,
            ROUND(MAX(fare_amount), 2) AS max_fare,
            ROUND(AVG(fare_amount), 2) AS avg_fare,
            ROUND(AVG(trip_distance), 2) AS avg_distance,
            ROUND(AVG(tip_percentage), 2) AS avg_tip_pct
        FROM quartiled
        GROUP BY fare_quartile
        ORDER BY fare_quartile;
        """,
        engine=con
    )
    if hasattr(df_21, "to_pandas"):
        df_21 = df_21.to_pandas()
    return (df_21,)


@app.cell
def _(df_21, plot_grouped_bar):
    plot_grouped_bar(
        labels=[f"Q{q}" for q in df_21["fare_quartile"]],
        group_dict={
            "Avg Fare ($)": df_21["avg_fare"].tolist(),
            "Avg Distance (mi)": df_21["avg_distance"].tolist(),
            "Avg Tip %": df_21["avg_tip_pct"].tolist(),
        },
        title="Fare Quartile Comparison (NTILE)",
        ylabel="Value"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### R4 — Percentile ranking of pickup locations 

    *(PERCENT_RANK)*

    `PERCENT_RANK()` returns a value between 0 and 1
    indicating where each row stands relative to all
    other rows.

    Locations with a `pct_rank` near 1.0 are the busiest.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_22 = mo.sql(
        f"""
        WITH loc_stats AS (SELECT pickup_location_id, COUNT(*) AS num_rides, ROUND(PERCENT_RANK() OVER(ORDER BY COUNT(*)), 4) AS pct_rank FROM rides GROUP BY pickup_location_id)
        SELECT *
        FROM loc_stats
        WHERE pct_rank >= 0.95
        ORDER BY pct_rank DESC;
        """,
        engine=con
    )
    if hasattr(df_22, "to_pandas"):
        df_22 = df_22.to_pandas()
    return (df_22,)


@app.cell
def _(df_22, plot_horizontal_bar):
    plot_horizontal_bar(
        labels=df_22["pickup_location_id"].astype(str).tolist(),
        values=df_22["num_rides"].tolist(),
        title="Top 5% Pickup Locations (PERCENT_RANK ≥ 0.95)",
        xlabel="Number of Rides", ylabel="Location ID"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### R5 — Top-earning pickup location for each hour

    **CTE + `ROW_NUMBER()` with `PARTITION BY`:** for every hour, find the single pickup
    location with the highest total revenue (`SUM(total_amount)`).
    `ROW_NUMBER() OVER (PARTITION BY hour_of_day ORDER BY SUM(total_amount) DESC, pickup_location_id)`
    restarts the numbering for each hour (ties broken by `pickup_location_id`), and we
    keep only row 1 — 15 rows, one per hour 0–14.
    """)
    return


@app.cell
def _(con, mo, rides):
    df_23 = mo.sql(
        f"""
        WITH hourly_revenue AS (
            SELECT
                hour_of_day,
                pickup_location_id,
                ROUND(SUM(total_amount), 2) AS total_rev,
                ROW_NUMBER() OVER (PARTITION BY hour_of_day
                                   ORDER BY SUM(total_amount) DESC, pickup_location_id) AS rn
            FROM rides
            GROUP BY hour_of_day, pickup_location_id
        )
        SELECT
            hour_of_day,
            pickup_location_id,
            total_rev
        FROM hourly_revenue
        WHERE rn = 1
        ORDER BY hour_of_day;
        """,
        engine=con
    )
    if hasattr(df_23, "to_pandas"):
        df_23 = df_23.to_pandas()
    return (df_23,)


@app.cell
def _(df_23, plot_bar):
    plot_bar(
        labels=[f"{r.hour_of_day}h\n(Loc {r.pickup_location_id})" for _, r in df_23.iterrows()],
        values=df_23["total_rev"].tolist(),
        title="Top-Earning Pickup Location per Hour (January 1, 2015)",
        xlabel="Hour (location)", ylabel="Total Revenue ($)",
        rotate_x=0, fmt_currency=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Reading it:** location 79 (East Village) earns the most in every hour from 0 to 5
    — the party crowd going home. From 6 am, airport pickups take over: location 132
    (JFK Airport) in hours 6–9 and 12–14, and location 138 (LaGuardia Airport) in hours
    10–11. (Zone names: NYC TLC's official taxi-zone list.)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary of SQL Concepts Covered

    | Section | Concepts |
    |---------|----------|
    | **Basic** | `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `COUNT`, `MIN`, `MAX`, `AVG` |
    | **Basic+** | `GROUP BY`, `HAVING`, `DISTINCT`, `BETWEEN`, `IN`, `CASE`, `SUM` |
    | **Intermediate** | Window functions (`SUM OVER`, ratio), subqueries, time analytics, multi-column `GROUP BY`, sampling|
    | **Ranking** | `WITH` (CTEs), `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `PERCENT_RANK`, `PARTITION BY` |

    ---
    *MSIS-2402 — Database Management Systems: Fundamentals of SQL — Santa Clara University.*
    """)
    return


@app.cell
def _(con):
    # Close the DuckDB connection
    con.close()
    print("Connection closed ✓")
    return


if __name__ == "__main__":
    app.run()

