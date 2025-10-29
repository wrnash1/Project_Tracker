"""
Verizon Tracker - Main Entry Point
Login page and application initialization
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import os
import base64
from PIL import Image
import io

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vtrack import auth
from src.vtrack.database import initialize_all_databases, G_DRIVE
from app.styles import apply_verizon_theme

# Profile pictures directory
PROFILE_PICS_DIR = G_DRIVE / "profile_pictures"
PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)

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
                Version 2.0.0 | © Verizon Communications
            </div>
        """, unsafe_allow_html=True)


def get_profile_picture_path(username):
    """Get the path to user's profile picture"""
    return PROFILE_PICS_DIR / f"{username}.png"

def get_default_avatar():
    """Generate default avatar SVG"""
    return """
    <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
        <circle cx="60" cy="60" r="60" fill="#EE0000"/>
        <circle cx="60" cy="45" r="20" fill="white"/>
        <ellipse cx="60" cy="95" rx="30" ry="25" fill="white"/>
    </svg>
    """

def show_digital_clock():
    """Display live digital clock with date"""
    st.markdown("""
        <style>
        .digital-clock {
            background: linear-gradient(135deg, #EE0000 0%, #CD040B 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(238, 0, 0, 0.2);
            margin-bottom: 1rem;
        }
        .clock-time {
            font-size: 2.5rem;
            font-weight: 700;
            color: white;
            font-family: 'Courier New', monospace;
            letter-spacing: 2px;
            margin: 0;
        }
        .clock-date {
            font-size: 1rem;
            color: rgba(255,255,255,0.9);
            margin-top: 0.5rem;
            font-weight: 500;
        }
        .clock-day {
            font-size: 0.85rem;
            color: rgba(255,255,255,0.8);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        </style>
        <script>
        function updateClock() {
            const now = new Date();
            const time = now.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true});
            const date = now.toLocaleDateString('en-US', {month: 'long', day: 'numeric', year: 'numeric'});
            const day = now.toLocaleDateString('en-US', {weekday: 'long'});

            document.getElementById('clock-time').textContent = time;
            document.getElementById('clock-date').textContent = date;
            document.getElementById('clock-day').textContent = day;
        }
        setInterval(updateClock, 1000);
        updateClock();
        </script>
        <div class="digital-clock">
            <div class="clock-time" id="clock-time"></div>
            <div class="clock-date" id="clock-date"></div>
            <div class="clock-day" id="clock-day"></div>
        </div>
    """, unsafe_allow_html=True)

