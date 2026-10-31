"""
Build the taxi_rides Jupyter notebook programmatically.
Run:  python build_notebook.py
Produces: taxi_rides_queries.ipynb
"""
import json, os

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip().split("\n")}

def code(source):
    lines = source.strip().split("\n")
    # add newlines to all but the last line
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type": "code", "metadata": {}, "source": src, "outputs": [], "execution_count": None}

cells = []

# ═══════════════════════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════════════════════
cells.append(md("""# NYC Taxi Rides — SQL Data Story
## Database Management Systems - Fundamentals of SQL (MSIS-2402)

This notebook uses **DuckDB** to explore ~210,000 NYC yellow‑taxi trips from January 2015.
Each section introduces a SQL concept, shows the query, displays the result, and (where helpful) plots it.

---"""))

# ═══════════════════════════════════════════════════════════════════════════════
# SETUP CELLS
# ═══════════════════════════════════════════════════════════════════════════════
cells.append(md("""## 0 — Environment Setup"""))

cells.append(code("""# Install required packages (run once)
# !pip install duckdb matplotlib numpy"""))

cells.append(code("""import duckdb
import pandas as pd
import os

# so plots appear inline
%matplotlib inline

# import our decoupled plotting module
from plot_helpers import (
    plot_bar, plot_horizontal_bar, plot_line, plot_multi_line,
    plot_histogram, plot_pie, plot_grouped_bar, plot_scatter,
    plot_stacked_bar,
)

print("All imports successful ✓")"""))

# ═══════════════════════════════════════════════════════════════════════════════
# CELL: Read CSV → DuckDB
# ═══════════════════════════════════════════════════════════════════════════════
cells.append(md("""## 1 — Load CSV into DuckDB

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
   - `day_of_week` — day name (Monday … Sunday)"""))

cells.append(code("""# ── 1a  Create / connect to the DuckDB file ──────────────────────────────────
DB_PATH = "taxi_rides.duckdb"

# Remove old DB so we start fresh each time this cell runs
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

con = duckdb.connect(DB_PATH)
print(f"Connected to {DB_PATH}")"""))

cells.append(code("""# ── 1b  Import CSV into a raw staging table ──────────────────────────────────
con.execute(\"\"\"
    CREATE OR REPLACE TABLE rides_raw AS
    SELECT * FROM read_csv_auto('taxi.csv', header=True);
\"\"\")
count = con.execute("SELECT COUNT(*) FROM rides_raw").fetchall()[0][0]
print(f"Imported {count:,} rows into rides_raw")"""))

cells.append(code("""# ── 1c  Rename columns, parse dates, add derived columns ──────────────────────
#
# NOTE: DuckDB's read_csv_auto already parsed the datetime columns as TIMESTAMP,
# so we use them directly — no strptime() needed.
con.execute(\"\"\"
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
\"\"\")

# Drop the raw staging table
con.execute("DROP TABLE rides_raw;")

count = con.execute("SELECT COUNT(*) FROM rides").fetchall()[0][0]
print(f"Table 'rides' created with {count:,} rows and derived columns ✓")"""))

cells.append(code("""# ── 1d  Quick look at the schema ──────────────────────────────────────────────
con.execute("DESCRIBE rides").df()"""))

cells.append(code("""# ── 1e  Preview the first 5 rows ─────────────────────────────────────────────
con.execute("SELECT * FROM rides LIMIT 5").df()"""))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: BASIC QUERIES (5)
# ═══════════════════════════════════════════════════════════════════════════════
cells.append(md("""---
## 2 — Basic Queries

These queries use the fundamental SQL building blocks: `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, and simple aggregates like `COUNT`.
"""))

# B1
cells.append(md("""### B1 — How many total rides are in the dataset?

The simplest aggregate: `COUNT(*)` returns the total number of rows."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT COUNT(*) AS total_rides
    FROM rides;
\"\"\").df()
df"""))

# B2
cells.append(md("""### B2 — What are the 10 longest trips by distance?

`ORDER BY … DESC` with `LIMIT` gives us a Top‑N query — one of the most common patterns in SQL."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT pickup_datetime, dropoff_datetime,
           trip_distance, fare_amount, total_amount
    FROM rides
    ORDER BY trip_distance DESC
    LIMIT 10;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=[f"Trip {i+1}" for i in range(len(df))],
    values=df["trip_distance"].tolist(),
    title="Top 10 Longest Trips by Distance",
    xlabel="Trip Rank", ylabel="Distance (miles)"
)"""))

