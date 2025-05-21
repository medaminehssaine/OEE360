# streamlit_app.py

import streamlit as st
import pandas as pd
from ts_oee360.generator import run_simulation
from ts_oee360.utils import load_simulation_data, plot_oee_components
import os

st.set_page_config(layout="wide")
st.title("📊 TS_OEE360 Simulator Dashboard")

if st.button("▶️ Run Simulation"):
    os.makedirs("data", exist_ok=True)
    run_simulation("data/ultra_complex_OEE.csv")
    st.success("Simulation completed! CSV saved.")

st.markdown("---")

if os.path.exists("data/ultra_complex_OEE.csv"):
    df = load_simulation_data()

    st.subheader("📈 OEE Overview")
    st.dataframe(df.tail(50))

    st.subheader("📉 OEE Component Plots")
    plot_oee_components(df)

    st.markdown("---")
    st.metric("Final OEE", f"{df['oee'].mean():.2f}")
    st.metric("Availability Avg", f"{df['availability'].mean():.2f}")
    st.metric("Performance Avg", f"{df['performance'].mean():.2f}")
    st.metric("Quality Avg", f"{df['quality'].mean():.2f}")
else:
    st.warning("No simulation data found. Please run the simulation first.")
