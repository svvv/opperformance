import streamlit as st

import pandas as pd

import os

import plotly.express as px

from datetime import datetime



DATA_FILE = "data.csv"



# Load existing data

if os.path.exists(DATA_FILE):

df = pd.read_csv(DATA_FILE)

else:

df = pd.DataFrame(columns=[

"Date",

"Total Call Registered",

"Total Call Closed",

"Total IW Calls Closed",

"Total OW Calls Closed",

"IW Part Consumption",

"OW Part Consumption",

"Calls Pending for Parts",

"Calls Pending for Delivery",

"Repeat Calls Registered",

"Calls Closed Within TAT",

"Customer Rating"

])



st.title("Mobile Service Operations Tracker")



menu = st.sidebar.selectbox(

"Select Option",

["Daily Entry", "Monthly Dashboard"]

)



if menu == "Daily Entry":



st.header("Daily KPI Entry")



date = st.date_input("Date", datetime.today())



registered = st.number_input("Total Call Registered", min_value=0)

closed = st.number_input("Total Call Closed", min_value=0)

iw_closed = st.number_input("Total IW Calls Closed", min_value=0)

ow_closed = st.number_input("Total OW Calls Closed", min_value=0)



iw_part = st.number_input("IW Part Consumption", min_value=0.0)

ow_part = st.number_input("OW Part Consumption", min_value=0.0)



pending_parts = st.number_input("Calls Pending for Parts", min_value=0)

pending_delivery = st.number_input("Calls Pending for Delivery", min_value=0)



repeat_calls = st.number_input("Repeat Calls Registered", min_value=0)



tat_closed = st.number_input("Calls Closed Within TAT", min_value=0)



rating = st.number_input(

"Customer Rating",

min_value=0.0,

max_value=5.0,

step=0.1

)



if st.button("Save Entry"):



new_row = {

"Date": date,

"Total Call Registered": registered,

"Total Call Closed": closed,

"Total IW Calls Closed": iw_closed,

"Total OW Calls Closed": ow_closed,

"IW Part Consumption": iw_part,

"OW Part Consumption": ow_part,

"Calls Pending for Parts": pending_parts,

"Calls Pending for Delivery": pending_delivery,

"Repeat Calls Registered": repeat_calls,

"Calls Closed Within TAT": tat_closed,

"Customer Rating": rating

}



df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

df.to_csv(DATA_FILE, index=False)



st.success("Data Saved Successfully")



if menu == "Monthly Dashboard":



st.header("Monthly Performance Dashboard")



if len(df) == 0:

st.warning("No data available")

else:



total_registered = df["Total Call Registered"].sum()

total_closed = df["Total Call Closed"].sum()



closure_pct = round((total_closed / total_registered) * 100, 2)



repeat_pct = round(

(df["Repeat Calls Registered"].sum() / total_registered) * 100,

2

)



avg_rating = round(df["Customer Rating"].mean(), 2)



col1, col2, col3, col4 = st.columns(4)



col1.metric("Total Registered", total_registered)

col2.metric("Total Closed", total_closed)

col3.metric("Closure %", f"{closure_pct}%")

col4.metric("Avg Rating", avg_rating)



st.subheader("Daily Closure Trend")



trend = px.line(

df,

x="Date",

y="Total Call Closed"

)



st.plotly_chart(trend, use_container_width=True)



st.subheader("Daily Data")

st.dataframe(df)



st.subheader("Performance Evaluation")



if closure_pct >= 95:

st.success("Closure performance is Excellent")

elif closure_pct >= 90:

st.warning("Closure performance needs improvement")

else:

st.error("Closure performance is Poor")



if repeat_pct < 2:

st.success("Repeat calls are under control")

else:

st.error("Repeat calls exceed target")

