import json
import csv
from urllib.request import urlopen
from datetime import datetime, timezone
from collections import defaultdict
import pandas as pd

API_URL = "https://api.energy-charts.info/public_power?country=at&start=2020-01-01&end=2025-12-31"

RAW_CSV = "at_wind_solar_raw_2020_2025.csv"
DAILY_CSV = "at_wind_solar_daily_2020_2025.csv"


def normalize_name(name: str) -> str:
    return name.strip().lower()


def find_series(production_types):
    """
    Return dict with expected keys:
    solar, wind_onshore, wind_offshore
    Missing series are filled with zeros later.
    """
    out = {"solar": None, "wind_onshore": None, "wind_offshore": None}

    for entry in production_types:
        name = normalize_name(entry.get("name", ""))
        data = entry.get("data", [])

        if "solar" in name and out["solar"] is None:
            out["solar"] = data
        elif "wind onshore" in name and out["wind_onshore"] is None:
            out["wind_onshore"] = data
        elif "wind offshore" in name and out["wind_offshore"] is None:
            out["wind_offshore"] = data

    return out


def infer_step_hours(unix_seconds):
    if len(unix_seconds) < 2:
        return 0.25  # fallback
    step_sec = unix_seconds[1] - unix_seconds[0]
    return step_sec / 3600.0


def main():
    # 1) Load JSON from API
    with urlopen(API_URL) as response:
        payload = json.load(response)

    unix_seconds = payload.get("unix_seconds", [])
    production_types = payload.get("production_types", [])

    if not unix_seconds or not production_types:
        raise RuntimeError("No data returned from API.")

    series = find_series(production_types)
    n = len(unix_seconds)

    solar = series["solar"] if series["solar"] is not None else [0.0] * n
    wind_on = series["wind_onshore"] if series["wind_onshore"] is not None else [0.0] * n
    wind_off = series["wind_offshore"] if series["wind_offshore"] is not None else [0.0] * n

    # Ensure all series lengths match timestamps
    if not (len(solar) == len(wind_on) == len(wind_off) == n):
        raise RuntimeError("Series length mismatch in API response.")

    # 2) Save raw time series CSV
    with open(RAW_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "unix_seconds",
            "timestamp_utc",
            "date",
            "solar_mw",
            "wind_onshore_mw",
            "wind_offshore_mw",
            "wind_total_mw",
        ])

        for i, ts in enumerate(unix_seconds):
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            date_str = dt.date().isoformat()
            w_total = (wind_on[i] or 0.0) + (wind_off[i] or 0.0)

            writer.writerow([
                ts,
                dt.isoformat(),
                date_str,
                solar[i],
                wind_on[i],
                wind_off[i],
                w_total,
            ])

    # 3) Aggregate to daily energy (MWh) and save daily CSV
    step_h = infer_step_hours(unix_seconds)
    daily = defaultdict(lambda: {
        "solar_mwh": 0.0,
        "wind_onshore_mwh": 0.0,
        "wind_offshore_mwh": 0.0,
        "wind_total_mwh": 0.0,
    })

    for i, ts in enumerate(unix_seconds):
        date_str = datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
        s = (solar[i] or 0.0) * step_h
        wo = (wind_on[i] or 0.0) * step_h
        wf = (wind_off[i] or 0.0) * step_h
        wt = wo + wf

        daily[date_str]["solar_mwh"] += s
        daily[date_str]["wind_onshore_mwh"] += wo
        daily[date_str]["wind_offshore_mwh"] += wf
        daily[date_str]["wind_total_mwh"] += wt

    with open(DAILY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "date",
            "solar_mwh",
            "wind_onshore_mwh",
            "wind_offshore_mwh",
            "wind_total_mwh",
        ])
        for d in sorted(daily.keys()):
            row = daily[d]
            writer.writerow([
                d,
                round(row["solar_mwh"], 3),
                round(row["wind_onshore_mwh"], 3),
                round(row["wind_offshore_mwh"], 3),
                round(row["wind_total_mwh"], 3),
            ])

    print(f"Saved raw data to: {RAW_CSV}")
    print(f"Saved daily data to: {DAILY_CSV}")


if __name__ == "__main__":
    main()

    df = pd.read_csv("at_wind_solar_daily_2020_2025.csv", index_col = 0)
    df = df[["solar_mwh", "wind_total_mwh"]]
    # Mean profile for each calendar day across all available years
    df_work = df.copy()
    df_work.index = pd.to_datetime(df_work.index)

    # Group by month-day (e.g. 01-01, 01-02, ...), then average across years
    daily_mean_one_year = (
        df_work.assign(month_day=df_work.index.strftime('%m-%d'))
        .groupby('month_day')[['solar_mwh', 'wind_total_mwh']]
        .mean()
        .sort_index()
        .reset_index()
        .rename(columns={'month_day': 'day_of_year_label'})
    )

    daily_mean_one_year['day_of_year'] = range(1, len(daily_mean_one_year) + 1)
    daily_mean_one_year = daily_mean_one_year[['day_of_year', 'day_of_year_label', 'solar_mwh', 'wind_total_mwh']]

    daily_mean_one_year = daily_mean_one_year[["wind_total_mwh", "solar_mwh"]]
    df_result = daily_mean_one_year.rolling(window = 14).mean()
    df_result.plot.area(stacked = False)