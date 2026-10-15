
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Squamish Wind AI",
    page_icon="🌬️",
    layout="wide"
)

API_URL = "https://api.weather.gc.ca/collections/swob-realtime/items"

@st.cache_data(ttl=600)
def get_pam_rocks():
    response = requests.get(
        API_URL,
        params={
            "url": "CWAS",
            "sortby": "-date_tm-value",
            "limit": 24,
            "f": "json"
        },
        timeout=20
    )
    response.raise_for_status()

    rows = []
    for feature in response.json().get("features", []):
        p = feature.get("properties", {})

        if p.get("tc_id-value") != "WAS":
            continue

        speed = p.get("avg_wnd_spd_10m_pst10mts")
        direction = p.get("avg_wnd_dir_10m_pst10mts")
        gust = p.get("max_wnd_spd_10m_pst10mts")
        timestamp = p.get("date_tm-value")

        if speed is None or not timestamp:
            continue

        rows.append({
            "Time": pd.to_datetime(timestamp, utc=True),
            "Wind (kn)": speed / 1.852,
            "Gust (kn)": gust / 1.852 if gust is not None else None,
            "Direction": direction,
            "Temperature": p.get("air_temp"),
            "Pressure": p.get("stn_pres")
        })

    if not rows:
        raise ValueError("No Pam Rocks observations found.")

    return pd.DataFrame(rows).sort_values("Time")


st.title("🌬️ Squamish Wind AI")
st.subheader("Wing Foiling Wind Dashboard")

location = st.selectbox(
    "Riding location",
    ["Waterfront Park", "The Spit"]
)

st.caption(
    "Pam Rocks is a regional indicator, not a direct "
    "measurement of wind at your selected riding spot."
)

if st.button("Refresh wind data"):
    get_pam_rocks.clear()

try:
    df = get_pam_rocks()
    latest = df.iloc[-1]

    local_time = latest["Time"].tz_convert(
        "America/Vancouver"
    )
    age_hours = (
        pd.Timestamp.now(tz="UTC") - latest["Time"]
    ).total_seconds() / 3600

    if age_hours > 2:
        st.warning(
            "Latest observation is over 2 hours old. "
            "Data may be stale."
        )

    st.caption(
        f"Pam Rocks observation: "
        f"{local_time:%b %d, %Y at %I:%M %p} Pacific"
    )

    a, b, c = st.columns(3)

    with a:
        st.metric(
            "Wind Speed",
            f"{latest['Wind (kn)']:.1f} kn"
        )

    with b:
        direction = latest["Direction"]
        st.metric(
            "Wind Direction",
            f"{direction:.0f}°"
            if pd.notna(direction) else "N/A"
        )

    with c:
        gust = latest["Gust (kn)"]
        st.metric(
            "10-Minute Maximum",
            f"{gust:.1f} kn"
            if pd.notna(gust) else "N/A"
        )

    st.subheader("Recent Pam Rocks Wind")
    chart = df.set_index("Time")[
        ["Wind (kn)", "Gust (kn)"]
    ]
    st.line_chart(chart)

    st.subheader("Additional Observations")
    x, y = st.columns(2)

    with x:
        temp = latest["Temperature"]
        st.metric(
            "Air Temperature",
            f"{temp:.1f} °C"
            if pd.notna(temp) else "N/A"
        )

    with y:
        pressure = latest["Pressure"]
        st.metric(
            "Station Pressure",
            f"{pressure:.1f} hPa"
            if pd.notna(pressure) else "N/A"
        )

except Exception as e:
    st.error(f"Weather data unavailable: {e}")

st.divider()
st.subheader("Squamish Forecast Model")
st.info(
    "Forecasting is not trained yet. "
    "Next steps: historical weather, local observations, "
    "and rider reports."
)

st.subheader("Rider Reports")
st.caption(
    "Rider report storage is not connected yet."
)
