import csv
from pathlib import Path

import requests

# Environment Canada: Pam Rocks weather station
URL = "https://api.weather.gc.ca/collections/swob-realtime/items"

# Historical wind database
DEST = Path("data/pam_rocks_hourly.csv")

FIELDS = [
    "timestamp_utc",
    "wind_kn",
    "max_10min_kn",
    "direction_deg",
    "temperature_c",
    "pressure_hpa",
]


def main():
    response = requests.get(
        URL,
        params={
            "url": "CWAS",
            "sortby": "-date_tm-value",
            "limit": 100,
            "f": "json",
        },
        timeout=30,
    )

    response.raise_for_status()

    existing = {}

    # Load previously collected observations
    if DEST.exists():
        with DEST.open(newline="", encoding="utf-8") as f:
            existing = {
                row["timestamp_utc"]: row
                for row in csv.DictReader(f)
            }

    # Collect new observations
    for feature in response.json().get("features", []):
        p = feature.get("properties", {})

        if p.get("tc_id-value") != "WAS":
            continue

        if p.get("stn_nam-value") != "HOWE SOUND - PAM ROCKS":
            continue

        timestamp = p.get("date_tm-value")
        speed = p.get("avg_wnd_spd_10m_pst10mts")

        if not timestamp or speed is None:
            continue

        def knots(value):
            if value is None:
                return ""
            return round(float(value) / 1.852, 2)

        existing[timestamp] = {
            "timestamp_utc": timestamp,
            "wind_kn": knots(speed),
            "max_10min_kn": knots(
                p.get("max_wnd_spd_10m_pst10mts")
            ),
            "direction_deg": p.get(
                "avg_wnd_dir_10m_pst10mts", ""
            ),
            "temperature_c": p.get("air_temp", ""),
            "pressure_hpa": p.get("stn_pres", ""),
        }

    if not existing:
        raise RuntimeError("No Pam Rocks observations returned")

    # Create data folder automatically
    DEST.parent.mkdir(parents=True, exist_ok=True)

    # Save observations without duplicates
    with DEST.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

        for timestamp in sorted(existing):
            writer.writerow(existing[timestamp])

    print(
        f"Saved {len(existing)} unique Pam Rocks observations"
    )


if __name__ == "__main__":
    main()