# B3
cells.append(md("""### B3 — How many rides had exactly 1 passenger?

A `WHERE` filter narrows the dataset before the aggregate runs."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT COUNT(*) AS solo_rides
    FROM rides
    WHERE passenger_count = 1;
\"\"\").df()
df"""))

# B4
cells.append(md("""### B4 — What are the minimum, maximum, and average fare amounts?

Multiple aggregate functions in one SELECT — SQL can compute several summaries in a single pass."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT
        MIN(fare_amount) AS min_fare,
        MAX(fare_amount) AS max_fare,
        ROUND(AVG(fare_amount), 2) AS avg_fare
    FROM rides;
\"\"\").df()
df"""))

# B5
cells.append(md("""### B5 — Show 10 sample rides that cost more than $50

Combining `WHERE` with `LIMIT` lets us inspect a filtered subset without flooding the screen."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT pickup_datetime, trip_distance,
           fare_amount, tip_amount, total_amount
    FROM rides
    WHERE total_amount > 50
    ORDER BY total_amount DESC
    LIMIT 10;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=[str(t)[:16] for t in df["pickup_datetime"]],
    values=df["total_amount"].tolist(),
    title="10 Sample Rides Over $50",
    xlabel="Pickup Time", ylabel="Total Amount ($)",
    rotate_x=45, fmt_currency=True
)"""))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: BASIC+ QUERIES (10)
# ═══════════════════════════════════════════════════════════════════════════════
cells.append(md("""---
## 3 — Basic+ Queries

These queries introduce `GROUP BY`, aggregate functions on groups, `HAVING`, `DISTINCT`, `BETWEEN`, `IN`, and `CASE`.
"""))

# BP1
cells.append(md("""### BP1 — Total rides per passenger count

`GROUP BY` splits the table into groups; `COUNT(*)` counts each group. This shows the distribution of passengers per ride."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT passenger_count,
           COUNT(*) AS num_rides
    FROM rides
    GROUP BY passenger_count
    ORDER BY passenger_count;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=df["passenger_count"].astype(str).tolist(),
    values=df["num_rides"].tolist(),
    title="Rides by Passenger Count",
    xlabel="Passengers", ylabel="Number of Rides"
)"""))

# BP2
cells.append(md("""### BP2 — Average fare by payment type

Payment type is coded as integers (1=Credit Card, 2=Cash, 3=No Charge, 4=Dispute, 5=Unknown, 6=Voided).
We use `CASE` inside the `GROUP BY` to give them readable labels."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT
        CASE payment_type
            WHEN 1 THEN 'Credit Card'
            WHEN 2 THEN 'Cash'
            WHEN 3 THEN 'No Charge'
            WHEN 4 THEN 'Dispute'
            WHEN 5 THEN 'Unknown'
            WHEN 6 THEN 'Voided'
            ELSE 'Other'
        END AS payment_method,
        COUNT(*) AS num_rides,
        ROUND(AVG(fare_amount), 2) AS avg_fare
    FROM rides
    GROUP BY payment_type
    ORDER BY num_rides DESC;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=df["payment_method"].tolist(),
    values=df["avg_fare"].tolist(),
    title="Average Fare by Payment Method",
    xlabel="Payment Method", ylabel="Avg Fare ($)",
    fmt_currency=True
)"""))

# BP3
cells.append(md("""### BP3 — Average trip distance per vendor

Two vendor IDs are present (1 = Creative Mobile Technologies, 2 = VeriFone Inc.).
`GROUP BY vendor_id` compares them."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT vendor_id,
           COUNT(*) AS num_rides,
           ROUND(AVG(trip_distance), 2) AS avg_distance,
           ROUND(AVG(fare_amount), 2) AS avg_fare
    FROM rides
    GROUP BY vendor_id
    ORDER BY vendor_id;
\"\"\").df()
df"""))
cells.append(code("""plot_grouped_bar(
    labels=[f"Vendor {v}" for v in df["vendor_id"]],
    group_dict={
        "Avg Distance (mi)": df["avg_distance"].tolist(),
        "Avg Fare ($)": df["avg_fare"].tolist(),
    },
    title="Vendor Comparison",
    ylabel="Value"
)"""))

