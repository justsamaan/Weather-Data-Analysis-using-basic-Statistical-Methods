"""
main.py
Entry point for Weather Data Analysis Using Basic Statistical Methods.
Orchestrates: location detection → data fetch → statistics → report → charts.
"""

import sys
import os

# Ensure the project directory is on the path when run from other locations
sys.path.insert(0, os.path.dirname(__file__))

from location       import get_location
from weather_api    import fetch_weather
from statistics_engine import compute_statistics
from report         import print_report, C
from visualizer     import create_charts


def main() -> None:
    print(f"\n{C.BOLD}{C.CYAN}  ╔══════════════════════════════════════════════╗")
    print(f"  ║  WEATHER DATA ANALYSIS — Python Statistics  ║")
    print(f"  ╚══════════════════════════════════════════════╝{C.RESET}\n")

    # Step 1 — Detect location
    print(f"  {C.DIM}[1/4]{C.RESET} Detecting your location via IP geolocation …", end=" ", flush=True)
    try:
        location = get_location()
        print(f"{C.GREEN}✔{C.RESET}  {location.city}, {location.country}")
    except RuntimeError as exc:
        print(f"\n{C.RED}  ✘ {exc}{C.RESET}")
        sys.exit(1)

    # Step 2 — Fetch weather data
    print(f"  {C.DIM}[2/4]{C.RESET} Fetching 7-day hourly data from Open-Meteo …", end=" ", flush=True)
    try:
        current, df = fetch_weather(location)
        print(f"{C.GREEN}✔{C.RESET}  {len(df)} hourly records retrieved")
    except RuntimeError as exc:
        print(f"\n{C.RED}  ✘ {exc}{C.RESET}")
        sys.exit(1)

    # Step 3 — Compute statistics
    print(f"  {C.DIM}[3/4]{C.RESET} Running statistical analysis …", end=" ", flush=True)
    stat_report = compute_statistics(df)
    print(f"{C.GREEN}✔{C.RESET}  {len(stat_report.variable_stats)} variables analysed")

    # Step 4 — Print report
    print(f"  {C.DIM}[4/4]{C.RESET} Generating report …\n")
    print_report(location, current, stat_report)

    # Step 5 — Charts
    print(f"  {C.CYAN}Rendering charts …{C.RESET}")
    create_charts(df, stat_report, location)
    print(f"\n{C.BOLD}{C.GREEN}  Analysis complete!{C.RESET}\n")


if __name__ == "__main__":
    main()
