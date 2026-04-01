import streamlit as st
import pandas as pd
from src.data import get_cortex_search_daily, get_cortex_search_serving

st.title(":material/search: Cortex Search Costs")

st.markdown(
    "Cortex Search has a **continuous serving cost** even when idle. "
    "Suspend non-production services to avoid charges."
)

days = st.sidebar.slider("Lookback (days)", 7, 180, 90)

with st.spinner("Loading Cortex Search data..."):
    df_daily = get_cortex_search_daily(days)
    df_serving = get_cortex_search_serving(days)

tab1, tab2 = st.tabs(["Daily Usage (Serving + Embedding)", "Serving Detail"])

with tab1:
    if df_daily.empty:
        st.warning("No Cortex Search daily usage data found.")
    else:
        df_daily["USAGE_DATE"] = pd.to_datetime(df_daily["USAGE_DATE"])
        df_daily["TOTAL_CREDITS"] = pd.to_numeric(df_daily["TOTAL_CREDITS"], errors="coerce")

        total = df_daily["TOTAL_CREDITS"].sum()
        st.metric("Total Cortex Search Credits", f"{total:,.4f}")

        st.subheader("Credits by Consumption Type")
        by_type = df_daily.groupby("CONSUMPTION_TYPE")["TOTAL_CREDITS"].sum().reset_index()
        st.bar_chart(by_type.set_index("CONSUMPTION_TYPE"), y="TOTAL_CREDITS", use_container_width=True)

        st.subheader("Daily Trend by Service")
        daily_svc = df_daily.groupby(["USAGE_DATE", "SERVICE_NAME"])["TOTAL_CREDITS"].sum().reset_index()
        if not daily_svc.empty:
            pivot = daily_svc.pivot(index="USAGE_DATE", columns="SERVICE_NAME", values="TOTAL_CREDITS").fillna(0)
            st.line_chart(pivot, use_container_width=True)

        st.dataframe(df_daily.sort_values("USAGE_DATE", ascending=False), use_container_width=True)

with tab2:
    if df_serving.empty:
        st.warning("No Cortex Search serving data found.")
    else:
        df_serving["USAGE_DATE"] = pd.to_datetime(df_serving["USAGE_DATE"])
        df_serving["TOTAL_CREDITS"] = pd.to_numeric(df_serving["TOTAL_CREDITS"], errors="coerce")

        st.subheader("Serving Credits by Service")
        by_svc = df_serving.groupby("SERVICE_NAME")["TOTAL_CREDITS"].sum().sort_values(ascending=False).reset_index()
        st.bar_chart(by_svc.set_index("SERVICE_NAME"), y="TOTAL_CREDITS", use_container_width=True)

        st.subheader("Daily Serving Trend")
        daily_serving = df_serving.groupby("USAGE_DATE")["TOTAL_CREDITS"].sum().reset_index()
        st.area_chart(daily_serving.set_index("USAGE_DATE"), y="TOTAL_CREDITS", use_container_width=True)

        st.subheader("Serving Detail")
        st.dataframe(df_serving.sort_values("USAGE_DATE", ascending=False), use_container_width=True)

    with st.expander("Suspend Idle Search Services"):
        st.markdown("""
**Check running services:**
```sql
SHOW CORTEX SEARCH SERVICES IN ACCOUNT;
```

**Suspend to stop serving charges:**
```sql
ALTER CORTEX SEARCH SERVICE my_search_service SUSPEND SERVING;
```

**Resume when needed:**
```sql
ALTER CORTEX SEARCH SERVICE my_search_service RESUME SERVING;
```

Serving costs accrue **24/7** based on indexed data size, regardless of query volume.
A 50GB index costs ~315 credits/month even with zero queries.
""")
