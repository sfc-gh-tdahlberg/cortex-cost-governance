import streamlit as st
import pandas as pd
from src.data import get_cortex_code_usage, get_cortex_code_queries, get_cortex_code_cli_usage

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
    df_cli = get_cortex_code_cli_usage(days)

tab1, tab2, tab3 = st.tabs(["AI Services Credits", "Cortex-Related Queries", "Cortex Code CLI Usage"])

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

with tab3:
    if df_cli.empty:
        st.warning("No Cortex Code CLI usage data found.")
    else:
        df_cli["USAGE_DATE"] = pd.to_datetime(df_cli["USAGE_DATE"])
        df_cli["TOTAL_CREDITS"] = pd.to_numeric(df_cli["TOTAL_CREDITS"], errors="coerce")
        df_cli["TOTAL_TOKENS"] = pd.to_numeric(df_cli["TOTAL_TOKENS"], errors="coerce")
        df_cli["REQUEST_COUNT"] = pd.to_numeric(df_cli["REQUEST_COUNT"], errors="coerce")

        c1, c2, c3 = st.columns(3)
        c1.metric("CLI Token Credits", f"{df_cli['TOTAL_CREDITS'].sum():,.4f}")
        c2.metric("CLI Tokens", f"{df_cli['TOTAL_TOKENS'].sum():,.0f}")
        c3.metric("CLI Requests", f"{df_cli['REQUEST_COUNT'].sum():,.0f}")

        st.subheader("Daily CLI Credit Trend")
        daily_cli = df_cli.groupby("USAGE_DATE")["TOTAL_CREDITS"].sum().reset_index()
        st.area_chart(daily_cli.set_index("USAGE_DATE"), y="TOTAL_CREDITS", use_container_width=True)

        st.subheader("CLI Credits by User")
        by_user_cli = df_cli.groupby("USER_NAME")["TOTAL_CREDITS"].sum().sort_values(ascending=False).reset_index()
        st.bar_chart(by_user_cli.set_index("USER_NAME"), y="TOTAL_CREDITS", use_container_width=True)

        st.subheader("CLI Usage Detail")
        st.dataframe(df_cli.sort_values("USAGE_DATE", ascending=False), use_container_width=True)
