"""
report.py
Print a formatted console report of weather statistics.
Uses tabulate for clean table output.
"""

from tabulate import tabulate
from config import VAR_LABELS, HOURLY_VARS
from statistics_engine import StatisticsReport
from location import LocationInfo


# ANSI colour helpers (work on Windows 10+ terminals)
class C:
    BOLD    = "\033[1m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    RESET   = "\033[0m"
    DIM     = "\033[2m"


def _header(text: str) -> str:
    width = 72
    line  = "═" * width
    return (
        f"\n{C.CYAN}{line}{C.RESET}\n"
        f"{C.BOLD}{C.CYAN}  {text}{C.RESET}\n"
        f"{C.CYAN}{line}{C.RESET}"
    )


def print_report(
    location: LocationInfo,
    current: dict,
    stat_report: StatisticsReport,
) -> None:

    print("\n" + "═" * 72)
    print(f"{C.BOLD}{C.CYAN}  WEATHER DATA ANALYSIS — STATISTICAL REPORT{C.RESET}")
    print("═" * 72)

    # ── Location ──────────────────────────────────────────────────────────────
    print(_header("📍  Location"))
    print(f"  City      : {C.BOLD}{location.city}, {location.region}{C.RESET}")
    print(f"  Country   : {location.country}")
    print(f"  Latitude  : {location.latitude}°   Longitude : {location.longitude}°")
    print(f"  Timezone  : {location.timezone}")
    print(f"  Detected IP: {location.ip}")

    # ── Current Conditions ────────────────────────────────────────────────────
    print(_header("🌤️  Current Conditions"))
    print(f"  Timestamp : {current.get('timestamp', 'N/A')}\n")
    current_rows = []
    for col in HOURLY_VARS:
        if col in current:
            current_rows.append([VAR_LABELS.get(col, col), current[col]])
    print(tabulate(current_rows, headers=["Parameter", "Value"],
                   tablefmt="rounded_outline", colalign=("left", "right")))

    # ── Statistical Summary ───────────────────────────────────────────────────
    print(_header("📊  Statistical Summary (7-Day Hourly Data)"))
    for col, vs in stat_report.variable_stats.items():
        print(f"\n  {C.BOLD}{C.GREEN}{vs.label}{C.RESET}")
        rows = [
            ["Mean",       vs.mean],
            ["Median",     vs.median],
            ["Mode",       vs.mode],
            ["Std Dev",    vs.std_dev],
            ["Variance",   vs.variance],
            ["Min",        vs.minimum],
            ["Max",        vs.maximum],
            ["Range",      vs.data_range],
            ["Q25 (25th %ile)", vs.q25],
            ["Q75 (75th %ile)", vs.q75],
            ["IQR",        vs.iqr],
            ["Skewness",   vs.skewness],
            ["Kurtosis",   vs.kurtosis],
        ]
        print(tabulate(rows, headers=["Statistic", "Value"],
                       tablefmt="simple", colalign=("left", "right")))

    # ── Correlations ──────────────────────────────────────────────────────────
    print(_header("🔗  Pearson Correlation Analysis"))
    corr_rows = []
    for c in stat_report.correlations:
        sig = "✔" if c.p_value < 0.05 else "✘"
        corr_rows.append([
            c.var_x, c.var_y,
            f"{c.pearson_r:+.4f}",
            f"{c.p_value:.6f}",
            c.strength,
            c.direction,
            sig,
        ])
    print(tabulate(
        corr_rows,
        headers=["Variable X", "Variable Y", "r", "p-value",
                 "Strength", "Direction", "Sig.(p<0.05)"],
        tablefmt="rounded_outline",
    ))

    # ── Regression ────────────────────────────────────────────────────────────
    if stat_report.regression:
        reg = stat_report.regression
        print(_header("📈  Linear Regression"))
        print(f"  {reg.var_x}  →  {reg.var_y}")
        reg_rows = [
            ["Slope (m)",   reg.slope],
            ["Intercept (b)", reg.intercept],
            ["R² (fit quality)", reg.r_squared],
            ["Std Error",   reg.std_err],
        ]
        print(tabulate(reg_rows, tablefmt="simple", colalign=("left", "right")))
        print(f"\n  Equation: {C.YELLOW}y = {reg.slope}x + {reg.intercept}{C.RESET}")

    # ── Outliers ──────────────────────────────────────────────────────────────
    print(_header("⚠️  Outlier Detection (Z-score ≥ 2.0 on Temperature)"))
    temp_outliers = stat_report.outliers.get("temperature_2m", [])
    if temp_outliers:
        out_rows = [[t, f"{v}°C"] for t, v in temp_outliers]
        print(tabulate(out_rows, headers=["Timestamp", "Temperature"],
                       tablefmt="rounded_outline"))
    else:
        print(f"  {C.GREEN}No significant outliers detected.{C.RESET}")

    # ── Daily Means ───────────────────────────────────────────────────────────
    print(_header("📅  Daily Mean Values"))
    if stat_report.daily_means is not None:
        dm = stat_report.daily_means.copy()
        dm.index = dm.index.strftime("%A, %d %b %Y")
        dm.columns = [VAR_LABELS.get(c, c) for c in dm.columns]
        print(tabulate(dm, headers="keys", tablefmt="rounded_outline",
                       floatfmt=".2f"))

    print(f"\n{'═' * 72}\n")
