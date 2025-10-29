"""
Reports Page - Advanced analytics and KPI reporting
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
from src.vtrack.database import MasterProjectsDB
from app.styles import apply_verizon_theme
from app import sidebar

st.set_page_config(page_title="Reports & Analytics", page_icon="📈", layout="wide")
apply_verizon_theme()
auth.require_auth()
sidebar.show_sidebar()

st.markdown("""
    <h1>📈 Reports & Analytics</h1>
    <div class="vz-title-accent"></div>
    <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Comprehensive project analytics and KPI dashboards
    </p>
""", unsafe_allow_html=True)

# Connect to database
projects_db = MasterProjectsDB()
projects_db.connect()

# Get all data
projects = projects_db.fetchall("""
    SELECT
        p.*,
        u.full_name as pm_name,
        prog.program_name,
        pt.type_name as project_type
    FROM projects p
    LEFT JOIN users u ON p.pm_id = u.user_id
    LEFT JOIN programs prog ON p.program_id = prog.program_id
    LEFT JOIN project_types pt ON p.project_type_id = pt.type_id
""")

kpis = projects_db.fetchall("""
    SELECT
        k.*,
        p.name as project_name,
        p.ccr_nfid
    FROM kpi_snapshots k
    JOIN projects p ON k.project_id = p.project_id
    ORDER BY k.snapshot_date DESC
