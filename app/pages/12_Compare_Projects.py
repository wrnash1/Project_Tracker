"""
Project Comparison Tool
Compare multiple projects side-by-side
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vtrack import auth
from src.vtrack.database import MasterProjectsDB, LocalProjectsDB
from src.vtrack.health_score import HealthScoreCalculator
from app.styles import apply_verizon_theme

# Page config
st.set_page_config(
    page_title="Compare Projects - Verizon Tracker",
    page_icon="⚖️",
    layout="wide"
)

# Apply theme
apply_verizon_theme()

# Require authentication
auth.require_auth()

# Show sidebar
from app import sidebar
sidebar.show_sidebar()

# Main content
st.markdown("""
    <h1>⚖️ Compare Projects</h1>
    <div class="vz-title-accent"></div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="vz-card" style="margin-bottom: 2rem;">
        <p style="margin: 0;">
            Select up to 4 projects to compare side-by-side. View differences in budget, schedule, status, and health scores.
        </p>
    </div>
""", unsafe_allow_html=True)

# Get projects based on role
role = st.session_state.role

if role == "Sr. Project Manager":
    db = LocalProjectsDB(st.session_state.user_id)
    db.connect()
    all_projects = db.fetchall("SELECT * FROM projects WHERE pm_id = ? ORDER BY name", (st.session_state.user_id,))
    db.close()
else:
    db = MasterProjectsDB()
    db.connect()
    all_projects = db.fetchall("SELECT * FROM projects ORDER BY name", ())
    db.close()

if not all_projects:
    st.warning("No projects available to compare.")
    st.stop()

# Project selection
st.markdown("### 📌 Select Projects to Compare")

col1, col2, col3, col4 = st.columns(4)

# Create project options
project_options = {f"{p['name']} ({p['ccr_nfid']})": p for p in all_projects}
project_names = list(project_options.keys())

selected_projects = []

with col1:
    project1 = st.selectbox("Project 1*", options=[""] + project_names, key="proj1")
    if project1:
        selected_projects.append(project_options[project1])

with col2:
    project2 = st.selectbox("Project 2*", options=[""] + project_names, key="proj2")
    if project2:
        selected_projects.append(project_options[project2])

with col3:
    project3 = st.selectbox("Project 3 (optional)", options=[""] + project_names, key="proj3")
    if project3:
        selected_projects.append(project_options[project3])

with col4:
    project4 = st.selectbox("Project 4 (optional)", options=[""] + project_names, key="proj4")
    if project4:
        selected_projects.append(project_options[project4])

if len(selected_projects) < 2:
    st.info("Please select at least 2 projects to compare.")
    st.stop()

st.markdown("---")

# Comparison sections
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Budget & Schedule", "🏥 Health Scores", "📋 Detailed Fields"])

with tab1:
    st.markdown("## Project Overview Comparison")

    # Create comparison table
    comparison_data = []

    for proj in selected_projects:
        proj_dict = dict(proj)
        health = HealthScoreCalculator.calculate_project_health(proj_dict)

        comparison_data.append({
            'Project': proj_dict['name'],
            'CCR/NFID': proj_dict.get('ccr_nfid', 'N/A'),
            'Status': proj_dict['status'],
            'Customer': proj_dict.get('customer', 'N/A'),
            'Health Score': f"{health['total_score']} ({health['grade']})",
            'Start Date': proj_dict.get('project_start_date', 'N/A'),
            'Complete Date': proj_dict.get('project_complete_date', 'N/A')
        })

    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Visual comparison - Status
    st.markdown("### Status Comparison")

    status_colors = {
        'Active': '#4CAF50',
        'On Hold': '#FF9800',
        'Completed': '#2196F3',
        'Cancelled': '#F44336'
    }

    fig_status = go.Figure()

    for proj in selected_projects:
        proj_dict = dict(proj)
        status = proj_dict['status']
        color = status_colors.get(status, '#999')

        fig_status.add_trace(go.Bar(
            name=proj_dict['name'][:20],
            x=['Status'],
            y=[1],
            marker_color=color,
            text=status,
            textposition='inside'
        ))

    fig_status.update_layout(
        barmode='group',
        showlegend=True,
        height=300,
        yaxis=dict(showticklabels=False, title=None),
        xaxis=dict(title=None)
    )

    st.plotly_chart(fig_status, use_container_width=True)

with tab2:
    st.markdown("## Budget & Schedule Comparison")

    # Budget comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💰 Budget Amount")

        budget_data = []
        for proj in selected_projects:
            proj_dict = dict(proj)
            budget = proj_dict.get('budget_amount', 0) or 0
            budget_data.append({
                'Project': proj_dict['name'][:20],
                'Budget': budget
            })

        if any(b['Budget'] > 0 for b in budget_data):
            fig_budget = go.Figure()

            for data in budget_data:
                fig_budget.add_trace(go.Bar(
                    name=data['Project'],
                    x=[data['Project']],
                    y=[data['Budget']],
                    text=f"${data['Budget']:,.2f}" if data['Budget'] > 0 else "N/A",
                    textposition='auto'
                ))

            fig_budget.update_layout(
                showlegend=False,
                height=300,
                yaxis=dict(title="Budget ($)"),
                xaxis=dict(title=None)
            )

            st.plotly_chart(fig_budget, use_container_width=True)
        else:
            st.info("No budget data available for selected projects.")

    with col2:
        st.markdown("### 📅 Project Duration")

        duration_data = []
        for proj in selected_projects:
            proj_dict = dict(proj)

            start = proj_dict.get('project_start_date')
            end = proj_dict.get('project_complete_date')

            if start and end:
                from datetime import datetime
                try:
                    start_dt = datetime.strptime(start, '%Y-%m-%d')
                    end_dt = datetime.strptime(end, '%Y-%m-%d')
                    days = (end_dt - start_dt).days
                except:
                    days = 0
            else:
                days = 0

            duration_data.append({
                'Project': proj_dict['name'][:20],
                'Days': days
            })

        if any(d['Days'] > 0 for d in duration_data):
            fig_duration = go.Figure()

            for data in duration_data:
                fig_duration.add_trace(go.Bar(
                    name=data['Project'],
                    x=[data['Project']],
                    y=[data['Days']],
                    text=f"{data['Days']} days" if data['Days'] > 0 else "N/A",
                    textposition='auto',
                    marker_color='#2196F3'
                ))

            fig_duration.update_layout(
                showlegend=False,
                height=300,
                yaxis=dict(title="Duration (Days)"),
                xaxis=dict(title=None)
            )

            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("No schedule data available for selected projects.")

with tab3:
    st.markdown("## Health Score Comparison")

    # Calculate health for all projects
    health_scores = []
    for proj in selected_projects:
        proj_dict = dict(proj)
        health = HealthScoreCalculator.calculate_project_health(proj_dict)
        health_scores.append({
            'project': proj_dict,
            'health': health
        })

    # Display health scores
    cols = st.columns(len(selected_projects))

    for idx, (col, item) in enumerate(zip(cols, health_scores)):
        with col:
            st.markdown(f"### {item['project']['name'][:25]}")

            health = item['health']

            st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    {HealthScoreCalculator.get_health_indicator_html(health, 'normal')}
                    <div style="margin-top: 1rem; font-size: 1.5rem; font-weight: 700; color: {health['color']};">
                        {health['total_score']}
                    </div>
                    <div style="color: #666; font-size: 0.9rem;">
                        {health['status_text']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Breakdown
            st.markdown("**Score Breakdown:**")
            for key, score in health['breakdown'].items():
                label = key.replace('_', ' ').title()
                st.markdown(f"- {label}: {score:.0f}/100")

    # Radar chart comparison
    st.markdown("---")
    st.markdown("### 🎯 Health Factors Radar Chart")

    fig_radar = go.Figure()

    categories = list(health_scores[0]['health']['breakdown'].keys())
    categories = [c.replace('_', ' ').title() for c in categories]

    for item in health_scores:
        values = list(item['health']['breakdown'].values())
        values.append(values[0])  # Close the radar

        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=item['project']['name'][:20]
        ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        height=500
    )

    st.plotly_chart(fig_radar, use_container_width=True)

with tab4:
    st.markdown("## Detailed Field Comparison")

    # Field categories
    field_categories = {
        'Basic Info': ['name', 'ccr_nfid', 'status', 'customer', 'pm_id'],
        'Location': ['clli', 'site_address', 'city', 'state', 'zip_code'],
        'Technical': ['system_type', 'circuit_type', 'circuit_id', 'bandwidth'],
        'Project Management': ['phase', 'current_queue', 'project_priority', 'wbs_code'],
        'Dates': ['project_start_date', 'project_complete_date', 'created_at', 'updated_at']
    }

    for category, fields in field_categories.items():
        with st.expander(f"📁 {category}", expanded=(category == 'Basic Info')):
            comparison_table = {}

            for field in fields:
                row_data = [field.replace('_', ' ').title()]

                for proj in selected_projects:
                    proj_dict = dict(proj)
                    value = proj_dict.get(field, 'N/A')
                    if value is None:
                        value = 'N/A'
                    row_data.append(str(value))

                comparison_table[field] = row_data

            # Create DataFrame
            columns = ['Field'] + [p['name'][:20] for p in [dict(proj) for proj in selected_projects]]
            rows = list(comparison_table.values())

            df_detail = pd.DataFrame(rows, columns=columns)
            st.dataframe(df_detail, use_container_width=True, hide_index=True)

# Export comparison
st.markdown("---")
st.markdown("### 📥 Export Comparison")

if st.button("📊 Export Comparison as CSV", use_container_width=False):
    # Create comprehensive comparison data
    export_data = []

    for proj in selected_projects:
        proj_dict = dict(proj)
        health = HealthScoreCalculator.calculate_project_health(proj_dict)

        export_row = {
            'Project Name': proj_dict['name'],
            'CCR/NFID': proj_dict.get('ccr_nfid', ''),
            'Status': proj_dict['status'],
            'Customer': proj_dict.get('customer', ''),
            'Health Score': health['total_score'],
            'Health Grade': health['grade'],
            'Start Date': proj_dict.get('project_start_date', ''),
            'Complete Date': proj_dict.get('project_complete_date', ''),
            'Budget': proj_dict.get('budget_amount', 0),
            'Phase': proj_dict.get('phase', ''),
            'Priority': proj_dict.get('project_priority', '')
        }

        export_data.append(export_row)

    df_export = pd.DataFrame(export_data)
    csv = df_export.to_csv(index=False)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"project_comparison_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
