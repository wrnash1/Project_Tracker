"""
Team Dashboard - Admin view of all team projects and metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vtrack import auth
from src.vtrack.database import MasterProjectsDB, MasterUsersDB
from app.styles import apply_verizon_theme
from app import sidebar

st.set_page_config(page_title="Team Dashboard", page_icon="👥", layout="wide")
apply_verizon_theme()
auth.require_role(['Associate Director', 'Director'])
sidebar.show_sidebar()

st.markdown("""
    <h1>👥 Team Dashboard</h1>
    <div class="vz-title-accent"></div>
    <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Overview of all team projects and performance metrics
    </p>
""", unsafe_allow_html=True)

# Connect to databases
projects_db = MasterProjectsDB()
projects_db.connect()

users_db = MasterUsersDB()
users_db.connect()

# Get all projects with user and program data
projects = projects_db.fetchall("""
    SELECT
        p.*,
        u.full_name as pm_name,
        u.role as pm_role,
        prog.program_name,
        pt.type_name as project_type
    FROM projects p
    LEFT JOIN users u ON p.pm_id = u.user_id
    LEFT JOIN programs prog ON p.program_id = prog.program_id
    LEFT JOIN project_types pt ON p.project_type_id = pt.type_id
    ORDER BY p.updated_at DESC
