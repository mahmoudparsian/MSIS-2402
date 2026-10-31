"""
plot_utils.py - Reusable plotting functions for Shopify Sales analysis.

This module provides helper functions for creating various plots
from DuckDB query results (pandas DataFrames). Import this module
in the Marimo notebooks to keep plotting code decoupled from
the main analysis. Needs only matplotlib, pandas, and numpy.

Usage:
    from plot_utils import plot_bar, plot_horizontal_bar, plot_line, plot_pie, plot_grouped_bar, plot_heatmap
"""

import decimal

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np

# Set a clean style (white background with a light grid)
plt.rcParams.update({
    'axes.grid': True,
    'grid.color': '#dddddd',
    'axes.edgecolor': '#cccccc',
    'axes.axisbelow': True,
    'figure.figsize': (10, 6),
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 100
})

# Color palette (matplotlib's "Set2", repeated to 12 colors)
_SET2 = plt.get_cmap("Set2").colors
PALETTE = [_SET2[i % len(_SET2)] for i in range(12)]


def _annotated_heatmap(ax, df, fmt, cmap):
    """Matplotlib version of a seaborn-style annotated heatmap."""
    data = df.to_numpy(dtype=float)
    im = ax.imshow(data, cmap=cmap, aspect="auto")
    ax.figure.colorbar(im, ax=ax)
    ax.set_xticks(range(data.shape[1]))
    ax.set_xticklabels([str(c) for c in df.columns], rotation=45, ha="right")
    ax.set_yticks(range(data.shape[0]))
    ax.set_yticklabels([str(i) for i in df.index])
    ax.grid(False)
    lo, hi = np.nanmin(data), np.nanmax(data)
    mid = (lo + hi) / 2
    for r in range(data.shape[0]):
        for c in range(data.shape[1]):
            v = data[r, c]
            if np.isnan(v):
                continue
            ax.text(c, r, format(v, fmt), ha="center", va="center", fontsize=9,
                    color="white" if v > mid else "black")


