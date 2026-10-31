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
    # Notebook 3: Citi Bike Geographic Analysis (Maps)

    This notebook uses the **latitude and longitude** fields in the `rides` table
    to create interactive maps (Folium) and static geographic plots (Matplotlib).

    **Prerequisites:**
    - Run `notebook1_build_database_marimo.py` first to create `citibike.duckdb`
    - Install Folium: `pip install folium`

    **Maps:**
    1. All Stations Map — every station sized by ride count
    2. Top 10 Busiest Start Stations — interactive + static
    3. Top 10 Most Popular Routes — polylines connecting start/end
    4. Station Net Flow — arrivals vs departures (blue=inflow, red=outflow)
    5. Ride Density Heatmap — heat layer showing ride concentration
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup: Import Libraries and Connect to Database
    """)
    return


@app.cell
def _():
    # Install folium if needed
    # !pip install folium

    import duckdb
    from map_helpers import NYC_CENTER, map_all_stations, map_net_flow, map_popular_routes, map_ride_heatmap, map_top_stations, plot_net_flow_map, plot_ride_density_static, plot_top_stations_static
    DB_FILE = 'citibike.duckdb'
    con = duckdb.connect(DB_FILE, read_only=True)
    print('Connected to', DB_FILE)
    con.execute("SELECT COUNT(*) AS total_rides FROM rides").df()
    return con, map_all_stations, map_net_flow, map_popular_routes, map_ride_heatmap, map_top_stations, plot_net_flow_map, plot_ride_density_static, plot_top_stations_static


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Map 1: All Stations — Interactive Map

    **What are we doing?**

    We query every unique station (using both start and end station data) and count
    how many rides originated from or arrived at each station. The result is displayed
    on an interactive Folium map where **marker size is proportional to ride count**.

    **SQL Concepts:** `UNION ALL`, `GROUP BY`, aggregate functions

    This gives us a bird's-eye view of the entire Citi Bike network in NYC.
    """)
    return


@app.cell
def _(con, mo):
    df = mo.sql(
        f"""
        WITH all_stations AS (SELECT start_station_name AS station_name, start_station_latitude AS lat, start_station_longitude AS lon FROM rides WHERE start_station_name IS NOT NULL UNION ALL SELECT end_station_name AS station_name, end_station_latitude AS lat, end_station_longitude AS lon FROM rides WHERE end_station_name IS NOT NULL)
        SELECT
            station_name,
            ROUND(AVG(lat), 6) AS lat,
            ROUND(AVG(lon), 6) AS lon,
            COUNT(*) AS ride_count
        FROM all_stations
        GROUP BY station_name
        ORDER BY ride_count DESC;
        """,
        engine=con
    )
    return (df,)


@app.cell
def _(df, map_all_stations):
    # Interactive map: all stations sized by ride count
    map_all_stations(df)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Map 2: Top 10 Busiest Start Stations

    **What are we doing?**

    We find the **10 stations with the most ride departures** and plot them on both
    an interactive Folium map and a static Matplotlib scatter plot. Each station is
    color-coded and sized by its ride count.

    **SQL Concepts:** `GROUP BY`, `ORDER BY ... DESC`, `LIMIT`, aggregate functions
    """)
    return


@app.cell
def _(con, mo):
    df_2 = mo.sql(
        f"""
        SELECT
            start_station_name,
            ROUND(AVG(start_station_latitude), 6) AS lat,
            ROUND(AVG(start_station_longitude), 6) AS lon,
            COUNT(*) AS ride_count
        FROM rides
        WHERE
            start_station_name IS NOT NULL
            AND start_station_latitude IS NOT NULL
        GROUP BY start_station_name
        ORDER BY ride_count DESC
        LIMIT 10;
        """,
        engine=con
    )
    return (df_2,)


@app.cell
def _(df_2, map_top_stations):
    # Interactive map: top 10 stations
    map_top_stations(df_2)
    return


@app.cell
def _(df_2, plot_top_stations_static):
    # Static scatter plot: top 10 stations on lat/lon axes
    plot_top_stations_static(df_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Map 3: Top 10 Most Popular Routes

    **What are we doing?**

    We find the **10 most-traveled routes** (start station -> end station pairs) and draw
    them as colored lines on an interactive map. Green dots mark the start, red dots mark
    the end. Line thickness is proportional to ride count.

    **SQL Concepts:** `GROUP BY` on multiple columns, `HAVING`, `ORDER BY`, aggregate functions

    This reveals the most common commuter corridors in the bike-share network.
    """)
    return


@app.cell
def _(con, mo):
    df_3 = mo.sql(
        f"""
        SELECT
            start_station_name,
            end_station_name,
            ROUND(AVG(start_station_latitude), 6) AS start_lat,
            ROUND(AVG(start_station_longitude), 6) AS start_lon,
            ROUND(AVG(end_station_latitude), 6) AS end_lat,
            ROUND(AVG(end_station_longitude), 6) AS end_lon,
            COUNT(*) AS ride_count
        FROM rides
        WHERE
            start_station_name IS NOT NULL
            AND end_station_name IS NOT NULL
            AND start_station_latitude IS NOT NULL
            AND end_station_latitude IS NOT NULL
        GROUP BY
            start_station_name,
            end_station_name
        ORDER BY ride_count DESC
        LIMIT 10;
        """,
        engine=con
    )
    return (df_3,)


