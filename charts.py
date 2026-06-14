"""
charts.py - All required chart / visualisation functions
NYC 311 Service Requests Dashboard
SAP ID: 70176600
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ─── GLOBAL STYLE ────────────────────────────────────────────────────────────

PALETTE   = "Blues_d"
BG_COLOR  = "#F7F9FC"
ACCENT    = "#1565C0"
GRID_CLR  = "#E0E6EF"

BOROUGH_COLORS = {
    "BRONX":         "#1565C0",
    "BROOKLYN":      "#0288D1",
    "MANHATTAN":     "#00838F",
    "QUEENS":        "#2E7D32",
    "STATEN ISLAND": "#6A1B9A",
    "Unspecified":   "#9E9E9E",
}

def _base_style(ax, title: str, xlabel: str = "", ylabel: str = ""):
    ax.set_title(title, fontsize=14, fontweight="bold", color="#1A237E", pad=12)
    ax.set_xlabel(xlabel, fontsize=10, color="#424242")
    ax.set_ylabel(ylabel, fontsize=10, color="#424242")
    ax.tick_params(colors="#424242", labelsize=9)
    ax.set_facecolor(BG_COLOR)
    for spine in ax.spines.values():
        spine.set_color(GRID_CLR)
    ax.yaxis.grid(True, color=GRID_CLR, linestyle="--", linewidth=0.7)
    ax.set_axisbelow(True)


def _fig(w=9, h=5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG_COLOR)
    return fig, ax


# ─── 1. PIE CHART ────────────────────────────────────────────────────────────

def chart_pie(df: pd.DataFrame) -> plt.Figure:
    """Proportional distribution of complaints by Borough."""
    col = "borough" if "borough" in df.columns else df.columns[0]
    counts = df[col].value_counts()
    colors = [BOROUGH_COLORS.get(b, "#90CAF9") for b in counts.index]

    fig, ax = _fig(7, 7)
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        pctdistance=0.82,
        wedgeprops=dict(edgecolor="white", linewidth=1.5),
    )
    for t in texts:
        t.set_fontsize(10)
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title("Complaints by Borough", fontsize=14, fontweight="bold",
                 color="#1A237E", pad=16)
    ax.legend(wedges, counts.index, loc="lower right", fontsize=9)
    fig.tight_layout()
    return fig


# ─── 2. HISTOGRAM ────────────────────────────────────────────────────────────

def chart_histogram(df: pd.DataFrame) -> plt.Figure:
    """Frequency distribution of resolution time (days)."""
    col = "resolution_days"
    if col not in df.columns or df[col].dropna().empty:
        fig, ax = _fig()
        ax.text(0.5, 0.5, "No resolution-time data available",
                ha="center", va="center", transform=ax.transAxes)
        return fig

    data = df[col].dropna()
    data = data[data <= data.quantile(0.97)]   # clip extreme tail

    fig, ax = _fig()
    ax.hist(data, bins=40, color=ACCENT, edgecolor="white", linewidth=0.6, alpha=0.9)
    ax.axvline(data.mean(), color="#E53935", linestyle="--",
               linewidth=1.5, label=f"Mean: {data.mean():.1f} days")
    ax.axvline(data.median(), color="#43A047", linestyle="--",
               linewidth=1.5, label=f"Median: {data.median():.1f} days")
    _base_style(ax, "Distribution of Resolution Time",
                "Days to Resolve", "Number of Complaints")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


# ─── 3. LINE CHART ───────────────────────────────────────────────────────────

def chart_line(df: pd.DataFrame) -> plt.Figure:
    """Monthly complaint volume trend."""
    if "created_date" not in df.columns:
        fig, ax = _fig(); return fig

    monthly = (
        df.set_index("created_date")
          .resample("ME")
          .size()
          .reset_index(name="count")
    )
    monthly.columns = ["date", "count"]

    fig, ax = _fig(10, 5)
    ax.plot(monthly["date"], monthly["count"], color=ACCENT,
            linewidth=2, marker="o", markersize=3, alpha=0.9)
    ax.fill_between(monthly["date"], monthly["count"],
                    alpha=0.15, color=ACCENT)
    _base_style(ax, "Monthly Complaint Volume Over Time",
                "Month", "Number of Complaints")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(10))
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    return fig


# ─── 4. BAR CHART ────────────────────────────────────────────────────────────

def chart_bar(df: pd.DataFrame) -> plt.Figure:
    """Top-15 complaint types by volume."""
    col = "complaint_type" if "complaint_type" in df.columns else df.columns[0]
    top = df[col].value_counts().head(15)

    fig, ax = _fig(10, 6)
    bars = ax.barh(top.index[::-1], top.values[::-1],
                   color=sns.color_palette("Blues_d", len(top))[::-1],
                   edgecolor="white")
    for bar, val in zip(bars, top.values[::-1]):
        ax.text(bar.get_width() + top.values.max() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", fontsize=8, color="#424242")
    _base_style(ax, "Top 15 Complaint Types", "Number of Complaints", "Complaint Type")
    fig.tight_layout()
    return fig


# ─── 5. SCATTER PLOT ─────────────────────────────────────────────────────────

def chart_scatter(df: pd.DataFrame) -> plt.Figure:
    """Hour of day vs. resolution days, coloured by borough."""
    needed = {"hour", "resolution_days", "borough"}
    if not needed.issubset(df.columns):
        fig, ax = _fig()
        ax.text(0.5, 0.5, "Required columns not available",
                ha="center", va="center", transform=ax.transAxes)
        return fig

    sample = df[list(needed)].dropna()
    sample = sample[sample["resolution_days"] <= sample["resolution_days"].quantile(0.95)]
    if len(sample) > 8_000:
        sample = sample.sample(8_000, random_state=42)

    fig, ax = _fig(10, 6)
    for borough, grp in sample.groupby("borough"):
        ax.scatter(grp["hour"], grp["resolution_days"],
                   color=BOROUGH_COLORS.get(borough, "#90CAF9"),
                   alpha=0.35, s=12, label=borough)
    _base_style(ax, "Hour of Day vs. Resolution Time by Borough",
                "Hour Filed (0–23)", "Days to Resolve")
    ax.legend(fontsize=8, markerscale=1.5)
    fig.tight_layout()
    return fig


# ─── 6. BOX PLOT ─────────────────────────────────────────────────────────────

def chart_box(df: pd.DataFrame) -> plt.Figure:
    """Resolution time spread per borough."""
    needed = {"borough", "resolution_days"}
    if not needed.issubset(df.columns):
        fig, ax = _fig(); return fig

    data = df[list(needed)].dropna()
    data = data[data["resolution_days"] <= data["resolution_days"].quantile(0.95)]
    boroughs = data["borough"].value_counts().index.tolist()
    plot_data = [data[data["borough"] == b]["resolution_days"].values
                 for b in boroughs]

    fig, ax = _fig(10, 6)
    bp = ax.boxplot(plot_data, patch_artist=True, notch=False,
                    medianprops=dict(color="#E53935", linewidth=2))
    colors = [BOROUGH_COLORS.get(b, "#90CAF9") for b in boroughs]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_xticks(range(1, len(boroughs) + 1))
    ax.set_xticklabels(boroughs, rotation=20, ha="right", fontsize=9)
    _base_style(ax, "Resolution Time Spread by Borough",
                "Borough", "Days to Resolve")
    fig.tight_layout()
    return fig


# ─── 7. HEATMAP ──────────────────────────────────────────────────────────────

def chart_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Complaints heatmap: Hour of day × Day of week."""
    needed = {"hour", "day_of_week"}
    if not needed.issubset(df.columns):
        fig, ax = _fig(); return fig

    order = ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]
    pivot = (
        df.groupby(["day_of_week", "hour"])
          .size()
          .unstack(fill_value=0)
    )
    pivot = pivot.reindex([d for d in order if d in pivot.index])

    fig, ax = _fig(12, 5)
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd", linewidths=0.3,
                linecolor="#F0F0F0", cbar_kws={"label": "# Complaints"})
    ax.set_title("Complaint Volume: Day of Week × Hour",
                 fontsize=14, fontweight="bold", color="#1A237E", pad=12)
    ax.set_xlabel("Hour of Day", fontsize=10)
    ax.set_ylabel("Day of Week", fontsize=10)
    fig.tight_layout()
    return fig


