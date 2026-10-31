"""
plotting_utils.py
=================
Decoupled plotting helpers for the Olympics 120 Years analysis notebook.
Each function accepts a pandas DataFrame (the result of a DuckDB query) and
renders a matplotlib figure (no other plotting library needed).  Import this module in the notebook and
call the helpers directly — keep the notebook cells clean of matplotlib boilerplate.

Usage inside the notebook:
    import plotting_utils as pu
    pu.bar_h(df, x="noc", y="total_medals", title="Top Countries by Total Medals")
"""

import decimal

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from cycler import cycler

# ── Global style ─────────────────────────────────────────────────────────────
# White background, light grid, and the "muted" color palette.
MUTED = ["#4878D0", "#EE854A", "#6ACC64", "#D65F5F", "#956CB4",
         "#8C613C", "#DC7EC0", "#797979", "#D5BB67", "#82C6E2"]


def _muted(n):
    """The first n colors of the muted palette (repeating if n > 10)."""
    return [MUTED[i % len(MUTED)] for i in range(n)]


plt.rcParams.update({
    "axes.grid": True,
    "grid.color": "#dddddd",
    "axes.edgecolor": "#cccccc",
    "axes.axisbelow": True,
    "axes.prop_cycle": cycler(color=MUTED),
    "font.size": 11,
})


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
FIGSIZE_WIDE  = (12, 5)
FIGSIZE_SQUARE = (8, 6)
FIGSIZE_TALL   = (10, 7)


# ─────────────────────────────────────────────────────────────────────────────
# Generic helpers
# ─────────────────────────────────────────────────────────────────────────────

def _save_or_show(fig, title: str):
    """Tight-layout + show."""
    fig.suptitle(title, fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.show()
    plt.close(fig)


def _to_pandas(df):
    """
    Coerce a query result to a pandas DataFrame if it isn't one already,
    and normalize any DECIMAL-typed columns to plain floats.

    Callers may pass a Marimo `mo.sql()` result, whose type (polars vs.
    pandas) depends on the user's marimo config rather than anything in the
    notebook. Polars DataFrames/Series lack pandas-only methods used
    throughout this module (`.astype()`, `.dropna()`, `.groupby()` with the
    pandas API, etc.), so every plotting function normalizes to pandas
    first. This is a no-op if `df` is already pandas.

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


def bar_v(df: pd.DataFrame, x: str, y: str, title: str,
          xlabel: str = "", ylabel: str = "", color: str = "steelblue",
          rotate: int = 45, figsize=FIGSIZE_WIDE):
    """Vertical bar chart."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(df[x].astype(str), df[y], color=color, edgecolor="white")
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)
    ax.tick_params(axis="x", rotation=rotate)
    _save_or_show(fig, title)


def bar_h(df: pd.DataFrame, x: str, y: str, title: str,
          xlabel: str = "", ylabel: str = "", color: str = "steelblue",
          figsize=FIGSIZE_WIDE):
    """Horizontal bar chart (good for long category names)."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    ax.barh(df[y].astype(str), df[x], color=color, edgecolor="white")
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)
    ax.invert_yaxis()
    _save_or_show(fig, title)


def pie(df: pd.DataFrame, values: str, labels: str, title: str,
        figsize=FIGSIZE_SQUARE):
    """Pie / donut chart."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    ax.pie(
        df[values],
        labels=df[labels],
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"edgecolor": "white"},
    )
    ax.axis("equal")
    _save_or_show(fig, title)