""")

projects_db.close()

if not projects:
    st.warning("No project data available for reporting.")
    st.stop()

df = pd.DataFrame([dict(p) for p in projects])
kpi_df = pd.DataFrame([dict(k) for k in kpis]) if kpis else pd.DataFrame()

# === REPORT SELECTOR ===
st.markdown("### 📊 Select Report")

report_type = st.selectbox(
    "Choose Report Type",
    ["Executive Summary", "Project Status Report", "KPI Dashboard", "Timeline Analysis", "Program Performance"]
)

st.markdown("---")

# ========================================
# EXECUTIVE SUMMARY REPORT
# ========================================
if report_type == "Executive Summary":
    st.markdown("## 📋 Executive Summary Report")
    st.markdown(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Projects", len(df))
    with col2:
        active_pct = len(df[df['status'] == 'Active']) / len(df) * 100
        st.metric("Active Projects", len(df[df['status'] == 'Active']), f"{active_pct:.1f}%")
    with col3:
        completed_pct = len(df[df['status'] == 'Completed']) / len(df) * 100
        st.metric("Completed", len(df[df['status'] == 'Completed']), f"{completed_pct:.1f}%")
    with col4:
        on_hold = len(df[df['status'] == 'On Hold'])
        st.metric("On Hold", on_hold, f"⚠️" if on_hold > 0 else "✓")
    
    # Status Distribution
    st.markdown("### Project Status Distribution")
    status_counts = df['status'].value_counts()
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="",
        hole=0.4,
        color_discrete_sequence=['#4CAF50', '#FF9800', '#2196F3', '#F44336']
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary Table
    st.markdown("### Summary by Type")
    type_summary = df.groupby('project_type').agg({
        'project_id': 'count',
        'status': lambda x: (x == 'Completed').sum()
    }).rename(columns={'project_id': 'Total', 'status': 'Completed'})
    type_summary['Completion %'] = (type_summary['Completed'] / type_summary['Total'] * 100).round(1)
    st.dataframe(type_summary, use_container_width=True)

# ========================================
# PROJECT STATUS REPORT
# ========================================
elif report_type == "Project Status Report":
    st.markdown("## 📊 Project Status Report")
    st.markdown(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    # Status Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Status Breakdown")
        status_counts = df['status'].value_counts()
        fig = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title="Projects by Status",
            color=status_counts.values,
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Phase Distribution")
        if 'phase' in df.columns and df['phase'].notna().any():
            phase_counts = df['phase'].value_counts()
            fig = px.bar(
                x=phase_counts.index,
                y=phase_counts.values,
                title="Projects by Phase",
                color=phase_counts.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No phase data available")
    
    # Detailed Status Table
    st.markdown("### Detailed Project Status")
    
    status_filter = st.multiselect(
        "Filter by Status",
        options=df['status'].unique().tolist(),
        default=df['status'].unique().tolist()
    )
    
    filtered = df[df['status'].isin(status_filter)]
    
    display_cols = ['name', 'ccr_nfid', 'status', 'phase', 'pm_name', 'project_type', 'customer']
    display_cols = [col for col in display_cols if col in filtered.columns]
    
    st.dataframe(
        filtered[display_cols],
        hide_index=True,
        use_container_width=True,
        height=400
    )

# ========================================
# KPI DASHBOARD
# ========================================
elif report_type == "KPI Dashboard":
    st.markdown("## 📈 KPI Dashboard")
    st.markdown(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    if len(kpi_df) == 0:
        st.warning("No KPI snapshot data available. Project Managers need to create KPI snapshots.")
        st.info("💡 Go to 'My Dashboard' → 'Take KPI Snapshot' to create KPI data.")
    else:
        # KPI Summary Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Snapshots", len(kpi_df))
        with col2:
            on_budget = len(kpi_df[kpi_df['budget_status'] == 'On Budget'])
            st.metric("On Budget", on_budget, f"{on_budget/len(kpi_df)*100:.1f}%")
        with col3:
            on_schedule = len(kpi_df[kpi_df['schedule_status'] == 'On Schedule'])
            st.metric("On Schedule", on_schedule, f"{on_schedule/len(kpi_df)*100:.1f}%")
        with col4:
            avg_on_time = kpi_df['on_time_percent'].mean() if 'on_time_percent' in kpi_df.columns else 0
            st.metric("Avg On-Time %", f"{avg_on_time:.1f}%")
        
        # Budget Status Chart
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("### Budget Status")
            budget_counts = kpi_df['budget_status'].value_counts()
            fig = px.pie(
                values=budget_counts.values,
                names=budget_counts.index,
                title="",
                color_discrete_map={
                    'On Budget': '#4CAF50',
                    'Over Budget': '#F44336',
                    'Under Budget': '#2196F3',
                    'N/A': '#9E9E9E'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_b:
            st.markdown("### Schedule Status")
            schedule_counts = kpi_df['schedule_status'].value_counts()
            fig = px.pie(
                values=schedule_counts.values,
                names=schedule_counts.index,
                title="",
                color_discrete_map={
                    'On Schedule': '#4CAF50',
                    'Behind Schedule': '#F44336',
                    'Ahead of Schedule': '#2196F3',
                    'N/A': '#9E9E9E'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # KPI Trend Over Time
        st.markdown("### KPI Trends")
        kpi_df['snapshot_date'] = pd.to_datetime(kpi_df['snapshot_date'])
        kpi_df = kpi_df.sort_values('snapshot_date')
        
        if len(kpi_df) > 1:
            # On-time percentage trend
            fig = px.line(
                kpi_df,
                x='snapshot_date',
                y='on_time_percent',
                title='On-Time Completion Trend',
                labels={'snapshot_date': 'Date', 'on_time_percent': 'On-Time %'},
                markers=True
            )
            fig.add_hline(y=90, line_dash="dash", line_color="green", annotation_text="Target: 90%")
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent KPIs Table
        st.markdown("### Recent KPI Snapshots")
        recent_kpis = kpi_df.nlargest(20, 'snapshot_date')[
            ['project_name', 'snapshot_date', 'budget_status', 'schedule_status', 'on_time_percent']
        ]
        st.dataframe(recent_kpis, hide_index=True, use_container_width=True)

# ========================================
# TIMELINE ANALYSIS
# ========================================
elif report_type == "Timeline Analysis":
    st.markdown("## 📅 Timeline Analysis")
    st.markdown(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    # Projects with dates
    df['project_start_date'] = pd.to_datetime(df['project_start_date'], errors='coerce')
    df['project_complete_date'] = pd.to_datetime(df['project_complete_date'], errors='coerce')
    
    has_dates = df[df['project_start_date'].notna() | df['project_complete_date'].notna()]
    
    if len(has_dates) == 0:
        st.warning("No timeline data available. Add start/complete dates to projects.")
    else:
        st.markdown(f"### Projects with Timeline Data: {len(has_dates)} of {len(df)}")
        
        # Duration Analysis
        has_both_dates = df[df['project_start_date'].notna() & df['project_complete_date'].notna()]
        
        if len(has_both_dates) > 0:
            has_both_dates['duration_days'] = (
                has_both_dates['project_complete_date'] - has_both_dates['project_start_date']
            ).dt.days
            
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_duration = has_both_dates['duration_days'].mean()
                st.metric("Avg Duration", f"{avg_duration:.0f} days")
            with col2:
                min_duration = has_both_dates['duration_days'].min()
                st.metric("Min Duration", f"{min_duration:.0f} days")
            with col3:
                max_duration = has_both_dates['duration_days'].max()
                st.metric("Max Duration", f"{max_duration:.0f} days")
            
            # Duration Distribution
            fig = px.histogram(
                has_both_dates,
                x='duration_days',
                nbins=20,
                title="Project Duration Distribution",
                labels={'duration_days': 'Duration (days)'},
                color_discrete_sequence=['#EE0000']
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Gantt-style Timeline
            st.markdown("### Project Timeline")
            timeline_data = has_both_dates.nlargest(20, 'project_start_date')[
                ['name', 'project_start_date', 'project_complete_date', 'status']
            ].copy()
            
            if len(timeline_data) > 0:
                fig = px.timeline(
                    timeline_data,
                    x_start='project_start_date',
                    x_end='project_complete_date',
                    y='name',
                    color='status',
                    title="Recent Projects Timeline",
                    color_discrete_map={
                        'Active': '#4CAF50',
                        'Completed': '#2196F3',
                        'On Hold': '#FF9800',
                        'Cancelled': '#F44336'
                    }
                )
                fig.update_yaxes(categoryorder='total ascending')
                st.plotly_chart(fig, use_container_width=True)

# ========================================
# PROGRAM PERFORMANCE
# ========================================
elif report_type == "Program Performance":
    st.markdown("## 🎯 Program Performance")
    st.markdown(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    if 'program_name' not in df.columns or df['program_name'].isna().all():
        st.warning("No program data available. Assign projects to programs to see this report.")
    else:
        programs = df[df['program_name'].notna()]
        
        # Program Summary
        program_summary = programs.groupby('program_name').agg({
            'project_id': 'count',
            'status': lambda x: (x == 'Active').sum()
        }).rename(columns={'project_id': 'Total Projects', 'status': 'Active Projects'})
        
        program_summary['Completed'] = programs.groupby('program_name')['status'].apply(
            lambda x: (x == 'Completed').sum()
        )
        program_summary['Completion %'] = (
            program_summary['Completed'] / program_summary['Total Projects'] * 100
        ).round(1)
        
        st.markdown("### Program Overview")
        st.dataframe(program_summary, use_container_width=True)
        
        # Program Comparison Chart
        st.markdown("### Program Comparison")
        fig = go.Figure()
        
        for program in program_summary.index:
            program_data = programs[programs['program_name'] == program]
            status_counts = program_data['status'].value_counts()
            
            fig.add_trace(go.Bar(
                name=program,
                x=status_counts.index,
                y=status_counts.values,
            ))
        
        fig.update_layout(
            barmode='group',
            title="Projects by Program and Status",
            xaxis_title="Status",
            yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Program Breakdown
        st.markdown("### Program Details")
        selected_program = st.selectbox("Select Program", programs['program_name'].unique())
        
        program_projects = programs[programs['program_name'] == selected_program]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Projects", len(program_projects))
        with col2:
            active = len(program_projects[program_projects['status'] == 'Active'])
            st.metric("Active", active)
        with col3:
            completed = len(program_projects[program_projects['status'] == 'Completed'])
            st.metric("Completed", completed)
        
        st.dataframe(
            program_projects[['name', 'ccr_nfid', 'status', 'pm_name', 'phase']],
            hide_index=True,
            use_container_width=True
        )

# === EXPORT OPTIONS ===
st.markdown("---")
st.markdown("### 📥 Export Report")

col_e1, col_e2, col_e3 = st.columns([2, 1, 2])

with col_e2:
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Data (CSV)",
        data=csv_data,
        file_name=f"vtrack_report_{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
