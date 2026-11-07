"""
plot_helpers.py
===============
Reusable plotting functions for the Sales DuckDB notebook.
All plotting logic is decoupled from the main notebook.

Usage (inside a notebook cell):
    from plot_helpers import bar_chart, pie_chart, ...
"""

import matplotlib.pyplot as plt

# Show "$" in titles and labels as a plain dollar sign. Without this, matplotlib
# reads the text between two "$" signs (e.g. "$100-$250") as a math formula.
plt.rcParams["text.parse_math"] = False
import matplotlib.ticker as mticker

# ── Global style defaults ────────────────────────────────────────────
plt.rcParams.update({
    "figure.figsize": (10, 5),
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 100,
})

COLORS = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
    "#CCB974", "#64B5CD",
]


# ── Helper: dollar formatter ─────────────────────────────────────────
def _dollar_fmt(x, _):
    if x >= 1_000:
        return f"${x:,.0f}"
    return f"${x:.2f}"


# ── Bar chart (vertical) ─────────────────────────────────────────────
def bar_chart(labels, values, title="", xlabel="", ylabel="",
              color=None, rotate_labels=0, dollar=False, figsize=None):
    """Simple vertical bar chart."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    bars = ax.bar(labels, values, color=color or COLORS[: len(labels)],
                  edgecolor="white", linewidth=0.5)
    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if rotate_labels:
        plt.xticks(rotation=rotate_labels, ha="right")
    if dollar:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(_dollar_fmt))
    ax.spines[["top", "right"]].set_visible(False)
    # value labels on bars
    for bar in bars:
        h = bar.get_height()
        label = f"${h:,.2f}" if dollar else f"{h:,.2f}" if isinstance(h, float) else f"{h:,}"
        ax.text(bar.get_x() + bar.get_width() / 2, h,
                label, ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.show()


# ── Horizontal bar chart ─────────────────────────────────────────────
def hbar_chart(labels, values, title="", xlabel="", ylabel="",
               color=None, dollar=False, figsize=None):
    """Horizontal bar chart – good when labels are long."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    y_pos = range(len(labels))
    ax.barh(y_pos, values, color=color or COLORS[: len(labels)],
            edgecolor="white", linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if dollar:
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(_dollar_fmt))
    ax.spines[["top", "right"]].set_visible(False)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()


# ── Pie chart ─────────────────────────────────────────────────────────
def pie_chart(labels, values, title="", figsize=None):
    """Pie chart with percentages."""
    fig, ax = plt.subplots(figsize=figsize or (8, 8))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%",
        colors=COLORS[: len(labels)], startangle=140,
        textprops={"fontsize": 10},
    )
    for t in autotexts:
        t.set_fontsize(9)
        t.set_fontweight("bold")
    ax.set_title(title, fontweight="bold", pad=16)
    plt.tight_layout()
    plt.show()


# ── Line chart ────────────────────────────────────────────────────────
def line_chart(x, y, title="", xlabel="", ylabel="",
               marker="o", color=None, dollar=False, figsize=None):
    """Simple line chart."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    ax.plot(x, y, marker=marker, color=color or COLORS[0],
            linewidth=2, markersize=6)
    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if dollar:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(_dollar_fmt))
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()


# ── Grouped bar chart ─────────────────────────────────────────────────
def grouped_bar_chart(group_labels, series_dict, title="",
                      xlabel="", ylabel="", dollar=False, figsize=None):
    """
    Grouped bar chart.
    group_labels : list of x-axis category names
    series_dict  : {series_name: [values]}  – one list per series
    """
    import numpy as np
    fig, ax = plt.subplots(figsize=figsize or (12, 5))
    n_series = len(series_dict)
    x = np.arange(len(group_labels))
    width = 0.8 / n_series
    for i, (name, vals) in enumerate(series_dict.items()):
        ax.bar(x + i * width - (n_series - 1) * width / 2,
               vals, width, label=name, color=COLORS[i % len(COLORS)],
               edgecolor="white", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(group_labels)
    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if dollar:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(_dollar_fmt))
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.show()


# ── Stacked bar chart ─────────────────────────────────────────────────
def stacked_bar_chart(group_labels, series_dict, title="",
                      xlabel="", ylabel="", dollar=False, figsize=None):
    """Stacked bar chart."""
    import numpy as np
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    bottom = np.zeros(len(group_labels))
    for i, (name, vals) in enumerate(series_dict.items()):
        ax.bar(group_labels, vals, bottom=bottom, label=name,
               color=COLORS[i % len(COLORS)], edgecolor="white", linewidth=0.5)
        bottom += np.array(vals, dtype=float)
    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if dollar:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(_dollar_fmt))
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.show()


# ── Scatter plot ──────────────────────────────────────────────────────
def scatter_plot(x, y, title="", xlabel="", ylabel="",
                 color=None, dollar_x=False, dollar_y=False, figsize=None):
    """Simple scatter plot."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    ax.scatter(x, y, color=color or COLORS[0], alpha=0.7, edgecolors="white")
    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if dollar_x:
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(_dollar_fmt))
    if dollar_y:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(_dollar_fmt))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


# ── Histogram ─────────────────────────────────────────────────────────
def histogram(values, bins=20, title="", xlabel="", ylabel="Frequency",
              color=None, dollar=False, figsize=None):
    """Histogram."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    ax.hist(values, bins=bins, color=color or COLORS[0],
            edgecolor="white", linewidth=0.5)
    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if dollar:
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(_dollar_fmt))
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.show()
