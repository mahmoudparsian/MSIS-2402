"""
plot_helpers.py  —  Reusable matplotlib plotting functions for Nova Retail notebooks.

Import in any notebook with:
    from plot_helpers import plot_bar, plot_hbar, plot_line, plot_pie, plot_grouped_bar, plot_stacked_bar

All functions accept a pandas DataFrame (the query result) plus column names
so the SQL / query logic stays cleanly separated from the visualization code.
"""

import matplotlib.pyplot as plt

# Show "$" in titles and labels as a plain dollar sign. Without this, matplotlib
# reads the text between two "$" signs (e.g. "$100-$250") as a math formula.
plt.rcParams["text.parse_math"] = False
import matplotlib.ticker as mticker
import textwrap

# ── shared theme ────────────────────────────────────────────────
COLORS = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
    "#CCB974", "#64B5CD",
]


def _to_pandas(df):
    """
    Coerce a query result to a pandas DataFrame if it isn't one already.

    Callers of these helpers may pass a Marimo `mo.sql()` result, whose type
    (polars vs. pandas) depends on the user's marimo config rather than
    anything in the notebook. Polars DataFrames/Series lack pandas-only
    methods used below (`.astype()`, `.unique()` ordering, `.groupby()`
    with the pandas API, `.values`, etc.), so every helper normalizes to
    pandas here. This is a no-op for DataFrames that are already pandas.
    """
    if hasattr(df, "to_pandas"):
        return df.to_pandas()
    return df

def _apply_style(ax, title, xlabel, ylabel, rotate_x=0):
    """Apply a consistent, clean style to every chart."""
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if rotate_x:
        plt.xticks(rotation=rotate_x, ha="right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()


# ── public helpers ──────────────────────────────────────────────

def plot_bar(df, x_col, y_col, title="", xlabel="", ylabel="",
             figsize=(8, 4), rotate_x=0, color=None, show_values=True):
    """Vertical bar chart from two DataFrame columns."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(df[x_col].astype(str), df[y_col],
                  color=color or COLORS[0], edgecolor="white")
    if show_values:
        for bar in bars:
            height = bar.get_height()
            label = f"{height:,.0f}" if abs(height) >= 1 else f"{height:.2f}"
            ax.annotate(label,
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8)
    _apply_style(ax, title, xlabel, ylabel, rotate_x)
    plt.show()


def plot_hbar(df, label_col, value_col, title="", xlabel="", ylabel="",
              figsize=(8, 4), color=None, show_values=True):
    """Horizontal bar chart — good for long category labels."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    labels = df[label_col].astype(str)
    bars = ax.barh(labels, df[value_col],
                   color=color or COLORS[1], edgecolor="white")
    if show_values:
        for bar in bars:
            width = bar.get_width()
            label = f"{width:,.0f}" if abs(width) >= 1 else f"{width:.2f}"
            ax.annotate(label,
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(4, 0), textcoords="offset points",
                        ha="left", va="center", fontsize=8)
    _apply_style(ax, title, xlabel, ylabel)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()


def plot_line(df, x_col, y_col, title="", xlabel="", ylabel="",
              figsize=(9, 4), marker="o", color=None):
    """Line chart for time-series or sequential data."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(df[x_col].astype(str), df[y_col],
            marker=marker, color=color or COLORS[2],
            linewidth=2, markersize=5)
    _apply_style(ax, title, xlabel, ylabel, rotate_x=45)
    plt.show()


def plot_multi_line(df, x_col, y_col, group_col, title="", xlabel="", ylabel="",
                    figsize=(10, 5)):
    """Multiple lines on one chart, one per group."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    for i, (name, grp) in enumerate(df.groupby(group_col)):
        ax.plot(grp[x_col].astype(str), grp[y_col],
                marker="o", label=str(name),
                color=COLORS[i % len(COLORS)], linewidth=2, markersize=4)
    ax.legend(title=group_col, fontsize=8, title_fontsize=9)
    _apply_style(ax, title, xlabel, ylabel, rotate_x=45)
    plt.show()


def plot_pie(df, label_col, value_col, title="", figsize=(6, 6)):
    """Pie / donut chart."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    wedges, texts, autotexts = ax.pie(
        df[value_col], labels=df[label_col],
        autopct="%1.1f%%", startangle=140,
        colors=COLORS[: len(df)],
        pctdistance=0.80, textprops={"fontsize": 9},
    )
    # donut hole
    centre = plt.Circle((0, 0), 0.55, fc="white")
    ax.add_artist(centre)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    plt.tight_layout()
    plt.show()


def plot_grouped_bar(df, x_col, y_col, group_col, title="", xlabel="", ylabel="",
                     figsize=(10, 5), rotate_x=0):
    """Side-by-side grouped bars."""
    import numpy as np
    df = _to_pandas(df)
    groups = df[group_col].unique()
    x_labels = df[x_col].unique()
    x_pos = np.arange(len(x_labels))
    width = 0.8 / len(groups)

    fig, ax = plt.subplots(figsize=figsize)
    for i, g in enumerate(groups):
        subset = df[df[group_col] == g]
        # align on x_labels order
        vals = []
        for xl in x_labels:
            match = subset[subset[x_col] == xl]
            vals.append(match[y_col].values[0] if len(match) else 0)
        ax.bar(x_pos + i * width, vals, width,
               label=str(g), color=COLORS[i % len(COLORS)], edgecolor="white")

    ax.set_xticks(x_pos + width * (len(groups) - 1) / 2)
    ax.set_xticklabels([str(xl) for xl in x_labels])
    ax.legend(title=group_col, fontsize=8, title_fontsize=9)
    _apply_style(ax, title, xlabel, ylabel, rotate_x)
    plt.show()


def plot_stacked_bar(df_pivot, title="", xlabel="", ylabel="",
                     figsize=(10, 5), rotate_x=0):
    """
    Stacked bar chart.
    Expects a pivoted DataFrame where the index is the x-axis
    and each column is a stack segment.
    """
    df_pivot = _to_pandas(df_pivot)
    fig, ax = plt.subplots(figsize=figsize)
    df_pivot.plot.bar(stacked=True, ax=ax, color=COLORS[: len(df_pivot.columns)],
                      edgecolor="white")
    ax.legend(fontsize=8, title_fontsize=9)
    _apply_style(ax, title, xlabel, ylabel, rotate_x)
    plt.show()


def plot_scatter(df, x_col, y_col, title="", xlabel="", ylabel="",
                 figsize=(8, 5), color=None):
    """Simple scatter plot."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(df[x_col], df[y_col],
               color=color or COLORS[4], alpha=0.6, edgecolors="white", s=50)
    _apply_style(ax, title, xlabel, ylabel)
    plt.show()