# ─── 8. AREA CHART ───────────────────────────────────────────────────────────

def chart_area(df: pd.DataFrame) -> plt.Figure:
    """Cumulative complaints over time per top-4 boroughs."""
    needed = {"created_date", "borough"}
    if not needed.issubset(df.columns):
        fig, ax = _fig(); return fig

    top_boroughs = df["borough"].value_counts().head(5).index.tolist()
    sub = df[df["borough"].isin(top_boroughs)].copy()
    sub["month"] = sub["created_date"].dt.to_period("M").dt.to_timestamp()

    pivot = (
        sub.groupby(["month", "borough"])
           .size()
           .unstack(fill_value=0)
           .sort_index()
    )

    fig, ax = _fig(11, 5)
    colors = [BOROUGH_COLORS.get(b, "#90CAF9") for b in pivot.columns]
    pivot.plot.area(ax=ax, color=colors, alpha=0.75, legend=True)
    _base_style(ax, "Monthly Complaints by Borough (Area)",
                "Month", "Complaint Count")
    ax.legend(title="Borough", fontsize=9)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    return fig


# ─── 9. COUNT PLOT ───────────────────────────────────────────────────────────

def chart_countplot(df: pd.DataFrame) -> plt.Figure:
    """Complaint count by status."""
    col = "status" if "status" in df.columns else "borough"
    top = df[col].value_counts().head(8)

    fig, ax = _fig(9, 5)
    bars = ax.bar(top.index, top.values,
                  color=sns.color_palette("Set2", len(top)),
                  edgecolor="white", linewidth=1)
    for bar, val in zip(bars, top.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + top.values.max() * 0.01,
                f"{val:,}", ha="center", va="bottom", fontsize=9)
    _base_style(ax, f"Complaint Count by {col.replace('_', ' ').title()}",
                col.replace("_", " ").title(), "Count")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    return fig


# ─── 10. VIOLIN PLOT ─────────────────────────────────────────────────────────

def chart_violin(df: pd.DataFrame) -> plt.Figure:
    """Resolution time distribution (violin) per top-5 boroughs."""
    needed = {"borough", "resolution_days"}
    if not needed.issubset(df.columns):
        fig, ax = _fig(); return fig

    data = df[list(needed)].dropna()
    data = data[data["resolution_days"] <= data["resolution_days"].quantile(0.95)]
    top5 = data["borough"].value_counts().head(5).index.tolist()
    data = data[data["borough"].isin(top5)]

    fig, ax = _fig(10, 6)
    palette = {b: BOROUGH_COLORS.get(b, "#90CAF9") for b in top5}
    sns.violinplot(data=data, x="borough", y="resolution_days",
                   palette=palette, ax=ax, inner="box", cut=0)
    _base_style(ax, "Resolution Time Distribution by Borough (Violin)",
                "Borough", "Days to Resolve")
    plt.xticks(rotation=15, ha="right")
    fig.tight_layout()
    return fig
