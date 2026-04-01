import streamlit as st
import pandas as pd
from src.data import get_cortex_agent_usage

st.title(":material/support_agent: Cortex Agents")

st.markdown(
    "Track per-agent credit consumption. Use **Resource Budgets** (released March 2026) "
    "to set monthly spending limits with automated access revocation."
)

days = st.sidebar.slider("Lookback (days)", 7, 180, 90)

with st.spinner("Loading Cortex Agent usage..."):
    df = get_cortex_agent_usage(days)

if df.empty:
    st.warning("No Cortex Agent usage data found. This view requires agents to have been invoked.")
    st.stop()

df["USAGE_DATE"] = pd.to_datetime(df["USAGE_DATE"])
df["TOTAL_CREDITS"] = pd.to_numeric(df["TOTAL_CREDITS"], errors="coerce")
df["TOTAL_TOKENS"] = pd.to_numeric(df["TOTAL_TOKENS"], errors="coerce")
df["REQUEST_COUNT"] = pd.to_numeric(df["REQUEST_COUNT"], errors="coerce")

c1, c2, c3 = st.columns(3)
c1.metric("Total Agent Credits", f"{df['TOTAL_CREDITS'].sum():,.4f}")
c2.metric("Total Tokens", f"{df['TOTAL_TOKENS'].sum():,.0f}")
c3.metric("Total Requests", f"{df['REQUEST_COUNT'].sum():,.0f}")

st.divider()

st.subheader("Daily Agent Credit Trend")
daily = df.groupby("USAGE_DATE")["TOTAL_CREDITS"].sum().reset_index()
st.line_chart(daily.set_index("USAGE_DATE"), y="TOTAL_CREDITS", use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Credits by Agent")
    by_agent = df.groupby("AGENT_NAME")["TOTAL_CREDITS"].sum().sort_values(ascending=False).reset_index()
    st.bar_chart(by_agent.set_index("AGENT_NAME"), y="TOTAL_CREDITS", use_container_width=True)

with col2:
    st.subheader("Credits by User")
    by_user = df.groupby("USER_NAME")["TOTAL_CREDITS"].sum().sort_values(ascending=False).reset_index()
    st.bar_chart(by_user.set_index("USER_NAME"), y="TOTAL_CREDITS", use_container_width=True)

st.subheader("Agent Usage Detail")
st.dataframe(df.sort_values(["USAGE_DATE", "TOTAL_CREDITS"], ascending=[False, False]), use_container_width=True)

with st.expander("Resource Budget Setup Guide"):
    st.markdown("""
**Steps to create a Resource Budget for Cortex Agents:**

```sql
-- 1. Create a cost center tag
CREATE TAG cost_mgmt_db.tags.cost_center
   ALLOWED_VALUES 'cortex-agents'
   COMMENT = 'Cost center tag for agent budgets';

-- 2. Apply tag to your agent
ALTER AGENT my_agent
  SET TAG cost_mgmt_db.tags.cost_center = 'cortex-agents';

-- 3. Create a budget (via Snowsight or SQL)
CREATE SNOWFLAKE.CORE.BUDGET my_budget();
CALL my_budget!SET_SPENDING_LIMIT(1000);

-- 4. Scope budget to tagged agents
CALL my_budget!SET_RESOURCE_TAGS(
  [[(SELECT SYSTEM$REFERENCE('TAG', 'cost_mgmt_db.tags.cost_center',
    'SESSION', 'APPLYBUDGET')), 'cortex-agents']],
  'UNION'
);

-- 5. Add alert at 80% and revoke at 100%
CALL my_budget!ADD_CUSTOM_ACTION(..., 'ACTUAL', 80);
CALL my_budget!ADD_CUSTOM_ACTION(..., 'ACTUAL', 100);
```

See [Snowflake docs](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-resource-budgets) for full details.
""")