# BP4
cells.append(md("""### BP4 — Number of rides per day of the week

Using our derived `day_of_week` column with `GROUP BY` to see which days are busiest."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT day_of_week,
           COUNT(*) AS num_rides
    FROM rides
    GROUP BY day_of_week
    ORDER BY
        CASE day_of_week
            WHEN 'Monday'    THEN 1
            WHEN 'Tuesday'   THEN 2
            WHEN 'Wednesday' THEN 3
            WHEN 'Thursday'  THEN 4
            WHEN 'Friday'    THEN 5
            WHEN 'Saturday'  THEN 6
            WHEN 'Sunday'    THEN 7
        END;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=df["day_of_week"].tolist(),
    values=df["num_rides"].tolist(),
    title="Rides by Day of Week",
    xlabel="Day", ylabel="Number of Rides",
    rotate_x=30
)"""))

# BP5
cells.append(md("""### BP5 — Pickup locations with more than 2,000 rides (WHERE vs HAVING)

`WHERE` filters **rows before** grouping; `HAVING` filters **groups after** aggregation.
Here we need `HAVING` because we want to keep only locations whose *count* exceeds a threshold."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT pickup_location_id,
           COUNT(*) AS num_rides
    FROM rides
    GROUP BY pickup_location_id
    HAVING COUNT(*) > 2000
    ORDER BY num_rides DESC;
\"\"\").df()
df"""))
cells.append(code("""plot_horizontal_bar(
    labels=df["pickup_location_id"].astype(str).tolist(),
    values=df["num_rides"].tolist(),
    title="Busiest Pickup Locations (>2,000 rides)",
    xlabel="Number of Rides", ylabel="Location ID"
)"""))

# BP6
cells.append(md("""### BP6 — How many distinct pickup locations exist?

`COUNT(DISTINCT …)` counts unique values — useful for understanding cardinality."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT COUNT(DISTINCT pickup_location_id)  AS unique_pickup_locs,
           COUNT(DISTINCT drop_location_id)    AS unique_dropoff_locs
    FROM rides;
\"\"\").df()
df"""))

# BP7
cells.append(md("""### BP7 — Rides with fares between $10 and $20

`BETWEEN` is syntactic sugar for `>= AND <=`. Clean and readable."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT COUNT(*) AS rides_10_to_20
    FROM rides
    WHERE fare_amount BETWEEN 10 AND 20;
\"\"\").df()
df"""))

# BP8
cells.append(md("""### BP8 — Average tip percentage by passenger count

Combines our derived `tip_percentage` column with `GROUP BY` and `HAVING` to exclude groups with very few rides."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT passenger_count,
           COUNT(*) AS num_rides,
           ROUND(AVG(tip_percentage), 2) AS avg_tip_pct
    FROM rides
    WHERE passenger_count BETWEEN 1 AND 6
    GROUP BY passenger_count
    HAVING COUNT(*) > 100
    ORDER BY passenger_count;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=df["passenger_count"].astype(str).tolist(),
    values=df["avg_tip_pct"].tolist(),
    title="Average Tip % by Passenger Count",
    xlabel="Passengers", ylabel="Avg Tip %"
)"""))

# BP9
cells.append(md("""### BP9 — Rides paid with credit card vs. cash (using IN)

`IN (…)` is a concise alternative to multiple `OR` conditions."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT
        CASE payment_type
            WHEN 1 THEN 'Credit Card'
            WHEN 2 THEN 'Cash'
        END AS method,
        COUNT(*) AS num_rides,
        ROUND(SUM(total_amount), 2) AS total_revenue
    FROM rides
    WHERE payment_type IN (1, 2)
    GROUP BY payment_type
    ORDER BY num_rides DESC;
\"\"\").df()
df"""))
cells.append(code("""plot_pie(
    labels=df["method"].tolist(),
    values=df["num_rides"].tolist(),
    title="Credit Card vs Cash Rides"
)"""))

