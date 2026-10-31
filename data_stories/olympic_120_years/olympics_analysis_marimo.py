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
    # 🏅 Olympics 120 Years — DuckDB SQL Analysis
    **Dataset:** `data/athlete_events.csv`  (271 116 rows, 15 columns)  
    **Engine:** DuckDB (in-process, file-backed)  
    **Plotting:** `plotting_utils.py` (decoupled helper module)  

    ---
    """)
    return


@app.cell
def _():
    import sys, os
    import duckdb
    import pandas as pd
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.abspath('.'))
    import plotting_utils as pu

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 30)
    pd.set_option('display.float_format', '{:,.2f}'.format)
    print('✓ Imports OK')
    return duckdb, plt, pu


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup — Load CSV, Lowercase Columns, De-duplicate
    """)
    return


@app.cell
def _(display, duckdb):
    DB_PATH  = 'olympics_120_years.duckdb'
    CSV_PATH = 'data/athlete_events.csv'

    con = duckdb.connect(DB_PATH)
    print(f'✓ Connected to {DB_PATH}')

    # ── Drop and recreate table with lowercase column names ──────────────────
    con.execute('DROP TABLE IF EXISTS athlete_events')

    tmp = con.execute(f"SELECT * FROM read_csv_auto('{CSV_PATH}') LIMIT 0").df()
    orig_cols  = list(tmp.columns)
    lower_cols = [c.lower() for c in orig_cols]
    rename_sql = ', '.join(f'"{o}" AS {l}' for o, l in zip(orig_cols, lower_cols))

    con.execute(f'''
        CREATE TABLE athlete_events AS
        SELECT {rename_sql}
        FROM read_csv_auto(\'{CSV_PATH}\')
    ''')
    print(f'✓ Table created. Columns: {lower_cols}')

    # ── De-duplicate ─────────────────────────────────────────────────────────
    before = con.execute('SELECT COUNT(*) FROM athlete_events').fetchall()[0][0]
    con.execute('''
        CREATE OR REPLACE TABLE athlete_events AS
        SELECT DISTINCT * FROM athlete_events
    ''')
    after  = con.execute('SELECT COUNT(*) FROM athlete_events').fetchall()[0][0]
    print(f'✓ De-dup: {before:,} → {after:,} rows  ({before-after:,} duplicates removed)')

    schema = con.execute('DESCRIBE athlete_events').df()
    print('\nSchema:')
    display(schema)
    return (con,)


