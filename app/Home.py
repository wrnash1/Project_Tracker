"""
Verizon Tracker - Main Entry Point
Login page and application initialization
"""

import streamlit as st
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vtrack import auth
from src.vtrack.database import initialize_all_databases
from app.styles import apply_verizon_theme

# Page configuration
st.set_page_config(
    page_title="Verizon Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom styling
apply_verizon_theme()

# Initialize authentication state
auth.initialize_session_state()


def show_login_page():
    """Display the login form"""

    # Center container for login
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Verizon branding
        st.markdown("""
            <div class="login-container">
                <div class="login-logo">
                    <h1 style="color: #EE0000; margin: 0; font-size: 3rem;">Verizon</h1>
                    <div style="width: 80px; height: 4px; background: linear-gradient(90deg, #EE0000 0%, #CD040B 100%); margin: 0.5rem auto;"></div>
                </div>
                <div class="login-title">Project Tracker</div>
                <div class="login-subtitle">Sign in to manage your projects</div>
            </div>
        """, unsafe_allow_html=True)

        # Login form
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="login_username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )

            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submit = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("⚠️ Please enter both username and password")
                else:
                    with st.spinner("Authenticating..."):
                        if auth.login(username, password):
                            st.success(f"✅ Welcome, {st.session_state.full_name}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")

        # Default credentials info (for development)
        st.info("""
            **Default Accounts:**
            - **Admin:** username: `admin`, password: `admin123`
            - **PM User:** username: `pmuser`, password: `pm123`
        """)

        # Version info
        st.markdown("""
            <div style="text-align: center; margin-top: 2rem; color: #999; font-size: 0.85rem;">
                Version 1.0.0 | © Verizon Communications
            </div>
        """, unsafe_allow_html=True)


def show_dashboard():
    """Display the main dashboard after login"""

    # Import sidebar
    from app import sidebar

    # Show sidebar
    sidebar.show_sidebar()

    # Main content
    st.markdown(f"""
        <h1>Welcome, {st.session_state.full_name}</h1>
        <div class="vz-title-accent"></div>
    """, unsafe_allow_html=True)

    # Role-specific dashboard
    role = st.session_state.role

    st.markdown(f"""
        <div class="vz-card">
            <h3>👤 Your Profile</h3>
            <p><strong>Role:</strong> {role}</p>
            <p><strong>Username:</strong> {st.session_state.username}</p>
            <p><strong>Email:</strong> {st.session_state.user.get('email', 'N/A')}</p>
        </div>
    """, unsafe_allow_html=True)

    # Quick stats
    st.markdown("### 📊 Quick Stats")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Active Projects</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Pending Sync</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Completed</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">100%</div>
                <div class="metric-label">On-Time</div>
            </div>
        """, unsafe_allow_html=True)

    # Getting started guide
    st.markdown("### 🚀 Getting Started")

    if role == "Sr. Project Manager":
        st.markdown("""
            <div class="vz-card">
                <h4>Project Manager Quick Start</h4>
                <ol>
                    <li>Navigate to <strong>My Dashboard</strong> to view your projects</li>
                    <li>Click <strong>New Project</strong> to create a new project</li>
                    <li>Use <strong>Sync Data</strong> to push changes to the master database</li>
                    <li>Track KPIs and manage project dependencies</li>
                </ol>
            </div>
        """, unsafe_allow_html=True)

    elif role == "Associate Director":
        st.markdown("""
            <div class="vz-card">
                <h4>Administrator Quick Start</h4>
                <ol>
                    <li>Access <strong>Team Dashboard</strong> to view all projects</li>
                    <li>Use <strong>Admin Panel</strong> to manage users and settings</li>
                    <li>Process sync data from <strong>Process Sync Inbox</strong></li>
                    <li>Import legacy data via <strong>Import Data</strong></li>
                </ol>
            </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
            <div class="vz-card">
                <h4>Welcome!</h4>
                <p>Use the sidebar navigation to access:</p>
                <ul>
                    <li><strong>All Projects</strong> - View all projects in the system</li>
                    <li><strong>Reports</strong> - Access analytics and dashboards</li>
                    <li><strong>AI Assistant</strong> - Get intelligent insights</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # Recent activity placeholder
    st.markdown("### 📋 Recent Activity")
    st.info("No recent activity to display. Start by creating a project!")


def main():
    """Main application logic"""

    # Initialize databases on first run
    try:
        initialize_all_databases()
    except Exception as e:
        st.error(f"Database initialization error: {e}")

    # Route based on authentication status
    if st.session_state.authenticated:
        show_dashboard()
    else:
        show_login_page()


if __name__ == "__main__":
    main()
