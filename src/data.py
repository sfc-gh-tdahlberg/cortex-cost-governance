import streamlit as st
import pandas as pd
from datetime import timedelta


def get_conn():
    return st.connection("snowflake")


def run_query(sql: str, ttl: int = 600) -> pd.DataFrame:
    try:
        conn = get_conn()
        return conn.query(sql, ttl=ttl)
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()


def get_metering_daily(days: int = 90) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            TO_DATE(USAGE_DATE) AS USAGE_DATE,
            SERVICE_TYPE,
            SUM(CREDITS_USED) AS CREDITS_USED
        FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY
        WHERE SERVICE_TYPE IN ('AI_SERVICES', 'AI_INFERENCE')
          AND USAGE_DATE >= DATEADD('day', -{days}, CURRENT_DATE())
        GROUP BY 1, 2
        ORDER BY 1 DESC
    """)


def get_ai_functions_usage(days: int = 90) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            DATE_TRUNC('day', START_TIME) AS USAGE_DATE,
            FUNCTION_NAME,
            MODEL_NAME,
            SUM(CREDITS) AS TOTAL_CREDITS,
            SUM(
                COALESCE(f.value:value::NUMBER, 0)
            ) AS TOTAL_TOKENS,
            COUNT(DISTINCT QUERY_ID) AS QUERY_COUNT
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY,
             LATERAL FLATTEN(INPUT => METRICS) f
        WHERE START_TIME >= DATEADD('day', -{days}, CURRENT_TIMESTAMP())
        GROUP BY 1, 2, 3
        ORDER BY 1 DESC, 4 DESC
    """)


def get_ai_functions_by_user(days: int = 90) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            DATE_TRUNC('month', h.START_TIME) AS USAGE_MONTH,
            u.NAME AS USER_NAME,
            u.EMAIL,
            u.DEFAULT_ROLE,
            SUM(h.CREDITS) AS TOTAL_CREDITS,
            SUM(
                COALESCE(f.value:value::NUMBER, 0)
            ) AS TOTAL_TOKENS,
            COUNT(DISTINCT h.QUERY_ID) AS QUERY_COUNT
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY h
        JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON h.USER_ID = u.USER_ID,
             LATERAL FLATTEN(INPUT => h.METRICS) f
        WHERE h.START_TIME >= DATEADD('day', -{days}, CURRENT_TIMESTAMP())
        GROUP BY 1, 2, 3, 4
        ORDER BY 1 DESC, 5 DESC
    """)


def get_cortex_code_usage(days: int = 90) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            TO_DATE(USAGE_DATE) AS USAGE_DATE,
            SERVICE_TYPE,
            SUM(CREDITS_USED) AS CREDITS_USED
        FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY
        WHERE SERVICE_TYPE = 'AI_SERVICES'
          AND USAGE_DATE >= DATEADD('day', -{days}, CURRENT_DATE())
        GROUP BY 1, 2
        ORDER BY 1 DESC
    """)


def get_cortex_code_queries(days: int = 30) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            DATE_TRUNC('day', START_TIME) AS USAGE_DATE,
            USER_NAME,
            WAREHOUSE_NAME,
            COUNT(*) AS QUERY_COUNT,
            SUM(CREDITS_USED_CLOUD_SERVICES) AS CLOUD_CREDITS,
            ROUND(SUM(TOTAL_ELAPSED_TIME) / 1000, 2) AS TOTAL_SECONDS
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE QUERY_TEXT ILIKE '%CORTEX%'
          AND START_TIME >= DATEADD('day', -{days}, CURRENT_TIMESTAMP())
        GROUP BY 1, 2, 3
        ORDER BY 1 DESC, 5 DESC
    """)


def get_cortex_code_cli_usage(days: int = 90) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            DATE_TRUNC('day', c.USAGE_TIME) AS USAGE_DATE,
            u.NAME AS USER_NAME,
            SUM(c.TOKEN_CREDITS) AS TOTAL_CREDITS,
            SUM(c.TOKENS) AS TOTAL_TOKENS,
            COUNT(*) AS REQUEST_COUNT
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY c
        JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON c.USER_ID = u.USER_ID
        WHERE c.USAGE_TIME >= DATEADD('day', -{days}, CURRENT_TIMESTAMP())
        GROUP BY 1, 2
        ORDER BY 1 DESC, 3 DESC
    """)


def get_cortex_agent_usage(days: int = 90) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            DATE_TRUNC('day', START_TIME) AS USAGE_DATE,
            AGENT_NAME,
            USER_NAME,
            SUM(TOKEN_CREDITS) AS TOTAL_CREDITS,
            SUM(TOKENS) AS TOTAL_TOKENS,
            COUNT(*) AS REQUEST_COUNT
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
        WHERE START_TIME >= DATEADD('day', -{days}, CURRENT_TIMESTAMP())
        GROUP BY 1, 2, 3
        ORDER BY 1 DESC, 4 DESC
    """)


def get_cortex_search_daily(days: int = 90) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            TO_DATE(USAGE_DATE) AS USAGE_DATE,
            SERVICE_NAME,
            CONSUMPTION_TYPE,
            SUM(CREDITS) AS TOTAL_CREDITS,
            SUM(TOKENS) AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY
        WHERE USAGE_DATE >= DATEADD('day', -{days}, CURRENT_DATE())
        GROUP BY 1, 2, 3
        ORDER BY 1 DESC, 4 DESC
    """)


def get_cortex_search_serving(days: int = 90) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            DATE_TRUNC('day', START_TIME) AS USAGE_DATE,
            DATABASE_NAME,
            SCHEMA_NAME,
            SERVICE_NAME,
            SUM(CREDITS) AS TOTAL_CREDITS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_SERVING_USAGE_HISTORY
        WHERE START_TIME >= DATEADD('day', -{days}, CURRENT_TIMESTAMP())
        GROUP BY 1, 2, 3, 4
        ORDER BY 1 DESC, 5 DESC
    """)


def get_all_metering(days: int = 90) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            TO_DATE(USAGE_DATE) AS USAGE_DATE,
            SERVICE_TYPE,
            SUM(CREDITS_USED) AS CREDITS_USED
        FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY
        WHERE USAGE_DATE >= DATEADD('day', -{days}, CURRENT_DATE())
        GROUP BY 1, 2
        ORDER BY 1 DESC
    """)