# BP10
cells.append(md("""### BP10 — Categorize trips by distance (Short / Medium / Long)

`CASE` expressions create computed categories on the fly — like adding a virtual column."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT
        CASE
            WHEN trip_distance < 2   THEN 'Short (<2 mi)'
            WHEN trip_distance < 10  THEN 'Medium (2–10 mi)'
            ELSE                          'Long (10+ mi)'
        END AS distance_category,
        COUNT(*) AS num_rides,
        ROUND(AVG(fare_amount), 2) AS avg_fare
    FROM rides
    GROUP BY distance_category
    ORDER BY avg_fare;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=df["distance_category"].tolist(),
    values=df["num_rides"].tolist(),
    title="Rides by Distance Category",
    xlabel="Category", ylabel="Number of Rides"
)"""))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: INTERMEDIATE QUERIES (10)
# ═══════════════════════════════════════════════════════════════════════════════
cells.append(md("""---
## 4 — Intermediate Queries

Window functions, subqueries, time‑based analytics, correlated filters, and more.
"""))

# I1
cells.append(md("""### I1 — Hourly ride volume (time‑based analytics)

Using `hour_of_day` to see when New Yorkers ride the most."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT hour_of_day,
           COUNT(*) AS num_rides
    FROM rides
    GROUP BY hour_of_day
    ORDER BY hour_of_day;
\"\"\").df()
df"""))
cells.append(code("""plot_line(
    x=df["hour_of_day"].tolist(),
    y=df["num_rides"].tolist(),
    title="Ride Volume by Hour of Day",
    xlabel="Hour (0–23)", ylabel="Number of Rides"
)"""))

# I2
cells.append(md("""### I2 — Running total of rides per hour (window function: SUM … OVER)

A **window function** computes a value across a set of rows related to the current row — without collapsing the result.
Here, `SUM(num_rides) OVER (ORDER BY hour_of_day)` produces a cumulative (running) total."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT hour_of_day,
           COUNT(*) AS num_rides,
           SUM(COUNT(*)) OVER (ORDER BY hour_of_day) AS running_total
    FROM rides
    GROUP BY hour_of_day
    ORDER BY hour_of_day;
\"\"\").df()
df"""))
cells.append(code("""plot_multi_line(
    x=df["hour_of_day"].tolist(),
    y_dict={
        "Rides This Hour": df["num_rides"].tolist(),
        "Running Total": df["running_total"].tolist(),
    },
    title="Hourly Rides with Running Total",
    xlabel="Hour of Day", ylabel="Count"
)"""))

# I3
cells.append(md("""### I3 — Trip distance distribution (histogram via SQL buckets)

We can create histogram buckets in SQL with `FLOOR(trip_distance)` and then plot the distribution."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT FLOOR(trip_distance) AS distance_bucket,
           COUNT(*) AS num_rides
    FROM rides
    WHERE trip_distance BETWEEN 0 AND 20
    GROUP BY distance_bucket
    ORDER BY distance_bucket;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=df["distance_bucket"].astype(int).astype(str).tolist(),
    values=df["num_rides"].tolist(),
    title="Trip Distance Distribution (0–20 miles)",
    xlabel="Distance (miles, floored)", ylabel="Number of Rides"
)"""))

# I4
cells.append(md("""### I4 — Average fare per mile by hour of day

Dividing fare by distance gives a "price per mile" metric. We exclude very short trips (< 0.5 mi) to avoid division noise."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT hour_of_day,
           ROUND(AVG(fare_amount / trip_distance), 2) AS avg_fare_per_mile
    FROM rides
    WHERE trip_distance >= 0.5
    GROUP BY hour_of_day
    ORDER BY hour_of_day;
\"\"\").df()
df"""))
cells.append(code("""plot_line(
    x=df["hour_of_day"].tolist(),
    y=df["avg_fare_per_mile"].tolist(),
    title="Average Fare per Mile by Hour",
    xlabel="Hour of Day", ylabel="$/mile"
)"""))

# I5
cells.append(md("""### I5 — Top 5 busiest pickup → drop‑off routes

Combining two `GROUP BY` columns reveals popular origin–destination pairs."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT pickup_location_id,
           drop_location_id,
           COUNT(*) AS num_rides,
           ROUND(AVG(trip_distance), 2) AS avg_distance,
           ROUND(AVG(total_amount), 2)  AS avg_total
    FROM rides
    GROUP BY pickup_location_id, drop_location_id
    ORDER BY num_rides DESC
    LIMIT 5;
\"\"\").df()
df"""))
cells.append(code("""plot_horizontal_bar(
    labels=[f"{r.pickup_location_id} → {r.drop_location_id}" for _, r in df.iterrows()],
    values=df["num_rides"].tolist(),
    title="Top 5 Busiest Routes",
    xlabel="Number of Rides", ylabel="Route (Pickup → Dropoff)"
)"""))

