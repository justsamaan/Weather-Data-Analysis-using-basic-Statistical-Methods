"""
statistics_engine.py
Compute a comprehensive suite of basic statistical measures on weather data.
"""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass, field
from typing import Any

from config import HOURLY_VARS, VAR_LABELS, ROLLING_WINDOW_HOURS, Z_SCORE_THRESHOLD


@dataclass
class VariableStats:
    """All statistics for a single weather variable."""
    label:      str
    mean:       float
    median:     float
    mode:       float
    variance:   float
    std_dev:    float
    minimum:    float
    maximum:    float
    data_range: float
    q25:        float
    q75:        float
    iqr:        float
    skewness:   float
    kurtosis:   float


@dataclass
class CorrelationResult:
    var_x:     str
    var_y:     str
    pearson_r: float
    p_value:   float
    strength:  str   # "Strong", "Moderate", "Weak"
    direction: str   # "Positive" / "Negative"


@dataclass
class RegressionResult:
    var_x:     str
    var_y:     str
    slope:     float
    intercept: float
    r_squared: float
    std_err:   float


@dataclass
class StatisticsReport:
    variable_stats: dict[str, VariableStats]            = field(default_factory=dict)
    correlations:   list[CorrelationResult]             = field(default_factory=list)
    regression:     RegressionResult | None             = None
    rolling_mean:   pd.Series | None                   = None
    outliers:       dict[str, list[tuple[str, float]]] = field(default_factory=dict)
    daily_means:    pd.DataFrame | None                 = None


def _strength_label(r: float) -> str:
    ar = abs(r)
    if ar >= 0.7:
        return "Strong"
    elif ar >= 0.4:
        return "Moderate"
    return "Weak"


def compute_statistics(df: pd.DataFrame) -> StatisticsReport:
    """
    Run all statistical analyses on the weather DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        7-day hourly data as returned by weather_api.fetch_weather().

    Returns
    -------
    StatisticsReport
    """
    report = StatisticsReport()

    # ── Per-variable statistics ───────────────────────────────────────────────
    for col in HOURLY_VARS:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if series.empty:
            continue

        arr = series.to_numpy(dtype=float)
        mode_result = stats.mode(np.round(arr, 1), keepdims=True)
        mode_val = float(mode_result.mode[0])

        q25, q75 = float(np.percentile(arr, 25)), float(np.percentile(arr, 75))

        report.variable_stats[col] = VariableStats(
            label      = VAR_LABELS.get(col, col),
            mean       = round(float(np.mean(arr)), 3),
            median     = round(float(np.median(arr)), 3),
            mode       = round(mode_val, 3),
            variance   = round(float(np.var(arr, ddof=1)), 3),
            std_dev    = round(float(np.std(arr, ddof=1)), 3),
            minimum    = round(float(arr.min()), 3),
            maximum    = round(float(arr.max()), 3),
            data_range = round(float(arr.max() - arr.min()), 3),
            q25        = round(q25, 3),
            q75        = round(q75, 3),
            iqr        = round(q75 - q25, 3),
            skewness   = round(float(stats.skew(arr)), 3),
            kurtosis   = round(float(stats.kurtosis(arr)), 3),
        )

    # ── Outlier detection (z-score) on temperature ────────────────────────────
    temp_col = "temperature_2m"
    if temp_col in df.columns:
        temp = df[temp_col].dropna()
        z_scores = np.abs(stats.zscore(temp.to_numpy(dtype=float)))
        outlier_mask = z_scores >= Z_SCORE_THRESHOLD
        outlier_times  = temp.index[outlier_mask]
        outlier_values = temp.values[outlier_mask]
        report.outliers[temp_col] = [
            (t.strftime("%Y-%m-%d %H:%M"), round(float(v), 2))
            for t, v in zip(outlier_times, outlier_values)
        ]

    # ── Correlations ──────────────────────────────────────────────────────────
    correlation_pairs = [
        ("temperature_2m", "relative_humidity_2m"),
        ("temperature_2m", "wind_speed_10m"),
        ("temperature_2m", "apparent_temperature"),
        ("relative_humidity_2m", "precipitation"),
    ]
    for var_x, var_y in correlation_pairs:
        if var_x not in df.columns or var_y not in df.columns:
            continue
        merged = df[[var_x, var_y]].dropna()
        if len(merged) < 3:
            continue
        r, p = stats.pearsonr(merged[var_x], merged[var_y])
        report.correlations.append(CorrelationResult(
            var_x     = VAR_LABELS.get(var_x, var_x),
            var_y     = VAR_LABELS.get(var_y, var_y),
            pearson_r = round(float(r), 4),
            p_value   = round(float(p), 6),
            strength  = _strength_label(r),
            direction = "Positive" if r >= 0 else "Negative",
        ))

    # ── Linear regression: Temperature → Apparent Temperature ─────────────────
    if "temperature_2m" in df.columns and "apparent_temperature" in df.columns:
        lr_data = df[["temperature_2m", "apparent_temperature"]].dropna()
        if len(lr_data) >= 3:
            slope, intercept, r_val, _, std_err = stats.linregress(
                lr_data["temperature_2m"],
                lr_data["apparent_temperature"],
            )
            report.regression = RegressionResult(
                var_x     = VAR_LABELS["temperature_2m"],
                var_y     = VAR_LABELS["apparent_temperature"],
                slope     = round(float(slope), 4),
                intercept = round(float(intercept), 4),
                r_squared = round(float(r_val ** 2), 4),
                std_err   = round(float(std_err), 4),
            )

    # ── Rolling mean (24-hr window) on temperature ────────────────────────────
    if "temperature_2m" in df.columns:
        report.rolling_mean = (
            df["temperature_2m"]
            .rolling(window=ROLLING_WINDOW_HOURS, min_periods=1)
            .mean()
            .round(3)
        )

    # ── Daily means ───────────────────────────────────────────────────────────
    numeric_cols = [c for c in HOURLY_VARS if c in df.columns]
    report.daily_means = (
        df[numeric_cols]
        .resample("D")
        .mean()
        .round(2)
    )

    return report
