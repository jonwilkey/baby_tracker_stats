"""Main streamlit app for Baby Tracker app stats.

Assumes that user will upload a compatible zip file.
"""

import plotly.express as px
import streamlit as st

from baby_tracker_stats.analysis import analyze_daytime_sleep
from baby_tracker_stats.io import extract_zip_data


# Upload and read data
last_n_weeks = st.number_input("Analyze the last N weeks of uploaded data set.", step=1)
uploaded_file = st.file_uploader(
    "Select the exported CSV zip-file from Baby Tracker App to upload here"
)
if uploaded_file is not None:
    baby_stats = extract_zip_data(uploaded_file)
    sleep_df, summary = analyze_daytime_sleep(baby_stats.sleep, last_n_weeks)
    fig = px.histogram(
        data_frame=sleep_df,
        x="dt_hours",
        marginal="box",
        title=(
            f"Hours between start of daytime naps in last {last_n_weeks} weeks"
            f"<br><sup>{summary}</sup>"
        )
    )
    st.plotly_chart(fig, use_container_width=True)