# I6
cells.append(md("""### I6 — Percentage of rides per payment type (window function: ratio)

`COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()` computes each group's share of the grand total — a window aggregate over the entire result set."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT
        CASE payment_type
            WHEN 1 THEN 'Credit Card'
            WHEN 2 THEN 'Cash'
            WHEN 3 THEN 'No Charge'
            WHEN 4 THEN 'Dispute'
            ELSE 'Other'
        END AS payment_method,
        COUNT(*) AS num_rides,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_total
    FROM rides
    GROUP BY payment_type
    ORDER BY num_rides DESC;
\"\"\").df()
df"""))
cells.append(code("""plot_pie(
    labels=df["payment_method"].tolist(),
    values=df["num_rides"].tolist(),
    title="Ride Share by Payment Method"
)"""))

# I7
cells.append(md("""### I7 — Trips where the tip exceeded the fare (subquery filter)

A subquery in the `WHERE` clause identifies unusual rides where passengers tipped more than the fare itself."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT pickup_datetime, trip_distance,
           fare_amount, tip_amount, tip_percentage
    FROM rides
    WHERE tip_amount > fare_amount
      AND fare_amount > 0
    ORDER BY tip_percentage DESC
    LIMIT 10;
\"\"\").df()
df"""))

# I8
cells.append(md("""### I8 — Hour-by-hour average duration and distance (multi-metric time series)

Grouping by `hour_of_day` and computing several averages gives a rich picture of how trips differ throughout the day."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT hour_of_day,
           ROUND(AVG(trip_duration_minutes), 2) AS avg_duration,
           ROUND(AVG(trip_distance), 2)         AS avg_distance,
           ROUND(AVG(total_amount), 2)          AS avg_total
    FROM rides
    WHERE trip_duration_minutes > 0
    GROUP BY hour_of_day
    ORDER BY hour_of_day;
\"\"\").df()
df"""))
cells.append(code("""plot_multi_line(
    x=df["hour_of_day"].tolist(),
    y_dict={
        "Avg Duration (min)": df["avg_duration"].tolist(),
        "Avg Distance (mi)": df["avg_distance"].tolist(),
    },
    title="Trip Duration & Distance by Hour",
    xlabel="Hour of Day", ylabel="Value"
)"""))

# I9
cells.append(md("""### I9 — Fare vs. distance scatter (do fares follow distance?)

This query extracts a sample of 5,000 rides so we can plot fare vs. distance and visually check the relationship."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT trip_distance, fare_amount
    FROM rides
    WHERE trip_distance BETWEEN 0.5 AND 30
      AND fare_amount BETWEEN 2.5 AND 200
    USING SAMPLE 5000;
\"\"\").df()
df.head()"""))
cells.append(code("""plot_scatter(
    x=df["trip_distance"].tolist(),
    y=df["fare_amount"].tolist(),
    title="Fare vs. Trip Distance (5,000 sample)",
    xlabel="Distance (miles)", ylabel="Fare ($)"
)"""))

