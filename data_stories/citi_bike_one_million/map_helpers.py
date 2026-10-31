"""
map_helpers.py — Map visualization functions for Citi Bike Geographic Analysis (Notebook 3)

All map plotting logic is decoupled from the main notebook into this module.
Each function takes a pandas DataFrame (from a DuckDB query) and produces
either a Folium interactive map or a Matplotlib static plot.

Usage in notebook:
    from map_helpers import *
    m = map_all_stations(df)
    m  # displays in notebook
"""

import decimal

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors
import numpy as np

try:
    import folium
    from folium.plugins import HeatMap
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    print("folium not installed. Run: pip install folium")

# ── Helpers ──────────────────────────────────────────────────────────────────

def _to_pandas(df):
    """
    Coerce a query result to a pandas DataFrame if it isn't one already,
    and normalize any DECIMAL-typed columns to plain floats.

    Callers may pass a Marimo `mo.sql()` result, whose type (polars vs.
    pandas) depends on the user's marimo config rather than anything in the
    notebook. Polars DataFrames/Series lack pandas-only methods used
    throughout this module (`.notna()`, `.copy()`, `.iterrows()`, boolean-
    mask indexing, etc.), so every map/plot function normalizes to pandas
    first via `_clean`/`_clean_coords`. This is a no-op if `df` is already
    pandas.

    Separately, DuckDB aggregates like SUM()/AVG() over integer columns can
    come back as a DECIMAL type, which lands as an `object` column of
    `decimal.Decimal` values after conversion to pandas. `Decimal` doesn't
    support mixed arithmetic with plain floats (e.g. marker-size math like
    `20 * row['ride_count'] / max_rides`), so any object column whose
    values are `Decimal` gets cast to float here too.
    """
    if hasattr(df, "to_pandas"):
        df = df.to_pandas()
    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna()
            if len(sample) and isinstance(sample.iloc[0], decimal.Decimal):
                df[col] = df[col].astype(float)
    return df


def _clean(df, col):
    """Drop rows where *col* is None / NaN and return a copy."""
    df = _to_pandas(df)
    return df[df[col].notna()].copy()


def _clean_coords(df, lat_col='start_station_latitude', lon_col='start_station_longitude'):
    """Drop rows where lat or lon is None / NaN."""
    df = _to_pandas(df)
    df = df[df[lat_col].notna() & df[lon_col].notna()].copy()
    return df


NYC_CENTER = [40.7128, -74.0060]


# ═════════════════════════════════════════════════════════════════════════════
# MAP 1 — All Stations (Folium interactive)
# ═════════════════════════════════════════════════════════════════════════════

def map_all_stations(df):
    """
    Interactive Folium map showing every unique station as a circle marker.
    Marker size is proportional to ride count.
    df must have: station_name, lat, lon, ride_count
    """
    df = _clean(df, 'lat')
    df = _clean(df, 'lon')
    df = _clean(df, 'station_name')

    m = folium.Map(location=NYC_CENTER, zoom_start=13, tiles='OpenStreetMap')

    max_rides = df['ride_count'].max()
    for _, row in df.iterrows():
        radius = max(3, 20 * row['ride_count'] / max_rides)
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=radius,
            color='#2196F3',
            fill=True,
            fill_color='#2196F3',
            fill_opacity=0.6,
            popup=f"<b>{row['station_name']}</b><br>Rides: {row['ride_count']:,}",
            tooltip=row['station_name']
        ).add_to(m)

    return m


# ═════════════════════════════════════════════════════════════════════════════
# MAP 2 — Top 10 Busiest Start Stations (Folium + Matplotlib)
# ═════════════════════════════════════════════════════════════════════════════

def map_top_stations(df):
    """
    Interactive Folium map with top 10 busiest start stations as large markers.
    df must have: start_station_name, lat, lon, ride_count
    """
    df = _clean(df, 'lat')
    df = _clean(df, 'lon')
    df = _clean(df, 'start_station_name')

    m = folium.Map(location=NYC_CENTER, zoom_start=13, tiles='OpenStreetMap')

    max_rides = df['ride_count'].max()
    colors = ['#F44336', '#E91E63', '#9C27B0', '#673AB7', '#3F51B5',
              '#2196F3', '#00BCD4', '#009688', '#4CAF50', '#FF9800']

    for i, (_, row) in enumerate(df.iterrows()):
        radius = max(8, 25 * row['ride_count'] / max_rides)
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=radius,
            color=colors[i % len(colors)],
            fill=True,
            fill_color=colors[i % len(colors)],
            fill_opacity=0.7,
            popup=f"<b>#{i+1} {row['start_station_name']}</b><br>Rides: {row['ride_count']:,}",
            tooltip=f"#{i+1} {row['start_station_name']}"
        ).add_to(m)

    return m


def plot_top_stations_static(df):
    """
    Static Matplotlib scatter: top 10 stations on lat/lon axes, sized by ride count.
    df must have: start_station_name, lat, lon, ride_count
    """
    df = _clean(df, 'lat')
    df = _clean(df, 'lon')
    df = _clean(df, 'start_station_name')

    fig, ax = plt.subplots(figsize=(10, 8))
    sizes = 100 + 400 * (df['ride_count'] / df['ride_count'].max())
    scatter = ax.scatter(df['lon'], df['lat'], s=sizes,
                         c=df['ride_count'], cmap='YlOrRd',
                         edgecolors='black', linewidths=0.5, alpha=0.8)
    for _, row in df.iterrows():
        ax.annotate(row['start_station_name'],
                    (row['lon'], row['lat']),
                    fontsize=7, ha='left', va='bottom',
                    xytext=(5, 5), textcoords='offset points')
    plt.colorbar(scatter, ax=ax, label='Ride Count')
    ax.set_title('Top 10 Busiest Start Stations')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


