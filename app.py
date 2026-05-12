import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# Configuration
DATA_FILE = "data.csv"
st.set_page_config(page_title="Mobile Ops Tracker", layout="wide")

# --- DATA LOADING ---
# --- IMPROVED DATA LOADING ---
if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
    try:
        df = pd.read_csv(DATA_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
    except Exception as e:
        st.error(f"Error loading data: {e}")
        df = pd.DataFrame() # Fallback to empty
else:
    # This creates the structure if the file is missing or empty
    df = pd.DataFrame(columns=[
        "Date", "Total Call Registered", "Total Call Closed", 
        "Total IW Calls Closed", "Total OW Calls Closed", 
        "IW Part Consumption", "OW Part Consumption", 
        "Calls Pending for Parts", "Calls Pending for Delivery", 
        "Repeat Calls Registered", "Calls Closed Within TAT", "Customer Rating"
    ])

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Operations Menu")
menu = st.sidebar.selectbox("Go To:", ["Daily Entry", "Monthly Dashboard", "View Logs"])

# --- SCREEN 1: DAILY ENTRY ---
if menu == "Daily Entry":
    st.header("📝 Daily KPI Entry")
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Operation Date", datetime.today())
            reg = st.number_input("Total Calls Registered", min_value=0, step=1)
            closed = st.number_input("Total Calls Closed", min_value=0, step=1)
            iw_closed = st.number_input("In-Warranty (IW) Closed", min_value=0, step=1)
            ow_closed = st.number_input("Out-of-Warranty (OW) Closed", min_value=0, step=1)
            tat_closed = st.number_input("Closed Within TAT", min_value=0, step=1)

        with col2:
            iw_cost = st.number_input("IW Part Consumption (Value)", min_value=0.0)
            ow_cost = st.number_input("OW Part Consumption (Value)", min_value=0.0)
            p_parts = st.number_input("Pending for Parts", min_value=0, step=1)
            p_del = st.number_input("Pending for Delivery", min_value=0, step=1)
            repeat = st.number_input("Repeat Calls Registered", min_value=0, step=1)
            rating = st.slider("Customer Rating", 0.0, 5.0, 4.5)

        submit = st.form_submit_button("Save Daily Data")

    if submit:
        new_data = {
            "Date": date, "Total Call Registered": reg, "Total Call Closed": closed,
            "Total IW Calls Closed": iw_closed, "Total OW Calls Closed": ow_closed,
            "IW Part Consumption": iw_cost, "OW Part Consumption": ow_cost,
            "Calls Pending for Parts": p_parts, "Calls Pending for Delivery": p_del,
            "Repeat Calls Registered": repeat, "Calls Closed Within TAT": tat_closed,
            "Customer Rating": rating
        }
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"Data for {date} saved successfully!")
        st.balloons()

# --- SCREEN 2: DASHBOARD ---
elif menu == "Monthly Dashboard":
    st.header("📊 Performance Dashboard")
    
    if df.empty:
        st.warning("No data found. Please enter daily data first.")
    else:
        # Calculations
        total_reg = df["Total Call Registered"].sum()
        total_closed = df["Total Call Closed"].sum()
        closure_rate = (total_closed / total_reg * 100) if total_reg > 0 else 0
        avg_rating = df["Customer Rating"].mean()
        tat_perf = (df["Calls Closed Within TAT"].sum() / total_closed * 100) if total_closed > 0 else 0
        
        # Summary Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Registered", total_reg)
        c2.metric("Closure %", f"{closure_rate:.1f}%", delta=f"{closure_rate-95:.1f}%")
        c3.metric("TAT Achievement", f"{tat_perf:.1f}%")
        c4.metric("Avg Rating", f"{avg_rating:.2f}/5")

        # Visuals
        st.subheader("Daily Closure Trend")
        fig = px.line(df, x="Date", y="Total Call Closed", markers=True, 
                     title="Daily Calls Closed", line_shape="spline")
        st.plotly_chart(fig, use_container_width=True)

        # Performance Status
        st.subheader("KPI Status Check")
        col_a, col_b = st.columns(2)
        
        with col_a:
            if closure_rate >= 95:
                st.success(f"✅ High Efficiency: {closure_rate:.1f}% Closure")
            else:
                st.error(f"🚨 Low Efficiency: {closure_rate:.1f}% Closure (Target 95%)")
        
        with col_b:
            repeat_rate = (df["Repeat Calls Registered"].sum() / total_reg * 100) if total_reg > 0 else 0
            if repeat_rate <= 2:
                st.success(f"✅ Quality OK: {repeat_rate:.1f}% Repeats")
            else:
                st.warning(f"⚠️ Quality Alert: {repeat_rate:.1f}% Repeats")

# --- SCREEN 3: DATA LOGS ---
elif menu == "View Logs":
    st.header("📋 Raw Data Logs")
    if not df.empty:
        st.dataframe(df.sort_values(by="Date", ascending=False))
        if st.button("Clear All Data"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.rerun()
    else:
        st.info("Log is empty.")
