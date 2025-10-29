"""
Admin Panel - User management and system configuration
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vtrack import auth
from src.vtrack.database import MasterUsersDB, ConfigDB
from app.styles import apply_verizon_theme
from app import sidebar

st.set_page_config(page_title="Admin Panel", page_icon="🔧", layout="wide")
apply_verizon_theme()
auth.require_role(['Associate Director'])
sidebar.show_sidebar()

st.markdown("""
    <h1>🔧 Admin Panel</h1>
    <div class="vz-title-accent"></div>
    <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Manage users, configuration, and system settings
    </p>
""", unsafe_allow_html=True)

# Tabs for different admin functions
tab1, tab2, tab3, tab4 = st.tabs(["👥 User Management", "⚙️ Configuration", "📊 System Info", "💾 Backup & Restore"])

# ===== TAB 1: User Management =====
with tab1:
    st.markdown("### 👥 User Management")

    users_db = MasterUsersDB()
    users_db.connect()

    # Display existing users
    users = users_db.fetchall("""
        SELECT
            u.user_id,
            u.username,
            u.full_name,
            u.email,
            u.role,
            u.active,
            m.full_name as reports_to,
            u.created_at
        FROM users u
        LEFT JOIN users m ON u.reports_to_id = m.user_id
        ORDER BY u.created_at DESC
    """)

    if users:
        df = pd.DataFrame([dict(u) for u in users])

        st.markdown(f"**Current Users ({len(df)}):**")

        # Display users table
        display_df = df[['username', 'full_name', 'email', 'role', 'reports_to', 'active']]
        st.dataframe(
            display_df,
            column_config={
                "username": "Username",
                "full_name": "Full Name",
                "email": "Email",
                "role": "Role",
                "reports_to": "Reports To",
                "active": st.column_config.CheckboxColumn("Active")
            },
            hide_index=True,
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("### ➕ Create New User")

    with st.form("create_user_form"):
        col1, col2 = st.columns(2)

        with col1:
            new_username = st.text_input("Username *", placeholder="e.g., jdoe")
            new_full_name = st.text_input("Full Name *", placeholder="e.g., John Doe")
            new_email = st.text_input("Email", placeholder="e.g., john.doe@verizon.com")

        with col2:
            new_role = st.selectbox(
                "Role *",
                options=['Sr. Project Manager', 'Principal Engineer', 'Associate Director', 'Director']
            )

            # Get list of users for reports_to dropdown
            manager_options = {u['user_id']: u['full_name'] for u in users}
            reports_to = st.selectbox(
                "Reports To",
                options=[None] + list(manager_options.keys()),
                format_func=lambda x: "-- None --" if x is None else manager_options[x]
            )

            new_password = st.text_input("Initial Password *", type="password", placeholder="Must be 8+ characters")

        submit_user = st.form_submit_button("Create User", use_container_width=True, type="primary")

        if submit_user:
            if not new_username or not new_full_name or not new_password:
                st.error("Please fill in all required fields (*)")
            elif len(new_password) < 8:
                st.error("Password must be at least 8 characters long")
            else:
                try:
                    # Hash password
                    import bcrypt
                    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

                    # Insert user
                    users_db.execute("""
                        INSERT INTO users (username, password_hash, full_name, email, role, reports_to_id, active)
                        VALUES (?, ?, ?, ?, ?, ?, 1)
                    """, (new_username, hashed.decode('utf-8'), new_full_name, new_email, new_role, reports_to))

                    st.success(f"✅ User '{new_username}' created successfully!")
                    st.rerun()

                except Exception as e:
                    if "UNIQUE constraint failed" in str(e):
                        st.error(f"Username '{new_username}' already exists!")
                    else:
                        st.error(f"Error creating user: {e}")

    users_db.close()

# ===== TAB 2: Configuration =====
with tab2:
    st.markdown("### ⚙️ System Configuration")

    config_db = ConfigDB()
    config_db.connect()

    # Get all config settings
    settings = config_db.fetchall("SELECT * FROM config_settings ORDER BY setting_key")

    if settings:
        st.markdown("**Current Settings:**")

        # Display settings
        for setting in settings:
            with st.expander(f"🔧 {setting['setting_key']}", expanded=False):
                st.markdown(f"**Description:** {setting['description']}")
                st.markdown(f"**Current Value:** `{setting['setting_value']}`")

                # Edit form
                new_value = st.text_input(
                    "New Value",
                    value=setting['setting_value'],
                    key=f"config_{setting['setting_key']}"
                )

                if st.button("Update", key=f"btn_{setting['setting_key']}"):
                    config_db.set_config(setting['setting_key'], new_value)
                    st.success(f"✅ Updated {setting['setting_key']}")
                    st.rerun()

    st.markdown("---")
    st.markdown("### ➕ Add New Configuration")

    with st.form("add_config_form"):
        config_key = st.text_input("Configuration Key", placeholder="e.g., max_projects_per_user")
        config_value = st.text_input("Value", placeholder="e.g., 100")
        config_desc = st.text_area("Description", placeholder="Description of this setting...")

        if st.form_submit_button("Add Configuration"):
            if config_key and config_value:
                try:
                    config_db.execute("""
                        INSERT INTO config_settings (setting_key, setting_value, description)
                        VALUES (?, ?, ?)
                    """, (config_key, config_value, config_desc))
                    st.success(f"✅ Configuration '{config_key}' added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Key and Value are required")

    config_db.close()

# ===== TAB 3: System Info =====
with tab3:
    st.markdown("### 📊 System Information")

    import os
    from pathlib import Path

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown("""
            <div class="vz-card">
                <h4>Application Info</h4>
                <ul>
                    <li><strong>Version:</strong> 1.0.0</li>
                    <li><strong>Environment:</strong> Development</li>
                    <li><strong>Python Version:</strong> 3.10+</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        # Database sizes
        st.markdown("""
            <div class="vz-card">
                <h4>Database Information</h4>
            </div>
        """, unsafe_allow_html=True)

        from src.vtrack.database import G_DRIVE, LOCAL_DRIVE

        db_files = [
            ("Master Users", G_DRIVE / "master_users.db"),
            ("Master Projects", G_DRIVE / "master_projects.db"),
            ("Config", G_DRIVE / "config.db"),
        ]

        for name, path in db_files:
            if path.exists():
                size = path.stat().st_size / 1024  # KB
                st.markdown(f"- **{name}:** {size:.2f} KB")
            else:
                st.markdown(f"- **{name}:** Not found")

    with info_col2:
        # Sync inbox status
        from src.vtrack.database import SYNC_INBOX, ARCHIVE

        st.markdown("""
            <div class="vz-card">
                <h4>Sync Status</h4>
            </div>
        """, unsafe_allow_html=True)

        if SYNC_INBOX.exists():
            inbox_files = list(SYNC_INBOX.glob("*.json"))
            st.markdown(f"- **Pending Syncs:** {len(inbox_files)}")
        else:
            st.markdown(f"- **Pending Syncs:** 0")

        if ARCHIVE.exists():
            archive_files = list(ARCHIVE.glob("*.json"))
            st.markdown(f"- **Processed Syncs:** {len(archive_files)}")
        else:
            st.markdown(f"- **Processed Syncs:** 0")

        # Quick actions
        st.markdown("""
            <div class="vz-card">
                <h4>Quick Actions</h4>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Refresh Database Stats"):
            st.rerun()

        if st.button("📋 View All Projects"):
            st.switch_page("pages/9_All_Projects.py")

        if st.button("📊 View Reports"):
            st.switch_page("pages/8_Reports.py")

# ===== TAB 4: Backup & Restore =====
with tab4:
    st.markdown("### 💾 Backup & Restore")

    from src.vtrack.backup import BackupManager

    # Backup statistics
    stats = BackupManager.get_backup_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #673AB7;">{stats['total_backups']}</div>
                <div class="metric-label">Total Backups</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #2196F3;">{stats['total_size_mb']}</div>
                <div class="metric-label">Size (MB)</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #4CAF50; font-size: 0.9rem;">{stats['most_recent'][:10]}</div>
                <div class="metric-label">Most Recent</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #FF9800; font-size: 0.9rem;">{stats['oldest'][:10]}</div>
                <div class="metric-label">Oldest</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Create backup section
    with st.expander("➕ Create New Backup", expanded=True):
        with st.form("create_backup_form"):
            backup_name = st.text_input("Backup Name (optional)", placeholder="e.g., before_major_update")
            include_local = st.checkbox("Include local databases", value=False,
                                       help="Include all user local databases in backup")

            col_a, col_b = st.columns([1, 3])
            with col_a:
                if st.form_submit_button("🔒 Create Backup", use_container_width=True):
                    with st.spinner("Creating backup..."):
                        success, message, path = BackupManager.create_backup(backup_name, include_local)

                        if success:
                            st.success(message)
                            st.info(f"Backup location: {path}")
                            st.rerun()
                        else:
                            st.error(message)

    # List existing backups
    st.markdown("### 📦 Available Backups")

    backups = BackupManager.list_backups()

    if backups:
        for backup in backups:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                with col1:
                    st.markdown(f"""
                        <div style="
                            background: white;
                            padding: 1rem;
                            border-radius: 8px;
                            border-left: 4px solid #2196F3;
                            margin-bottom: 0.5rem;
                        ">
                            <div style="font-weight: 600; color: #333;">
                                {backup['backup_name']}
                            </div>
                            <div style="color: #666; font-size: 0.85rem; margin-top: 0.25rem;">
                                Created: {backup['created_at']} | Size: {backup['size_mb']} MB
                            </div>
                            <div style="color: #999; font-size: 0.75rem; margin-top: 0.25rem;">
                                Files: {len(backup.get('files_backed_up', []))}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("📥 Export", key=f"export_{backup['backup_folder_name']}", use_container_width=True):
                        zip_data = BackupManager.export_backup(backup['backup_folder_name'])
                        if zip_data:
                            st.download_button(
                                "Download ZIP",
                                data=zip_data,
                                file_name=f"{backup['backup_folder_name']}.zip",
                                mime="application/zip",
                                key=f"download_{backup['backup_folder_name']}",
                                use_container_width=True
                            )
                        else:
                            st.error("Export failed")

                with col3:
                    if st.button("♻️ Restore", key=f"restore_{backup['backup_folder_name']}", use_container_width=True):
                        st.session_state[f"confirm_restore_{backup['backup_folder_name']}"] = True

                with col4:
                    if st.button("🗑️ Delete", key=f"delete_{backup['backup_folder_name']}", use_container_width=True, type="secondary"):
                        st.session_state[f"confirm_delete_{backup['backup_folder_name']}"] = True

                # Confirmation dialogs
                if st.session_state.get(f"confirm_restore_{backup['backup_folder_name']}", False):
                    st.warning("⚠️ This will overwrite current databases!")
                    col_x, col_y = st.columns(2)
                    with col_x:
                        if st.button("✅ Confirm Restore", key=f"confirm_restore_yes_{backup['backup_folder_name']}", use_container_width=True):
                            success, message = BackupManager.restore_backup(backup['backup_folder_name'])
                            if success:
                                st.success(message)
                                del st.session_state[f"confirm_restore_{backup['backup_folder_name']}"]
                                st.rerun()
                            else:
                                st.error(message)
                    with col_y:
                        if st.button("❌ Cancel", key=f"confirm_restore_no_{backup['backup_folder_name']}", use_container_width=True):
                            del st.session_state[f"confirm_restore_{backup['backup_folder_name']}"]
                            st.rerun()

                if st.session_state.get(f"confirm_delete_{backup['backup_folder_name']}", False):
                    st.warning("⚠️ This will permanently delete the backup!")
                    col_x, col_y = st.columns(2)
                    with col_x:
                        if st.button("✅ Confirm Delete", key=f"confirm_delete_yes_{backup['backup_folder_name']}", use_container_width=True):
                            success, message = BackupManager.delete_backup(backup['backup_folder_name'])
                            if success:
                                st.success(message)
                                del st.session_state[f"confirm_delete_{backup['backup_folder_name']}"]
                                st.rerun()
                            else:
                                st.error(message)
                    with col_y:
                        if st.button("❌ Cancel", key=f"confirm_delete_no_{backup['backup_folder_name']}", use_container_width=True):
                            del st.session_state[f"confirm_delete_{backup['backup_folder_name']}"]
                            st.rerun()

    else:
        st.info("No backups available. Create your first backup above!")

    # Backup tips
    st.markdown("---")
    st.markdown("### 💡 Backup Best Practices")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="vz-card">
                <h4>🔒 Regular Backups</h4>
                <p style="margin: 0;">Create backups before:</p>
                <ul style="margin: 0.5rem 0;">
                    <li>Major updates</li>
                    <li>Data imports</li>
                    <li>Configuration changes</li>
                    <li>User management</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="vz-card">
                <h4>💾 Storage</h4>
                <p style="margin: 0;">Backup storage tips:</p>
                <ul style="margin: 0.5rem 0;">
                    <li>Export to external drive</li>
                    <li>Keep at least 3 backups</li>
                    <li>Rotate old backups</li>
                    <li>Test restore periodically</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="vz-card">
                <h4>⚠️ Caution</h4>
                <p style="margin: 0;">Important notes:</p>
                <ul style="margin: 0.5rem 0;">
                    <li>Restore overwrites current data</li>
                    <li>Local DBs optional in backup</li>
                    <li>Export backups off-system</li>
                    <li>Document backup reasons</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
