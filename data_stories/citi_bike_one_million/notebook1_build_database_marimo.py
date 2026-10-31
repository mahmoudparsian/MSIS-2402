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
    # Notebook 1: Build the Citi Bike DuckDB Database

    This notebook reads the raw `citibike_tutorial.csv` file (1,001,032 rows) and creates a clean, 
    analysis-ready DuckDB database called `citibike.duckdb`.

    **Steps:**
    1. Load the CSV into DuckDB
    2. Rename columns for consistency (snake_case)
    3. Add derived columns (ride duration in minutes, day of week, hour, month, year, age, distance)
    4. Standardize date formats
    5. Explore deduplication (explain the concept — but keep the full dataset for richer analysis)
    6. Verify the final table
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup: Install and Import Libraries
    """)
    return


@app.cell
def _():
    # Install duckdb if not already installed
    # !pip install duckdb

    import duckdb
    import os

    # Path configuration
    CSV_FILE = 'citibike_tutorial.csv'
    DB_FILE  = 'citibike.duckdb'

    # Remove old database if it exists (fresh start)
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f'Removed old {DB_FILE}')

    print('Setup complete.')
    return CSV_FILE, DB_FILE, duckdb, os


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 1: Load the CSV into DuckDB

    We read `citibike_tutorial.csv` directly into a DuckDB table called `rides_raw`.  
    DuckDB's CSV reader automatically infers column types and handles the header row.
    """)
    return


@app.cell
def _(CSV_FILE, DB_FILE, duckdb):
    # Connect to a persistent DuckDB database file
    con = duckdb.connect(DB_FILE)

    # Load the CSV into a raw staging table
    con.execute(f"""
        CREATE TABLE rides_raw AS
        SELECT * FROM read_csv_auto('{CSV_FILE}', header=True, sample_size=10000);
    """)

    # Check how many rows were loaded
    _row_count = con.execute("SELECT COUNT(*) FROM rides_raw").fetchall()[0][0]
    print(f'Loaded {_row_count:,} rows into rides_raw')

    # Preview the first 5 rows
    con.execute("SELECT * FROM rides_raw LIMIT 5").df()
    return (con,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 2: Inspect the Raw Schema

    Let's look at the column names and data types DuckDB inferred.  
    This helps us plan the renaming and type conversions.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        DESCRIBE rides_raw
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 3: Check Date Formats

    The `starttime` and `stoptime` columns were loaded as `VARCHAR` (strings).  
    The format is `M/D/YY H:MM` (e.g., `11/20/13 20:21` means November 20, 2013 at 8:21 PM).  

    We cannot use `CAST(... AS TIMESTAMP)` because DuckDB doesn't recognize this format automatically.  
    Instead, we'll use `STRPTIME(col, '%m/%d/%y %H:%M')` to explicitly parse it.
    """)
    return


@app.cell
def _(con, mo, rides_raw):
    _df = mo.sql(
        f"""
        SELECT
            starttime,
            LENGTH(starttime::VARCHAR) AS len
        FROM rides_raw
        WHERE starttime IS NOT NULL
        ORDER BY len
        LIMIT 10
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo, rides_raw):
    _df = mo.sql(
        f"""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(starttime) AS non_null_starttime,
            COUNT(*) - COUNT(starttime) AS null_starttime
        FROM rides_raw;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 4: Create the Clean `rides` Table

    In this step we:

    1. **Rename columns** to consistent snake_case:
       - `tripduration` -> `trip_duration`
       - `starttime` -> `start_time`
       - `stoptime` -> `stop_time`
       - `bikeid` -> `bike_id`
       - `usertype` -> `user_type`

    2. **Standardize date columns** using `STRPTIME` to parse `M/D/YY H:MM` into proper TIMESTAMPs  
       - Why `STRPTIME` instead of `CAST`? Because `CAST(... AS TIMESTAMP)` cannot handle the  
         `M/D/YY H:MM` format — it expects ISO 8601 (`YYYY-MM-DD HH:MM:SS`).  
       - `STRPTIME` lets us specify the **exact format**: `%m/%d/%y %H:%M`  
         (`%m` = month, `%d` = day, `%y` = 2-digit year, `%H` = hour, `%M` = minute)

    3. **Add derived columns** for easier analysis:
       - `trip_duration_min` — duration in minutes (more human-readable)
       - `start_hour` — hour of day the trip started (0-23)
       - `start_day_of_week` — day name (Monday, Tuesday, ...)
       - `start_month` — month number (1-12)
       - `start_year` — year of the trip
       - `rider_age` — approximate age at time of ride (year - birth_year)
       - `distance_km` — approximate straight-line distance using the Haversine formula
    """)
    return