# I10
cells.append(md("""### I10 — Day‑of‑week × hour heatmap data (two‑dimensional GROUP BY)

Grouping by **two** time dimensions produces a matrix. We pivot it in pandas for a quick heatmap."""))
cells.append(code("""df = con.execute(\"\"\"
    SELECT day_of_week, hour_of_day,
           COUNT(*) AS num_rides
    FROM rides
    GROUP BY day_of_week, hour_of_day
    ORDER BY
        CASE day_of_week
            WHEN 'Monday'    THEN 1
            WHEN 'Tuesday'   THEN 2
            WHEN 'Wednesday' THEN 3
            WHEN 'Thursday'  THEN 4
            WHEN 'Friday'    THEN 5
            WHEN 'Saturday'  THEN 6
            WHEN 'Sunday'    THEN 7
        END,
        hour_of_day;
\"\"\").df()

# Pivot for heatmap
import matplotlib.pyplot as plt
pivot = df.pivot(index="day_of_week", columns="hour_of_day", values="num_rides")
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
pivot = pivot.reindex(day_order)

fig, ax = plt.subplots(figsize=(14, 5))
im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd")
ax.set_xticks(range(24))
ax.set_xticklabels(range(24))
ax.set_yticks(range(7))
ax.set_yticklabels(day_order)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Day of Week")
ax.set_title("Ride Volume: Day of Week × Hour of Day", fontweight="bold")
plt.colorbar(im, ax=ax, label="Number of Rides")
plt.tight_layout()
plt.show()"""))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: RANKING FUNCTION QUERIES (5)
# ═══════════════════════════════════════════════════════════════════════════════
cells.append(md("""---
## 5 — Ranking Function Queries (CTEs + Window Rankings)

These queries use **Common Table Expressions** (`WITH`) and ranking window functions:
`ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `NTILE()`, and `PERCENT_RANK()`.
"""))

# R1
cells.append(md("""### R1 — Top 3 pickup locations by ride volume (ROW_NUMBER)

`ROW_NUMBER()` assigns a unique sequential integer to each row within a partition.
We use a CTE (`WITH`) to first compute counts, then filter to the top 3."""))
cells.append(code("""df = con.execute(\"\"\"
    WITH location_counts AS (
        SELECT pickup_location_id,
               COUNT(*) AS num_rides,
               ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rn
        FROM rides
        GROUP BY pickup_location_id
    )
    SELECT pickup_location_id, num_rides, rn
    FROM location_counts
    WHERE rn <= 3;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=df["pickup_location_id"].astype(str).tolist(),
    values=df["num_rides"].tolist(),
    title="Top 3 Pickup Locations (ROW_NUMBER)",
    xlabel="Location ID", ylabel="Number of Rides"
)"""))

# R2
cells.append(md("""### R2 — Rank hours by average fare with ties (RANK vs DENSE_RANK)

`RANK()` leaves gaps after ties; `DENSE_RANK()` does not.
This query shows both side‑by‑side so students can compare."""))
cells.append(code("""df = con.execute(\"\"\"
    WITH hourly_fares AS (
        SELECT hour_of_day,
               ROUND(AVG(fare_amount), 2) AS avg_fare
        FROM rides
        GROUP BY hour_of_day
    )
    SELECT hour_of_day,
           avg_fare,
           RANK()       OVER (ORDER BY avg_fare DESC) AS fare_rank,
           DENSE_RANK() OVER (ORDER BY avg_fare DESC) AS fare_dense_rank
    FROM hourly_fares
    ORDER BY fare_rank
    LIMIT 10;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=df["hour_of_day"].astype(str).tolist(),
    values=df["avg_fare"].tolist(),
    title="Top 10 Hours by Average Fare (Ranked)",
    xlabel="Hour of Day", ylabel="Avg Fare ($)",
    fmt_currency=True
)"""))

# R3
cells.append(md("""### R3 — Divide trips into 4 fare quartiles (NTILE)

`NTILE(4)` splits the ordered data into four roughly equal groups — quartiles.
We then summarize each quartile."""))
cells.append(code("""df = con.execute(\"\"\"
    WITH quartiled AS (
        SELECT fare_amount,
               trip_distance,
               tip_percentage,
               NTILE(4) OVER (ORDER BY fare_amount) AS fare_quartile
        FROM rides
        WHERE fare_amount > 0
    )
    SELECT fare_quartile,
           COUNT(*)                         AS num_rides,
           ROUND(MIN(fare_amount), 2)       AS min_fare,
           ROUND(MAX(fare_amount), 2)       AS max_fare,
           ROUND(AVG(fare_amount), 2)       AS avg_fare,
           ROUND(AVG(trip_distance), 2)     AS avg_distance,
           ROUND(AVG(tip_percentage), 2)    AS avg_tip_pct
    FROM quartiled
    GROUP BY fare_quartile
    ORDER BY fare_quartile;
\"\"\").df()
df"""))
cells.append(code("""plot_grouped_bar(
    labels=[f"Q{q}" for q in df["fare_quartile"]],
    group_dict={
        "Avg Fare ($)": df["avg_fare"].tolist(),
        "Avg Distance (mi)": df["avg_distance"].tolist(),
        "Avg Tip %": df["avg_tip_pct"].tolist(),
    },
    title="Fare Quartile Comparison (NTILE)",
    ylabel="Value"
)"""))

