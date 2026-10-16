import csv
from datetime import datetime, timezone
from pathlib import Path

import requests

# Squamish Airport (WSK)
URL = "https://api.weather.gc.ca/collections/swob-realtime/items"
DEST = Path("data/squamish_airport_hourly.csv")

FIELDS = [
    "timestamp_utc",
    "wind_kn",
    "direction_deg",
    "temperature_c",
    "pressure_hpa",
]


def get_value(properties, *names):
    for name in names:
        value = properties.get(name)
        if isinstance(value, dict):
            value = value.get("value")
        if value is not None and value != "":
            return value
    return None


def main():
    response = requests.get(
        URL,
        params={
            "url": "WSK",
            "sortby": "-date_tm-value",
            "limit": 100,
            "f": "json",
        },
        timeout=30,
    )
    response.raise_for_status()

    features = response.json().get("features", [])
    rows = {}

    if DEST.exists():
        with DEST.open(newline="") as file:
            for row in csv.DictReader(file):
                rows[row["timestamp_utc"]] = row

    for feature in features:
        p = feature.get("properties", {})

        timestamp = get_value(
            p, "date_tm-value", "date_tm", "datetime"
        )

        if not timestamp:
            continue

        wind_kmh = get_value(p, "avg_wnd_spd_10m-value")

        try:
            wind_kn = (
                round(float(wind_kmh) / 1.852, 2)
                if wind_kmh is not None
                else None
            )
        except (TypeError, ValueError):
            wind_kn = None

        rows[str(timestamp)] = {
            "timestamp_utc": timestamp,
            "wind_kn": wind_kn,
            "direction_deg": get_value(
                p, "avg_wnd_dir_10m-value"
            ),
            "temperature_c": get_value(
                p, "air_temp-value"
            ),
            "pressure_hpa": get_value(
                p, "stn_pres-value"
            ),
        }

    if not rows:
        raise RuntimeError(
            "No airport observations found. Verify station "
            "identifier and API response."
        )

    DEST.parent.mkdir(parents=True, exist_ok=True)

    with DEST.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()

        for timestamp in sorted(rows):
            writer.writerow(rows[timestamp])

    print(f"Saved {len(rows)} airport observations")


if __name__ == "__main__":
    main()