@app.cell
def _(athlete_events, con, mo):
    sample = mo.sql(
        f"""
        SELECT *
        FROM athlete_events
        LIMIT 5
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part 1 — Basic Queries (5)
    Straightforward counts and lists to get oriented in the dataset.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query B1: Total Number of Records

    Count every row in the cleaned table to confirm the dataset size after de-duplication.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    _df = mo.sql(
        f"""
        SELECT COUNT(*) AS total_rows
        FROM athlete_events
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query B2: All Unique Sports

    List every distinct sport ever contested at the Olympics, sorted alphabetically.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    _df = mo.sql(
        f"""
        SELECT DISTINCT sport
        FROM athlete_events
        ORDER BY sport
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query B3: Athlete Entries by Gender (male/female)

    How many athlete-event entries belong to male versus female athletes?
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df = mo.sql(
        f"""
        SELECT
            sex,
            COUNT(*) AS entries
        FROM athlete_events
        GROUP BY sex
        ORDER BY entries DESC
        """,
        engine=con
    )
    return (df,)


@app.cell
def _(df, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.pie(df, values="entries", labels="sex", title="Athlete Entries by Sex")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query B4: Top 10 Countries by Total Medals

    Which 10 NOCs have accumulated the most medals (Gold + Silver + Bronze combined)?
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_2 = mo.sql(
        f"""
        SELECT
            noc,
            COUNT(*) AS total_medals
        FROM athlete_events
        WHERE medal IN ('Gold', 'Silver', 'Bronze')
        GROUP BY noc
        ORDER BY total_medals DESC
        LIMIT 10
        """,
        engine=con
    )
    return (df_2,)


@app.cell
def _(df_2, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_h(df_2, x="total_medals", y="noc",
             title="Top 10 Countries by Total Medals",
             xlabel="Total Medals", ylabel="NOC")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query B5: Number of Olympics by Season

    How many distinct Games exist in the dataset for Summer vs Winter?
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_3 = mo.sql(
        f"""
        SELECT
            season,
            COUNT(DISTINCT games) AS num_games,
            MIN(year) AS first_year,
            MAX(year) AS last_year
        FROM athlete_events
        GROUP BY season
        ORDER BY season
        """,
        engine=con
    )
    return (df_3,)


@app.cell
def _(df_3, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_v(df_3, x="season", y="num_games",
             title="Number of Olympic Games by Season",
             xlabel="Season", ylabel="Count", rotate=0)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part 2 — Basic+ Queries (10)
    Single-table aggregations, rankings, and filters that go a step beyond simple counts.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query BP1: Count Unique Athletes

    Separate individual people from entries — how many distinct athletes (by ID) appear?
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    _df = mo.sql(
        f"""
        SELECT COUNT(DISTINCT id) AS unique_athletes
        FROM athlete_events
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query BP2: Average Age by Gender (male/female)

    Compare mean, min, and max age for male and female athletes.
    """)
    return


@app.cell
def _(con, display):
    # This query is intentionally left broken — see the markdown cell right
    # below for the explanation and the fix. `age` was read from the CSV as
    # VARCHAR (because of literal 'NA' strings), so AVG()/MIN()/MAX() can't
    # run on it. In the original Jupyter notebook this cell's traceback was
    # simply displayed inline without stopping the notebook; running as a
    # marimo *script* would otherwise abort at the first uncaught exception,
    # so the error is caught and printed here instead, matching what the
    # student would have seen in Jupyter.
    SQL_BROKEN = """
        SELECT
            sex,
            ROUND(AVG(age), 2) AS avg_age,
            MIN(age) AS min_age,
            MAX(age) AS max_age
        FROM athlete_events
        WHERE age IS NOT NULL
        GROUP BY sex
        ORDER BY sex
    """
    print("SQL:")
    print(SQL_BROKEN)
    try:
        _df = con.execute(SQL_BROKEN).df()
        display(_df)
    except Exception as e:
        print(f"❌ Query failed as expected: {type(e).__name__}: {e}")
    return (athlete_events,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### ✅ Fix for Query BP2 — `BinderException: avg(VARCHAR)`

    **Why did In[13] fail?**  
    `read_csv_auto` inferred `age` as **VARCHAR** because the raw CSV contains the literal
    string `'NA'` (not a SQL NULL) for missing values.  DuckDB cannot apply `AVG()` to a text column.

    **The fix:** use `TRY_CAST(age AS DOUBLE)` inside every numeric function that touches
    `age`, `height`, or `weight`. `TRY_CAST` silently returns `NULL` for non-numeric
    strings (like `'NA'`), so `AVG()` / `MIN()` / `MAX()` ignore them automatically —
    no `WHERE` filter needed.

    > **Teaching note:** a production-grade solution is to fix the column type at load
    > time (see the *Permanent Fix* cell below). The query-level cast shown here is the
    > minimal, self-contained repair.
    """)
    return


@app.cell
def _(con, display):
    # ── Fix for BP2: AVG on a VARCHAR column (age / height / weight read as text) ─
    #
    # Root cause:  read_csv_auto saw 'NA' strings → inferred column type as VARCHAR.
    # Solution:    TRY_CAST converts 'NA' → NULL so numeric aggregates work correctly.

    SQL_FIX = """
        SELECT
            sex,
            ROUND(AVG(TRY_CAST(age AS DOUBLE)), 2)  AS avg_age,
            MIN(TRY_CAST(age AS INTEGER))            AS min_age,
            MAX(TRY_CAST(age AS INTEGER))            AS max_age
        FROM   athlete_events
        GROUP BY sex
        ORDER BY sex
    """
    print('SQL (fixed):')
    print(SQL_FIX)

    df_fix = con.execute(SQL_FIX).df()
    display(df_fix)

    # ── Permanent fix: alter the table so all downstream queries work without casts ─
    con.execute("""
        CREATE OR REPLACE TABLE athlete_events AS
        SELECT
            id, name, sex,
            TRY_CAST(age    AS INTEGER) AS age,
            TRY_CAST(height AS DOUBLE)  AS height,
            TRY_CAST(weight AS DOUBLE)  AS weight,
            team, noc, games,
            TRY_CAST(year AS INTEGER)   AS year,
            season, city, sport, event, medal
        FROM athlete_events
    """)
    print('✓ Permanent fix applied — age/height/weight are now typed correctly.')
    print('  All subsequent queries will work without explicit casts.')

    return (df_fix,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### ✅ Fix for In[15] — `KeyError: 'sex'`

    **Why did the plot cell fail?**  
    In[13] raised a `BinderException` *before* the assignment `df = ...` could complete,
    so `df` was never updated. Python kept the previous value of `df` — the BP1 result,
    which has only one column (`unique_athletes`). When the plot cell ran `df['sex']`,
    that column simply didn't exist.

    **The fix:** reference `df_fix` — the correctly-typed result produced by the In[14]
    fix cell — instead of the stale `df`.

    > **Teaching note:** this is a classic Jupyter state pitfall. Variables are shared
    > across all cells in the kernel session. A cell that raises an exception mid-way
    > leaves variables in whatever state they were *before* the crash, not in the state
    > you might expect from reading the cell's code top-to-bottom.
    """)
    return


@app.cell
def _(df_fix, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    # Note: uses df_fix (from the In[14] fix cell) because In[13] crashed before
    #       df could be assigned — df_fix holds the correctly-typed query result.
    pu.bar_v(df_fix, x="sex", y="avg_age",
             title="Average Age of Athletes by Gender",
             xlabel="Sex", ylabel="Average Age (years)", rotate=0)
    return


@app.cell
def _(df_fix, pu):
    # ── Fix for In[15] plot: use df_fix (from the In[14] fix cell) ───────────────
    # df_fix has the correctly-typed columns: sex, avg_age, min_age, max_age

    pu.bar_v(
        df_fix,
        x="sex",
        y="avg_age",
        title="Average Age of Athletes by Gender (fixed)",
        xlabel="Sex",
        ylabel="Average Age (years)",
        rotate=0,
    )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query BP3: Medal Distribution — Gold / Silver / Bronze

    How many of each medal type have been awarded across all Games?
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_4 = mo.sql(
        f"""
        SELECT
            medal,
            COUNT(*) AS total
        FROM athlete_events
        WHERE medal IN ('Gold', 'Silver', 'Bronze')
        GROUP BY medal
        ORDER BY CASE medal WHEN 'Gold' THEN 1 WHEN 'Silver' THEN 2 WHEN 'Bronze' THEN 3 END
        """,
        engine=con
    )
    return (df_4,)


@app.cell
def _(df_4, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    colors = ["gold", "silver", "#cd7f32"]
    pu.bar_v(df_4, x="medal", y="total",
             title="Total Medal Distribution",
             xlabel="Medal", ylabel="Count",
             color=colors, rotate=0)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query BP4: Top 10 Countries by Gold Medals

    Which nations have earned the most Gold medals in Olympic history?
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_5 = mo.sql(
        f"""
        SELECT
            noc,
            COUNT(*) AS gold_medals
        FROM athlete_events
        WHERE medal = 'Gold'
        GROUP BY noc
        ORDER BY gold_medals DESC
        LIMIT 10
        """,
        engine=con
    )
    return (df_5,)


@app.cell
def _(df_5, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_h(df_5, x="gold_medals", y="noc",
             title="Top 10 Countries by Gold Medals",
             xlabel="Gold Medals", ylabel="NOC", color="gold")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query BP5: Total Athlete Entries per Year

    Track how overall Olympic participation has grown from the first Games to the most recent.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_6 = mo.sql(
        f"""
        SELECT
            year,
            COUNT(*) AS entries
        FROM athlete_events
        GROUP BY year
        ORDER BY year
        """,
        engine=con
    )
    return (df_6,)


@app.cell
def _(df_6, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.line(df_6, x="year", y="entries",
            title="Total Athlete Entries per Olympic Year",
            xlabel="Year", ylabel="Entries")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query BP6: Top 10 Sports by Total Entries

    Which sports attracted the most athlete-event entries across all Olympics?
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_7 = mo.sql(
        f"""
        SELECT
            sport,
            COUNT(*) AS entries
        FROM athlete_events
        GROUP BY sport
        ORDER BY entries DESC
        LIMIT 10
        """,
        engine=con
    )
    return (df_7,)


@app.cell
def _(df_7, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_h(df_7, x="entries", y="sport",
             title="Top 10 Sports by Total Entries",
             xlabel="Entries", ylabel="Sport")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query BP7: Average Height and Weight by Gender
    Compare the physical profiles of male and female Olympic athletes.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_8 = mo.sql(
        f"""
        SELECT
            sex,
            ROUND(AVG(height), 1) AS avg_height_cm,
            ROUND(AVG(weight), 1) AS avg_weight_kg
        FROM athlete_events
        WHERE
            height IS NOT NULL
            AND weight IS NOT NULL
        GROUP BY sex
        ORDER BY sex
        """,
        engine=con
    )
    return (df_8,)


@app.cell
def _(df_8, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.grouped_bar(df_8, x="sex",
                   groups=["avg_height_cm", "avg_weight_kg"],
                   title="Avg Height (cm) and Weight (kg) by Gender",
                   xlabel="Sex", ylabel="Value")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query BP8: Top 10 Most Decorated Athletes

    Who are the athletes with the highest total medal counts in this dataset?
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_9 = mo.sql(
        f"""
        SELECT
            name,
            noc,
            sport,
            COUNT(*) AS total_medals
        FROM athlete_events
        WHERE medal IN ('Gold', 'Silver', 'Bronze')
        GROUP BY
            name,
            noc,
            sport
        ORDER BY total_medals DESC
        LIMIT 10
        """,
        engine=con
    )
    return (df_9,)


@app.cell
def _(df_9, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_h(df_9, x="total_medals", y="name",
             title="Top 10 Most Decorated Olympic Athletes",
             xlabel="Total Medals", ylabel="Athlete")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query BP9: Cities That Hosted More Than One Games

    Which host cities have welcomed the Olympics more than once?
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_10 = mo.sql(
        f"""
        SELECT
            city,
            COUNT(DISTINCT games) AS times_hosted
        FROM athlete_events
        GROUP BY city
        HAVING COUNT(DISTINCT games) > 1
        ORDER BY
            times_hosted DESC,
            city
        """,
        engine=con
    )
    return (df_10,)


@app.cell
def _(df_10, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_v(df_10, x="city", y="times_hosted",
             title="Cities That Hosted Multiple Olympic Games",
             xlabel="City", ylabel="Times Hosted")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query BP10: Distinct Events per Olympic Year by Season

    Shows how the programme (number of individual events) has expanded over time.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_11 = mo.sql(
        f"""
        SELECT
            year,
            season,
            COUNT(DISTINCT event) AS num_events
        FROM athlete_events
        GROUP BY
            year,
            season
        ORDER BY year
        """,
        engine=con
    )
    if hasattr(df_11, "to_pandas"):
        df_11 = df_11.to_pandas()
    return (df_11,)


@app.cell
def _(df_11, plt):
    # ── Plot ─────────────────────────────────────────────────────────────────
    summer = df_11[df_11['season']=='Summer']
    winter = df_11[df_11['season']=='Winter']
    _fig, _ax = plt.subplots(figsize=(12,5))
    _ax.plot(summer['year'], summer['num_events'], marker='o', label='Summer')
    _ax.plot(winter['year'], winter['num_events'], marker='s', label='Winter')
    _ax.set_xlabel('Year'); _ax.set_ylabel('Number of Events'); _ax.legend()
    plt.title('Distinct Events per Olympic Year', fontsize=14, fontweight='bold')
    plt.tight_layout(); plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part 3 — Intermediate Queries (10)
    Multi-step analytics with CTEs, window functions, and advanced aggregations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query I1: Female Athlete Participation Rate by Decade

    Track the share of female entries relative to total entries across decades to visualise gender inclusion progress.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_12 = mo.sql(
        f"""
        WITH decade_counts AS (SELECT (year / 10) * 10 AS decade, SUM(CASE WHEN sex = 'F' THEN 1 ELSE 0 END) AS female_entries, COUNT(*) AS total_entries FROM athlete_events GROUP BY (year / 10) * 10)
        SELECT
            decade,
            female_entries,
            total_entries,
            ROUND(100.0 * female_entries / total_entries, 2) AS pct_female
        FROM decade_counts
        ORDER BY decade
        """,
        engine=con
    )
    return (df_12,)


@app.cell
def _(df_12, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.line(df_12, x="decade", y="pct_female",
            title="Female Athlete Participation Rate by Decade (%)",
            xlabel="Decade", ylabel="% Female Entries")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query I2: Countries Winning Gold in the Most Distinct Sports

    Identify versatile medal powerhouses — nations that claim gold across many disciplines.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_13 = mo.sql(
        f"""
        SELECT
            noc,
            COUNT(DISTINCT sport) AS gold_sports
        FROM athlete_events
        WHERE medal = 'Gold'
        GROUP BY noc
        ORDER BY gold_sports DESC
        LIMIT 15
        """,
        engine=con
    )
    return (df_13,)


@app.cell
def _(df_13, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_h(df_13, x="gold_sports", y="noc",
             title="Top 15 NOCs by Number of Sports with Gold Medals",
             xlabel="Distinct Sports", ylabel="NOC")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query I3: Athletes Who Competed in 4+ Olympics

    Find dedicated athletes who kept returning to the Games — grouped by how many times.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_14 = mo.sql(
        f"""
        SELECT
            name,
            noc,
            sport,
            COUNT(DISTINCT games) AS olympics_count,
            MIN(year) AS first_year,
            MAX(year) AS last_year
        FROM athlete_events
        GROUP BY
            name,
            noc,
            sport
        HAVING COUNT(DISTINCT games) >= 4
        ORDER BY
            olympics_count DESC,
            name
        LIMIT 20
        """,
        engine=con
    )
    if hasattr(df_14, "to_pandas"):
        df_14 = df_14.to_pandas()
    return (df_14,)


@app.cell
def _(df_14, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    counts = df_14['olympics_count'].value_counts().sort_index().reset_index()
    counts.columns = ['olympics_count', 'athletes']
    pu.bar_v(counts, x='olympics_count', y='athletes',
             title='Athletes Competing in 4+ Olympics — Distribution',
             xlabel='Number of Olympics', ylabel='Athlete Count', rotate=0)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query I4: Average Age of Gold Medalists — Top 15 Sports by Entries

    Do some sports reward youth while others favour experience? Compare average gold-medallist age across the most popular sports.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_15 = mo.sql(
        f"""
        WITH popular_sports AS (SELECT sport FROM athlete_events GROUP BY sport ORDER BY COUNT(*) DESC LIMIT 15)
        SELECT
            ae.sport,
            ROUND(AVG(ae.age), 1) AS avg_gold_age
        FROM athlete_events ae
        JOIN popular_sports ps
        ON ae.sport = ps.sport
        WHERE
            ae.medal = 'Gold'
            AND ae.age IS NOT NULL
        GROUP BY ae.sport
        ORDER BY avg_gold_age DESC
        """,
        engine=con
    )
    return (df_15,)


@app.cell
def _(df_15, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_h(df_15, x="avg_gold_age", y="sport",
             title="Average Age of Gold Medalists — Top 15 Sports",
             xlabel="Average Age (years)", ylabel="Sport")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query I5: NOCs with Best Gold Efficiency (min 50 medals)

    Which countries convert the highest proportion of their medals into gold?
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_16 = mo.sql(
        f"""
        WITH medal_summary AS (SELECT noc, COUNT(*) AS total_medals, SUM(CASE WHEN medal = 'Gold' THEN 1 ELSE 0 END) AS gold, SUM(CASE WHEN medal = 'Silver' THEN 1 ELSE 0 END) AS silver, SUM(CASE WHEN medal = 'Bronze' THEN 1 ELSE 0 END) AS bronze FROM athlete_events WHERE medal IN ('Gold', 'Silver', 'Bronze') GROUP BY noc)
        SELECT
            noc,
            total_medals,
            gold,
            silver,
            bronze,
            ROUND(100.0 * gold / total_medals, 1) AS gold_pct
        FROM medal_summary
        WHERE total_medals >= 50
        ORDER BY gold_pct DESC
        LIMIT 15
        """,
        engine=con
    )
    return (df_16,)


@app.cell
def _(df_16, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_h(df_16, x="gold_pct", y="noc",
             title="Gold Medal Rate (%) — NOCs with ≥50 Total Medals",
             xlabel="% Gold Medals", ylabel="NOC", color="gold")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query I6: Decade-over-Decade Growth in Athlete Entries

    Use a window function (LAG) to quantify how much Olympic participation grew each decade.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_17 = mo.sql(
        f"""
        WITH decade_totals AS (SELECT (year / 10) * 10 AS decade, COUNT(*) AS entries FROM athlete_events GROUP BY (year / 10) * 10)
        SELECT
            decade,
            entries,
            LAG(entries) OVER(ORDER BY decade) AS prev_entries,
            ROUND(100.0 * (entries - LAG(entries) OVER(ORDER BY decade)) / NULLIF(LAG(entries) OVER(ORDER BY decade), 0), 1) AS pct_change
        FROM decade_totals
        ORDER BY decade
        """,
        engine=con
    )
    if hasattr(df_17, "to_pandas"):
        df_17 = df_17.to_pandas()
    return (df_17,)


@app.cell
def _(df_17, plt):
    # ── Plot ─────────────────────────────────────────────────────────────────
    df_clean = df_17.dropna(subset=['pct_change'])
    _fig, ax1 = plt.subplots(figsize=(12,5))
    ax2 = ax1.twinx()
    ax1.bar(df_17['decade'].astype(str), df_17['entries'], color='steelblue', alpha=0.6, label='Entries')
    ax2.plot(df_clean['decade'].astype(str), df_clean['pct_change'],
             color='crimson', marker='o', label='% Change')
    ax1.set_xlabel('Decade'); ax1.set_ylabel('Total Entries', color='steelblue')
    ax2.set_ylabel('% Change vs Prior Decade', color='crimson')
    plt.title('Decade-over-Decade Growth in Athlete Entries', fontsize=14, fontweight='bold')
    plt.tight_layout(); plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query I7: Athletes Who Medalled in Both Summer and Winter Olympics

    A rare feat — find athletes who won medals in both editions by self-joining on season.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_18 = mo.sql(
        f"""
        WITH medal_seasons AS (SELECT name, noc, season, COUNT(DISTINCT games) AS medalled_games FROM athlete_events WHERE medal IN ('Gold', 'Silver', 'Bronze') GROUP BY name, noc, season)
        SELECT
            s.name,
            s.noc,
            s.medalled_games AS summer_medal_games,
            w.medalled_games AS winter_medal_games
        FROM medal_seasons s
        JOIN medal_seasons w
        ON
            s.name = w.name
            AND s.noc = w.noc
            AND s.season = 'Summer'
            AND w.season = 'Winter'
        ORDER BY (s.medalled_games + w.medalled_games) DESC
        """,
        engine=con
    )
    if hasattr(df_18, "to_pandas"):
        df_18 = df_18.to_pandas()
    return (df_18,)


@app.cell
def _(df_18, plt):
    # ── Plot ─────────────────────────────────────────────────────────────────
    top = df_18.head(15).copy().sort_values('summer_medal_games')
    _fig, _ax = plt.subplots(figsize=(10,6))
    _ax.barh(top['name'], top['summer_medal_games'], label='Summer', color='tomato')
    _ax.barh(top['name'], top['winter_medal_games'],
            left=top['summer_medal_games'], label='Winter', color='steelblue')
    _ax.set_xlabel('Medal Games Count'); _ax.legend()
    plt.title('Athletes with Medals in Both Summer & Winter Olympics (top 15)',
              fontsize=12, fontweight='bold')
    plt.tight_layout(); plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query I8: Age Distribution: Medal Winners vs. No Medal

    Use percentile functions to compare the age profiles of medalists and non-medalists.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    _df = mo.sql(
        f"""
        SELECT
            CASE WHEN medal IN ('Gold', 'Silver', 'Bronze') THEN 'Medal Winner' ELSE 'No Medal' END AS outcome,
            COUNT(*) AS entries,
            ROUND(AVG(age), 1) AS avg_age,
            PERCENTILE_CONT(0.25) WITHIN GROUP(ORDER BY age) AS q1_age,
            PERCENTILE_CONT(0.50) WITHIN GROUP(ORDER BY age) AS median_age,
            PERCENTILE_CONT(0.75) WITHIN GROUP(ORDER BY age) AS q3_age,
            MIN(age) AS min_age,
            MAX(age) AS max_age
        FROM athlete_events
        WHERE age IS NOT NULL
        GROUP BY outcome
        ORDER BY outcome
        """,
        engine=con
    )
    return


@app.cell
def _(con, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    # Fetch raw sample for box plot (decoupled from summary above)
    raw_sql = (
        'SELECT age, '
        "CASE WHEN medal IN ('Gold','Silver','Bronze') "
        "THEN 'Medal Winner' ELSE 'No Medal' END AS outcome "
        'FROM athlete_events WHERE age IS NOT NULL'
    )
    raw = con.execute(raw_sql).df()
    pu.box(raw, x='outcome', y='age',
           title='Age Distribution: Medal Winners vs. No Medal',
           xlabel='Outcome', ylabel='Age')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query I9: Top 10 Most Dominant Country–Sport Combinations

    Find the NOC–sport pairings with the highest gold count — the clearest examples of a country 'owning' a discipline.
    """)
    return


@app.cell
def _(con, display):
    # ── What are we doing? ─────────────────────────────────────────────────
    # Find the NOC–sport pairings with the highest gold count — the clearest examples of a country 'owning' a discipline.

    # ── SQL ────────────────────────────────────────────────────────────────
    SQL = """

        SELECT
            noc,
            sport,
            COUNT(*) AS gold_medals
        FROM   athlete_events
        WHERE  medal = 'Gold'
        GROUP BY noc, sport
        ORDER BY gold_medals DESC
        LIMIT 10

    """
    print("SQL:")
    print(SQL)

    # ── Result ──────────────────────────────────────────────────────────────
    df_19 = con.execute(SQL).df()
    df_19['label'] = df_19['noc'] + ' — ' + df_19['sport']

    display(df_19)
    return (df_19,)


@app.cell
def _(df_19, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_h(df_19, x="gold_medals", y="label",
             title="Top 10 Most Dominant Country–Sport Combinations",
             xlabel="Gold Medals", ylabel="NOC — Sport", color="gold")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Query I10: First Appearance of New NOCs by Decade

    Illustrate how the Olympic family grew over time by counting new national delegations debuting in each decade.
    """)
    return


@app.cell
def _(athlete_events, con, mo):
    df_20 = mo.sql(
        f"""
        WITH first_appearance AS (SELECT noc, MIN(year) AS debut_year FROM athlete_events GROUP BY noc)
        SELECT
            (debut_year / 10) * 10 AS decade,
            COUNT(noc) AS new_nocs,
            STRING_AGG(noc, ', ' ORDER BY noc) AS noc_list
        FROM first_appearance
        GROUP BY (debut_year / 10) * 10
        ORDER BY decade
        """,
        engine=con
    )
    return (df_20,)


@app.cell
def _(df_20, pu):
    # ── Plot ─────────────────────────────────────────────────────────────────
    pu.bar_v(df_20, x="decade", y="new_nocs",
             title="New NOC Debuts by Decade",
             xlabel="Decade", ylabel="New NOCs")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    | Category | Queries |
    |----------|---------|
    | Basic (B1–B5) | 5 |
    | Basic+ (BP1–BP10) | 10 |
    | Intermediate (I1–I10) | 10 |
    | **Total** | **25** |

    All queries run against `olympics_120_years.duckdb` via DuckDB SQL.  
    Plotting helpers live in `plotting_utils.py` and are imported as `pu`.
    """)
    return


@app.cell
def _(con):
    con.close()
    print('✓ DuckDB connection closed.')
    return


if __name__ == "__main__":
    app.run()

