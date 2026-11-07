"""
plot_helpers.py  —  Reusable plotting functions for the Coffee Shop SQL Analysis notebook.

Usage (inside any notebook cell):
    from plot_helpers import bar_chart, hbar_chart, line_chart, pie_chart, heatmap_chart

All functions accept a Pandas DataFrame and column names, so the SQL
query result can be passed directly.
"""

import matplotlib.pyplot as plt

# Show "$" in titles and labels as a plain dollar sign. Without this, matplotlib
# reads the text between two "$" signs (e.g. "$100-$250") as a math formula.
plt.rcParams["text.parse_math"] = False
import pandas as pd
import numpy as np


# ─────────────────────────────────────────────
# Vertical bar chart
# ─────────────────────────────────────────────
def bar_chart(df, x_col, y_col, title="", xlabel="", ylabel="",
              figsize=(10, 5), rotation=20, color="#4C72B0"):
    """Simple vertical bar chart."""
    plt.figure(figsize=figsize)
    plt.bar(df[x_col].astype(str), df[y_col], color=color)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation, ha="right")
    plt.tight_layout()
    plt.show()


# ─────────────────────────────────────────────
# Horizontal bar chart  (good for long labels)
# ─────────────────────────────────────────────
def hbar_chart(df, label_col, value_col, title="", xlabel="", ylabel="",
               figsize=(11, 6), color="#55A868"):
    """Horizontal bar chart — items ordered top-to-bottom by value."""
    ordered = df.sort_values(value_col, ascending=True)
    plt.figure(figsize=figsize)
    plt.barh(ordered[label_col].astype(str), ordered[value_col], color=color)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.show()


# ─────────────────────────────────────────────
# Line chart  (time-series or continuous x)
# ─────────────────────────────────────────────
def line_chart(df, x_col, y_col, title="", xlabel="", ylabel="",
               figsize=(12, 5), marker="o", color="#4C72B0"):
    """Line chart with optional markers."""
    plt.figure(figsize=figsize)
    plt.plot(df[x_col], df[y_col], marker=marker, color=color, markersize=4)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


# ─────────────────────────────────────────────
# Multi-line chart  (overlay several series)
# ─────────────────────────────────────────────
def multi_line_chart(df, x_col, y_cols, labels=None, title="",
                     xlabel="", ylabel="", figsize=(12, 5)):
    """Plot multiple y columns against the same x column."""
    if labels is None:
        labels = y_cols
    plt.figure(figsize=figsize)
    for y, lab in zip(y_cols, labels):
        plt.plot(df[x_col], df[y], label=lab, marker="o", markersize=3)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


# ─────────────────────────────────────────────
# Pie chart
# ─────────────────────────────────────────────
def pie_chart(df, label_col, value_col, title="", figsize=(8, 8)):
    """Pie chart with percentage labels."""
    plt.figure(figsize=figsize)
    plt.pie(df[value_col], labels=df[label_col], autopct="%1.1f%%", startangle=90)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()


# ─────────────────────────────────────────────
# Heatmap (pivot table rendered with imshow)
# ─────────────────────────────────────────────
def heatmap_chart(df, index_col, columns_col, values_col,
                  title="", xlabel="", ylabel="",
                  index_order=None, figsize=(12, 5), cmap="YlOrRd"):
    """
    Build a pivot table from long-form data and display it as a heatmap.

    Parameters
    ----------
    index_order : list, optional
        Custom ordering for the index (e.g., weekday order).
    """
    pivot = pd.pivot_table(
        df, index=index_col, columns=columns_col,
        values=values_col, aggfunc="sum"
    ).fillna(0)

    if index_order is not None:
        pivot = pivot.reindex(index_order)

    plt.figure(figsize=figsize)
    plt.imshow(pivot, aspect="auto", cmap=cmap)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(range(len(pivot.columns)), pivot.columns)
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.colorbar(label=values_col)
    plt.tight_layout()
    plt.show()

    return pivot


# ─────────────────────────────────────────────
# Grouped bar chart
# ─────────────────────────────────────────────
def grouped_bar_chart(df, group_col, category_col, value_col,
                      title="", xlabel="", ylabel="", figsize=(12, 5)):
    """Side-by-side bars for each group, split by category."""
    pivot = df.pivot(index=group_col, columns=category_col, values=value_col).fillna(0)
    pivot.plot(kind="bar", figsize=figsize)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=20, ha="right")
    plt.legend(title=category_col, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()
