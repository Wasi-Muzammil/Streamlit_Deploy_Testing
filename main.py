# import streamlit as st

# st.write("Fingerprint Attendance System")
# st.write("Testing")


import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import API client
from utils.api_client import api_client

# Page configuration
st.set_page_config(
    page_title="Fingerprint Attendance System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS (same as before)
def load_css():
    st.markdown("""
    <style>
    :root {
        --primary-color: #2E3192;
        --secondary-color: #00A8E8;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main-header {
        background: linear-gradient(135deg, #2E3192 0%, #00A8E8 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        text-align: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'
if 'selected_user_id' not in st.session_state:
    st.session_state.selected_user_id = None
if 'api_token' not in st.session_state:
    st.session_state.api_token = None

# ==================== LOGIN PAGE ====================
def login_page():
    """Display login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="main-header">
            <h1>🔐 Fingerprint Attendance System</h1>
            <p style="color: white; text-align: center; margin-top: 1rem;">
                Secure Login Portal
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check API health
        if not api_client.health_check():
            st.error("⚠️ Cannot connect to API server. Make sure the backend is running on http://localhost:8000")
            st.info("Start backend with: `cd backend && uvicorn main:app --reload`")
            return
        
        st.markdown("### Admin Login")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("🔓 Login", use_container_width=True):
                if username and password:
                    with st.spinner("Authenticating..."):
                        success, message = api_client.login(username, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.api_token = api_client.token
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        st.markdown("---")
        st.info("**Default credentials:** username: `admin` | password: `admin123`")

# ==================== NAVIGATION ====================
def navigation():
    """Display navigation bar"""
    st.sidebar.markdown("""
    <div class="main-header">
        <h1 style="font-size: 1.5rem;">🔐 FP Attendance</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    pages = {
        "🏠 Home": "Home",
        "ℹ️ About": "About",
        "📞 Contact": "Contact"
    }
    
    for label, page in pages.items():
        if st.sidebar.button(label, use_container_width=True):
            st.session_state.current_page = page
            st.session_state.selected_user_id = None
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # User info
    st.sidebar.markdown(f"**👤 User:** {st.session_state.get('username', 'Admin')}")
    st.sidebar.markdown(f"**📅 Date:** {datetime.now().strftime('%Y-%m-%d')}")
    st.sidebar.markdown(f"**⏰ Time:** {datetime.now().strftime('%H:%M:%S')}")
    
    st.sidebar.markdown("---")
    
    # ESP32 Status
    with st.sidebar.expander("🔌 ESP32 Device Status"):
        success, info = api_client.get_esp32_status()
        if success and info.get('connected'):
            device_info = info.get('device_info', {})
            st.write(f"**Device:** {device_info.get('device_name', 'Unknown')}")
            st.write(f"**Version:** {device_info.get('firmware_version', 'N/A')}")
            enrolled = device_info.get('enrolled_count', 0)
            total = device_info.get('total_fingerprints', 127)
            st.write(f"**Enrolled:** {enrolled}/{total}")
            st.success("✅ Device Online")
        else:
            st.error("❌ Device Offline")
    
    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        api_client.logout()
        st.session_state.authenticated = False
        st.session_state.api_token = None
        st.rerun()

# ==================== HOME PAGE ====================
def home_page():
    """Main dashboard with all operations"""
    st.markdown("""
    <div class="main-header">
        <h1>🏠 Admin Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Get dashboard stats from API
    success, stats = api_client.get_dashboard_stats()
    
    if success:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">👥 Total Users</div>
                <div class="metric-value">{stats.get('total_users', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <div class="metric-label">✅ Today's Records</div>
                <div class="metric-value">{stats.get('today_records', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="metric-label">📥 Checked In</div>
                <div class="metric-value">{stats.get('checked_in', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="metric-label">📤 Checked Out</div>
                <div class="metric-value">{stats.get('checked_out', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main operations tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Add User", 
        "👤 Manage Users", 
        "📊 Attendance Reports",
        "🔄 Live Sync"
    ])
    
    with tab1:
        add_user_section()
    
    with tab2:
        manage_users_section()
    
    with tab3:
        attendance_reports_section()
    
    with tab4:
        live_sync_section()

# ==================== SECTION FUNCTIONS ====================

def add_user_section():
    """Add new user section"""
    st.markdown('<div class="section-header">➕ Add New User</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("add_user_form"):
            name = st.text_input("👤 Full Name *", placeholder="Enter full name")
            department = st.text_input("🏢 Department *", placeholder="e.g., Engineering, HR, Sales")
            fingerprint_id = st.number_input("🔢 Fingerprint ID", min_value=1, max_value=127, value=1)
            uploaded_file = st.file_uploader("📸 Profile Picture (Optional)", type=['png', 'jpg', 'jpeg'])
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_b:
                submit = st.form_submit_button("✅ Add User", use_container_width=True)
            
            if submit:
                if name and department:
                    with st.spinner("Adding user..."):
                        # Prepare image file
                        image_file = None
                        if uploaded_file:
                            image_file = ("image", uploaded_file.getvalue(), uploaded_file.type)
                        
                        success, result = api_client.create_user(
                            name, department, fingerprint_id, image_file
                        )
                        
                        if success:
                            st.success(f"✅ User '{name}' added successfully!")
                            st.balloons()
                        else:
                            st.error(f"❌ Error: {result}")
                else:
                    st.warning("⚠️ Please fill in all required fields")
    
    with col2:
        st.info("""
        **📋 Instructions:**
        
        1. Enter user's full name
        2. Specify department
        3. Assign fingerprint ID (1-127)
        4. Optionally upload photo
        5. Click 'Add User'
        6. Follow ESP32 prompts
        
        **💡 Tips:**
        - Use unique fingerprint IDs
        - Photos help identification
        """)

def manage_users_section():
    """Manage existing users"""
    st.markdown('<div class="section-header">👥 Manage Users</div>', unsafe_allow_html=True)
    
    # Get all users from API
    success, users = api_client.get_all_users()
    
    if not success or not users:
        st.info("No users found. Add a user to get started!")
        return
    
    # User selection
    user_options = {f"{user['name']} ({user['department']}) - ID: {user['id']}": user['id'] 
                   for user in users}
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox("🔍 Select User", options=list(user_options.keys()))
        st.session_state.selected_user_id = user_options[selected]
    
    with col2:
        if st.button("🗑️ Delete User", use_container_width=True, type="secondary"):
            if st.session_state.get('confirm_delete'):
                with st.spinner("Deleting user..."):
                    success, message = api_client.delete_user(st.session_state.selected_user_id)
                    if success:
                        st.success("✅ User deleted successfully!")
                        st.session_state.selected_user_id = None
                        st.session_state.confirm_delete = False
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            else:
                st.session_state.confirm_delete = True
                st.warning("⚠️ Click again to confirm deletion")
    
    if st.session_state.selected_user_id:
        # Get user details
        success, user = api_client.get_user(st.session_state.selected_user_id)
        
        if success:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 2])
            
            with col1:
                if user.get('image_path'):
                    try:
                        image_url = api_client.get_user_image_url(user['id'])
                        st.image(image_url, caption="Profile Picture", width=150)
                    except:
                        st.image("https://via.placeholder.com/150?text=No+Photo", width=150)
                else:
                    st.image("https://via.placeholder.com/150?text=No+Photo", width=150)
            
            with col2:
                st.markdown(f"""
                **Name:** {user['name']}  
                **Department:** {user['department']}  
                **User ID:** {user['id']}  
                **Fingerprint ID:** {user.get('fingerprint_id', 'Not Enrolled')}
                """)
            
            with col3:
                if st.button("📊 View Attendance History", use_container_width=True):
                    st.session_state.show_user_history = True
                
                if st.button("📄 Export User Report", use_container_width=True):
                    with st.spinner("Generating PDF..."):
                        success, pdf_data = api_client.download_user_report(user['id'])
                        if success:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=pdf_data,
                                file_name=f"attendance_{user['name'].replace(' ', '_')}.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.error(f"❌ {pdf_data}")
                
                if st.button("🔄 Re-enroll Fingerprint", use_container_width=True):
                    fp_id = user.get('fingerprint_id', 1)
                    with st.spinner("Re-enrolling..."):
                        success, message = api_client.enroll_fingerprint(user['id'], fp_id)
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
            
            # Edit form
            with st.expander("✏️ Edit User Information"):
                with st.form("edit_user_form"):
                    new_name = st.text_input("Name", value=user['name'])
                    new_dept = st.text_input("Department", value=user['department'])
                    new_fp_id = st.number_input("Fingerprint ID", 
                                               value=user.get('fingerprint_id', 1), 
                                               min_value=1, max_value=127)
                    
                    if st.form_submit_button("💾 Save Changes"):
                        with st.spinner("Updating..."):
                            success, message = api_client.update_user(
                                user['id'], new_name, new_dept, new_fp_id
                            )
                            if success:
                                st.success("✅ User updated!")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
            
            # Show attendance history
            if st.session_state.get('show_user_history'):
                st.markdown("---")
                st.markdown("### 📋 Attendance History")
                success, data = api_client.get_user_attendance(user['id'])
                
                if success and data['records']:
                    df = pd.DataFrame(data['records'])
                    df['date'] = pd.to_datetime(df['timestamp']).dt.date
                    df['time'] = pd.to_datetime(df['timestamp']).dt.time
                    st.dataframe(df[['date', 'time', 'status']], use_container_width=True)
                else:
                    st.info("No attendance records found.")

def attendance_reports_section():
    """Attendance reports section"""
    st.markdown('<div class="section-header">📊 Attendance Reports</div>', unsafe_allow_html=True)
    
    report_type = st.radio(
        "Select Report Type:",
        ["📅 Single Day Report", "📆 Date Range Report", "📊 Today's Summary"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if report_type == "📅 Single Day Report":
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_date = st.date_input("Select Date", value=date.today())
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            generate = st.button("📄 Generate PDF", use_container_width=True)
        
        if generate:
            date_str = selected_date.strftime("%Y-%m-%d")
            
            with st.spinner("Generating PDF..."):
                success, pdf_data = api_client.download_daily_report(date_str)
                
                if success:
                    st.success(f"✅ Report generated for {date_str}")
                    st.download_button(
                        label="⬇️ Download Report",
                        data=pdf_data,
                        file_name=f"attendance_{date_str}.pdf",
                        mime="application/pdf"
                    )
                    
                    # Preview
                    st.markdown("### 👁️ Preview")
                    success, data = api_client.get_attendance_by_date(date_str)
                    if success and data['records']:
                        df = pd.DataFrame(data['records'])
                        st.dataframe(df, use_container_width=True)
                else:
                    st.error(f"❌ {pdf_data}")
    
    elif report_type == "📆 Date Range Report":
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=7))
        
        with col2:
            end_date = st.date_input("End Date", value=date.today())
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            generate = st.button("📄 Generate PDF", use_container_width=True)
        
        if generate:
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            with st.spinner("Generating PDF..."):
                success, pdf_data = api_client.download_range_report(start_str, end_str)
                
                if success:
                    st.success(f"✅ Report generated")
                    st.download_button(
                        label="⬇️ Download Report",
                        data=pdf_data,
                        file_name=f"attendance_{start_str}_to_{end_str}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error(f"❌ {pdf_data}")
    
    else:  # Today's Summary
        today_str = date.today().strftime("%Y-%m-%d")
        success, data = api_client.get_attendance_by_date(today_str)
        
        if success and data['records']:
            st.markdown("### 📊 Today's Attendance")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", data['count'])
            with col2:
                check_ins = len([r for r in data['records'] if r['status'] == 'IN'])
                st.metric("Check-Ins", check_ins)
            with col3:
                check_outs = len([r for r in data['records'] if r['status'] == 'OUT'])
                st.metric("Check-Outs", check_outs)
            
            df = pd.DataFrame(data['records'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ No attendance records for today yet.")

def live_sync_section():
    """Live sync with ESP32"""
    st.markdown('<div class="section-header">🔄 Live Sync with ESP32</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Fetch Latest Attendance", use_container_width=True):
            with st.spinner("Fetching..."):
                success, data = api_client.get_live_attendance()
                if success and data.get('success'):
                    st.success("✅ Data fetched!")
                    st.json(data.get('data'))
                else:
                    st.info("ℹ️ No new data")
    
    with col2:
        if st.button("📥 Bulk Sync All Records", use_container_width=True):
            with st.spinner("Syncing..."):
                success, data = api_client.sync_esp32_attendance()
                if success and data.get('success'):
                    st.success(f"✅ {data.get('message')}")
                    st.balloons()
                else:
                    st.info("ℹ️ No records to sync")
    
    # Manual entry for testing
    with st.expander("➕ Manual Attendance Entry (Testing)"):
        with st.form("manual_entry"):
            success, users = api_client.get_all_users()
            if success and users:
                user_options = {f"{u['name']} - {u['department']}": u['id'] for u in users}
                selected_user = st.selectbox("Select User", options=list(user_options.keys()))
                status = st.radio("Status", ["IN", "OUT"], horizontal=True)
                
                if st.form_submit_button("Add Record"):
                    user_id = user_options[selected_user]
                    success, message = api_client.create_attendance(user_id, status)
                    if success:
                        st.success("✅ Attendance recorded!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

# About and Contact pages remain the same...

def about_page():
    st.markdown("""
    <div class="main-header">
        <h1>ℹ️ About the System</h1>
    </div>
    """, unsafe_allow_html=True)
    st.info("System powered by FastAPI backend + Streamlit frontend")

def contact_page():
    st.markdown("""
    <div class="main-header">
        <h1>📞 Contact & Support</h1>
    </div>
    """, unsafe_allow_html=True)
    st.info("For support, contact your system administrator")

# ==================== MAIN APPLICATION ====================
def main():
    # Restore token if exists
    if st.session_state.get('api_token'):
        api_client.token = st.session_state.api_token
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Verify token is still valid
    if not api_client.verify_token():
        st.session_state.authenticated = False
        st.error("Session expired. Please login again.")
        st.rerun()
        return
    
    # Display navigation
    navigation()
    
    # Route to appropriate page
    current_page = st.session_state.get('current_page', 'Home')
    
    if current_page == 'Home':
        home_page()
    elif current_page == 'About':
        about_page()
    elif current_page == 'Contact':
        contact_page()

if __name__ == "__main__":
    main()