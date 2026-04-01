import streamlit as st

st.set_page_config(
    page_title="Cortex Cost Governance",
    page_icon=":snowflake:",
    layout="wide",
    initial_sidebar_state="expanded",
)

page = st.navigation([
    st.Page("app_pages/home.py", title="Home", icon=":material/home:"),
    st.Page("app_pages/executive_overview.py", title="Executive Overview", icon=":material/bar_chart:"),
    st.Page("app_pages/ai_functions.py", title="AI Functions", icon=":material/smart_toy:"),
    st.Page("app_pages/cortex_code.py", title="Cortex Code", icon=":material/code:"),
    st.Page("app_pages/cortex_agents.py", title="Cortex Agents", icon=":material/support_agent:"),
    st.Page("app_pages/cortex_search.py", title="Cortex Search", icon=":material/search:"),
    st.Page("app_pages/user_spend.py", title="User Spend Analysis", icon=":material/person:"),
])

page.run()
