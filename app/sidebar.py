"""
Sidebar component for Verizon Tracker
Navigation and user info display
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vtrack import auth


def show_sidebar():
    """Display the sidebar with navigation and user info"""

    with st.sidebar:
        # Verizon branding
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0 2rem 0;">
                <h1 style="color: #EE0000; margin: 0; font-size: 2.5rem; font-weight: 700;">Verizon</h1>
                <div style="width: 60px; height: 3px; background: linear-gradient(90deg, #EE0000 0%, #CD040B 100%); margin: 0.5rem auto;"></div>
                <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: 500;">Project Tracker</p>
            </div>
        """, unsafe_allow_html=True)

        # User info
        if st.session_state.authenticated:
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                    <p style="color: white; margin: 0; font-size: 0.875rem; opacity: 0.8;">Logged in as</p>
                    <p style="color: white; margin: 0.25rem 0 0 0; font-size: 1.1rem; font-weight: 600;">{st.session_state.full_name}</p>
                    <p style="color: #EE0000; margin: 0.25rem 0 0 0; font-size: 0.875rem; font-weight: 500;">{st.session_state.role}</p>
                </div>
            """, unsafe_allow_html=True)

            # Navigation
            st.markdown("### Navigation")

            role = st.session_state.role

            # Common pages for all users
            st.page_link("Home.py", label="Home", icon="🏠")

            # Project Manager pages
            if role == "Sr. Project Manager":
                st.markdown("**My Projects**")
                st.page_link("pages/1_My_Dashboard.py", label="My Dashboard", icon="📊")
                st.page_link("pages/2_New_Project.py", label="New Project", icon="➕")
                st.page_link("pages/3_Sync_Data.py", label="Sync Data", icon="🔄")
                st.page_link("pages/11_Project_Templates.py", label="Templates", icon="📋")

            # Admin pages
            if role == "Associate Director":
                st.markdown("**Team Management**")
                st.page_link("pages/4_Team_Dashboard.py", label="Team Dashboard", icon="👥")
                st.page_link("pages/5_Import_Data.py", label="Import Data", icon="📤")
                st.page_link("pages/6_Process_Sync_Inbox.py", label="Process Sync", icon="⚙️")
                st.page_link("pages/7_Admin_Panel.py", label="Admin Panel", icon="🔧")
                st.page_link("pages/11_Project_Templates.py", label="Templates", icon="📋")

            # Reports and views for Directors and Principal Engineers
            if role in ["Director", "Principal Engineer", "Associate Director", "Sr. Project Manager"]:
                st.markdown("**Reports & Analytics**")
                st.page_link("pages/8_Reports.py", label="Reports", icon="📈")
                st.page_link("pages/9_All_Projects.py", label="All Projects", icon="📋")
                st.page_link("pages/12_Compare_Projects.py", label="Compare Projects", icon="⚖️")

            # AI Assistant for all
            st.markdown("**AI Tools**")
            st.page_link("pages/10_AI_Assistant.py", label="AI Assistant", icon="🤖")

            # Divider
            st.markdown("<hr style='margin: 1.5rem 0; border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)

            # Notifications
            from src.vtrack.notifications import show_notification_panel
            show_notification_panel()

            # Keyboard shortcuts
            st.markdown("**Quick Tools**")

            # Keyboard shortcuts modal
            with st.expander("⌨️ Keyboard Shortcuts"):
                st.markdown("""
                    <div style="font-size: 0.85rem; color: white;">
                        <p><strong>Navigation:</strong></p>
                        <ul style="margin: 0.5rem 0;">
                            <li><code>Ctrl + K</code> - Search</li>
                            <li><code>Ctrl + H</code> - Home</li>
                            <li><code>Ctrl + N</code> - New Project</li>
                        </ul>
                        <p><strong>Actions:</strong></p>
                        <ul style="margin: 0.5rem 0;">
                            <li><code>Ctrl + S</code> - Save</li>
                            <li><code>Ctrl + E</code> - Export</li>
                            <li><code>Esc</code> - Close Modal</li>
                        </ul>
                        <p><strong>View:</strong></p>
                        <ul style="margin: 0.5rem 0;">
                            <li><code>Ctrl + [</code> - Toggle Sidebar</li>
                            <li><code>Ctrl + R</code> - Refresh</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)

            # Help & Support
            with st.expander("❓ Help & Support"):
                st.markdown("""
                    <div style="font-size: 0.85rem; color: white;">
                        <p><strong>Documentation:</strong></p>
                        <ul style="margin: 0.5rem 0;">
                            <li>📖 User Guide</li>
                            <li>🚀 Quick Start</li>
                            <li>📝 Release Notes</li>
                        </ul>
                        <p><strong>Need Help?</strong></p>
                        <p style="margin: 0.5rem 0;">
                            Contact your system administrator<br/>
                            or check the documentation.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

            # Logout button
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            if st.button("🚪 Sign Out", use_container_width=True, key="sidebar_logout"):
                auth.logout()
                st.rerun()

        # Footer
        st.markdown("""
            <div style="position: fixed; bottom: 1rem; left: 1rem; right: 1rem; text-align: center;">
                <p style="color: rgba(255,255,255,0.5); font-size: 0.75rem; margin: 0;">
                    Version 2.0.0<br/>
                    © 2025 Verizon
                </p>
            </div>
        """, unsafe_allow_html=True)
