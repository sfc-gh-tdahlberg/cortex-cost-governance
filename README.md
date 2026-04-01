# Cortex Cost Governance Dashboard

A multi-page Streamlit in Snowflake (SiS) application for monitoring, analyzing, and governing Snowflake Cortex AI spending across your account.

## Overview

As organizations adopt Snowflake Cortex AI services — AI Functions, Cortex Code, Cortex Agents, and Cortex Search — tracking and controlling costs becomes critical. This dashboard provides a centralized FinOps view for account administrators to:

- Monitor total AI credit consumption with month-over-month trends
- Drill down into per-function, per-model, and per-agent costs
- Identify top-spending users and roles
- Detect idle Cortex Search services accumulating charges
- Access built-in governance guides (Resource Budgets, per-user limits, idle service suspension)

## Pages

### Home
Welcome page with a summary of all monitored areas and data source information.

### Executive Overview
High-level KPI cards and trend analysis:
- **Total AI Credits** consumed in the selected period
- **MTD Credits** for the current month
- **Prior Month Credits** for comparison
- **Month-over-Month Change** percentage
- Daily AI credit consumption area chart
- Credits breakdown by service type (AI_SERVICES, AI_INFERENCE)
- Top 10 AI functions ranked by credit usage

### AI Functions
Deep-dive into Cortex AI function usage (AI_COMPLETE, AI_EXTRACT, AI_EMBED, AI_SUMMARIZE, AI_TRANSLATE, etc.):
- KPI cards: total credits, tokens, and query count
- Daily credit trend line chart
- Credits by function name (bar chart)
- Credits by model name (bar chart)
- Function x Model cross-tabulation with credits, tokens, and query counts

### Cortex Code
Tracks AI_SERVICES credits attributable to Cortex Code (CLI and UI):
- **Note:** As of early 2026, Snowflake does not charge separately for Cortex Code. LLM invocations appear as AI_SERVICES credits.
- Tab 1 — AI Services Credits: daily trend and totals
- Tab 2 — Cortex-Related Queries: queries from QUERY_HISTORY containing "CORTEX", broken down by user

### Cortex Agents
Per-agent credit and token consumption:
- KPI cards: total agent credits, tokens, and request count
- Daily agent credit trend
- Credits by agent name
- Credits by user
- Expandable **Resource Budget Setup Guide** with SQL examples for tag-based budgets, spending limits, and automated access revocation

### Cortex Search
Cortex Search has a continuous serving cost even when idle. This page helps identify and manage that:
- Tab 1 — Daily Usage: credits by consumption type (serving vs. embedding), daily trend by service
- Tab 2 — Serving Detail: per-service serving credits, daily serving trend
- Expandable guide for **suspending idle search services** with SQL examples

### User Spend Analysis
Per-user AI spending attribution:
- KPI cards: unique users, total credits, total queries
- Top 15 users by credits (bar chart)
- Credits by default role
- Monthly trend for top 5 spenders
- User spend detail table (user, email, role, credits, tokens, queries)
- Expandable **Per-User Spending Limits** guide with SQL for revoking and managing SNOWFLAKE.CORTEX_USER access

## Data Sources

All data is sourced from `SNOWFLAKE.ACCOUNT_USAGE` views:

| View | Used By |
|------|---------|
| `METERING_DAILY_HISTORY` | Executive Overview, Cortex Code |
| `CORTEX_AI_FUNCTIONS_USAGE_HISTORY` | Executive Overview, AI Functions, User Spend |
| `CORTEX_AGENT_USAGE_HISTORY` | Cortex Agents |
| `CORTEX_SEARCH_DAILY_USAGE_HISTORY` | Cortex Search |
| `CORTEX_SEARCH_SERVING_USAGE_HISTORY` | Cortex Search |
| `QUERY_HISTORY` | Cortex Code |
| `USERS` | User Spend Analysis |

Query results are cached for 10 minutes (`ttl=600`) to balance freshness with performance.

## Architecture