# R4
cells.append(md("""### R4 — Percentile ranking of pickup locations (PERCENT_RANK)

`PERCENT_RANK()` returns a value between 0 and 1 indicating where each row stands relative to all other rows.
Locations with a `pct_rank` near 1.0 are the busiest."""))
cells.append(code("""df = con.execute(\"\"\"
    WITH loc_stats AS (
        SELECT pickup_location_id,
               COUNT(*) AS num_rides,
               ROUND(PERCENT_RANK() OVER (ORDER BY COUNT(*)), 4) AS pct_rank
        FROM rides
        GROUP BY pickup_location_id
    )
    SELECT *
    FROM loc_stats
    WHERE pct_rank >= 0.95
    ORDER BY pct_rank DESC;
\"\"\").df()
df"""))
cells.append(code("""plot_horizontal_bar(
    labels=df["pickup_location_id"].astype(str).tolist(),
    values=df["num_rides"].tolist(),
    title="Top 5% Pickup Locations (PERCENT_RANK ≥ 0.95)",
    xlabel="Number of Rides", ylabel="Location ID"
)"""))

# R5
cells.append(md("""### R5 — Top earner per day of week (CTE + ROW_NUMBER partition)

This query finds the single highest‑earning pickup location for each day of the week.
`ROW_NUMBER() … PARTITION BY day_of_week` restarts the numbering within each day, and we keep only rank 1."""))
cells.append(code("""df = con.execute(\"\"\"
    WITH daily_revenue AS (
        SELECT day_of_week,
               pickup_location_id,
               ROUND(SUM(total_amount), 2) AS total_rev,
               ROW_NUMBER() OVER (
                   PARTITION BY day_of_week
                   ORDER BY SUM(total_amount) DESC
               ) AS rn
        FROM rides
        GROUP BY day_of_week, pickup_location_id
    )
    SELECT day_of_week, pickup_location_id, total_rev
    FROM daily_revenue
    WHERE rn = 1
    ORDER BY
        CASE day_of_week
            WHEN 'Monday'    THEN 1
            WHEN 'Tuesday'   THEN 2
            WHEN 'Wednesday' THEN 3
            WHEN 'Thursday'  THEN 4
            WHEN 'Friday'    THEN 5
            WHEN 'Saturday'  THEN 6
            WHEN 'Sunday'    THEN 7
        END;
\"\"\").df()
df"""))
cells.append(code("""plot_bar(
    labels=[f"{r.day_of_week}\\n(Loc {r.pickup_location_id})" for _, r in df.iterrows()],
    values=df["total_rev"].tolist(),
    title="Top Earning Location per Day of Week",
    xlabel="Day (Location)", ylabel="Total Revenue ($)",
    rotate_x=30, fmt_currency=True
)"""))

# ═══════════════════════════════════════════════════════════════════════════════
# CLOSING
# ═══════════════════════════════════════════════════════════════════════════════
cells.append(md("""---
## Summary of SQL Concepts Covered

| Section | Concepts |
|---------|----------|
| **Basic** | `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `COUNT`, `MIN`, `MAX`, `AVG` |
| **Basic+** | `GROUP BY`, `HAVING`, `DISTINCT`, `BETWEEN`, `IN`, `CASE`, `SUM` |
| **Intermediate** | Window functions (`SUM OVER`, ratio), subqueries, time analytics, multi-column `GROUP BY`, sampling |
| **Ranking** | `WITH` (CTEs), `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `PERCENT_RANK`, `PARTITION BY` |

---
*Notebook generated for MSIS-2402 — Database Management Systems - Fundamentals of SQL, Santa Clara University.*"""))

cells.append(code("""# Close the DuckDB connection
con.close()
print("Connection closed ✓")"""))

# ═══════════════════════════════════════════════════════════════════════════════
# ASSEMBLE NOTEBOOK
# ═══════════════════════════════════════════════════════════════════════════════
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        }
    },
    "cells": cells,
}

out_path = "taxi_rides_queries.ipynb"
with open(out_path, "w") as f:
    json.dump(nb, f, indent=1)

print(f"Wrote {len(cells)} cells to {out_path}")
