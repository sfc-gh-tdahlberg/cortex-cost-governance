import streamlit as st

st.title(":snowflake: Cortex Cost Governance Dashboard")
st.markdown("""
Welcome to the **Cortex Cost Governance** dashboard. Use the sidebar to navigate between pages.

### What this app monitors:
| Page | Description |
|------|------------|
| **Executive Overview** | KPI cards, total AI credit trends, month-over-month comparison |
| **AI Functions** | Deep-dive into AI_COMPLETE, AI_EXTRACT, AI_EMBED costs by function, model, day |
| **Cortex Code** | Track Cortex Code CLI/UI AI_SERVICES consumption |
| **Cortex Agents** | Agent-level credit consumption with token granularity |
| **Cortex Search** | Serving vs embedding costs, idle service detection |
| **User Spend Analysis** | Per-user spending breakdown, top consumers, role attribution |

### Data Sources
All data comes from `SNOWFLAKE.ACCOUNT_USAGE` views with 10-minute caching.
Queries require **ACCOUNTADMIN** or equivalent privileges on the SNOWFLAKE database.
""")