# ═════════════════════════════════════════════════════════════════════════════
# MAP 3 — Top 10 Most Popular Routes (Folium with polylines)
# ═════════════════════════════════════════════════════════════════════════════

def map_popular_routes(df):
    """
    Interactive Folium map showing top 10 routes as colored lines.
    df must have: start_lat, start_lon, end_lat, end_lon,
                  start_station_name, end_station_name, ride_count
    """
    df = _clean_coords(df, 'start_lat', 'start_lon')
    df = _clean_coords(df, 'end_lat', 'end_lon')

    m = folium.Map(location=NYC_CENTER, zoom_start=13, tiles='OpenStreetMap')

    colors = ['#F44336', '#E91E63', '#9C27B0', '#3F51B5', '#2196F3',
              '#009688', '#4CAF50', '#FF9800', '#795548', '#607D8B']

    for i, (_, row) in enumerate(df.iterrows()):
        start = [row['start_lat'], row['start_lon']]
        end = [row['end_lat'], row['end_lon']]
        weight = max(3, 10 * row['ride_count'] / df['ride_count'].max())

        # Draw the route line
        folium.PolyLine(
            locations=[start, end],
            weight=weight,
            color=colors[i % len(colors)],
            opacity=0.8,
            popup=f"<b>#{i+1}</b><br>{row['start_station_name']} -> {row['end_station_name']}<br>Rides: {row['ride_count']:,}",
            tooltip=f"#{i+1}: {row['ride_count']:,} rides"
        ).add_to(m)

        # Start marker (green)
        folium.CircleMarker(
            location=start, radius=6,
            color='green', fill=True, fill_opacity=0.8,
            tooltip=f"Start: {row['start_station_name']}"
        ).add_to(m)

        # End marker (red)
        folium.CircleMarker(
            location=end, radius=6,
            color='red', fill=True, fill_opacity=0.8,
            tooltip=f"End: {row['end_station_name']}"
        ).add_to(m)

    return m


# ═════════════════════════════════════════════════════════════════════════════
# MAP 4 — Station Net Flow (Matplotlib static)
# ═════════════════════════════════════════════════════════════════════════════

def plot_net_flow_map(df):
    """
    Static scatter plot: stations colored by net flow (arrivals - departures).
    Blue = net inflow (more arrivals), Red = net outflow (more departures).
    df must have: station_name, lat, lon, net_flow
    """
    df = _clean(df, 'lat')
    df = _clean(df, 'lon')
    df = _clean(df, 'net_flow')

    fig, ax = plt.subplots(figsize=(10, 8))

    # Normalize net_flow for color mapping
    max_abs = max(abs(df['net_flow'].min()), abs(df['net_flow'].max()))
    norm = mcolors.TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)

    sizes = 30 + 150 * (abs(df['net_flow']) / max_abs)
    scatter = ax.scatter(df['lon'], df['lat'], s=sizes,
                         c=df['net_flow'], cmap='RdYlBu', norm=norm,
                         edgecolors='black', linewidths=0.3, alpha=0.7)
    cbar = plt.colorbar(scatter, ax=ax, label='Net Flow (arrivals - departures)')
    ax.set_title('Station Net Flow: Blue = Net Inflow, Red = Net Outflow')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def map_net_flow(df):
    """
    Interactive Folium map: stations colored by net flow.
    df must have: station_name, lat, lon, net_flow
    """
    df = _clean(df, 'lat')
    df = _clean(df, 'lon')
    df = _clean(df, 'net_flow')

    m = folium.Map(location=NYC_CENTER, zoom_start=13, tiles='OpenStreetMap')

    max_abs = max(abs(df['net_flow'].min()), abs(df['net_flow'].max()))

    for _, row in df.iterrows():
        nf = row['net_flow']
        color = '#2196F3' if nf >= 0 else '#F44336'
        radius = max(3, 15 * abs(nf) / max_abs)
        label = 'inflow' if nf >= 0 else 'outflow'

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=f"<b>{row['station_name']}</b><br>Net flow: {nf:+,} ({label})",
            tooltip=f"{row['station_name']}: {nf:+,}"
        ).add_to(m)

    return m


# ═════════════════════════════════════════════════════════════════════════════
# MAP 5 — Ride Density Heatmap (Folium)
# ═════════════════════════════════════════════════════════════════════════════

def map_ride_heatmap(df):
    """
    Interactive Folium heatmap showing ride density by start station location.
    df must have: lat, lon, ride_count
    """
    df = _clean(df, 'lat')
    df = _clean(df, 'lon')
    df = _clean(df, 'ride_count')

    m = folium.Map(location=NYC_CENTER, zoom_start=13, tiles='OpenStreetMap')

    heat_data = [[row['lat'], row['lon'], row['ride_count']]
                 for _, row in df.iterrows()]

    HeatMap(heat_data, radius=20, blur=15, max_zoom=15).add_to(m)

    return m


def plot_ride_density_static(df):
    """
    Static Matplotlib scatter: all stations colored by ride count (density view).
    df must have: lat, lon, ride_count
    """
    df = _clean(df, 'lat')
    df = _clean(df, 'lon')
    df = _clean(df, 'ride_count')

    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(df['lon'], df['lat'],
                         s=10 + 200 * (df['ride_count'] / df['ride_count'].max()),
                         c=df['ride_count'], cmap='hot_r',
                         edgecolors='gray', linewidths=0.3, alpha=0.7)
    plt.colorbar(scatter, ax=ax, label='Ride Count')
    ax.set_title('Ride Density by Station Location')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
