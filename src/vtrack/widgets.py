"""
Dashboard Widgets for Verizon Tracker
Reusable visualization components
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
from .database import MasterProjectsDB, LocalProjectsDB
import streamlit as st
import pandas as pd


class DashboardWidgets:
    """Reusable dashboard widgets with visualizations"""

    @staticmethod
    def create_mini_donut_chart(value: int, total: int, title: str, color: str = "#EE0000") -> go.Figure:
        """
        Create a mini donut chart

        Args:
            value: Current value
            total: Total value
            title: Chart title
            color: Main color

        Returns:
            Plotly figure
        """
        percentage = (value / total * 100) if total > 0 else 0

        fig = go.Figure(data=[go.Pie(
            values=[value, total - value],
            hole=.7,
            marker_colors=[color, '#E0E0E0'],
            textinfo='none',
            hoverinfo='skip',
            showlegend=False
        )])

        fig.add_annotation(
            text=f"<b>{percentage:.0f}%</b>",
            x=0.5, y=0.5,
            font_size=20,
            showarrow=False
        )

        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0),
            height=150,
            title=dict(
                text=title,
                font=dict(size=12),
                x=0.5,
                xanchor='center'
            )
        )

        return fig

    @staticmethod
    def get_project_status_distribution(user_id: int, role: str) -> Dict:
        """Get project count by status"""
        try:
            if role == "Sr. Project Manager":
                db = LocalProjectsDB(user_id)
                db.connect()
                results = db.fetchall("""
                    SELECT status, COUNT(*) as count
                    FROM projects
                    WHERE pm_id = ?
                    GROUP BY status
                """, (user_id,))
                db.close()
            else:
                db = MasterProjectsDB()
                db.connect()
                results = db.fetchall("""
                    SELECT status, COUNT(*) as count
                    FROM projects
                    GROUP BY status
                """, ())
                db.close()

            return {row['status']: row['count'] for row in results}
        except:
            return {}

    @staticmethod
    def get_program_distribution(user_id: int, role: str) -> Dict:
        """Get project count by program"""
        try:
            if role == "Sr. Project Manager":
                db = LocalProjectsDB(user_id)
                db.connect()
                results = db.fetchall("""
                    SELECT
                        COALESCE(p.program_id, 0) as program_id,
                        COUNT(*) as count
                    FROM projects p
                    WHERE p.pm_id = ?
                    GROUP BY p.program_id
                    LIMIT 5
                """, (user_id,))
                db.close()
            else:
                db = MasterProjectsDB()
                db.connect()
                results = db.fetchall("""
                    SELECT
                        COALESCE(p.program_id, 0) as program_id,
                        COUNT(*) as count
                    FROM projects p
                    GROUP BY p.program_id
                    ORDER BY count DESC
                    LIMIT 5
                """, ())
                db.close()

            return {f"Program {row['program_id']}": row['count'] for row in results}
        except:
            return {}

    @staticmethod
    def create_status_mini_bar(status_dist: Dict) -> go.Figure:
        """Create horizontal mini bar chart for status distribution"""
        if not status_dist:
            return None

        colors = {
            'Active': '#4CAF50',
            'On Hold': '#FF9800',
            'Completed': '#2196F3',
            'Cancelled': '#F44336'
        }

        statuses = list(status_dist.keys())
        counts = list(status_dist.values())
        bar_colors = [colors.get(s, '#999') for s in statuses]

        fig = go.Figure(data=[
            go.Bar(
                y=statuses,
                x=counts,
                orientation='h',
                marker_color=bar_colors,
                text=counts,
                textposition='auto'
            )
        ])

        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0),
            height=150,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False),
            title=dict(
                text="Projects by Status",
                font=dict(size=12),
                x=0
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        return fig

    @staticmethod
    def get_kpi_trend_data(user_id: int, role: str, days: int = 90) -> pd.DataFrame:
        """Get KPI snapshot trend data"""
        try:
            from datetime import datetime, timedelta
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            if role == "Sr. Project Manager":
                db = LocalProjectsDB(user_id)
                db.connect()
                results = db.fetchall("""
                    SELECT
                        k.snapshot_date,
                        AVG(k.on_time_percent) as avg_ontime
                    FROM kpi_snapshots k
                    JOIN projects p ON k.project_id = p.project_id
                    WHERE p.pm_id = ? AND k.snapshot_date >= ?
                    GROUP BY k.snapshot_date
                    ORDER BY k.snapshot_date
                """, (user_id, start_date))
                db.close()
            else:
                db = MasterProjectsDB()
                db.connect()
                results = db.fetchall("""
                    SELECT
                        snapshot_date,
                        AVG(on_time_percent) as avg_ontime
                    FROM kpi_snapshots
                    WHERE snapshot_date >= ?
                    GROUP BY snapshot_date
                    ORDER BY snapshot_date
                """, (start_date,))
                db.close()

            if results:
                df = pd.DataFrame([dict(row) for row in results])
                return df
            return pd.DataFrame()
        except:
            return pd.DataFrame()

    @staticmethod
    def create_kpi_trend_chart(df: pd.DataFrame) -> go.Figure:
        """Create line chart for KPI trend"""
        if df.empty:
            return None

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['snapshot_date'],
            y=df['avg_ontime'],
            mode='lines+markers',
            line=dict(color='#EE0000', width=3),
            marker=dict(size=8, color='#EE0000'),
            fill='tozeroy',
            fillcolor='rgba(238, 0, 0, 0.1)'
        ))

        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0),
            height=150,
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(showgrid=True, gridcolor='#E0E0E0', title=None, range=[0, 100]),
            title=dict(
                text="On-Time Performance Trend",
                font=dict(size=12),
                x=0
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified'
        )

        return fig


def show_dashboard_widgets():
    """Display dashboard widgets on home page"""

    st.markdown("### 📊 Dashboard Insights")

    # Create three columns for widgets
    col1, col2, col3 = st.columns(3)

    user_id = st.session_state.user_id
    role = st.session_state.role

    with col1:
        # Status distribution widget
        status_dist = DashboardWidgets.get_project_status_distribution(user_id, role)
        if status_dist:
            st.markdown("""
                <div class="vz-card" style="padding: 1rem;">
            """, unsafe_allow_html=True)

            fig = DashboardWidgets.create_status_mini_bar(status_dist)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Active vs Total mini donut
        if status_dist:
            active_count = status_dist.get('Active', 0)
            total_count = sum(status_dist.values())

            st.markdown("""
                <div class="vz-card" style="padding: 1rem;">
            """, unsafe_allow_html=True)

            fig = DashboardWidgets.create_mini_donut_chart(
                active_count,
                total_count,
                "Active Projects",
                "#4CAF50"
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        # KPI trend widget
        kpi_df = DashboardWidgets.get_kpi_trend_data(user_id, role, days=90)
        if not kpi_df.empty:
            st.markdown("""
                <div class="vz-card" style="padding: 1rem;">
            """, unsafe_allow_html=True)

            fig = DashboardWidgets.create_kpi_trend_chart(kpi_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="vz-card" style="padding: 1rem; text-align: center;">
                    <p style="color: #999; margin: 3rem 0;">📊</p>
                    <p style="color: #666; font-size: 0.9rem;">No KPI data yet</p>
                </div>
            """, unsafe_allow_html=True)
