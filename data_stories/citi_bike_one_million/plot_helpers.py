"""
plot_helpers.py — Plotting functions for Citi Bike SQL Analysis (Notebook 2)

All plotting logic is decoupled from the main notebook into this module.
Each function takes a pandas DataFrame (from a DuckDB query) and produces
a matplotlib figure. None/NaN values are filtered before plotting.

Usage in notebook:
    from plot_helpers import plot_rides_per_user_type
    plot_rides_per_user_type(df)
"""

import decimal

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ── Global style ─────────────────────────────────────────────────────────────
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3


def _comma_fmt(x, _):
    """Format axis tick as 1,234,567."""
    return f'{x:,.0f}'


def _to_pandas(df):
    """
    Coerce a query result to a pandas DataFrame if it isn't one already,
    and normalize any DECIMAL-typed columns to plain floats.

    Callers may pass a Marimo `mo.sql()` result, whose type (polars vs.
    pandas) depends on the user's marimo config rather than anything in the
    notebook. Polars DataFrames/Series lack pandas-only methods used
    throughout this module (`.notna()`, `.copy()`, `.dropna()`,
    `.iterrows()`, boolean-mask indexing, etc.), so every plotting function
    normalizes to pandas first. This is a no-op if `df` is already pandas.

    Separately, DuckDB aggregates like SUM()/AVG() over integer columns can
    come back as a DECIMAL type. When such a column is converted to pandas
    (especially via polars' Arrow-backed `.to_pandas()`), it lands as an
    `object` column of `decimal.Decimal` values rather than float64 —
    `Decimal` doesn't support mixed arithmetic with plain floats (e.g.
    `decimal.Decimal(3) * 0.02` raises TypeError), which breaks the
    matplotlib label math below. Any object column whose values are
    `Decimal` gets cast to float here so downstream arithmetic just works.
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
    return df[df[col].notna()].copy()


# ═════════════════════════════════════════════════════════════════════════════
# PART 2 — Basic+ Queries
# ═════════════════════════════════════════════════════════════════════════════

def plot_rides_per_user_type(df):
    """Q6 — Bar chart: ride count by user_type."""
    df = _clean(_to_pandas(df), 'user_type')
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ['#2196F3', '#FF9800', '#4CAF50'][:len(df)]
    ax.bar(df['user_type'].astype(str), df['ride_count'], color=colors)
    ax.set_title('Ride Count by User Type')
    ax.set_ylabel('Number of Rides')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_rides_per_gender(df):
    """Q7 — Bar chart: ride count by gender."""
    df = _clean(_to_pandas(df), 'gender')
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ['#4CAF50', '#E91E63', '#9C27B0'][:len(df)]
    ax.bar(df['gender'].astype(str), df['ride_count'], color=colors)
    ax.set_title('Ride Count by Gender')
    ax.set_ylabel('Number of Rides')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_rides_per_year(df):
    """Q8 — Bar chart: total rides per year."""
    df = _clean(_to_pandas(df), 'start_year')
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df['start_year'].astype(int), df['ride_count'], color='#2196F3')
    ax.set_title('Total Rides per Year')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Rides')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_rides_per_month(df):
    """Q9 — Bar chart: rides per month (all years combined)."""
    df = _clean(_to_pandas(df), 'start_month')
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df['start_month'].astype(int), df['ride_count'], color='#FF9800')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names)
    ax.set_title('Rides per Month (All Years Combined)')
    ax.set_ylabel('Number of Rides')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_rides_per_hour(df):
    """Q10 — Line chart with fill: rides per hour of day."""
    df = _clean(_to_pandas(df), 'start_hour')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['start_hour'], df['ride_count'],
            marker='o', linewidth=2, color='#E91E63')
    ax.fill_between(df['start_hour'], df['ride_count'],
                    alpha=0.2, color='#E91E63')
    ax.set_title('Rides per Hour of Day')
    ax.set_xlabel('Hour (0 = midnight)')
    ax.set_ylabel('Number of Rides')
    ax.set_xticks(range(0, 24))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_rides_per_day_of_week(df):
    """Q11 — Bar chart: rides per day of week (weekdays blue, weekends orange)."""
    df = _clean(_to_pandas(df), 'start_day_of_week')
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ['#2196F3'] * 5 + ['#FF9800'] * 2
    colors = colors[:len(df)]
    ax.bar(df['start_day_of_week'], df['ride_count'], color=colors)
    ax.set_title('Rides per Day of Week')
    ax.set_ylabel('Number of Rides')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def plot_top_start_stations(df):
    """Q12 — Horizontal bar: top 10 start stations."""
    df = _clean(_to_pandas(df), 'start_station_name')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(df['start_station_name'][::-1],
            df['ride_count'][::-1], color='#4CAF50')
    ax.set_title('Top 10 Most Popular Start Stations')
    ax.set_xlabel('Number of Rides')
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_top_end_stations(df):
    """Q13 — Horizontal bar: top 10 end stations (destinations)."""
    df = _clean(_to_pandas(df), 'end_station_name')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(df['end_station_name'][::-1],
            df['ride_count'][::-1], color='#9C27B0')
    ax.set_title('Top 10 Most Popular Destinations (End Stations)')
    ax.set_xlabel('Number of Rides')
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_age_group_duration(df):
    """Q15 — Dual-axis: ride count bars + avg duration line by age group."""
    df = _to_pandas(df)
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(df['age_group'], df['ride_count'],
            color='#2196F3', alpha=0.7, label='Ride Count')
    ax1.set_ylabel('Ride Count', color='#2196F3')
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))

    ax2 = ax1.twinx()
    ax2.plot(df['age_group'], df['avg_duration_min'],
             'o-', color='#E91E63', linewidth=2, label='Avg Duration')
    ax2.set_ylabel('Avg Duration (min)', color='#E91E63')

    ax1.set_title('Rides and Average Duration by Age Group')
    plt.tight_layout()
    plt.show()


# ═════════════════════════════════════════════════════════════════════════════
# PART 3 — Intermediate Queries
# ═════════════════════════════════════════════════════════════════════════════

def plot_top_routes(df):
    """Q16 — Horizontal bar: top 10 most popular routes."""
    df = _clean(_to_pandas(df), 'route')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df['route'][::-1], df['ride_count'][::-1], color='#FF5722')
    ax.set_title('Top 10 Most Popular Routes')
    ax.set_xlabel('Number of Rides')
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_round_trip_vs_one_way(df):
    """Q17 — Pie chart: round-trip vs one-way rides."""
    df = _clean(_to_pandas(df), 'trip_type')
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = ['#2196F3', '#FF9800'][:len(df)]
    ax.pie(df['ride_count'], labels=df['trip_type'],
           autopct='%1.1f%%', colors=colors, startangle=90)
    ax.set_title('Round Trip vs One-Way Rides')
    plt.tight_layout()
    plt.show()


def plot_monthly_trend_by_year(df):
    """Q18 — Multi-line: monthly rides by year (year-over-year comparison)."""
    df = _clean(_to_pandas(df), 'start_year')
    fig, ax = plt.subplots(figsize=(12, 5))
    for year in sorted(df['start_year'].unique()):
        year_data = df[df['start_year'] == year]
        ax.plot(year_data['start_month'], year_data['ride_count'],
                marker='o', linewidth=2, label=str(int(year)))

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ax.set_title('Monthly Rides by Year (Year-over-Year Comparison)')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Rides')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names)
    ax.legend(title='Year')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_weekday_vs_weekend(df):
    """Q19 — Dual line + fill: hourly patterns weekday vs weekend."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=(10, 5))
    for dtype, color in [('Weekday', '#2196F3'), ('Weekend', '#FF9800')]:
        subset = df[df['day_type'] == dtype]
        ax.plot(subset['start_hour'], subset['ride_count'],
                marker='o', linewidth=2, label=dtype, color=color)
        ax.fill_between(subset['start_hour'], subset['ride_count'],
                        alpha=0.15, color=color)

    ax.set_title('Hourly Ride Patterns: Weekday vs Weekend')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Number of Rides')
    ax.set_xticks(range(0, 24))
    ax.legend()
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_cumulative_rides(df):
    """Q20 — Area chart: cumulative rides over time."""
    df = _clean(_to_pandas(df), 'start_year')
    df = _clean(df, 'start_month')
    labels = [f"{int(r['start_year'])}-{int(r['start_month']):02d}"
              for _, r in df.iterrows()]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.fill_between(range(len(df)), df['cumulative_rides'],
                    alpha=0.3, color='#4CAF50')
    ax.plot(range(len(df)), df['cumulative_rides'],
            linewidth=2, color='#4CAF50')
    ax.set_title('Cumulative Rides Over Time')
    ax.set_ylabel('Cumulative Rides')
    step = max(1, len(df) // 12)
    ax.set_xticks(range(0, len(df), step))
    ax.set_xticklabels([labels[i] for i in range(0, len(df), step)],
                       rotation=45, ha='right')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_mom_growth(df):
    """Q21 — Bar chart: month-over-month ride growth (%)."""
    df = _to_pandas(df)
    valid = df.dropna(subset=['pct_change', 'start_year', 'start_month']).copy()
    labels = [f"{int(r['start_year'])}-{int(r['start_month']):02d}"
              for _, r in valid.iterrows()]
    colors = ['#4CAF50' if v >= 0 else '#F44336' for v in valid['pct_change']]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(range(len(valid)), valid['pct_change'], color=colors)
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_title('Month-over-Month Ride Growth (%)')
    ax.set_ylabel('% Change')
    step = max(1, len(valid) // 12)
    ax.set_xticks(range(0, len(valid), step))
    ax.set_xticklabels([labels[i] for i in range(0, len(valid), step)],
                       rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def plot_duration_distribution(df):
    """Q23 — Bar chart with % labels: ride duration distribution."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = [b.split('. ')[1] for b in df['duration_bucket']]
    ax.bar(labels, df['ride_count'], color='#673AB7')
    ax.set_title('Ride Duration Distribution')
    ax.set_xlabel('Duration Bucket')
    ax.set_ylabel('Number of Rides')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))

    max_val = df['ride_count'].max()
    for i, (count, pct) in enumerate(zip(df['ride_count'], df['pct'])):
        ax.text(i, count + max_val * 0.02, f'{pct}%', ha='center', fontsize=9)

    plt.tight_layout()
    plt.show()


def plot_net_inflow(df):
    """Q24 — Horizontal bar: station net inflow (arrivals - departures)."""
    df = _clean(_to_pandas(df), 'station')
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#4CAF50' if v >= 0 else '#F44336' for v in df['net_inflow']]
    ax.barh(df['station'][::-1], df['net_inflow'][::-1],
            color=[c for c in reversed(colors)])
    ax.axvline(x=0, color='black', linewidth=0.5)
    ax.set_title('Station Net Inflow (Arrivals - Departures)')
    ax.set_xlabel('Net Inflow (positive = bikes accumulate)')
    plt.tight_layout()
    plt.show()


def plot_most_used_bikes(df):
    """Q25 — Bar chart: top 15 most used bikes."""
    df = _clean(_to_pandas(df), 'bike_id')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df['bike_id'].astype(str), df['total_rides'], color='#00BCD4')
    ax.set_title('Top 15 Most Used Bikes by Ride Count')
    ax.set_xlabel('Bike ID')
    ax.set_ylabel('Total Rides')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


# ═════════════════════════════════════════════════════════════════════════════
# PART 4 — Ranking Queries
# ═════════════════════════════════════════════════════════════════════════════

def plot_top_stations_per_year(df):
    """Q26 — Grouped bar: top 3 start stations per year."""
    df = _clean(_to_pandas(df), 'start_year')
    years = sorted(df['start_year'].unique())
    x = np.arange(len(years))
    width = 0.25
    colors = ['#2196F3', '#FF9800', '#4CAF50']

    fig, ax = plt.subplots(figsize=(12, 6))
    for rank in [1, 2, 3]:
        subset = df[df['rank'] == rank]
        vals = []
        for y in years:
            match = subset[subset['start_year'] == y]
            vals.append(match['ride_count'].values[0] if len(match) > 0 else 0)
        offset = (rank - 2) * width
        ax.bar(x + offset, vals, width,
               label=f'Rank {rank}', color=colors[rank - 1])

    ax.set_title('Top 3 Start Stations by Year')
    ax.set_xlabel('Year')
    ax.set_ylabel('Ride Count')
    ax.set_xticks(x)
    ax.set_xticklabels([str(int(y)) for y in years])
    ax.legend()
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()


def plot_quartile_summary(df):
    """Q28 — Bar chart with station-count labels: rides by station quartile."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=(8, 5))
    quartile_labels = ['Q1 (Top 25%)', 'Q2', 'Q3', 'Q4 (Bottom 25%)']
    quartile_labels = quartile_labels[:len(df)]
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336'][:len(df)]
    ax.bar(quartile_labels, df['total_rides'], color=colors)
    ax.set_title('Total Rides by Station Quartile')
    ax.set_ylabel('Total Rides')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))

    max_val = df['total_rides'].max()
    for i, (count, stations) in enumerate(
            zip(df['total_rides'], df['num_stations'])):
        ax.text(i, count + max_val * 0.02,
                f'{int(stations)} stations', ha='center', fontsize=9)

    plt.tight_layout()
    plt.show()


def plot_peak_hours_per_day(df):
    """Q30 — Grouped bar with hour labels: top 3 peak hours per day of week."""
    df = _to_pandas(df)
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                  'Friday', 'Saturday', 'Sunday']
    x = np.arange(len(days_order))
    width = 0.25
    colors = ['#E91E63', '#FF9800', '#FFC107']

    fig, ax = plt.subplots(figsize=(10, 5))
    for rank in [1, 2, 3]:
        subset = df[df['rank'] == rank]
        vals, hour_labels = [], []
        for d in days_order:
            row = subset[subset['day'] == d]
            if len(row) > 0:
                vals.append(row['ride_count'].values[0])
                hour_labels.append(f"{int(row['peak_hour'].values[0])}:00")
            else:
                vals.append(0)
                hour_labels.append('')
        offset = (rank - 2) * width
        ax.bar(x + offset, vals, width,
               label=f'Peak #{rank}', color=colors[rank - 1])
        max_val = max(vals) if vals else 0
        for i, (v, lbl) in enumerate(zip(vals, hour_labels)):
            ax.text(x[i] + offset, v + max_val * 0.02,
                    lbl, ha='center', fontsize=7, rotation=45)

    ax.set_title('Top 3 Peak Hours per Day of Week')
    ax.set_ylabel('Ride Count')
    ax.set_xticks(x)
    ax.set_xticklabels(days_order, rotation=45, ha='right')
    ax.legend()
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_comma_fmt))
    plt.tight_layout()
    plt.show()
