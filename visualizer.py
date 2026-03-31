"""
visualizer.py
Generate a 5-panel matplotlib dashboard for the weather statistics project.
All charts use a dark theme consistent with config.PALETTE.
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
from scipy import stats

from config import PALETTE, CHART_OUTPUT_FILE, CHART_DPI, VAR_LABELS
from statistics_engine import StatisticsReport
from location import LocationInfo

matplotlib.rcParams.update({
    "font.family":      "DejaVu Sans",
    "font.size":        9,
    "axes.facecolor":   PALETTE["surface"],
    "figure.facecolor": PALETTE["background"],
    "axes.edgecolor":   PALETTE["grid"],
    "axes.labelcolor":  PALETTE["text"],
    "xtick.color":      PALETTE["muted"],
    "ytick.color":      PALETTE["muted"],
    "text.color":       PALETTE["text"],
    "grid.color":       PALETTE["grid"],
    "grid.linestyle":   "--",
    "grid.linewidth":   0.5,
    "legend.facecolor": PALETTE["surface"],
    "legend.edgecolor": PALETTE["grid"],
})


def _apply_ax_style(ax, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, fontsize=11, fontweight="bold", color=PALETTE["text"], pad=10)
    ax.set_xlabel(xlabel, color=PALETTE["muted"], fontsize=8)
    ax.set_ylabel(ylabel, color=PALETTE["muted"], fontsize=8)
    ax.grid(True, alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(PALETTE["grid"])
    ax.spines["bottom"].set_color(PALETTE["grid"])


def create_charts(
    df: pd.DataFrame,
    stat_report: StatisticsReport,
    location: LocationInfo,
) -> None:
    """
    Produce and save the 5-panel weather dashboard.
    """
    temp_col = "temperature_2m"
    hum_col  = "relative_humidity_2m"

    fig = plt.figure(figsize=(18, 14))
    fig.suptitle(
        f"Weather Data Analysis  ·  {location.city}, {location.region}, {location.country}",
        fontsize=15, fontweight="bold", color=PALETTE["text"], y=0.98,
    )

    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

    # ── 1. Line chart: 7-day temperature trend + rolling average ─────────────
    ax1 = fig.add_subplot(gs[0, :])   # full-width top row
    if temp_col in df.columns:
        temp_series = df[temp_col]
        ax1.plot(
            temp_series.index, temp_series.values,
            color=PALETTE["primary"], linewidth=1.2, alpha=0.6, label="Hourly Temp",
        )
        if stat_report.rolling_mean is not None:
            ax1.plot(
                stat_report.rolling_mean.index,
                stat_report.rolling_mean.values,
                color=PALETTE["secondary"], linewidth=2.2, label="24-hr Rolling Mean",
            )
        # Regression overlay
        if stat_report.regression is not None:
            x_num = np.arange(len(temp_series))
            y_reg = (stat_report.regression.slope * x_num +
                     stat_report.regression.intercept)
            ax1.plot(
                temp_series.index, y_reg,
                color=PALETTE["highlight"], linewidth=1.5,
                linestyle="--", label=f"Linear Trend (R²={stat_report.regression.r_squared})",
            )
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%a %d %b"))
        ax1.xaxis.set_major_locator(mdates.DayLocator())
        ax1.tick_params(axis="x", rotation=30)
        ax1.legend(fontsize=8)
        ax1.fill_between(temp_series.index, temp_series.values,
                         alpha=0.08, color=PALETTE["primary"])
    _apply_ax_style(ax1, "7-Day Temperature Trend", ylabel="Temperature (°C)")

    # ── 2. Bar chart: daily mean temperatures ─────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    if stat_report.daily_means is not None and temp_col in stat_report.daily_means.columns:
        daily = stat_report.daily_means[temp_col]
        bars = ax2.bar(
            [d.strftime("%a\n%d %b") for d in daily.index],
            daily.values,
            color=[PALETTE["primary"] if v >= 0 else PALETTE["secondary"]
                   for v in daily.values],
            edgecolor=PALETTE["grid"], linewidth=0.5, width=0.6,
        )
        for bar, val in zip(bars, daily.values):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                f"{val:.1f}°", ha="center", va="bottom",
                fontsize=7.5, color=PALETTE["text"],
            )
        ax2.set_ylim(bottom=min(daily.values) - 2)
    _apply_ax_style(ax2, "Daily Mean Temperature", ylabel="°C")

    # ── 3. Histogram: temperature distribution ────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 1])
    if temp_col in df.columns:
        temp_vals = df[temp_col].dropna().values
        n, bins, patches = ax3.hist(
            temp_vals, bins=24, color=PALETTE["accent"],
            edgecolor=PALETTE["background"], linewidth=0.3, alpha=0.85,
        )
        # Normal curve overlay
        mu, sigma = np.mean(temp_vals), np.std(temp_vals, ddof=1)
        x_norm = np.linspace(bins[0], bins[-1], 200)
        y_norm = stats.norm.pdf(x_norm, mu, sigma) * len(temp_vals) * (bins[1] - bins[0])
        ax3.plot(x_norm, y_norm, color=PALETTE["secondary"],
                 linewidth=2, label=f"Normal (μ={mu:.1f}, σ={sigma:.1f})")
        ax3.axvline(mu, color=PALETTE["highlight"], linestyle="--",
                    linewidth=1.5, label=f"Mean = {mu:.1f}°C")
        ax3.legend(fontsize=7.5)
    _apply_ax_style(ax3, "Temperature Distribution", xlabel="°C", ylabel="Frequency")

    # ── 4. Box plot: temperature per day ──────────────────────────────────────
    ax4 = fig.add_subplot(gs[2, 0])
    if temp_col in df.columns:
        groups = [grp[temp_col].dropna().values
                  for _, grp in df.groupby(df.index.date)]
        labels = [str(d) for d in sorted(df.index.normalize().unique())]
        labels = [pd.Timestamp(l).strftime("%a\n%d") for l in labels]
        bp = ax4.boxplot(
            groups, labels=labels, patch_artist=True,
            boxprops=dict(facecolor=PALETTE["primary"], alpha=0.5, color=PALETTE["muted"]),
            whiskerprops=dict(color=PALETTE["muted"]),
            capprops=dict(color=PALETTE["muted"]),
            flierprops=dict(marker="o", markerfacecolor=PALETTE["secondary"],
                            markersize=4, alpha=0.7, markeredgewidth=0),
            medianprops=dict(color=PALETTE["highlight"], linewidth=2),
        )
    _apply_ax_style(ax4, "Temperature Box Plot (Per Day)", ylabel="°C")

    # ── 5. Scatter: Temperature vs Humidity + regression line ─────────────────
    ax5 = fig.add_subplot(gs[2, 1])
    if temp_col in df.columns and hum_col in df.columns:
        scatter_data = df[[temp_col, hum_col]].dropna()
        ax5.scatter(
            scatter_data[temp_col], scatter_data[hum_col],
            color=PALETTE["primary"], alpha=0.35, s=12, edgecolors="none",
        )
        if len(scatter_data) >= 3:
            slope, intercept, r_val, _, _ = stats.linregress(
                scatter_data[temp_col], scatter_data[hum_col]
            )
            x_line = np.linspace(scatter_data[temp_col].min(),
                                  scatter_data[temp_col].max(), 100)
            y_line = slope * x_line + intercept
            ax5.plot(x_line, y_line, color=PALETTE["secondary"],
                     linewidth=2, label=f"Regression (r={r_val:.3f})")
            ax5.legend(fontsize=8)
    _apply_ax_style(
        ax5, "Temperature vs Humidity",
        xlabel="Temperature (°C)", ylabel="Relative Humidity (%)"
    )

    plt.savefig(CHART_OUTPUT_FILE, dpi=CHART_DPI, bbox_inches="tight",
                facecolor=PALETTE["background"])
    print(f"\n  Charts saved → {CHART_OUTPUT_FILE}")
    plt.show()