def calculate_profile_completeness(user):
    """Calculate profile completeness percentage"""
    fields = ['full_name', 'email', 'role']
    completed = sum(1 for field in fields if user.get(field))

    # Check if profile picture exists
    pic_path = get_profile_picture_path(st.session_state.username)
    if pic_path.exists():
        completed += 1
        total = len(fields) + 1
    else:
        total = len(fields) + 1

    return int((completed / total) * 100)

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

    # Create two columns: left for profile, right for clock
    col_profile, col_clock = st.columns([2, 1])

    with col_clock:
        # Digital clock
        show_digital_clock()

    with col_profile:
        # Profile header with settings
        col_title, col_settings = st.columns([4, 1])
        with col_title:
            st.markdown("### 👤 Your Profile")
        with col_settings:
            with st.popover("⚙️"):
                st.markdown("**Profile Settings**")

                # Theme preference
                theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], key="theme_pref")

                # Notification preferences
                st.markdown("**Notifications:**")
                email_notif = st.checkbox("Email notifications", value=True, key="email_notif")
                sync_notif = st.checkbox("Sync reminders", value=True, key="sync_notif")
                kpi_notif = st.checkbox("KPI alerts", value=True, key="kpi_notif")

                # Display preferences
                st.markdown("**Display:**")
                show_tips = st.checkbox("Show tips", value=True, key="show_tips")
                compact_view = st.checkbox("Compact view", value=False, key="compact_view")

                # Export profile data
                st.markdown("**Data:**")
                if st.button("📥 Export Profile Data", use_container_width=True):
                    import json
                    profile_data = {
                        "username": st.session_state.username,
                        "full_name": st.session_state.full_name,
                        "email": st.session_state.user.get('email', 'N/A'),
                        "role": st.session_state.role,
                        "user_id": st.session_state.user_id,
                        "exported_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    st.download_button(
                        "Download JSON",
                        data=json.dumps(profile_data, indent=2),
                        file_name=f"profile_{st.session_state.username}.json",
                        mime="application/json",
                        use_container_width=True
                    )

                st.info("💡 Settings are saved automatically")

        # Profile section with picture
        profile_col1, profile_col2 = st.columns([1, 3])

        with profile_col1:
            # Profile picture
            pic_path = get_profile_picture_path(st.session_state.username)

            if pic_path.exists():
                try:
                    image = Image.open(pic_path)
                    st.image(image, width=120, use_container_width=False)
                except:
                    st.markdown(get_default_avatar(), unsafe_allow_html=True)
            else:
                st.markdown(get_default_avatar(), unsafe_allow_html=True)

            # Upload new picture button
            with st.expander("📸 Change Picture"):
                uploaded_file = st.file_uploader(
                    "Upload new profile picture",
                    type=['png', 'jpg', 'jpeg'],
                    key="profile_pic_upload",
                    help="Recommended: Square image, 200x200px or larger"
                )

                if uploaded_file:
                    try:
                        image = Image.open(uploaded_file)
                        # Resize to square
                        size = (200, 200)
                        image = image.resize(size, Image.Resampling.LANCZOS)
                        # Save
                        image.save(pic_path)
                        st.success("✅ Picture updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error uploading picture: {e}")

                # Remove picture option
                if pic_path.exists():
                    if st.button("🗑️ Remove Picture", use_container_width=True):
                        pic_path.unlink()
                        st.success("Picture removed!")
                        st.rerun()

        with profile_col2:
            # Profile information
            st.markdown(f"""
                <div class="vz-card" style="padding: 1rem;">
                    <p style="margin: 0.5rem 0;"><strong>Role:</strong> {role}</p>
                    <p style="margin: 0.5rem 0;"><strong>Username:</strong> {st.session_state.username}</p>
                    <p style="margin: 0.5rem 0;"><strong>Email:</strong> {st.session_state.user.get('email', 'N/A')}</p>
                    <p style="margin: 0.5rem 0;"><strong>User ID:</strong> #{st.session_state.user_id}</p>
                    <p style="margin: 0.5rem 0;"><strong>Status:</strong> <span style="color: #4CAF50;">● Active</span></p>
                </div>
            """, unsafe_allow_html=True)

            # Profile completeness indicator
            completeness = calculate_profile_completeness(st.session_state.user)
            color = "#4CAF50" if completeness == 100 else "#FF9800" if completeness >= 75 else "#EE0000"

            st.markdown(f"""
                <div style="margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600;">Profile Completeness</span>
                        <span style="font-weight: 700; color: {color};">{completeness}%</span>
                    </div>
                    <div style="background: #E0E0E0; border-radius: 10px; height: 8px; overflow: hidden;">
                        <div style="background: {color}; width: {completeness}%; height: 100%; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if completeness < 100:
                st.info("💡 Complete your profile by adding a profile picture and email!")

    st.markdown("---")

    # Quick stats with real data
    st.markdown("### 📊 Quick Stats")

    # Get actual statistics from database
    from src.vtrack.database import MasterProjectsDB, LocalProjectsDB

    try:
        # For PM users, show local stats
        if role == "Sr. Project Manager":
            local_db = LocalProjectsDB(st.session_state.user_id)
            local_db.connect()

            # Active projects
            active = local_db.fetchone("SELECT COUNT(*) as count FROM projects WHERE pm_id = ? AND status = 'Active'",
                                       (st.session_state.user_id,))
            active_count = active['count'] if active else 0

            # Pending sync
            pending = local_db.fetchone("SELECT COUNT(*) as count FROM projects WHERE sync_status IN ('new', 'updated')", ())
            pending_count = pending['count'] if pending else 0

            # Completed
            completed = local_db.fetchone("SELECT COUNT(*) as count FROM projects WHERE pm_id = ? AND status = 'Completed'",
                                         (st.session_state.user_id,))
            completed_count = completed['count'] if completed else 0

            # Total projects
            total = local_db.fetchone("SELECT COUNT(*) as count FROM projects WHERE pm_id = ?",
                                     (st.session_state.user_id,))
            total_count = total['count'] if total else 0

            local_db.close()
        else:
            # For other roles, show master stats
            master_db = MasterProjectsDB()
            master_db.connect()

            if role in ["Associate Director", "Director"]:
                # Show all projects
                active = master_db.fetchone("SELECT COUNT(*) as count FROM projects WHERE status = 'Active'", ())
                active_count = active['count'] if active else 0

                completed = master_db.fetchone("SELECT COUNT(*) as count FROM projects WHERE status = 'Completed'", ())
                completed_count = completed['count'] if completed else 0

                total = master_db.fetchone("SELECT COUNT(*) as count FROM projects", ())
                total_count = total['count'] if total else 0

                on_hold = master_db.fetchone("SELECT COUNT(*) as count FROM projects WHERE status = 'On Hold'", ())
                on_hold_count = on_hold['count'] if on_hold else 0
            else:
                # Principal Engineer - read-only view
                active = master_db.fetchone("SELECT COUNT(*) as count FROM projects WHERE status = 'Active'", ())
                active_count = active['count'] if active else 0

                completed = master_db.fetchone("SELECT COUNT(*) as count FROM projects WHERE status = 'Completed'", ())
                completed_count = completed['count'] if completed else 0

                total = master_db.fetchone("SELECT COUNT(*) as count FROM projects", ())
                total_count = total['count'] if total else 0

                pending_count = 0

            master_db.close()
    except Exception as e:
        # Fallback to zeros if database error
        active_count = 0
        pending_count = 0
        completed_count = 0
        total_count = 0

    # Display metrics based on role
    if role == "Sr. Project Manager":
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #4CAF50;">{active_count}</div>
                    <div class="metric-label">Active Projects</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            badge_color = "#FF9800" if pending_count > 0 else "#4CAF50"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {badge_color};">{pending_count}</div>
                    <div class="metric-label">Pending Sync</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #2196F3;">{completed_count}</div>
                    <div class="metric-label">Completed</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #673AB7;">{total_count}</div>
                    <div class="metric-label">Total Projects</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #673AB7;">{total_count}</div>
                    <div class="metric-label">Total Projects</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #4CAF50;">{active_count}</div>
                    <div class="metric-label">Active</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #2196F3;">{completed_count}</div>
                    <div class="metric-label">Completed</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            if role in ["Associate Director", "Director"]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #FF9800;">{on_hold_count}</div>
                        <div class="metric-label">On Hold</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #999;">--</div>
                        <div class="metric-label">N/A</div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Dashboard Widgets
    from src.vtrack.widgets import show_dashboard_widgets
    show_dashboard_widgets()

    st.markdown("---")

    # Search and Recent Projects section
    search_col, recent_col = st.columns([2, 1])

    with search_col:
        from src.vtrack.search import show_search_bar
        st.markdown("### 🔍 Quick Search")
        show_search_bar()

    with recent_col:
        from src.vtrack.search import show_recent_projects_widget
        from src.vtrack.favorites import show_favorites_widget

        # Show favorites first
        show_favorites_widget()

        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)

        # Then recent projects
        show_recent_projects_widget()

    st.markdown("---")

    # Project Health Summary (for PMs and Admins)
    if role in ["Sr. Project Manager", "Associate Director"]:
        st.markdown("### 🏥 Project Health Summary")

        from src.vtrack.health_score import HealthScoreCalculator

        # Get projects
        if role == "Sr. Project Manager":
            local_db = LocalProjectsDB(st.session_state.user_id)
            local_db.connect()
            projects = local_db.fetchall("""
                SELECT * FROM projects
                WHERE pm_id = ? AND status IN ('Active', 'On Hold')
                ORDER BY name
                LIMIT 5
            """, (st.session_state.user_id,))
            local_db.close()
        else:
            master_db = MasterProjectsDB()
            master_db.connect()
            projects = master_db.fetchall("""
                SELECT * FROM projects
                WHERE status = 'Active'
                ORDER BY updated_at DESC
                LIMIT 5
            """, ())
            master_db.close()

        if projects:
            health_col1, health_col2 = st.columns(2)

            for idx, proj in enumerate(projects[:4]):
                project_dict = dict(proj)
                health = HealthScoreCalculator.calculate_project_health(project_dict)

                with (health_col1 if idx % 2 == 0 else health_col2):
                    st.markdown(f"""
                        <div class="vz-card" style="padding: 1rem; margin-bottom: 0.5rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="flex: 1;">
                                    <div style="font-weight: 600; color: #333; margin-bottom: 0.25rem;">
                                        {project_dict['name'][:30]}{'...' if len(project_dict['name']) > 30 else ''}
                                    </div>
                                    <div style="font-size: 0.85rem; color: #666;">
                                        {project_dict.get('ccr_nfid', 'N/A')[:20]}
                                    </div>
                                </div>
                                <div>
                                    {HealthScoreCalculator.get_health_indicator_html(health, 'small')}
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No active projects to display health scores for.")

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

    # Recent activity timeline
    st.markdown("### 📋 Recent Activity")

    from src.vtrack.activity_logger import ActivityLogger
    from datetime import datetime as dt

    # Get recent activities
    if role in ["Associate Director", "Director"]:
        # Show team activities for admins
        activities = ActivityLogger.get_team_activities(limit=10)
    else:
        # Show user's own activities
        activities = ActivityLogger.get_recent_activities(st.session_state.user_id, limit=10)

    if activities:
        # Activity timeline
        st.markdown("""
            <style>
            .activity-timeline {
                position: relative;
                padding-left: 2rem;
            }
            .activity-item {
                position: relative;
                padding: 1rem;
                margin-bottom: 1rem;
                background: white;
                border-radius: 8px;
                border-left: 4px solid #EE0000;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .activity-item:hover {
                transform: translateX(5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .activity-icon {
                position: absolute;
                left: -2.5rem;
                top: 1rem;
                width: 2rem;
                height: 2rem;
                background: #EE0000;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.9rem;
                font-weight: bold;
            }
            .activity-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.5rem;
            }
            .activity-type {
                font-weight: 600;
                color: #333;
                font-size: 0.95rem;
            }
            .activity-time {
                color: #999;
                font-size: 0.85rem;
            }
            .activity-desc {
                color: #666;
                font-size: 0.9rem;
            }
            .activity-project {
                display: inline-block;
                background: #F0F0F0;
                padding: 0.2rem 0.6rem;
                border-radius: 4px;
                font-size: 0.85rem;
                margin-top: 0.5rem;
                color: #555;
            }
            </style>
        """, unsafe_allow_html=True)

        activity_html = '<div class="activity-timeline">'

        for activity in activities:
            # Get activity icon based on type
            icon_map = {
                'login': '🔐',
                'logout': '👋',
                'create_project': '➕',
                'update_project': '✏️',
                'sync': '🔄',
                'kpi_snapshot': '📊',
                'import': '📥',
                'export': '📤'
            }
            icon = icon_map.get(activity['activity_type'], '📝')

            # Format time
            try:
                created_at = dt.strptime(activity['created_at'], '%Y-%m-%d %H:%M:%S')
                time_diff = dt.now() - created_at
                if time_diff.days > 0:
                    time_str = f"{time_diff.days}d ago"
                elif time_diff.seconds // 3600 > 0:
                    time_str = f"{time_diff.seconds // 3600}h ago"
                elif time_diff.seconds // 60 > 0:
                    time_str = f"{time_diff.seconds // 60}m ago"
                else:
                    time_str = "just now"
            except:
                time_str = "recently"

            # User name for team view
            user_info = ""
            if role in ["Associate Director", "Director"] and 'user_name' in activity:
                user_info = f" by {activity['user_name']}"

            # Project link
            project_info = ""
            if activity.get('project_name'):
                project_info = f'<div class="activity-project">📁 {activity["project_name"]}</div>'

            activity_html += f"""
                <div class="activity-item">
                    <div class="activity-icon">{icon}</div>
                    <div class="activity-header">
                        <span class="activity-type">{activity['activity_type'].replace('_', ' ').title()}{user_info}</span>
                        <span class="activity-time">{time_str}</span>
                    </div>
                    <div class="activity-desc">{activity['activity_description']}</div>
                    {project_info}
                </div>
            """

        activity_html += '</div>'
        st.markdown(activity_html, unsafe_allow_html=True)

    else:
        st.info("💡 No recent activity to display. Start by creating a project or syncing data!")


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
