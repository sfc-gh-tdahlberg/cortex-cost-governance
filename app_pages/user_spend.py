import streamlit as st
import pandas as pd
from src.data import get_ai_functions_by_user

st.title(":material/person: User Spend Analysis")

days = st.sidebar.slider("Lookback (days)", 7, 180, 90)

with st.spinner("Loading per-user spending data..."):
    df = get_ai_functions_by_user(days)

if df.empty:
    st.warning("No per-user AI spending data found.")
    st.stop()

df["USAGE_MONTH"] = pd.to_datetime(df["USAGE_MONTH"])
df["TOTAL_CREDITS"] = pd.to_numeric(df["TOTAL_CREDITS"], errors="coerce")
df["TOTAL_TOKENS"] = pd.to_numeric(df["TOTAL_TOKENS"], errors="coerce")
df["QUERY_COUNT"] = pd.to_numeric(df["QUERY_COUNT"], errors="coerce")

c1, c2, c3 = st.columns(3)
c1.metric("Unique Users", f"{df['USER_NAME'].nunique()}")
c2.metric("Total Credits", f"{df['TOTAL_CREDITS'].sum():,.4f}")
c3.metric("Total Queries", f"{df['QUERY_COUNT'].sum():,.0f}")

st.divider()

st.subheader("Top 15 Users by Credits")
top_users = df.groupby("USER_NAME")["TOTAL_CREDITS"].sum().nlargest(15).reset_index()
st.bar_chart(top_users.set_index("USER_NAME"), y="TOTAL_CREDITS", use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Credits by Role")
    by_role = df.groupby("DEFAULT_ROLE")["TOTAL_CREDITS"].sum().sort_values(ascending=False).reset_index()
    st.bar_chart(by_role.set_index("DEFAULT_ROLE"), y="TOTAL_CREDITS", use_container_width=True)

with col2:
    st.subheader("Monthly Trend by User")
    monthly_users = df.groupby(["USAGE_MONTH", "USER_NAME"])["TOTAL_CREDITS"].sum().reset_index()
    top5 = df.groupby("USER_NAME")["TOTAL_CREDITS"].sum().nlargest(5).index.tolist()
    filtered = monthly_users[monthly_users["USER_NAME"].isin(top5)]
    if not filtered.empty:
        pivot = filtered.pivot(index="USAGE_MONTH", columns="USER_NAME", values="TOTAL_CREDITS").fillna(0)
        st.line_chart(pivot, use_container_width=True)

st.subheader("User Spend Detail")
user_summary = df.groupby(["USER_NAME", "EMAIL", "DEFAULT_ROLE"]).agg(
    TOTAL_CREDITS=("TOTAL_CREDITS", "sum"),
    TOTAL_TOKENS=("TOTAL_TOKENS", "sum"),
    TOTAL_QUERIES=("QUERY_COUNT", "sum"),
).reset_index().sort_values("TOTAL_CREDITS", ascending=False)
st.dataframe(user_summary, use_container_width=True)

with st.expander("Per-User Spending Limits"):
    st.markdown("""
**To enforce per-user AI spending limits:**

1. Revoke default Cortex access from PUBLIC:
```sql
REVOKE DATABASE ROLE SNOWFLAKE.CORTEX_USER FROM ROLE PUBLIC;
```

2. Create a managed role:
```sql
CREATE ROLE AI_FUNCTIONS_USER_ROLE;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE AI_FUNCTIONS_USER_ROLE;
```

3. Create an access control table with per-user limits
4. Set up hourly monitoring tasks to revoke access when limits are exceeded
5. Monthly task to restore access at the start of each billing cycle

See [Snowflake docs](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-func-cost-management) for full implementation.
""")
