"""
config.py
Global constants and configuration for the Weather Data Analysis project.
"""

# ── Open-Meteo API ────────────────────────────────────────────────────────────
BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Variables to request (hourly)
HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "wind_speed_10m",
    "surface_pressure",
]

# Friendly display names
VAR_LABELS = {
    "temperature_2m":       "Temperature (°C)",
    "relative_humidity_2m": "Relative Humidity (%)",
    "apparent_temperature": "Apparent Temperature (°C)",
    "precipitation":        "Precipitation (mm)",
    "wind_speed_10m":       "Wind Speed (km/h)",
    "surface_pressure":     "Surface Pressure (hPa)",
}

# Forecast horizon (days)
FORECAST_DAYS = 7

# ── IP Geolocation ────────────────────────────────────────────────────────────
GEO_URL = "http://ip-api.com/json/"

# ── Statistics ────────────────────────────────────────────────────────────────
ROLLING_WINDOW_HOURS = 24      # rolling mean window
Z_SCORE_THRESHOLD    = 2.0     # flag as outlier if |z| >= this

# ── Chart colours ────────────────────────────────────────────────────────────
PALETTE = {
    "primary":     "#4FC3F7",   # sky blue
    "secondary":   "#FF7043",   # deep orange
    "accent":      "#A5D6A7",   # soft green
    "highlight":   "#FFD54F",   # amber
    "background":  "#0D1117",   # dark background
    "surface":     "#161B22",   # card surface
    "text":        "#E6EDF3",   # primary text
    "muted":       "#8B949E",   # muted text
    "grid":        "#21262D",   # gridlines
}

# ── Output ────────────────────────────────────────────────────────────────────
CHART_OUTPUT_FILE = "weather_analysis_charts.png"
CHART_DPI         = 150
