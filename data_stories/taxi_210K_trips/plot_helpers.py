"""
plot_helpers.py — Reusable plotting functions for the Taxi Rides SQL notebook.
Decoupled from the main notebook so query cells stay clean.

Usage:
    from plot_helpers import plot_bar, plot_horizontal_bar, plot_line, plot_histogram, plot_pie, plot_grouped_bar, plot_scatter
"""

import matplotlib.pyplot as plt

# Show "$" in titles and labels as a plain dollar sign. Without this, matplotlib
# reads the text between two "$" signs (e.g. "$100-$250") as a math formula.
plt.rcParams["text.parse_math"] = False
import matplotlib.ticker as ticker
import numpy as np

# ── Global style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.figsize": (10, 5),
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 100,
})

COLORS = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
    "#CCB974", "#64B5CD",
]


def _apply_common(ax, title, xlabel, ylabel, rotate_x=0):
    """Apply shared formatting to an axes object."""
    if title:
        ax.set_title(title, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if rotate_x:
        ax.tick_params(axis="x", rotation=rotate_x)
    ax.grid(axis="y", alpha=0.3, linestyle="--")


# ── Bar chart (vertical) ─────────────────────────────────────────────────────
def plot_bar(labels, values, title=None, xlabel=None, ylabel=None,
             rotate_x=0, color=None, fmt_currency=False, figsize=None):
    """Vertical bar chart."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    bars = ax.bar(labels, values, color=color or COLORS[0], edgecolor="white", width=0.6)
    _apply_common(ax, title, xlabel, ylabel, rotate_x)
    if fmt_currency:
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.2f}"))
    # value labels on bars
    for bar in bars:
        height = bar.get_height()
        label = f"${height:,.2f}" if fmt_currency else f"{height:,.1f}" if isinstance(height, float) else f"{height:,}"
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                label, ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.show()


# ── Bar chart (horizontal) ───────────────────────────────────────────────────
def plot_horizontal_bar(labels, values, title=None, xlabel=None, ylabel=None,
                        color=None, fmt_currency=False, figsize=None):
    """Horizontal bar chart — good when labels are long."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    y_pos = range(len(labels))
    ax.barh(y_pos, values, color=color or COLORS[0], edgecolor="white", height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    _apply_common(ax, title, xlabel, ylabel)
    if fmt_currency:
        ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.2f}"))
    plt.tight_layout()
    plt.show()


# ── Line chart ────────────────────────────────────────────────────────────────
def plot_line(x, y, title=None, xlabel=None, ylabel=None,
              marker="o", color=None, figsize=None):
    """Simple line chart with markers."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    ax.plot(x, y, marker=marker, color=color or COLORS[0],
            linewidth=2, markersize=6)
    _apply_common(ax, title, xlabel, ylabel)
    plt.tight_layout()
    plt.show()


# ── Multi-line chart ─────────────────────────────────────────────────────────
def plot_multi_line(x, y_dict, title=None, xlabel=None, ylabel=None,
                    marker="o", figsize=None):
    """Multiple lines on one chart. y_dict = {label: values}."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    for i, (label, y_vals) in enumerate(y_dict.items()):
        ax.plot(x, y_vals, marker=marker, color=COLORS[i % len(COLORS)],
                linewidth=2, markersize=5, label=label)
    _apply_common(ax, title, xlabel, ylabel)
    ax.legend()
    plt.tight_layout()
    plt.show()


# ── Histogram ─────────────────────────────────────────────────────────────────
def plot_histogram(values, bins=30, title=None, xlabel=None, ylabel="Frequency",
                   color=None, figsize=None):
    """Histogram for distributions."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    ax.hist(values, bins=bins, color=color or COLORS[0],
            edgecolor="white", alpha=0.85)
    _apply_common(ax, title, xlabel, ylabel)
    plt.tight_layout()
    plt.show()


# ── Pie chart ─────────────────────────────────────────────────────────────────
def plot_pie(labels, values, title=None, figsize=None):
    """Pie chart with percentage labels."""
    fig, ax = plt.subplots(figsize=figsize or (7, 7))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%",
        colors=COLORS[: len(labels)], startangle=140,
        textprops={"fontsize": 11},
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
    if title:
        ax.set_title(title, fontweight="bold", pad=16)
    plt.tight_layout()
    plt.show()


# ── Grouped bar chart ────────────────────────────────────────────────────────
def plot_grouped_bar(labels, group_dict, title=None, xlabel=None, ylabel=None,
                     rotate_x=0, figsize=None):
    """Grouped (side-by-side) bar chart. group_dict = {group_name: values}."""
    fig, ax = plt.subplots(figsize=figsize or (12, 5))
    n_groups = len(group_dict)
    x = np.arange(len(labels))
    width = 0.8 / n_groups
    for i, (name, vals) in enumerate(group_dict.items()):
        offset = (i - n_groups / 2 + 0.5) * width
        ax.bar(x + offset, vals, width, label=name,
               color=COLORS[i % len(COLORS)], edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    _apply_common(ax, title, xlabel, ylabel, rotate_x)
    ax.legend()
    plt.tight_layout()
    plt.show()


# ── Scatter plot ──────────────────────────────────────────────────────────────
def plot_scatter(x, y, title=None, xlabel=None, ylabel=None,
                 color=None, alpha=0.5, figsize=None):
    """Scatter plot for correlations."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    ax.scatter(x, y, color=color or COLORS[0], alpha=alpha, s=20, edgecolors="none")
    _apply_common(ax, title, xlabel, ylabel)
    plt.tight_layout()
    plt.show()


# ── Stacked bar chart ────────────────────────────────────────────────────────
def plot_stacked_bar(labels, group_dict, title=None, xlabel=None, ylabel=None,
                     rotate_x=0, figsize=None):
    """Stacked bar chart. group_dict = {group_name: values}."""
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    bottom = np.zeros(len(labels))
    for i, (name, vals) in enumerate(group_dict.items()):
        ax.bar(labels, vals, bottom=bottom, label=name,
               color=COLORS[i % len(COLORS)], edgecolor="white", width=0.6)
        bottom += np.array(vals)
    _apply_common(ax, title, xlabel, ylabel, rotate_x)
    ax.legend()
    plt.tight_layout()
    plt.show()
