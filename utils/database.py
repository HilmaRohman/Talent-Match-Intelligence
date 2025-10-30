import streamlit as st
import pandas as pd
import psycopg2
import ssl

def get_db_connection():
    """Create secure database connection to Supabase"""
    try:
        conn = psycopg2.connect(
            host=st.secrets["database"]["DB_HOST"],
            database=st.secrets["database"]["DB_NAME"],
            user=st.secrets["database"]["DB_USER"],
            password=st.secrets["database"]["DB_PASSWORD"],
            port=st.secrets["database"]["DB_PORT"],
            sslmode=st.secrets["database"].get("DB_SSLMODE", "require"),
            connect_timeout=st.secrets["database"].get("DB_CONNECT_TIMEOUT", 10)
        )
        return conn

    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        return None


def get_available_employees():
    """Get list of employees from Supabase database (join dimension tables)"""
    query = """
    SELECT 
        e.employee_id, 
        e.fullname, 
        p.name AS position,
        g.name AS grade,
        d.name AS directorate,
        dep.name AS department,
        div.name AS division,
        c.name AS company,
        e.years_of_service_months
    FROM employees e
    LEFT JOIN dim_positions p ON e.position_id = p.position_id
    LEFT JOIN dim_grades g ON e.grade_id = g.grade_id
    LEFT JOIN dim_directorates d ON e.directorate_id = d.directorate_id
    LEFT JOIN dim_departments dep ON e.department_id = dep.department_id
    LEFT JOIN dim_divisions div ON e.division_id = div.division_id
    LEFT JOIN dim_companies c ON e.company_id = c.company_id
    WHERE e.employee_id IS NOT NULL 
    ORDER BY e.fullname
    LIMIT 100;
    """

    try:
        conn = get_db_connection()
        if conn:
            df = pd.read_sql(query, conn)
            conn.close()

            if not df.empty:
                return df
            else:
                st.warning("⚠️ No employees found in database.")
                return pd.DataFrame()
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"❌ Database query failed: {str(e)}")
        return pd.DataFrame()


def execute_sql_query(query, params=None):
    """Execute SQL query (with optional params) and return DataFrame"""
    try:
        conn = get_db_connection()
        if not conn:
            return pd.DataFrame()

        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df

    except Exception as e:
        st.error(f"❌ Query execution failed: {str(e)}")
        return pd.DataFrame()
