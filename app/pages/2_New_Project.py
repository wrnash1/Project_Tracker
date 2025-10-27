"""
New Project Page
Create new projects in local database
"""

import streamlit as st
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
    page_title="New Project - Verizon Tracker",
    page_icon="➕",
    layout="wide"
)

# Apply styling
apply_verizon_theme()

# Require PM authentication
auth.require_role(['Sr. Project Manager', 'Associate Director'])

# Show sidebar
sidebar.show_sidebar()

# Page header
st.markdown("""
    <h1>➕ New Project</h1>
    <div class="vz-title-accent"></div>
    <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Create a new project in your local database
    </p>
""", unsafe_allow_html=True)

# Get local database from session
local_db = st.session_state.local_db

# Fetch programs and project types for dropdowns
master_db = MasterProjectsDB()
master_db.connect()

programs = master_db.fetchall("SELECT program_id, program_name FROM programs ORDER BY program_name")
program_options = {p['program_id']: p['program_name'] for p in programs}

project_types = master_db.fetchall("SELECT type_id, type_name FROM project_types ORDER BY type_name")
type_options = {t['type_id']: t['type_name'] for t in project_types}

master_db.close()

# Project form
st.markdown("### 📝 Project Information")

with st.form("new_project_form", clear_on_submit=True):
    # Basic Information
    st.markdown("**Basic Information**")
    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input(
            "Project Name *",
            placeholder="Enter project name",
            help="A descriptive name for this project"
        )

        ccr_nfid = st.text_input(
            "CCR/NFID *",
            placeholder="Unique identifier",
            help="Unique project identifier (CCR or NFID)"
        )

        program_id = st.selectbox(
            "Program",
            options=[None] + list(program_options.keys()),
            format_func=lambda x: "-- Select Program --" if x is None else program_options[x],
            help="Associate this project with a program"
        )

        project_type_id = st.selectbox(
            "Project Type",
            options=[None] + list(type_options.keys()),
            format_func=lambda x: "-- Select Type --" if x is None else type_options[x],
            help="Select the project type"
        )

    with col2:
        status = st.selectbox(
            "Status *",
            options=["Active", "On Hold", "Completed", "Cancelled"],
            index=0
        )

        phase = st.text_input(
            "Phase",
            placeholder="e.g., Planning, Execution, Closeout"
        )

        customer = st.text_input(
            "Customer",
            placeholder="Customer name"
        )

        clli = st.text_input(
            "CLLI",
            placeholder="Common Language Location Identifier"
        )

    # Legacy Oracle Fields
    st.markdown("---")
    st.markdown("**Legacy System Fields**")

    col3, col4 = st.columns(2)

    with col3:
        nfid = st.text_input(
            "NFID",
            placeholder="Network Facility ID"
        )

        system_type = st.text_input(
            "System Type",
            placeholder="Equipment/System type"
        )

        current_queue = st.text_input(
            "Current Queue",
            placeholder="Current work queue"
        )

    with col4:
        rft_date = st.date_input(
            "RFT Date",
            value=None,
            help="Ready For Test date"
        )

        site_address = st.text_area(
            "Site Address",
            placeholder="Physical address of the site",
            height=100
        )

    # Scorecard Reporting Fields
    st.markdown("---")
    st.markdown("**Project Timeline**")

    col5, col6 = st.columns(2)

    with col5:
        project_start_date = st.date_input(
            "Project Start Date",
            value=None,
            help="When the project officially started"
        )

    with col6:
        project_complete_date = st.date_input(
            "Project Complete Date",
            value=None,
            help="When the project is expected to complete or was completed"
        )

    # Notes
    st.markdown("---")
    notes = st.text_area(
        "Notes",
        placeholder="Additional notes or comments about this project...",
        height=100
    )

    # Submit buttons
    st.markdown("---")
    col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 2])

    with col_b:
        cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

    with col_c:
        submit = st.form_submit_button("✅ Create Project", use_container_width=True, type="primary")

    if cancel:
        st.switch_page("pages/1_My_Dashboard.py")

    if submit:
        # Validation
        if not project_name or not ccr_nfid:
            st.error("⚠️ Please fill in all required fields (marked with *)")
        else:
            try:
                # Insert new project
                local_db.execute("""
                    INSERT INTO projects (
                        name, ccr_nfid, program_id, project_type_id, pm_id,
                        status, phase, notes,
                        nfid, customer, clli, rft_date, system_type, current_queue, site_address,
                        project_start_date, project_complete_date,
                        sync_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new')
                """, (
                    project_name,
                    ccr_nfid,
                    program_id,
                    project_type_id,
                    st.session_state.user_id,
                    status,
                    phase,
                    notes,
                    nfid,
                    customer,
                    clli,
                    rft_date,
                    system_type,
                    current_queue,
                    site_address,
                    project_start_date,
                    project_complete_date
                ))

                st.success(f"✅ Project '{project_name}' created successfully!")
                st.info("💡 Don't forget to sync your data to push this project to the master database.")

                # Option to create another or go to dashboard
                col_x, col_y = st.columns(2)
                with col_x:
                    if st.button("➕ Create Another Project", use_container_width=True):
                        st.rerun()
                with col_y:
                    if st.button("📊 Go to Dashboard", use_container_width=True):
                        st.switch_page("pages/1_My_Dashboard.py")

            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    st.error(f"❌ A project with CCR/NFID '{ccr_nfid}' already exists!")
                else:
                    st.error(f"❌ Error creating project: {e}")

# Tips section
st.markdown("---")
st.markdown("### 💡 Quick Tips")

tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.markdown("""
        <div class="vz-card">
            <h4>Required Fields</h4>
            <ul>
                <li><strong>Project Name:</strong> A clear, descriptive name</li>
                <li><strong>CCR/NFID:</strong> Must be unique across all projects</li>
                <li><strong>Status:</strong> Current project status</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with tips_col2:
    st.markdown("""
        <div class="vz-card">
            <h4>After Creating</h4>
            <ul>
                <li>Your project is saved in your <strong>local database</strong></li>
                <li>Use <strong>Sync Data</strong> to push to master database</li>
                <li>Add KPI snapshots and dependencies from the dashboard</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
