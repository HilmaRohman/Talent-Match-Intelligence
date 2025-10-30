import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import time

# ======================================================
# Membuat koneksi engine ke Supabase
# ======================================================
def get_engine(max_retries=3, wait=3):
    """Create secure database engine connection using SQLAlchemy (with retry)"""
    db_conf = st.secrets["database"]

    engine_url = (
        f"postgresql+psycopg://{db_conf['DB_USER']}:{db_conf['DB_PASSWORD']}"
        f"@{db_conf['DB_HOST']}:{db_conf['DB_PORT']}/{db_conf['DB_NAME']}"
        f"?sslmode={db_conf.get('DB_SSLMODE', 'require')}"
    )

    for attempt in range(max_retries):
        try:
            engine = create_engine(
                engine_url,
                connect_args={"connect_timeout": db_conf.get("DB_CONNECT_TIMEOUT", 30)},
                pool_pre_ping=True,  # penting untuk Streamlit Cloud
            )
            # test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as e:
            st.warning(f"⚠️ Attempt {attempt+1} failed: {e}")
            time.sleep(wait)
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return None

    st.error("❌ All connection attempts failed.")
    return None


# ======================================================
# Ambil daftar karyawan dari database
# ======================================================
def get_available_employees():
    """Get list of employees from Supabase database"""
    query = text("""
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
        ORDER BY e.fullname;
    """)

    try:
        engine = get_engine()
        if not engine:
            return pd.DataFrame()

        with engine.connect() as conn:
            df = pd.read_sql(query, conn)

        if df.empty:
            st.warning("⚠️ No employees found in database.")
        return df

    except Exception as e:
        st.error(f"❌ Database query failed: {str(e)}")
        return pd.DataFrame()


# ======================================================
# Eksekusi query SQL umum
# ======================================================
def execute_sql_query(query, params=None):
    """Execute SQL query (with optional params) and return DataFrame"""
    try:
        engine = get_engine()
        if not engine:
            return pd.DataFrame()

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)
        return df

    except Exception as e:
        st.error(f"❌ Query execution failed: {str(e)}")
        return pd.DataFrame()
