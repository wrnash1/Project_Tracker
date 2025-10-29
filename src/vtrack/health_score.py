"""
Project Health Score Calculator for Verizon Tracker
Calculates health scores based on multiple factors
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from .database import MasterProjectsDB, LocalProjectsDB
import streamlit as st


class HealthScoreCalculator:
    """Calculate project health scores"""

    @staticmethod
    def calculate_project_health(project: Dict) -> Dict:
        """
        Calculate comprehensive health score for a project

        Factors:
        - Schedule adherence (30%)
        - KPI freshness (20%)
        - Status (20%)
        - Budget (if available) (15%)
        - Dependency resolution (15%)

        Args:
            project: Project dictionary

        Returns:
            Dictionary with score, grade, and breakdown
        """
        scores = {
            'schedule': 0,
            'kpi_freshness': 0,
            'status': 0,
            'budget': 0,
            'dependencies': 0
        }
        weights = {
            'schedule': 0.30,
            'kpi_freshness': 0.20,
            'status': 0.20,
            'budget': 0.15,
            'dependencies': 0.15
        }

        # Schedule Score
        scores['schedule'] = HealthScoreCalculator._calculate_schedule_score(project)

        # KPI Freshness Score
        scores['kpi_freshness'] = HealthScoreCalculator._calculate_kpi_freshness_score(project)

        # Status Score
        scores['status'] = HealthScoreCalculator._calculate_status_score(project)

        # Budget Score (default to 100 if no data)
        scores['budget'] = 100

        # Dependency Score (default to 100 if no data)
        scores['dependencies'] = 100

        # Calculate weighted average
        total_score = sum(scores[k] * weights[k] for k in scores.keys())

        # Determine grade
        if total_score >= 90:
            grade = 'A'
            color = '#4CAF50'
            status_text = 'Excellent'
        elif total_score >= 80:
            grade = 'B'
            color = '#8BC34A'
            status_text = 'Good'
        elif total_score >= 70:
            grade = 'C'
            color = '#FFC107'
            status_text = 'Fair'
        elif total_score >= 60:
            grade = 'D'
            color = '#FF9800'
            status_text = 'Needs Attention'
        else:
            grade = 'F'
            color = '#F44336'
            status_text = 'Critical'

        return {
            'total_score': round(total_score, 1),
            'grade': grade,
            'color': color,
            'status_text': status_text,
            'breakdown': scores,
            'weights': weights
        }

    @staticmethod
    def _calculate_schedule_score(project: Dict) -> float:
        """Calculate score based on schedule adherence"""
        try:
            # If no completion date set, return 70 (neutral)
            if not project.get('project_complete_date'):
                return 70.0

            complete_date = datetime.strptime(project['project_complete_date'], '%Y-%m-%d')
            today = datetime.now()

            # If completed
            if project.get('status') == 'Completed':
                return 100.0

            # If overdue
            if complete_date < today and project.get('status') == 'Active':
                days_overdue = (today - complete_date).days
                # Lose 5 points per day overdue, minimum 0
                return max(0, 100 - (days_overdue * 5))

            # If on track
            if complete_date >= today:
                return 100.0

            return 70.0
        except:
            return 70.0

    @staticmethod
    def _calculate_kpi_freshness_score(project: Dict) -> float:
        """Calculate score based on KPI data freshness"""
        try:
            # Check last KPI snapshot date
            project_id = project.get('project_id')
            if not project_id:
                return 50.0

            # Try to get latest KPI
            # This is a simplified version - in production would query database
            # For now, return default score
            return 70.0
        except:
            return 50.0

    @staticmethod
    def _calculate_status_score(project: Dict) -> float:
        """Calculate score based on project status"""
        status = project.get('status', '')

        status_scores = {
            'Active': 100.0,
            'On Hold': 60.0,
            'Completed': 100.0,
            'Cancelled': 0.0
        }

        return status_scores.get(status, 70.0)

    @staticmethod
    def get_health_badge_html(health_data: Dict) -> str:
        """Generate HTML for health badge"""
        return f"""
        <div style="
            display: inline-block;
            background: {health_data['color']};
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.9rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        ">
            {health_data['grade']} - {health_data['total_score']}
        </div>
        """

    @staticmethod
    def get_health_indicator_html(health_data: Dict, size: str = 'normal') -> str:
        """Generate HTML for health indicator with tooltip"""

        if size == 'small':
            width = '40px'
            height = '40px'
            font_size = '1rem'
        else:
            width = '60px'
            height = '60px'
            font_size = '1.5rem'

        return f"""
        <div style="
            width: {width};
            height: {height};
            background: linear-gradient(135deg, {health_data['color']} 0%, {health_data['color']}cc 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: {font_size};
            box-shadow: 0 3px 6px rgba(0,0,0,0.2);
            cursor: help;
        " title="{health_data['status_text']} - Score: {health_data['total_score']}">
            {health_data['grade']}
        </div>
        """

    @staticmethod
    def show_health_breakdown(health_data: Dict):
        """Display detailed health score breakdown"""
        st.markdown(f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                    <h3 style="margin: 0;">Project Health Score</h3>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        {HealthScoreCalculator.get_health_indicator_html(health_data, 'normal')}
                        <div>
                            <div style="font-size: 2rem; font-weight: 700; color: {health_data['color']};">
                                {health_data['total_score']}
                            </div>
                            <div style="color: #666; font-size: 0.9rem;">
                                {health_data['status_text']}
                            </div>
                        </div>
                    </div>
                </div>

                <div style="margin-top: 1.5rem;">
                    <h4 style="font-size: 0.95rem; color: #333; margin-bottom: 1rem;">Score Breakdown</h4>
        """, unsafe_allow_html=True)

        # Show breakdown bars
        for key, score in health_data['breakdown'].items():
            weight = health_data['weights'][key]
            weighted_contribution = score * weight

            # Color based on score
            if score >= 80:
                bar_color = '#4CAF50'
            elif score >= 60:
                bar_color = '#FFC107'
            else:
                bar_color = '#F44336'

            label = key.replace('_', ' ').title()

            st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <span style="font-size: 0.85rem; font-weight: 600; color: #555;">
                            {label} <span style="color: #999;">({weight*100:.0f}% weight)</span>
                        </span>
                        <span style="font-size: 0.85rem; font-weight: 700; color: {bar_color};">
                            {score:.0f}/100
                        </span>
                    </div>
                    <div style="
                        background: #E0E0E0;
                        border-radius: 10px;
                        height: 8px;
                        overflow: hidden;
                    ">
                        <div style="
                            background: {bar_color};
                            width: {score}%;
                            height: 100%;
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)


def show_project_health_widget(project: Dict):
    """Display compact health widget for a project"""
    health = HealthScoreCalculator.calculate_project_health(project)

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown(HealthScoreCalculator.get_health_indicator_html(health), unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div>
                <div style="font-size: 1.2rem; font-weight: 700; color: {health['color']};">
                    {health['status_text']}
                </div>
                <div style="color: #666; font-size: 0.85rem;">
                    Health Score: {health['total_score']}/100
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Show details in expander
    with st.expander("📊 View Detailed Breakdown"):
        HealthScoreCalculator.show_health_breakdown(health)
