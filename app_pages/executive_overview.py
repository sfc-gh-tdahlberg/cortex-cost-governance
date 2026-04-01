import streamlit as st
import pandas as pd
from src.data import get_metering_daily, get_ai_functions_usage

st.title(":material/bar_chart: Executive Overview")

days = st.sidebar.slider("Lookback (days)", 7, 180, 90)

with st.spinner("Loading metering data..."):
    df_meter = get_metering_daily(days)
    df_funcs = get_ai_functions_usage(days)

if df_meter.empty:
    st.warning("No AI metering data found for the selected period.")
    st.stop()

df_meter["USAGE_DATE"] = pd.to_datetime(df_meter["USAGE_DATE"])
df_meter["CREDITS_USED"] = pd.to_numeric(df_meter["CREDITS_USED"], errors="coerce")

total_credits = df_meter["CREDITS_USED"].sum()
current_month = df_meter[df_meter["USAGE_DATE"].dt.month == pd.Timestamp.now().month]["CREDITS_USED"].sum()
prior_month = df_meter[df_meter["USAGE_DATE"].dt.month == (pd.Timestamp.now().month - 1)]["CREDITS_USED"].sum()
mom_delta = ((current_month - prior_month) / prior_month * 100) if prior_month > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total AI Credits", f"{total_credits:,.2f}")
c2.metric("MTD Credits", f"{current_month:,.2f}")
c3.metric("Prior Month", f"{prior_month:,.2f}")
c4.metric("MoM Change", f"{mom_delta:+.1f}%")

st.divider()

st.subheader("Daily AI Credit Consumption")
daily_total = df_meter.groupby("USAGE_DATE")["CREDITS_USED"].sum().reset_index()
st.area_chart(daily_total.set_index("USAGE_DATE"), y="CREDITS_USED", use_container_width=True)

st.subheader("Credits by Service Type")
by_service = df_meter.groupby("SERVICE_TYPE")["CREDITS_USED"].sum().reset_index()
st.bar_chart(by_service.set_index("SERVICE_TYPE"), y="CREDITS_USED", use_container_width=True)

if not df_funcs.empty:
    df_funcs["TOTAL_CREDITS"] = pd.to_numeric(df_funcs["TOTAL_CREDITS"], errors="coerce")
    st.subheader("Top 10 Functions by Credits")
    top_funcs = df_funcs.groupby("FUNCTION_NAME")["TOTAL_CREDITS"].sum().nlargest(10).reset_index()
    st.bar_chart(top_funcs.set_index("FUNCTION_NAME"), y="TOTAL_CREDITS", use_container_width=True)

st.subheader("Raw Metering Data")
st.dataframe(df_meter.sort_values("USAGE_DATE", ascending=False), use_container_width=True)
