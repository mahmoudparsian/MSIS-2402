"""
plot_helpers.py — Plotting functions for the Book-Crossing SQL analysis notebook.

All plotting logic lives here, outside the notebook, so the notebook's query
cells stay pure SQL. Each function takes the DataFrame produced by one query and
returns a matplotlib figure.

Usage in the notebook:

    from plot_helpers import plot_rating_distribution
    plot_rating_distribution(q3_rating_distribution)

Five functions, one per plotted query:

    Q3   plot_rating_distribution   how the 1-10 scores are spread
    Q4   plot_top_books             the most-rated titles
    Q7   plot_ratings_by_country    where the raters are
    Q8   plot_books_per_decade      catalogue coverage over time
    Q12  plot_user_segments         engagement split, as a pie
    Q13  plot_reader_activity       the power-law shape of participation

DESIGN NOTES
------------
Colours come from a validated palette: every adjacent pair clears the
colour-vision-deficiency separation threshold against the chart surface, so the
charts stay readable for colourblind viewers and in greyscale print.

Only Q10 uses two colours; it plots two percentages on ONE shared axis rather
than two different scales on left and right. A dual-axis chart lets you imply
any correlation you like by rescaling, so it is avoided.
"""

import decimal

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── Palette (validated: CVD ΔE 24.7 worst adjacent pair, all contrast ≥ 3:1) ──
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

SERIES_1 = "#2a78d6"   # blue
SERIES_2 = "#eb6834"   # orange
SERIES_3 = "#1baf7a"   # aqua

plt.rcParams.update({
    "figure.figsize": (10, 5),
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_SECONDARY,
    "axes.titlecolor": INK,
    "axes.titlesize": 13,
    "axes.titleweight": "600",
    "axes.titlelocation": "left",
    "axes.titlepad": 14,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": GRIDLINE,
    "grid.linewidth": 0.8,
    "text.color": INK,
    "xtick.color": INK_MUTED,
    "ytick.color": INK_MUTED,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.frameon": False,
    "legend.fontsize": 10,
})


# ── Internal helpers ─────────────────────────────────────────────────────────

def _to_pandas(df):
    """
    Normalise a query result to a pandas DataFrame with plain float numerics.

    `mo.sql()` returns polars or pandas depending on the user's marimo config,
    not on anything in the notebook, so every entry point coerces first. Polars
    frames expose `.to_pandas()`; pandas frames pass straight through.

    DuckDB also returns DECIMAL for some aggregates, which lands in pandas as an
    object column of `decimal.Decimal`. Matplotlib cannot plot those, so any
    column holding Decimals is cast to float.
    """
    if hasattr(df, "to_pandas"):
        df = df.to_pandas()
    else:
        df = df.copy()

    for col in df.columns:
        if df[col].dtype == object:
            non_null = df[col].dropna()
            if len(non_null) and isinstance(non_null.iloc[0], decimal.Decimal):
                df[col] = df[col].astype(float)
    return df


def _style(ax, title, xlabel=None, ylabel=None, horizontal=False):
    """Apply the shared chrome: recessive axes, one grid direction, no box."""
    ax.set_title(title, color=INK)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, labelpad=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, labelpad=10)

    # Grid runs along the measured axis only; the categorical axis gets none.
    ax.grid(axis="x" if horizontal else "y")
    ax.grid(axis="y" if horizontal else "x", visible=False)

    for side in ("top", "right", "left" if not horizontal else "bottom"):
        ax.spines[side].set_visible(False)
    for side in ax.spines:
        if ax.spines[side].get_visible():
            ax.spines[side].set_linewidth(1.0)

    ax.tick_params(length=0)
    return ax