@app.cell
def _(df_3, map_popular_routes):
    # Interactive map: top 10 routes as colored lines
    map_popular_routes(df_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Map 4: Station Net Flow (Arrivals vs Departures)

    **What are we doing?**

    For each station we count **arrivals** (rides ending there) minus **departures**
    (rides starting there). The difference is the **net flow**:
    - **Positive (blue)** = more bikes arrive than leave (net inflow)
    - **Negative (red)** = more bikes leave than arrive (net outflow)

    This helps identify stations that consistently **gain** or **lose** bikes,
    which is critical for rebalancing operations.

    **SQL Concepts:** CTE (`WITH`), `FULL OUTER JOIN`, `COALESCE`, computed columns
    """)
    return


@app.cell
def _(con, mo):
    df_4 = mo.sql(
        f"""
        WITH departures AS (SELECT start_station_name AS station_name, AVG(start_station_latitude) AS lat, AVG(start_station_longitude) AS lon, COUNT(*) AS dep_count FROM rides WHERE start_station_name IS NOT NULL AND start_station_latitude IS NOT NULL GROUP BY start_station_name), arrivals AS (SELECT end_station_name AS station_name, AVG(end_station_latitude) AS lat, AVG(end_station_longitude) AS lon, COUNT(*) AS arr_count FROM rides WHERE end_station_name IS NOT NULL AND end_station_latitude IS NOT NULL GROUP BY end_station_name)
        SELECT
            COALESCE(d.station_name, a.station_name) AS station_name,
            ROUND(COALESCE(d.lat, a.lat), 6) AS lat,
            ROUND(COALESCE(d.lon, a.lon), 6) AS lon,
            COALESCE(a.arr_count, 0) AS arrivals,
            COALESCE(d.dep_count, 0) AS departures,
            COALESCE(a.arr_count, 0) - COALESCE(d.dep_count, 0) AS net_flow
        FROM departures d
        FULL OUTER JOIN arrivals a
        ON d.station_name = a.station_name
        ORDER BY net_flow DESC;
        """,
        engine=con
    )
    return (df_4,)


@app.cell
def _(df_4, map_net_flow):
    # Interactive map: net flow (blue=inflow, red=outflow)
    map_net_flow(df_4)
    return


@app.cell
def _(df_4, plot_net_flow_map):
    # Static plot: net flow on lat/lon axes
    plot_net_flow_map(df_4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Map 5: Ride Density Heatmap

    **What are we doing?**

    We create a **heatmap** showing where rides are concentrated across the city.
    Areas with more ride activity glow hotter. This uses the same station-level
    ride counts from Map 1, but visualizes them as a continuous heat layer instead
    of individual markers.

    **SQL Concepts:** Same query as Map 1 (reused), `GROUP BY`, `COUNT(*)`

    The Folium HeatMap plugin interpolates between station locations to show
    density gradients — perfect for spotting high-activity neighborhoods.
    """)
    return


@app.cell
def _(con, mo):
    df_5 = mo.sql(
        f"""
        WITH all_stations AS (SELECT start_station_name AS station_name, start_station_latitude AS lat, start_station_longitude AS lon FROM rides WHERE start_station_latitude IS NOT NULL UNION ALL SELECT end_station_name AS station_name, end_station_latitude AS lat, end_station_longitude AS lon FROM rides WHERE end_station_latitude IS NOT NULL)
        SELECT
            station_name,
            ROUND(AVG(lat), 6) AS lat,
            ROUND(AVG(lon), 6) AS lon,
            COUNT(*) AS ride_count
        FROM all_stations
        GROUP BY station_name
        ORDER BY ride_count DESC;
        """,
        engine=con
    )
    return (df_5,)


@app.cell
def _(df_5, map_ride_heatmap):
    # Interactive heatmap: ride density across NYC
    map_ride_heatmap(df_5)
    return


@app.cell
def _(df_5, plot_ride_density_static):
    # Static scatter: ride density view
    plot_ride_density_static(df_5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    | Map | Visualization | Type | SQL Concepts |
    |-----|--------------|------|-------------|
    | 1 | All Stations | Folium interactive | UNION ALL, GROUP BY, CTE |
    | 2 | Top 10 Busiest Stations | Folium + Matplotlib | GROUP BY, ORDER BY, LIMIT |
    | 3 | Popular Routes | Folium polylines | GROUP BY multiple cols, HAVING |
    | 4 | Station Net Flow | Folium + Matplotlib | CTE, FULL OUTER JOIN, COALESCE |
    | 5 | Ride Density Heatmap | Folium HeatMap + Matplotlib | UNION ALL, GROUP BY |

    **Key Takeaway:** The `latitude` and `longitude` fields transform SQL results from
    tables into geographic insights — showing WHERE things happen, not just WHAT happened.
    """)
    return


@app.cell
def _(con):
    # Close the database connection
    con.close()
    print('Done! Database connection closed.')
    return


if __name__ == "__main__":
    app.run()