def line(df: pd.DataFrame, x: str, y: str | list, title: str,
         xlabel: str = "", ylabel: str = "", markers: bool = True,
         figsize=FIGSIZE_WIDE):
    """Line chart; y can be a single column name or a list of column names."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    ys = [y] if isinstance(y, str) else y
    for col in ys:
        ax.plot(df[x], df[col], marker="o" if markers else None, label=col)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or (y if isinstance(y, str) else "value"))
    if len(ys) > 1:
        ax.legend()
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.xticks(rotation=45)
    _save_or_show(fig, title)


def grouped_bar(df: pd.DataFrame, x: str, groups: list[str], title: str,
                xlabel: str = "", ylabel: str = "", figsize=FIGSIZE_WIDE):
    """Grouped bar chart for comparing multiple series side-by-side."""
    df = _to_pandas(df)
    x_vals = df[x].astype(str).tolist()
    n_groups = len(groups)
    bar_width = 0.8 / n_groups
    positions = np.arange(len(x_vals))
    palette = _muted(n_groups)

    fig, ax = plt.subplots(figsize=figsize)
    for i, grp in enumerate(groups):
        offset = (i - n_groups / 2 + 0.5) * bar_width
        ax.bar(positions + offset, df[grp], width=bar_width,
               label=grp, color=palette[i], edgecolor="white")
    ax.set_xticks(positions)
    ax.set_xticklabels(x_vals, rotation=45, ha="right")
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or "value")
    ax.legend()
    _save_or_show(fig, title)


def scatter(df: pd.DataFrame, x: str, y: str, title: str,
            hue: str | None = None, alpha: float = 0.5,
            xlabel: str = "", ylabel: str = "",
            figsize=FIGSIZE_SQUARE):
    """Scatter plot, optionally coloured by a hue column."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    if hue:
        for label, grp in df.groupby(hue):
            ax.scatter(grp[x], grp[y], label=str(label), alpha=alpha, s=30)
        ax.legend(title=hue)
    else:
        ax.scatter(df[x], df[y], alpha=alpha, s=30, color="steelblue")
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)
    _save_or_show(fig, title)


def hist(df: pd.DataFrame, col: str, title: str,
         bins: int = 30, xlabel: str = "", ylabel: str = "Count",
         color: str = "steelblue", figsize=FIGSIZE_SQUARE):
    """Histogram."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(df[col].dropna(), bins=bins, color=color, edgecolor="white")
    ax.set_xlabel(xlabel or col)
    ax.set_ylabel(ylabel)
    _save_or_show(fig, title)


def stacked_bar(df: pd.DataFrame, x: str, groups: list[str], title: str,
                xlabel: str = "", ylabel: str = "", figsize=FIGSIZE_WIDE):
    """Stacked bar chart."""
    df = _to_pandas(df)
    palette = _muted(len(groups))
    fig, ax = plt.subplots(figsize=figsize)
    bottoms = [0] * len(df)
    for i, grp in enumerate(groups):
        ax.bar(df[x].astype(str), df[grp], bottom=bottoms,
               label=grp, color=palette[i], edgecolor="white")
        bottoms = [b + v for b, v in zip(bottoms, df[grp])]
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or "value")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    _save_or_show(fig, title)


def box(df: pd.DataFrame, x: str, y: str, title: str,
        xlabel: str = "", ylabel: str = "", figsize=FIGSIZE_WIDE):
    """Box plot: one box per category in column x."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    cats = list(df[x].dropna().unique())
    data = [df.loc[df[x] == c, y].dropna() for c in cats]
    parts = ax.boxplot(data, patch_artist=True, medianprops={"color": "black"})
    ax.set_xticks(range(1, len(cats) + 1))
    ax.set_xticklabels([str(c) for c in cats])
    for patch, color in zip(parts["boxes"], _muted(len(cats))):
        patch.set_facecolor(color)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)
    plt.xticks(rotation=45)
    _save_or_show(fig, title)


def heatmap(df: pd.DataFrame, title: str,
            fmt: str = ".1f", figsize=FIGSIZE_WIDE):
    """Heatmap from a pivot-ready DataFrame (index & columns already set)."""
    df = _to_pandas(df)
    fig, ax = plt.subplots(figsize=figsize)
    _annotated_heatmap(ax, df, fmt, "YlOrRd")
    _save_or_show(fig, title)
