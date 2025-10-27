"""
My Dashboard - Project Manager view
Display and edit local projects
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vtrack import auth
from src.vtrack.database import MasterProjectsDB
from app.styles import apply_verizon_theme
from app import sidebar

# Page config
st.set_page_config(
    page_title="My Dashboard - Verizon Tracker",
    page_icon="📊",
    layout="wide"
)

# Apply styling
apply_verizon_theme()

# Require PM authentication
auth.require_role(['Sr. Project Manager'])

# Show sidebar
sidebar.show_sidebar()

# Page header
st.markdown("""
    <h1>📊 My Dashboard</h1>
    <div class="vz-title-accent"></div>
    <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Manage your projects, track progress, and monitor KPIs
    </p>
""", unsafe_allow_html=True)


# Get local database from session
local_db = st.session_state.local_db

# Fetch user's projects
def get_my_projects():
    """Fetch all projects for the current user"""
    query = """
        SELECT
            local_id,
            name,
            ccr_nfid,
            status,
            phase,
            customer,
            clli,
            site_address,
            current_queue,
            system_type,
            project_start_date,
            project_complete_date,
            sync_status,
            notes
        FROM projects
        ORDER BY created_at DESC
    """
    results = local_db.fetchall(query)
    return [dict(row) for row in results]


# Load projects
projects = get_my_projects()

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_projects = len(projects)
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_projects}</div>
            <div class="metric-label">Total Projects</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    active_projects = len([p for p in projects if p['status'] == 'Active'])
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_projects}</div>
            <div class="metric-label">Active</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    pending_sync = len([p for p in projects if p['sync_status'] in ['new', 'updated']])
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{pending_sync}</div>
            <div class="metric-label">Pending Sync</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    completed_projects = len([p for p in projects if p['status'] == 'Completed'])
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{completed_projects}</div>
            <div class="metric-label">Completed</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Projects table
st.markdown("### 📋 My Projects")

if len(projects) == 0:
    st.info("👋 You don't have any projects yet. Click 'New Project' in the sidebar to create your first project!")
else:
    # Convert to DataFrame for display
    df = pd.DataFrame(projects)

    # Reorder columns for better display
    display_columns = [
        'name', 'ccr_nfid', 'status', 'customer', 'clli',
        'site_address', 'current_queue', 'system_type', 'sync_status'
    ]

    # Filter to only existing columns
    display_columns = [col for col in display_columns if col in df.columns]

    # Create editable data editor
    edited_df = st.data_editor(
        df[display_columns],
        hide_index=True,
        use_container_width=True,
        column_config={
            "name": st.column_config.TextColumn("Project Name", width="medium", required=True),
            "ccr_nfid": st.column_config.TextColumn("CCR/NFID", width="medium"),
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Active", "On Hold", "Completed", "Cancelled"],
                width="small"
            ),
            "customer": st.column_config.TextColumn("Customer", width="medium"),
            "clli": st.column_config.TextColumn("CLLI", width="small"),
            "site_address": st.column_config.TextColumn("Site Address", width="large"),
            "current_queue": st.column_config.TextColumn("Current Queue", width="medium"),
            "system_type": st.column_config.TextColumn("System Type", width="medium"),
            "sync_status": st.column_config.TextColumn("Sync Status", width="small"),
        },
        disabled=["ccr_nfid", "sync_status"],  # These fields are not editable
        key="projects_editor"
    )

    # Save changes button
    col_a, col_b, col_c = st.columns([3, 1, 3])
    with col_b:
        if st.button("💾 Save Changes", use_container_width=True):
            try:
                # Update each edited project
                for idx, row in edited_df.iterrows():
                    original = df.iloc[idx]
                    project_id = projects[idx]['local_id']

                    # Check if anything changed
                    if not row.equals(original[display_columns]):
                        # Update the project
                        local_db.execute("""
                            UPDATE projects
                            SET name = ?, status = ?, customer = ?, clli = ?,
                                site_address = ?, current_queue = ?, system_type = ?,
                                sync_status = CASE WHEN sync_status = 'synced' THEN 'updated' ELSE sync_status END,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE local_id = ?
                        """, (
                            row['name'], row['status'], row.get('customer', ''),
                            row.get('clli', ''), row.get('site_address', ''),
                            row.get('current_queue', ''), row.get('system_type', ''),
                            project_id
                        ))

                st.success("✅ Changes saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving changes: {e}")

# KPI Snapshots Section
st.markdown("---")
st.markdown("### 📸 KPI Snapshots")

with st.expander("➕ Take KPI Snapshot", expanded=False):
    st.markdown("Record a point-in-time snapshot of project KPIs for reporting and historical tracking.")

    kpi_col1, kpi_col2 = st.columns(2)

    with kpi_col1:
        # Select project
        if len(projects) > 0:
            project_options = {p['local_id']: f"{p['name']} ({p['ccr_nfid']})" for p in projects}
            selected_project_id = st.selectbox(
                "Select Project",
                options=list(project_options.keys()),
                format_func=lambda x: project_options[x],
                key="kpi_project"
            )

            snapshot_date = st.date_input("Snapshot Date", value=datetime.now().date())

            budget_status = st.selectbox(
                "Budget Status",
                options=["On Budget", "Over Budget", "Under Budget", "N/A"],
                key="kpi_budget"
            )

    with kpi_col2:
        schedule_status = st.selectbox(
            "Schedule Status",
            options=["On Schedule", "Behind Schedule", "Ahead of Schedule", "N/A"],
            key="kpi_schedule"
        )

        on_time_percent = st.slider(
            "On-Time Completion %",
            min_value=0,
            max_value=100,
            value=100,
            key="kpi_percent"
        )

        kpi_notes = st.text_area("Notes", key="kpi_notes", placeholder="Optional notes about this snapshot...")

    if st.button("📸 Save Snapshot", key="save_kpi"):
        if len(projects) > 0:
            try:
                local_db.execute("""
                    INSERT INTO kpi_snapshots
                    (local_project_id, snapshot_date, budget_status, schedule_status, on_time_percent, notes, sync_status)
                    VALUES (?, ?, ?, ?, ?, ?, 'new')
                """, (selected_project_id, snapshot_date, budget_status, schedule_status, on_time_percent, kpi_notes))

                st.success("✅ KPI snapshot saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving snapshot: {e}")
        else:
            st.warning("⚠️ Create a project first before taking KPI snapshots.")

# Project Dependencies Section
st.markdown("---")
st.markdown("### 🔗 Project Dependencies")

with st.expander("➕ Manage Dependencies", expanded=False):
    st.markdown("Define relationships between projects (e.g., Project B depends on Project A being completed).")

    if len(projects) >= 2:
        dep_col1, dep_col2 = st.columns(2)

        with dep_col1:
            project_options = {p['local_id']: f"{p['name']} ({p['ccr_nfid']})" for p in projects}

            dependent_project = st.selectbox(
                "Dependent Project (waits for)",
                options=list(project_options.keys()),
                format_func=lambda x: project_options[x],
                key="dep_project"
            )

        with dep_col2:
            depends_on_project = st.selectbox(
                "Depends On Project (must complete first)",
                options=list(project_options.keys()),
                format_func=lambda x: project_options[x],
                key="dep_depends_on"
            )

        dependency_type = st.selectbox(
            "Dependency Type",
            options=["Finish-to-Start", "Start-to-Start", "Finish-to-Finish", "Start-to-Finish"],
            key="dep_type"
        )

        dep_notes = st.text_area("Dependency Notes", key="dep_notes", placeholder="Optional notes...")

        if st.button("🔗 Add Dependency", key="save_dep"):
            if dependent_project == depends_on_project:
                st.error("❌ A project cannot depend on itself!")
            else:
                try:
                    local_db.execute("""
                        INSERT INTO project_dependencies
                        (local_project_id, depends_on_local_project_id, dependency_type, notes, sync_status)
                        VALUES (?, ?, ?, ?, 'new')
                    """, (dependent_project, depends_on_project, dependency_type, dep_notes))

                    st.success("✅ Dependency added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding dependency: {e}")
    else:
        st.info("👋 You need at least 2 projects to create dependencies.")

# Show existing dependencies
dependencies = local_db.fetchall("""
    SELECT
        d.local_dependency_id,
        p1.name as dependent_project,
        p2.name as depends_on_project,
        d.dependency_type,
        d.notes
    FROM project_dependencies d
    JOIN projects p1 ON d.local_project_id = p1.local_id
    JOIN projects p2 ON d.depends_on_local_project_id = p2.local_id
""")

if len(dependencies) > 0:
    st.markdown("**Current Dependencies:**")
    dep_df = pd.DataFrame([dict(d) for d in dependencies])
    st.dataframe(
        dep_df[['dependent_project', 'depends_on_project', 'dependency_type', 'notes']],
        hide_index=True,
        use_container_width=True
    )