def _commas(ax, axis="y"):
    """Format an axis as 1,234,567."""
    fmt = ticker.FuncFormatter(lambda x, _: f"{x:,.0f}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def _label_bars(ax, bars, values, fmt="{:,.0f}", horizontal=False, pad=0.01):
    """
    Direct-label each bar. Used only where the count of bars is small enough
    that labels stay legible — never on a dense series.
    """
    span = (max(values) if len(values) else 0) or 1
    for bar, value in zip(bars, values):
        if horizontal:
            ax.text(bar.get_width() + span * pad,
                    bar.get_y() + bar.get_height() / 2,
                    fmt.format(value), va="center", ha="left",
                    fontsize=9, color=INK_SECONDARY)
        else:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + span * pad,
                    fmt.format(value), ha="center", va="bottom",
                    fontsize=9, color=INK_SECONDARY)


def _truncate(s, n=42):
    s = str(s)
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


# Countries are stored lowercased in the source. Title-casing alone would render
# 'usa' as 'Usa', so acronyms are spelled out explicitly.
_COUNTRY_LABELS = {
    "usa": "USA", "uk": "UK", "united kingdom": "United Kingdom",
    "uae": "UAE", "usa.": "USA",
}


def _country_label(c):
    c = str(c).strip()
    return _COUNTRY_LABELS.get(c.lower(), c.title())


# ── Q3 ───────────────────────────────────────────────────────────────────────

def plot_rating_distribution(df):
    """
    Bar chart of explicit ratings 1-10.

    Expects columns: rating, n_ratings
    """
    d = _to_pandas(df).sort_values("rating")

    fig, ax = plt.subplots()
    bars = ax.bar(d["rating"], d["n_ratings"], width=0.78, color=SERIES_1)

    _style(ax,
           "Explicit ratings cluster high — 8 is the single most common score",
           xlabel="Rating (1–10)", ylabel="Number of ratings")
    _commas(ax, "y")
    ax.set_xticks(range(1, 11))
    ax.set_ylim(0, d["n_ratings"].max() * 1.12)
    _label_bars(ax, bars, d["n_ratings"].tolist(), fmt="{:,.0f}")

    fig.tight_layout()
    return fig


# ── Q4 ───────────────────────────────────────────────────────────────────────

def plot_top_books(df):
    """
    Horizontal bar chart of the most-rated titles.

    Expects columns: title, n_ratings
    """
    d = _to_pandas(df).sort_values("n_ratings")
    labels = [_truncate(t) for t in d["title"]]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(labels, d["n_ratings"], height=0.72, color=SERIES_1)

    _style(ax, "The most-rated titles in the catalogue",
           xlabel="Number of explicit ratings", horizontal=True)
    _commas(ax, "x")
    ax.set_xlim(0, d["n_ratings"].max() * 1.14)
    _label_bars(ax, bars, d["n_ratings"].tolist(), horizontal=True)

    fig.tight_layout()
    return fig


# ── Q7 ───────────────────────────────────────────────────────────────────────

def plot_ratings_by_country(df):
    """
    Horizontal bar chart of rating volume per country.

    Expects columns: country, n_ratings
    """
    d = _to_pandas(df).sort_values("n_ratings")
    labels = [_country_label(c) for c in d["country"]]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.barh(labels, d["n_ratings"], height=0.72, color=SERIES_1)

    _style(ax, "Rating volume is dominated by the United States",
           xlabel="Number of explicit ratings", horizontal=True)
    _commas(ax, "x")
    ax.set_xlim(0, d["n_ratings"].max() * 1.16)
    _label_bars(ax, bars, d["n_ratings"].tolist(), horizontal=True)

    fig.tight_layout()
    return fig


# ── Q8 ───────────────────────────────────────────────────────────────────────

def plot_books_per_decade(df):
    """
    Bar chart of catalogue coverage by decade of publication.

    Expects columns: decade, n_books
    """
    d = _to_pandas(df).sort_values("decade")
    labels = [f"{int(x)}s" for x in d["decade"]]

    fig, ax = plt.subplots()
    bars = ax.bar(labels, d["n_books"], width=0.78, color=SERIES_1)

    _style(ax, "The catalogue is overwhelmingly a 1990s snapshot",
           xlabel="Decade of publication", ylabel="Books in catalogue")
    _commas(ax, "y")
    ax.set_ylim(0, d["n_books"].max() * 1.12)
    _label_bars(ax, bars, d["n_books"].tolist())

    fig.tight_layout()
    return fig


