import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Mobile Ops Tracker Pro", layout="wide")

# --- GOOGLE SHEETS CONNECTION ---
# This looks for the configuration in your Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Function to fetch data safely
def fetch_data():
    return conn.read(ttl="0s") # ttl=0 ensures we get live data, not cached

df = fetch_data()

st.title("Mobile Service Operations - Google Sheets Edition")

# --- SIDEBAR NAVIGATION ---
menu = st.sidebar.selectbox("Go To:", ["Daily Entry", "Monthly Dashboard", "App Settings"])

if menu == "Daily Entry":
    st.header("📝 Daily KPI Entry")
    
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.today())
            reg = st.number_input("Total Calls Registered", min_value=0)
            closed = st.number_input("Total Calls Closed", min_value=0)
        with col2:
            rating = st.slider("Customer Rating", 0.0, 5.0, 4.5)
            # ... (Add other fields here as needed)
        
        submit = st.form_submit_button("Save to Google Sheets")

    if submit:
        # Create new row
        new_row = pd.DataFrame([{
            "Date": date.strftime('%Y-%m-%d'),
            "Total Call Registered": reg,
            "Total Call Closed": closed,
            "Customer Rating": rating
        }])
        
        # Append to existing data
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # Write back to Google Sheets
        conn.update(data=updated_df)
        st.success("Data successfully pushed to Google Sheets!")
        st.balloons()

elif menu == "Monthly Dashboard":
    st.header("📊 Performance Dashboard")
    if not df.empty:
        # Simple Metric Card
        total_reg = df["Total Call Registered"].astype(int).sum()
        st.metric("Total Regional Calls", total_reg)
        
        # Trend Line
        fig = px.line(df, x="Date", y="Total Call Registered", title="Registration Trend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sheet is empty.")

elif menu == "App Settings":
    st.header("⚙️ Configuration")
    st.info("To change the Spreadsheet URL or Keys, update the **Secrets** section in your Streamlit Cloud Dashboard.")
    
    # Optional: Allow user to view current Sheet URL (Read Only for security)
    current_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    st.text_input("Active Spreadsheet URL", value=current_url, disabled=True)
    
    if st.button("Force Refresh Data"):
        st.cache_data.clear()
        st.rerun()