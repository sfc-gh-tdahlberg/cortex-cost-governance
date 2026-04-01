import streamlit as st
import pandas as pd
from src.data import get_ai_functions_usage

st.title(":material/smart_toy: AI Functions Deep Dive")

days = st.sidebar.slider("Lookback (days)", 7, 180, 90)

with st.spinner("Loading AI functions usage..."):
    df = get_ai_functions_usage(days)

if df.empty:
    st.warning("No AI Functions usage data found.")
    st.stop()

df["USAGE_DATE"] = pd.to_datetime(df["USAGE_DATE"])
df["TOTAL_CREDITS"] = pd.to_numeric(df["TOTAL_CREDITS"], errors="coerce")
df["TOTAL_TOKENS"] = pd.to_numeric(df["TOTAL_TOKENS"], errors="coerce")
df["QUERY_COUNT"] = pd.to_numeric(df["QUERY_COUNT"], errors="coerce")

c1, c2, c3 = st.columns(3)
c1.metric("Total Credits", f"{df['TOTAL_CREDITS'].sum():,.4f}")
c2.metric("Total Tokens", f"{df['TOTAL_TOKENS'].sum():,.0f}")
c3.metric("Total Queries", f"{df['QUERY_COUNT'].sum():,.0f}")

st.divider()

st.subheader("Daily Credit Trend")
daily = df.groupby("USAGE_DATE")["TOTAL_CREDITS"].sum().reset_index()
st.line_chart(daily.set_index("USAGE_DATE"), y="TOTAL_CREDITS", use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Credits by Function")
    by_func = df.groupby("FUNCTION_NAME")["TOTAL_CREDITS"].sum().sort_values(ascending=False).reset_index()
    st.bar_chart(by_func.set_index("FUNCTION_NAME"), y="TOTAL_CREDITS", use_container_width=True)

with col2:
    st.subheader("Credits by Model")
    by_model = df.groupby("MODEL_NAME")["TOTAL_CREDITS"].sum().sort_values(ascending=False).reset_index()
    st.bar_chart(by_model.set_index("MODEL_NAME"), y="TOTAL_CREDITS", use_container_width=True)

st.subheader("Function x Model Breakdown")
pivot = df.groupby(["FUNCTION_NAME", "MODEL_NAME"]).agg(
    CREDITS=("TOTAL_CREDITS", "sum"),
    TOKENS=("TOTAL_TOKENS", "sum"),
    QUERIES=("QUERY_COUNT", "sum"),
).reset_index().sort_values("CREDITS", ascending=False)
st.dataframe(pivot, use_container_width=True)

st.subheader("Daily Detail")
st.dataframe(df.sort_values("USAGE_DATE", ascending=False), use_container_width=True)
