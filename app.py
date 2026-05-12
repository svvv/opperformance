import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px

# Page Configuration
st.set_page_config(page_title="Mobile Service Ops Tracker", layout="wide")

# --- GOOGLE SHEETS CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        # Pulls the URL from your Secrets
        return conn.read(ttl="0s")
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return pd.DataFrame()

df = fetch_data()

# --- SIDEBAR ---
st.sidebar.title("Operations Menu")
menu = st.sidebar.selectbox("Go To:", ["Daily Entry", "Monthly Dashboard", "View Raw Data"])

# --- SCREEN 1: DAILY ENTRY (ALL SECTIONS INCLUDED) ---
if menu == "Daily Entry":
    st.header("📝 Daily Operational KPI Entry")
    
    with st.form("kpi_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Call Volume")
            date = st.date_input("Date", datetime.today())
            reg = st.number_input("Total Call Registered", min_value=0, step=1)
            closed = st.number_input("Total Call Closed", min_value=0, step=1)
            iw_closed = st.number_input("Total IW Calls Closed", min_value=0, step=1)
            ow_closed = st.number_input("Total OW Calls Closed", min_value=0, step=1)
            
            st.subheader("Pending & Quality")
            p_parts = st.number_input("Calls Pending for Parts", min_value=0, step=1)
            p_del = st.number_input("Calls Pending for Delivery", min_value=0, step=1)
            repeat = st.number_input("Repeat Calls Registered", min_value=0, step=1)

        with col2:
            st.subheader("Consumption (Value)")
            iw_val = st.number_input("IW Part Consumption Value", min_value=0.0)
            ow_val = st.number_input("OW Part Consumption Value", min_value=0.0)
            
            st.subheader("Performance & Rating")
            tat_closed = st.number_input("Calls Closed Within TAT", min_value=0, step=1)
            rating = st.slider("Customer Rating", 0.0, 5.0, 4.5, step=0.1)
            
            st.info("Ensure all fields match the daily operation report before saving.")

        submit = st.form_submit_button("Save to Cloud Database")

    if submit:
        # Create new data row
        new_row = pd.DataFrame([{
            "Date": date.strftime('%Y-%m-%d'),
            "Total Call Registered": reg,
            "Total Call Closed": closed,
            "Total IW Calls Closed": iw_closed,
            "Total OW Calls Closed": ow_closed,
            "IW Part Consumption": iw_val,
            "OW Part Consumption": ow_val,
            "Calls Pending for Parts": p_parts,
            "Calls Pending for Delivery": p_del,
            "Repeat Calls Registered": repeat,
            "Calls Closed Within TAT": tat_closed,
            "Customer Rating": rating
        }])
        
        # Append and Update
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=updated_df)
        st.success(f"Data for {date} successfully synced to Google Sheets!")
        st.balloons()

# --- SCREEN 2: DASHBOARD (WITH KPI LOGIC) ---
elif menu == "Monthly Dashboard":
    st.header("📊 Performance Analytics")
    
    if df.empty:
        st.warning("No data found in Google Sheets.")
    else:
        # Basic Totals
        total_reg = df["Total Call Registered"].astype(float).sum()
        total_closed = df["Total Call Closed"].astype(float).sum()
        
        # Calculations
        closure_pct = (total_closed / total_reg * 100) if total_reg > 0 else 0
        avg_rating = df["Customer Rating"].astype(float).mean()
        tat_perf = (df["Calls Closed Within TAT"].astype(float).sum() / total_closed * 100) if total_closed > 0 else 0
        
        # Dashboard Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Registered", int(total_reg))
        c2.metric("Closure %", f"{closure_pct:.1f}%")
        c3.metric("TAT Achievement", f"{tat_perf:.1f}%")
        c4.metric("Avg Rating", f"{avg_rating:.2f}")

        # Charts
        st.subheader("Daily Closure Trend")
        fig = px.area(df, x="Date", y="Total Call Closed", title="Calls Closed Over Time")
        st.plotly_chart(fig, use_container_width=True)
        
        # KPI Target Evaluation
        st.subheader("Target Status")
        if closure_pct >= 95:
            st.success(f"Closure Efficiency: {closure_pct:.1f}% (Target: >95%)")
        else:
            st.error(f"Closure Efficiency: {closure_pct:.1f}% (Target: >95%)")

# --- SCREEN 3: RAW DATA ---
elif menu == "View Raw Data":
    st.header("📋 Google Sheets Data Log")
    if not df.empty:
        st.dataframe(df)
        st.download_button("Download as CSV", df.to_csv(index=False), "ops_data.csv", "text/csv")
    else:
        st.info("Database is currently empty.")