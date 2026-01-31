# import streamlit as st

# st.write("Fingerprint Attendance System")
# st.write("Testing")

import streamlit as st
import psycopg2

# For local testing only
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

DATABASE_URL = st.secrets["DATABASE_URL"]

st.title("Neon Database Test")

if not DATABASE_URL:
    st.error("DATABASE_URL not found")
    st.stop()

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users;")  # change table name if needed
    rows = cursor.fetchall()

    st.success("Connected to Neon Database")

    for row in rows:
        st.write(row)

    cursor.close()
    conn.close()

except Exception as e:
    st.error("Database connection failed")
    st.exception(e)