def _to_pandas(df):
    """
    Coerce a query result to a pandas DataFrame if it isn't one already,
    and normalize any DECIMAL-typed columns to plain floats.

    Callers may pass a Marimo `mo.sql()` result, whose type (polars vs.
    pandas) depends on the user's marimo config rather than anything in the
    notebook. Polars DataFrames/Series lack pandas-only methods used
    throughout this module (`.astype()`, `.loc[]`, `.values`, `.unique()`
    with pandas semantics, etc.), so every plotting function normalizes to
    pandas first. This is a no-op if `df` is already pandas.

    Separately, DuckDB aggregates like SUM()/AVG() over integer columns can
    come back as a DECIMAL type, which lands as an `object` column of
    `decimal.Decimal` values after conversion to pandas. `Decimal` doesn't
    support mixed arithmetic with plain floats, so any object column whose
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


def plot_bar(df, x, y, title, xlabel=None, ylabel=None, rotate_x=0, color=None, figsize=None, fmt_currency=False):
    """
    Create a vertical bar chart.

    Parameters:
        df: pandas DataFrame with query results
        x: column name for x-axis (categories)
        y: column name for y-axis (values)
        title: chart title
        xlabel: x-axis label (defaults to column name)
        ylabel: y-axis label (defaults to column name)
        rotate_x: rotation angle for x-axis labels
        color: bar color (uses palette default if None)
        figsize: tuple (width, height)
        fmt_currency: if True, format y-axis as currency
    """
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize or (10, 6))
    bars = ax.bar(df[x].astype(str), df[y], color=color or PALETTE[0], edgecolor='white', linewidth=0.5)

    ax.set_title(title, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)

    if rotate_x:
        plt.xticks(rotation=rotate_x, ha='right')

    if fmt_currency:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:,.0f}'))

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        label = f'${height:,.0f}' if fmt_currency else f'{height:,.0f}'
        ax.annotate(label, xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.show()


def plot_horizontal_bar(df, x, y, title, xlabel=None, ylabel=None, color=None, figsize=None, fmt_currency=False):
    """
    Create a horizontal bar chart (good for long category names).

    Parameters:
        df: pandas DataFrame
        x: column for values (horizontal axis)
        y: column for categories (vertical axis)
        title: chart title
    """
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize or (10, 6))
    bars = ax.barh(df[y].astype(str), df[x], color=color or PALETTE[1], edgecolor='white', linewidth=0.5)

    ax.set_title(title, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)

    if fmt_currency:
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:,.0f}'))

    plt.tight_layout()
    plt.show()


def plot_line(df, x, y, title, xlabel=None, ylabel=None, marker='o', color=None, figsize=None, fmt_currency=False):
    """
    Create a line chart (good for time series).

    Parameters:
        df: pandas DataFrame
        x: column for x-axis
        y: column (or list of columns) for y-axis
        title: chart title
        marker: marker style
    """
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize or (10, 6))

    if isinstance(y, list):
        for i, col in enumerate(y):
            ax.plot(df[x].astype(str), df[col], marker=marker, color=PALETTE[i], label=col, linewidth=2)
        ax.legend()
    else:
        ax.plot(df[x].astype(str), df[y], marker=marker, color=color or PALETTE[2], linewidth=2)

    ax.set_title(title, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or (y if isinstance(y, str) else ''))

    if fmt_currency:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:,.0f}'))

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def plot_pie(df, labels_col, values_col, title, figsize=None, show_pct=True):
    """
    Create a pie chart.

    Parameters:
        df: pandas DataFrame
        labels_col: column for slice labels
        values_col: column for slice sizes
        title: chart title
        show_pct: show percentage on slices
    """
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize or (8, 8))

    wedges, texts, autotexts = ax.pie(
        df[values_col],
        labels=df[labels_col],
        autopct='%1.1f%%' if show_pct else None,
        colors=PALETTE[:len(df)],
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
    )

    ax.set_title(title, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.show()


def plot_grouped_bar(df, x, y_cols, title, xlabel=None, ylabel=None, figsize=None, fmt_currency=False):
    """
    Create a grouped bar chart for comparing multiple metrics.

    Parameters:
        df: pandas DataFrame
        x: column for categories
        y_cols: list of column names to compare
        title: chart title
    """
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize or (12, 6))

    n_groups = len(df)
    n_bars = len(y_cols)
    bar_width = 0.8 / n_bars
    index = np.arange(n_groups)

    for i, col in enumerate(y_cols):
        ax.bar(index + i * bar_width, df[col], bar_width,
               label=col, color=PALETTE[i], edgecolor='white', linewidth=0.5)

    ax.set_title(title, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or '')
    ax.set_xticks(index + bar_width * (n_bars - 1) / 2)
    ax.set_xticklabels(df[x].astype(str), rotation=45, ha='right')
    ax.legend()

    if fmt_currency:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:,.0f}'))

    plt.tight_layout()
    plt.show()


def plot_heatmap(df, title, figsize=None, fmt='.0f', cmap='YlOrRd'):
    """
    Create a heatmap from a pivot table DataFrame.

    Parameters:
        df: pandas DataFrame (already pivoted)
        title: chart title
        fmt: number format for annotations
        cmap: colormap
    """
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize or (12, 8))

    _annotated_heatmap(ax, df, fmt, cmap)

    ax.set_title(title, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.show()


def plot_scatter(df, x, y, title, xlabel=None, ylabel=None, hue=None, figsize=None):
    """
    Create a scatter plot.

    Parameters:
        df: pandas DataFrame
        x: column for x-axis
        y: column for y-axis
        title: chart title
        hue: column for color coding points
    """
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize or (10, 6))

    if hue:
        for i, group in enumerate(df[hue].unique()):
            mask = df[hue] == group
            ax.scatter(df.loc[mask, x], df.loc[mask, y],
                      color=PALETTE[i % len(PALETTE)], label=group, alpha=0.7)
        ax.legend()
    else:
        ax.scatter(df[x], df[y], color=PALETTE[3], alpha=0.7)

    ax.set_title(title, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)

    plt.tight_layout()
    plt.show()


def plot_stacked_bar(df, x, y_cols, title, xlabel=None, ylabel=None, figsize=None, fmt_currency=False):
    """
    Create a stacked bar chart.

    Parameters:
        df: pandas DataFrame
        x: column for categories
        y_cols: list of columns to stack
        title: chart title
    """
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize or (10, 6))

    bottom = np.zeros(len(df))
    for i, col in enumerate(y_cols):
        ax.bar(df[x].astype(str), df[col], bottom=bottom,
               label=col, color=PALETTE[i], edgecolor='white', linewidth=0.5)
        bottom += df[col].values

    ax.set_title(title, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or '')
    ax.legend()

    if fmt_currency:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v:,.0f}'))

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
