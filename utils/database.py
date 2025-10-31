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
        # st.error(f"❌ Database connection failed: {str(e)}")
        return None


def get_available_employees():
    """Get list of employees from Supabase database (join dimension tables)
       Fallback otomatis ke data dummy jika database gagal diakses"""
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
    ORDER BY e.fullname;
    """

    try:
        conn = get_db_connection()
        if conn:
            df = pd.read_sql(query, conn)
            conn.close()

            if not df.empty:
                return df
            else:
                st.warning("⚠️ No employees found in database. Using dummy data instead.")
                return get_dummy_employees()
        else:
            st.warning("⚠️ Using dummy data due to issues with the database connection from Supabase.")
            return get_dummy_employees()

    except Exception as e:
        st.error(f"❌ Database query failed: {str(e)} — Using dummy data instead.")
        return get_dummy_employees()


def execute_sql_query(query, params=None):
    """Execute SQL query (with optional params) and return DataFrame"""
    try:
        conn = get_db_connection()
        if not conn:
            st.warning("⚠️ Using dummy data due to issues with the database connection from Supabase.")
            return pd.DataFrame()

        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df

    except Exception as e:
        st.error(f"❌ Query execution failed: {str(e)}")
        return pd.DataFrame()


def get_dummy_employees():
    """Generate dummy employee data for fallback mode"""
    data = {
        'employee_id': ['EMP100000', 'EMP100001', 'EMP100002', 'EMP100003', 'EMP100004', 'EMP100005', 'EMP100006', 'EMP100007', 'EMP100008', 'EMP100009'],
        'fullname': ['Rendra Pratama', 'Wulan Setiawan', 'Julia Jatmiko Situmorang', 'Oka Halim', 'Dwi Pratama', 'Bayu Zulfikar', 'Indra Santoso', 'Rani Mahendra', 'Gita Permadi', 'Julia Anggara'],
        'position': ['Brand Executive', 'HRBP', 'Sales Supervisor', 'HRBP', 'Supply Planner', 'Sales Supervisor', 'Finance Officer', 'HRBP', 'Finance Officer', 'Sales Supervisor'],
        'grade': ['V', 'III', 'V', 'IV', 'III', 'V', 'III', 'IV', 'IV', 'V'],
        'directorate': ['Technology', 'Technology', 'Technology', 'Commercial', 'Technology', 'Commercial', 'HR & Corp Affairs', 'HR & Corp Affairs', 'Commercial', 'Commercial'],
        'department': ['R&D', 'Operations', 'Finance', 'HR', 'Operations', 'HR', 'HR', 'IT', 'Finance', 'R&D'],
        'division': ['Product Dev', 'Talent Management', 'Digital Marketing', 'Digital Marketing', 'Product Dev', 'Product Dev', 'Digital Marketing', 'Operations', 'Talent Management', 'Sales'],
        'company': ['PT Aurora Beauty Indonesia', 'PT Mandala Distribution Center', 'PT Aurora Beauty Indonesia', 'PT Aurora Beauty Indonesia', 'PT Lumo Cosmetics Asia', 'PT Aurora Beauty Indonesia', 'PT Aurora Beauty Indonesia', 'PT Mandala Distribution Center', 'PT VASKA Wellness', 'PT Aurora Beauty Indonesia'],
        'years_of_service_months': [64, 16, 58, 15, 34, 66, 82, 56, 40, 77]
    }
    df = pd.DataFrame(data)
    # st.info("🧩 Using dummy employee dataset (database fallback mode).")
    return df