# ── Q12 ──────────────────────────────────────────────────────────────────────

def plot_user_segments(df):
    """
    Pie chart of how the user base splits by engagement.

    Expects columns: segment, n_users

    WHEN A PIE IS THE RIGHT CHOICE
    ------------------------------
    Pie charts get a bad reputation, mostly deserved: people are poor at comparing
    angles, so a pie with eight near-equal slices is unreadable, and one that does
    not sum to a meaningful whole is misleading.

    This case clears both objections. There are **three** slices, they are very
    different sizes, and every user falls into exactly one — the whole is real. The
    question being asked is "what fraction of the whole?", which is precisely what a
    pie encodes well.

    If you ever find yourself wanting more than about five slices, or the categories
    do not partition a whole, use a bar chart instead.

    Slices are ordered largest-first from 12 o'clock going clockwise, and every one
    is directly labelled with its name and share, so identity never depends on
    colour alone.
    """
    d = _to_pandas(df).sort_values("n_users", ascending=False)

    values = d["n_users"].tolist()
    total = sum(values)
    labels = [f"{s}\n{v:,} ({100 * v / total:.1f}%)"
              for s, v in zip(d["segment"], values)]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.pie(
        values,
        labels=labels,
        colors=[SERIES_1, SERIES_2, SERIES_3][: len(values)],
        startangle=90,
        counterclock=False,
        # A 2px surface-coloured gap keeps adjacent fills from bleeding together.
        wedgeprops={"edgecolor": SURFACE, "linewidth": 2},
        textprops={"fontsize": 10, "color": INK_SECONDARY},
        labeldistance=1.08,
    )
    ax.set_title("Two thirds of registered users never rated anything",
                 color=INK, loc="left", pad=18)
    ax.axis("equal")

    fig.tight_layout()
    return fig


# ── Q13 ──────────────────────────────────────────────────────────────────────

def plot_reader_activity(df):
    """
    Grouped bar chart contrasting each activity band's share of *users* with its
    share of *ratings* — the power-law signature.

    Both series are percentages, so they share one axis. Plotting user counts and
    rating counts on twin axes would let the visual gap be set by the scaling
    rather than by the data.

    Expects columns: activity_band, n_users, total_ratings
    """
    d = _to_pandas(df).copy()
    d["pct_users"] = 100 * d["n_users"] / d["n_users"].sum()
    d["pct_ratings"] = 100 * d["total_ratings"] / d["total_ratings"].sum()

    # Strip the 'a. ', 'b. ' sort prefixes used to order the bands in SQL.
    labels = [str(b).split(". ", 1)[-1] for b in d["activity_band"]]
    x = range(len(labels))
    w = 0.38

    fig, ax = plt.subplots(figsize=(10, 5.5))
    b1 = ax.bar([i - w / 2 - 0.01 for i in x], d["pct_users"], width=w,
                color=SERIES_1, label="Share of readers")
    b2 = ax.bar([i + w / 2 + 0.01 for i in x], d["pct_ratings"], width=w,
                color=SERIES_2, label="Share of ratings")

    _style(ax,
           "A few hundred readers produce a third of all ratings",
           xlabel="Ratings contributed per reader", ylabel="Percent of total")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_ylim(0, max(d["pct_users"].max(), d["pct_ratings"].max()) * 1.15)

    _label_bars(ax, b1, d["pct_users"].tolist(), fmt="{:.1f}%")
    _label_bars(ax, b2, d["pct_ratings"].tolist(), fmt="{:.1f}%")
    ax.legend(loc="upper right")

    fig.tight_layout()
    return fig
