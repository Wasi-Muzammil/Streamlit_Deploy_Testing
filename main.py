# import streamlit as st

# st.write("Fingerprint Attendance System")
# st.write("Testing")
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    
    required_packages = [
        'psycopg2',
        'uvicorn',
        'streamlit',
        'pillow',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"{package}")
        except ImportError:
            print(f"{package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n Missing packages: {', '.join(missing_packages)}")
        print("\nInstalling missing packages...")
        
        # Install missing packages
        subprocess.check_call([
            sys.executable, "-m", "pip", "install"
        ] + missing_packages)
        
        print("✅ All packages installed!")
    else:
        print("\n✅ All dependencies are installed")


check_dependencies()
import streamlit as st
import psycopg2
import os


# For local testing only
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")



st.title("Neon Database Test")

if not DATABASE_URL:
    st.error("DATABASE_URL not found")
    st.stop()

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_information;")  
    rows = cursor.fetchall()

    st.success("Connected to Neon Database")

    for row in rows:
        st.write(row)

    cursor.close()
    conn.close()

except Exception as e:
    st.error("Database connection failed")
    st.exception(e)
