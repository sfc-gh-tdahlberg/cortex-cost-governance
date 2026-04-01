import streamlit as st
import pandas as pd
from src.data import get_cortex_code_usage, get_cortex_code_queries

st.title(":material/code: Cortex Code Costs")

st.info(
    "**Note:** As of early 2026, Snowflake does not charge separately for Cortex Code. "
    "However, LLM invocations appear as **AI_SERVICES** credits. "
    "Once token pricing is enabled, costs will be tracked here."
)

days = st.sidebar.slider("Lookback (days)", 7, 180, 90)

with st.spinner("Loading Cortex Code data..."):
    df_services = get_cortex_code_usage(days)
    df_queries = get_cortex_code_queries(min(days, 30))

tab1, tab2 = st.tabs(["AI Services Credits", "Cortex-Related Queries"])

with tab1:
    if df_services.empty:
        st.warning("No AI_SERVICES metering data found.")
    else:
        df_services["USAGE_DATE"] = pd.to_datetime(df_services["USAGE_DATE"])
        df_services["CREDITS_USED"] = pd.to_numeric(df_services["CREDITS_USED"], errors="coerce")

        total = df_services["CREDITS_USED"].sum()
        st.metric("Total AI_SERVICES Credits", f"{total:,.4f}")

        st.subheader("Daily AI_SERVICES Credit Trend")
        st.area_chart(
            df_services.groupby("USAGE_DATE")["CREDITS_USED"].sum().reset_index().set_index("USAGE_DATE"),
            y="CREDITS_USED",
            use_container_width=True,
        )

        st.dataframe(df_services.sort_values("USAGE_DATE", ascending=False), use_container_width=True)

with tab2:
    if df_queries.empty:
        st.warning("No Cortex-related queries found in QUERY_HISTORY.")
    else:
        df_queries["USAGE_DATE"] = pd.to_datetime(df_queries["USAGE_DATE"])
        df_queries["CLOUD_CREDITS"] = pd.to_numeric(df_queries["CLOUD_CREDITS"], errors="coerce")
        df_queries["QUERY_COUNT"] = pd.to_numeric(df_queries["QUERY_COUNT"], errors="coerce")

        c1, c2 = st.columns(2)
        c1.metric("Total Cortex Queries", f"{df_queries['QUERY_COUNT'].sum():,.0f}")
        c2.metric("Cloud Service Credits", f"{df_queries['CLOUD_CREDITS'].sum():,.4f}")

        st.subheader("Queries by User")
        by_user = df_queries.groupby("USER_NAME").agg(
            QUERIES=("QUERY_COUNT", "sum"),
            CREDITS=("CLOUD_CREDITS", "sum"),
        ).sort_values("QUERIES", ascending=False).reset_index()
        st.bar_chart(by_user.set_index("USER_NAME"), y="QUERIES", use_container_width=True)

        st.subheader("Query Detail")
        st.dataframe(df_queries.sort_values("USAGE_DATE", ascending=False), use_container_width=True)
