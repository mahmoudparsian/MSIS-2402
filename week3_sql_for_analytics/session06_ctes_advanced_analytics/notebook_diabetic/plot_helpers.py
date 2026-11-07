"""
plot_helpers.py — Reusable matplotlib plotting functions for the
Diabetes 130-US Hospitals notebook.

Import in the notebook with:
    from plot_helpers import plot_bar, plot_hbar, plot_pie, plot_line

All functions accept a pandas (or polars — see `_to_pandas`) DataFrame (a
query result) plus column names, so the notebook's cells only ever call a
one-line `plot_xxx(df, ...)` — the matplotlib code itself lives here, not in
the notebook.
"""

import matplotlib.pyplot as plt

# ── shared theme ────────────────────────────────────────────────
COLORS = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
    "#CCB974", "#64B5CD",
]


def _to_pandas(df):
    """
    Coerce a query result to a pandas DataFrame if it isn't one already.

    A `mo.sql()` result can come back as pandas or polars depending on the
    user's marimo config (`default_sql_output`), not on anything in the
    notebook. Polars lacks some pandas-only methods used below (`.astype()`,
    etc.), so every helper normalizes to pandas here. No-op if already pandas.
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
             figsize=(8, 4), rotate_x=45, color=None, show_values=True):
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


def plot_pie(df, label_col, value_col, title="", figsize=(6, 6)):
    """Pie / donut chart — best for a small number of categories that sum to a whole."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    ax.pie(
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


def plot_line(df, x_col, y_col, title="", xlabel="", ylabel="",
              figsize=(7, 4), marker="o", color=None):
    """Line chart for sequential/ordered data (e.g. quartiles, ranks, trends)."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(df[x_col].astype(str), df[y_col],
            marker=marker, color=color or COLORS[2],
            linewidth=2, markersize=6)
    _apply_style(ax, title, xlabel, ylabel)
    plt.show()
