"""
All Projects - Read-only view of all master projects
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vtrack import auth
from src.vtrack.database import MasterProjectsDB, MasterUsersDB
from app.styles import apply_verizon_theme
from app import sidebar

st.set_page_config(page_title="All Projects", page_icon="📋", layout="wide")
apply_verizon_theme()
auth.require_auth()
sidebar.show_sidebar()

st.markdown("""
    <h1>📋 All Projects</h1>
    <div class="vz-title-accent"></div>
    <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        View all projects in the master database
    </p>
""", unsafe_allow_html=True)

# Connect to master database
projects_db = MasterProjectsDB()
projects_db.connect()

users_db = MasterUsersDB()
users_db.connect()

# Get all projects with related data
projects = projects_db.fetchall("""
    SELECT
        p.project_id,
        p.name,
        p.ccr_nfid,
        p.status,
        p.phase,
        p.customer,
        p.clli,
        p.site_address,
        p.current_queue,
        p.system_type,
        p.project_start_date,
        p.project_complete_date,
        prog.program_name,
        pt.type_name as project_type,
        u.full_name as pm_name,
        p.created_at,
        p.updated_at
    FROM projects p
    LEFT JOIN programs prog ON p.program_id = prog.program_id
    LEFT JOIN project_types pt ON p.project_type_id = pt.type_id
    LEFT JOIN users u ON p.pm_id = u.user_id
    ORDER BY p.updated_at DESC
""")

projects_db.close()
users_db.close()

# Convert to DataFrame
if projects:
    df = pd.DataFrame([dict(p) for p in projects])

    # Summary stats
    st.markdown("### 📊 Project Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total = len(df)
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total}</div>
                <div class="metric-label">Total Projects</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        active = len(df[df['status'] == 'Active'])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{active}</div>
                <div class="metric-label">Active</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        completed = len(df[df['status'] == 'Completed'])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{completed}</div>
                <div class="metric-label">Completed</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        on_hold = len(df[df['status'] == 'On Hold'])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{on_hold}</div>
                <div class="metric-label">On Hold</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Filters
    st.markdown("### 🔍 Filter Projects")

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        status_filter = st.multiselect(
            "Status",
            options=['Active', 'On Hold', 'Completed', 'Cancelled'],
            default=['Active', 'On Hold']
        )

    with col_f2:
        programs = df['program_name'].dropna().unique().tolist()
        program_filter = st.multiselect(
            "Program",
            options=programs,
            default=[]
        )

    with col_f3:
        types = df['project_type'].dropna().unique().tolist()
        type_filter = st.multiselect(
            "Project Type",
            options=types,
            default=[]
        )

    with col_f4:
        pms = df['pm_name'].dropna().unique().tolist()
        pm_filter = st.multiselect(
            "Project Manager",
            options=pms,
            default=[]
        )

    # Search box
    search_term = st.text_input("🔍 Search by name or CCR/NFID", placeholder="Type to search...")

    # Apply filters
    filtered_df = df.copy()

    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]

    if program_filter:
        filtered_df = filtered_df[filtered_df['program_name'].isin(program_filter)]

    if type_filter:
        filtered_df = filtered_df[filtered_df['project_type'].isin(type_filter)]

    if pm_filter:
        filtered_df = filtered_df[filtered_df['pm_name'].isin(pm_filter)]

    if search_term:
        mask = (
            filtered_df['name'].str.contains(search_term, case=False, na=False) |
            filtered_df['ccr_nfid'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    # Display projects table
    st.markdown(f"### 📋 Projects ({len(filtered_df)} of {len(df)})")

    # Select columns to display
    display_columns = [
        'name', 'ccr_nfid', 'status', 'pm_name',
        'program_name', 'project_type', 'customer',
        'clli', 'current_queue', 'phase'
    ]

    # Configure column display
    column_config = {
        "name": st.column_config.TextColumn("Project Name", width="medium"),
        "ccr_nfid": st.column_config.TextColumn("CCR/NFID", width="small"),
        "status": st.column_config.TextColumn("Status", width="small"),
        "pm_name": st.column_config.TextColumn("PM", width="medium"),
        "program_name": st.column_config.TextColumn("Program", width="medium"),
        "project_type": st.column_config.TextColumn("Type", width="small"),
        "customer": st.column_config.TextColumn("Customer", width="medium"),
        "clli": st.column_config.TextColumn("CLLI", width="small"),
        "current_queue": st.column_config.TextColumn("Queue", width="small"),
        "phase": st.column_config.TextColumn("Phase", width="small"),
    }

    # Display dataframe
    st.dataframe(
        filtered_df[display_columns],
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        height=500
    )

    # Export options
    st.markdown("---")
    st.markdown("### 📤 Export Data")

    col_e1, col_e2, col_e3 = st.columns([2, 1, 2])

    with col_e2:
        # Convert to CSV for download
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"verizon_projects_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Project statistics
    st.markdown("---")
    st.markdown("### 📈 Statistics")

    stat_col1, stat_col2 = st.columns(2)

    with stat_col1:
        st.markdown("**Projects by Status**")
        status_counts = filtered_df['status'].value_counts()
        st.bar_chart(status_counts)

    with stat_col2:
        st.markdown("**Projects by Type**")
        type_counts = filtered_df['project_type'].value_counts()
        st.bar_chart(type_counts)

else:
    st.info("No projects found in the master database. Create some projects and sync them!")
