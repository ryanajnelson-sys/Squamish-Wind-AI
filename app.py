import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Squamish Wind AI",
    page_icon="🌬️",
    layout="wide"
)

st.title("🌬️ Squamish Wind AI")
st.subheader("Wing Foiling Forecast Dashboard")

st.write("Your personal wind forecasting tool for Squamish.")

location = st.selectbox(
    "Choose your riding location",
    ["Waterfront Park", "The Spit"]
)

st.divider()

st.header("Today's Wind Forecast")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Wind Speed", "Coming soon")

with col2:
    st.metric("Best Riding Window", "Coming soon")

with col3:
    st.metric("Forecast Confidence", "Coming soon")

st.divider()

st.header("Is It Worth Going Today?")

st.info("Forecast model not connected yet.")

st.header("Rider Reports")

with st.form("rider_report"):
    wind = st.slider("Observed wind speed (knots)", 0, 40, 15)
    quality = st.selectbox(
        "How were the conditions?",
        ["Excellent", "Good", "Gusty", "Poor"]
    )
    notes = st.text_area("Session notes")

    submitted = st.form_submit_button("Submit Report")

    if submitted:
        st.success("Report entered! Database connection coming soon.")

st.caption(
    f"Squamish Wind AI | {datetime.now():%Y-%m-%d}"
)