```
streamlit_app.py              # Entry point — st.navigation multi-page router
app_pages/
    home.py                   # Welcome / landing page
    executive_overview.py     # KPI cards + trend charts
    ai_functions.py           # AI function deep-dive
    cortex_code.py            # Cortex Code cost tracking
    cortex_agents.py          # Agent usage + budget guide
    cortex_search.py          # Search serving/embedding costs
    user_spend.py             # Per-user spend analysis
src/
    __init__.py
    data.py                   # Centralized data access layer (all SQL queries)
snowflake.yml                 # SiS deployment manifest
pyproject.toml                # Python dependencies
```

The app uses `st.connection("snowflake")` for native SiS authentication — no credentials or connection strings needed. All SQL queries are centralized in `src/data.py` for maintainability.

## Prerequisites

- **Snowflake Account** with Cortex AI services enabled
- **ACCOUNTADMIN** role (or a role with IMPORTED PRIVILEGES on the SNOWFLAKE database) to access ACCOUNT_USAGE views
- **Snowflake CLI** v3.14.0+ (or use `uvx --from snowflake-cli` for the latest version)
- A **compute pool** for container runtime (e.g., `SYSTEM_COMPUTE_POOL_CPU`)
- **PYPI_ACCESS_INTEGRATION** external access integration

## Deployment

### 1. Create the database and schema

```sql
USE ROLE ACCOUNTADMIN;

CREATE DATABASE IF NOT EXISTS CORTEX_COST_GOVERNANCE;
CREATE SCHEMA IF NOT EXISTS CORTEX_COST_GOVERNANCE.STREAMLIT;
```

### 2. Grant permissions to the deploying role

```sql
GRANT ALL ON DATABASE CORTEX_COST_GOVERNANCE TO ROLE <YOUR_ROLE>;
GRANT ALL ON SCHEMA CORTEX_COST_GOVERNANCE.STREAMLIT TO ROLE <YOUR_ROLE>;
GRANT CREATE STREAMLIT ON SCHEMA CORTEX_COST_GOVERNANCE.STREAMLIT TO ROLE <YOUR_ROLE>;
GRANT USAGE ON COMPUTE POOL <YOUR_COMPUTE_POOL> TO ROLE <YOUR_ROLE>;
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE <YOUR_ROLE>;
GRANT USAGE ON INTEGRATION PYPI_ACCESS_INTEGRATION TO ROLE <YOUR_ROLE>;
```

### 3. Update snowflake.yml (if needed)

Edit `snowflake.yml` to match your environment:
- `query_warehouse`: your warehouse name
- `compute_pool`: your compute pool name

### 4. Deploy

```bash
# Using uvx (recommended if local CLI is < 3.14.0)
uvx --from snowflake-cli snow streamlit deploy --replace --connection <YOUR_CONNECTION>

# Or with a recent snow CLI
snow streamlit deploy --replace --connection <YOUR_CONNECTION>
```

### 5. Access the app

After deployment, the app is available at:
```
https://app.snowflake.com/<ORG>/<ACCOUNT>/#/streamlit-apps/CORTEX_COST_GOVERNANCE.STREAMLIT.CORTEX_COST_GOVERNANCE
```

Or find it in Snowsight under **Projects > Streamlit**.

## Cost Governance Best Practices

This app embeds actionable governance guides. Key recommendations:

1. **Resource Budgets for Agents** — Use tag-based budgets with multi-layer thresholds (50% projected, 80% actual, 100% actual) to control agent spending
2. **Per-User Spending Limits** — Revoke `SNOWFLAKE.CORTEX_USER` from `PUBLIC` and create managed roles with monitoring tasks
3. **Suspend Idle Search Services** — Cortex Search accrues serving costs 24/7 regardless of query volume; suspend non-production services
4. **Model Selection** — Choosing the right model can mean a 10x cost difference; use `AI_COUNT_TOKENS` for pre-execution estimation
5. **Query Tags** — Use query tags for team/project-level cost attribution

## Customization

- **Lookback period**: Each page has a sidebar slider (7-180 days)
- **Add new views**: Add a new file in `app_pages/`, create query functions in `src/data.py`, and register the page in `streamlit_app.py`
- **Change warehouse**: Update `query_warehouse` in `snowflake.yml` and redeploy

## License

Internal use. Modify and distribute as needed within your organization.
