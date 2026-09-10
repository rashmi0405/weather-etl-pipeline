import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ---------- Page config ----------
st.set_page_config(page_title="Weather ETL Dashboard", layout="wide")
st.title("🌤️ Weather ETL Dashboard")
st.caption("Live data from Postgres, loaded by the Airflow `weather_etl` DAG")

# ---------- Connect to Postgres ----------
@st.cache_resource
def get_engine():
    return create_engine("postgresql://localhost/weather_db")

@st.cache_data(ttl=60)  # refresh from DB every 60 seconds
def load_data():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM weather_data ORDER BY timestamp", engine)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

if df.empty:
    st.warning("No data found yet. Run the Airflow DAG first.")
    st.stop()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start, end = date_range
    mask = (df["timestamp"].dt.date >= start) & (df["timestamp"].dt.date <= end)
    df = df[mask]

metric = st.sidebar.radio(
    "Primary metric",
    ["temperature_f", "temperature_c", "humidity_pct", "precipitation_mm"],
    index=0
)

show_table = st.sidebar.checkbox("Show raw data table", value=False)

# ---------- KPI row ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Temp (°F)", f"{df['temperature_f'].mean():.1f}")
col2.metric("Max Temp (°F)", f"{df['temperature_f'].max():.1f}")
col3.metric("Avg Humidity (%)", f"{df['humidity_pct'].mean():.1f}")
col4.metric("Total Precip (mm)", f"{df['precipitation_mm'].sum():.1f}")

# ---------- Main chart ----------
st.subheader(f"{metric.replace('_', ' ').title()} over time")
fig = px.line(df, x="timestamp", y=metric, markers=True)
fig.update_layout(height=450)
st.plotly_chart(fig, use_container_width=True)

# ---------- Secondary comparison chart ----------
st.subheader("Temperature vs Humidity")
fig2 = px.line(df, x="timestamp", y=["temperature_f", "humidity_pct"])
fig2.update_layout(height=350)
st.plotly_chart(fig2, use_container_width=True)

# ---------- Precipitation bar chart ----------
st.subheader("Precipitation by hour")
fig3 = px.bar(df, x="timestamp", y="precipitation_mm")
fig3.update_layout(height=300)
st.plotly_chart(fig3, use_container_width=True)

# ---------- Raw data ----------
if show_table:
    st.subheader("Raw data")
    st.dataframe(df, use_container_width=True)

st.caption(f"Showing {len(df)} rows | Last refreshed data through {df['timestamp'].max()}")