@app.cell
def _(con):
    con.execute("""
        CREATE TABLE rides AS
        SELECT
            -- Renamed columns
            tripduration                                          AS trip_duration,
            STRPTIME(starttime, '%m/%d/%y %H:%M')                AS start_time,
            STRPTIME(stoptime,  '%m/%d/%y %H:%M')                AS stop_time,
            start_station_id,
            start_station_name,
            start_station_latitude,
            start_station_longitude,
            end_station_id,
            end_station_name,
            end_station_latitude,
            end_station_longitude,
            bikeid                                                AS bike_id,
            usertype                                              AS user_type,
            birth_year,
            gender,

            -- Derived: duration in minutes
            ROUND(tripduration / 60.0, 2)                        AS trip_duration_min,

            -- Derived: time parts
            EXTRACT(HOUR  FROM STRPTIME(starttime, '%m/%d/%y %H:%M'))  AS start_hour,
            DAYNAME(STRPTIME(starttime, '%m/%d/%y %H:%M'))             AS start_day_of_week,
            EXTRACT(MONTH FROM STRPTIME(starttime, '%m/%d/%y %H:%M'))  AS start_month,
            EXTRACT(YEAR  FROM STRPTIME(starttime, '%m/%d/%y %H:%M'))  AS start_year,

            -- Derived: rider age (approximate)
            CASE
                WHEN birth_year IS NOT NULL AND birth_year > 1900
                THEN EXTRACT(YEAR FROM STRPTIME(starttime, '%m/%d/%y %H:%M')) - birth_year
                ELSE NULL
            END                                                  AS rider_age,

            -- Derived: straight-line distance in km (Haversine formula)
            ROUND(
                2 * 6371 * ASIN(SQRT(
                    POWER(SIN(RADIANS(end_station_latitude - start_station_latitude) / 2), 2) +
                    COS(RADIANS(start_station_latitude)) *
                    COS(RADIANS(end_station_latitude)) *
                    POWER(SIN(RADIANS(end_station_longitude - start_station_longitude) / 2), 2)
                )),
            3)                                                   AS distance_km

        FROM rides_raw;
    """)

    _row_count = con.execute("SELECT COUNT(*) FROM rides").fetchall()[0][0]
    print(f'Created rides table with {_row_count:,} rows')

    # Preview
    con.execute("SELECT * FROM rides LIMIT 5").df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 5: Verify the Clean Schema
    """)
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 6: Exploring Deduplication (Concept Only)

    ### What is deduplication?

    Deduplication means **removing rows that are exact copies** of each other.  
    This can happen when CSV files are appended multiple times or data pipelines re-process records.

    ### How would we do it?

    The standard SQL approach is `SELECT DISTINCT *`, which keeps **one copy** of each unique  
    row and discards all duplicates.

    ```sql
    -- Example: creating a deduplicated table
    CREATE TABLE rides_deduped AS
    SELECT DISTINCT * FROM rides;
    ```

    ### Why we are NOT deduplicating this dataset

    This tutorial CSV was built by repeating a smaller set of ~10,000 unique rides many times  
    to reach ~1,000,000 rows. If we applied `SELECT DISTINCT *`, we'd go from **~1M rows  
    down to only ~10,000** — losing 99% of our data!

    For a **teaching dataset**, keeping the full 1M rows is preferable because:
    - Aggregations (`GROUP BY`, window functions) produce richer, more realistic results
    - The duplicates don't distort *ratios* or *averages* — they inflate counts proportionally
    - Working with 1M rows gives a better feel for real-world SQL performance

    Let's **measure** the duplication so we understand it, but leave the table as-is.
    """)
    return


@app.cell
def _(con):
    # Count total rows vs distinct rows to measure duplication
    total    = con.execute("SELECT COUNT(*) FROM rides").fetchall()[0][0]
    distinct = con.execute("SELECT COUNT(*) FROM (SELECT DISTINCT * FROM rides)").fetchall()[0][0]
    dupes    = total - distinct

    print(f'Total rows:          {total:>12,}')
    print(f'Distinct rows:       {distinct:>12,}')
    print(f'Duplicate rows:      {dupes:>12,}')
    print(f'Duplication ratio:   {total / distinct:.1f}x')
    print()
    print('NOTE: We are keeping ALL rows for analysis purposes.')
    print('      The duplicates do not affect ratios or averages.')
    return


@app.cell
def _(con):
    # Drop the raw staging table (no longer needed)
    con.execute("DROP TABLE rides_raw;")

    final_count = con.execute("SELECT COUNT(*) FROM rides").fetchall()[0][0]
    print(f'Final rides table: {final_count:,} rows (full dataset retained)')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 7: Verify Date Standardization

    Let's confirm all dates are proper TIMESTAMPs by checking the min/max values  
    and ensuring there are no NULLs from failed parsing.
    """)
    return


@app.cell
def _(con, mo, rides):
    _df = mo.sql(
        f"""
        SELECT
            MIN(start_time) AS earliest_ride,
            MAX(start_time) AS latest_ride,
            COUNT(*) FILTER(WHERE start_time IS NULL) AS null_start_times,
            COUNT(*) FILTER(WHERE stop_time IS NULL) AS null_stop_times
        FROM rides;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 8: Quick Summary Statistics

    A final sanity check on the clean data.
    """)
    return


@app.cell
def _(con, mo, rides):
    _df = mo.sql(
        f"""
        SELECT
            COUNT(*) AS total_rides,
            COUNT(DISTINCT bike_id) AS unique_bikes,
            COUNT(DISTINCT start_station_id) AS unique_start_stations,
            COUNT(DISTINCT end_station_id) AS unique_end_stations,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min,
            ROUND(AVG(distance_km), 3) AS avg_distance_km,
            MIN(start_year) AS first_year,
            MAX(start_year) AS last_year
        FROM rides;
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SHOW TABLES
        """,
        engine=con
    )
    return


@app.cell
def _(DB_FILE, con, os):
    # Close the connection — the database file is now saved
    con.close()
    print(f'Database saved to: {DB_FILE}')
    print(f'File size: {os.path.getsize(DB_FILE) / (1024*1024):.1f} MB')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Done!

    The `citibike.duckdb` database is ready. It contains one clean table called `rides` with:
    - Original columns renamed to snake_case
    - Timestamps standardized as proper `TIMESTAMP` types via `STRPTIME`
    - Derived columns for duration (minutes), time parts, rider age, and distance
    - Full ~1M row dataset retained (deduplication explained but not applied)

    **Next:** Open `notebook2_analyze_data_marimo.py` to run SQL queries against this database.
    """)
    return


if __name__ == "__main__":
    app.run()