""")

# Get all users
users = users_db.fetchall("SELECT * FROM users WHERE active = 1")

projects_db.close()
users_db.close()

if not projects:
    st.warning("No projects found. Create some projects to see team metrics!")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame([dict(p) for p in projects])
users_df = pd.DataFrame([dict(u) for u in users])

# === EXECUTIVE SUMMARY ===
st.markdown("### 📊 Executive Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_projects = len(df)
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_projects}</div>
            <div class="metric-label">Total Projects</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    active = len(df[df['status'] == 'Active'])
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #4CAF50;">
            <div class="metric-value">{active}</div>
            <div class="metric-label">Active</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    on_hold = len(df[df['status'] == 'On Hold'])
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #FF9800;">
            <div class="metric-value">{on_hold}</div>
            <div class="metric-label">On Hold</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    completed = len(df[df['status'] == 'Completed'])
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2196F3;">
            <div class="metric-value">{completed}</div>
            <div class="metric-label">Completed</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    total_pms = len(users_df[users_df['role'] == 'Sr. Project Manager'])
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #9C27B0;">
            <div class="metric-value">{total_pms}</div>
            <div class="metric-label">Project Managers</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# === CHARTS ROW 1 ===
st.markdown("### 📈 Project Analytics")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Projects by Status - Pie Chart
    status_counts = df['status'].value_counts()
    fig_status = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Projects by Status",
        color_discrete_sequence=['#4CAF50', '#FF9800', '#2196F3', '#F44336']
    )
    fig_status.update_layout(height=300)
    st.plotly_chart(fig_status, use_container_width=True)

with chart_col2:
    # Projects by Type - Bar Chart
    type_counts = df['project_type'].value_counts()
    fig_type = px.bar(
        x=type_counts.index,
        y=type_counts.values,
        title="Projects by Type",
        labels={'x': 'Project Type', 'y': 'Count'},
        color=type_counts.values,
        color_continuous_scale='Reds'
    )
    fig_type.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig_type, use_container_width=True)

# === CHARTS ROW 2 ===
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    # Projects by PM - Horizontal Bar
    pm_counts = df['pm_name'].value_counts().head(10)
    fig_pm = px.bar(
        x=pm_counts.values,
        y=pm_counts.index,
        title="Top 10 PMs by Project Count",
        labels={'x': 'Number of Projects', 'y': 'Project Manager'},
        orientation='h',
        color=pm_counts.values,
        color_continuous_scale='Blues'
    )
    fig_pm.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_pm, use_container_width=True)

with chart_col4:
    # Projects by Program
    if 'program_name' in df.columns and df['program_name'].notna().any():
        prog_counts = df['program_name'].value_counts()
        fig_prog = px.bar(
            x=prog_counts.index,
            y=prog_counts.values,
            title="Projects by Program",
            labels={'x': 'Program', 'y': 'Count'},
            color=prog_counts.values,
            color_continuous_scale='Greens'
        )
        fig_prog.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_prog, use_container_width=True)
    else:
        st.info("No program data available yet")

# === PROJECT MANAGER PERFORMANCE ===
st.markdown("---")
st.markdown("### 👤 Project Manager Performance")

# Calculate metrics per PM
pm_metrics = []
for pm_name in df['pm_name'].dropna().unique():
    pm_projects = df[df['pm_name'] == pm_name]
    
    total = len(pm_projects)
    active = len(pm_projects[pm_projects['status'] == 'Active'])
    completed = len(pm_projects[pm_projects['status'] == 'Completed'])
    on_hold = len(pm_projects[pm_projects['status'] == 'On Hold'])
    
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    pm_metrics.append({
        'Project Manager': pm_name,
        'Total Projects': total,
        'Active': active,
        'Completed': completed,
        'On Hold': on_hold,
        'Completion Rate': f"{completion_rate:.1f}%"
    })

if pm_metrics:
    pm_df = pd.DataFrame(pm_metrics)
    pm_df = pm_df.sort_values('Total Projects', ascending=False)
    
    st.dataframe(
        pm_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Project Manager": st.column_config.TextColumn("Project Manager", width="medium"),
            "Total Projects": st.column_config.NumberColumn("Total", width="small"),
            "Active": st.column_config.NumberColumn("Active", width="small"),
            "Completed": st.column_config.NumberColumn("Completed", width="small"),
            "On Hold": st.column_config.NumberColumn("On Hold", width="small"),
            "Completion Rate": st.column_config.TextColumn("Completion %", width="small"),
        }
    )

# === RECENT ACTIVITY ===
st.markdown("---")
st.markdown("### 🕐 Recent Activity")

# Get recently updated projects
recent_df = df.nlargest(10, 'updated_at')[['name', 'ccr_nfid', 'status', 'pm_name', 'updated_at']]
recent_df['updated_at'] = pd.to_datetime(recent_df['updated_at'])
recent_df['updated_at'] = recent_df['updated_at'].dt.strftime('%Y-%m-%d %H:%M')

st.dataframe(
    recent_df,
    hide_index=True,
    use_container_width=True,
    column_config={
        "name": "Project Name",
        "ccr_nfid": "CCR/NFID",
        "status": "Status",
        "pm_name": "PM",
        "updated_at": "Last Updated"
    }
)

# === FILTER & DRILL DOWN ===
st.markdown("---")
st.markdown("### 🔍 Detailed Project View")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    pm_filter = st.multiselect(
        "Filter by PM",
        options=df['pm_name'].dropna().unique().tolist(),
        default=[]
    )

with filter_col2:
    status_filter = st.multiselect(
        "Filter by Status",
        options=['Active', 'On Hold', 'Completed', 'Cancelled'],
        default=['Active', 'On Hold']
    )

with filter_col3:
    type_filter = st.multiselect(
        "Filter by Type",
        options=df['project_type'].dropna().unique().tolist(),
        default=[]
    )

# Apply filters
filtered_df = df.copy()

if pm_filter:
    filtered_df = filtered_df[filtered_df['pm_name'].isin(pm_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
if type_filter:
    filtered_df = filtered_df[filtered_df['project_type'].isin(type_filter)]

st.markdown(f"**Showing {len(filtered_df)} of {len(df)} projects**")

# Display filtered projects
display_cols = ['name', 'ccr_nfid', 'status', 'pm_name', 'project_type', 'customer', 'phase']
display_cols = [col for col in display_cols if col in filtered_df.columns]

st.dataframe(
    filtered_df[display_cols],
    hide_index=True,
    use_container_width=True,
    height=400
)

# === EXPORT ===
st.markdown("---")
col_e1, col_e2, col_e3 = st.columns([2, 1, 2])

with col_e2:
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Export to CSV",
        data=csv,
        file_name=f"team_dashboard_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
