"""
Notifications System for Verizon Tracker
Provides notification badges and alerts for users
"""

from typing import Dict, List
from .database import LocalProjectsDB, MasterProjectsDB
import streamlit as st


class NotificationCenter:
    """Manage user notifications"""

    @staticmethod
    def get_notification_counts(user_id: int, role: str) -> Dict[str, int]:
        """
        Get notification counts for a user

        Returns:
            Dictionary with notification types and counts
        """
        notifications = {
            'pending_sync': 0,
            'stale_kpis': 0,
            'overdue_projects': 0,
            'team_syncs': 0,
            'total': 0
        }

        try:
            if role == "Sr. Project Manager":
                # Check pending syncs
                local_db = LocalProjectsDB(user_id)
                local_db.connect()

                pending = local_db.fetchone(
                    "SELECT COUNT(*) as count FROM projects WHERE sync_status IN ('new', 'updated')",
                    ()
                )
                notifications['pending_sync'] = pending['count'] if pending else 0

                # Check stale KPIs (projects without KPI snapshot in last 30 days)
                from datetime import datetime, timedelta
                thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

                stale = local_db.fetchone(f"""
                    SELECT COUNT(DISTINCT p.project_id) as count
                    FROM projects p
                    LEFT JOIN kpi_snapshots k ON p.project_id = k.project_id
                        AND k.snapshot_date >= '{thirty_days_ago}'
                    WHERE p.pm_id = ? AND p.status = 'Active'
                        AND k.snapshot_id IS NULL
                """, (user_id,))
                notifications['stale_kpis'] = stale['count'] if stale else 0

                local_db.close()

            elif role in ["Associate Director", "Director"]:
                # Check team syncs waiting to be processed
                from pathlib import Path
                from .database import SYNC_INBOX

                try:
                    sync_files = list(SYNC_INBOX.glob("*.json"))
                    notifications['team_syncs'] = len(sync_files)
                except:
                    notifications['team_syncs'] = 0

                # Check overdue projects
                master_db = MasterProjectsDB()
                master_db.connect()

                from datetime import datetime
                today = datetime.now().strftime('%Y-%m-%d')

                overdue = master_db.fetchone(f"""
                    SELECT COUNT(*) as count
                    FROM projects
                    WHERE project_complete_date < '{today}'
                        AND status = 'Active'
                """, ())
                notifications['overdue_projects'] = overdue['count'] if overdue else 0

                master_db.close()

            # Calculate total
            notifications['total'] = sum([
                notifications['pending_sync'],
                notifications['stale_kpis'],
                notifications['overdue_projects'],
                notifications['team_syncs']
            ])

        except Exception as e:
            pass

        return notifications

    @staticmethod
    def get_notification_messages(user_id: int, role: str) -> List[Dict]:
        """
        Get detailed notification messages

        Returns:
            List of notification dictionaries
        """
        messages = []
        counts = NotificationCenter.get_notification_counts(user_id, role)

        try:
            if counts['pending_sync'] > 0:
                messages.append({
                    'type': 'warning',
                    'icon': '🔄',
                    'title': 'Pending Sync',
                    'message': f"{counts['pending_sync']} items waiting to sync",
                    'action': 'Go to Sync Data',
                    'action_page': 'pages/3_Sync_Data.py'
                })

            if counts['stale_kpis'] > 0:
                messages.append({
                    'type': 'info',
                    'icon': '📊',
                    'title': 'KPI Update Needed',
                    'message': f"{counts['stale_kpis']} projects need KPI snapshot",
                    'action': 'Go to My Dashboard',
                    'action_page': 'pages/1_My_Dashboard.py'
                })

            if counts['overdue_projects'] > 0:
                messages.append({
                    'type': 'error',
                    'icon': '⚠️',
                    'title': 'Overdue Projects',
                    'message': f"{counts['overdue_projects']} active projects are overdue",
                    'action': 'View Projects',
                    'action_page': 'pages/9_All_Projects.py'
                })

            if counts['team_syncs'] > 0:
                messages.append({
                    'type': 'info',
                    'icon': '📥',
                    'title': 'Team Syncs Pending',
                    'message': f"{counts['team_syncs']} sync files to process",
                    'action': 'Process Syncs',
                    'action_page': 'pages/6_Process_Sync_Inbox.py'
                })

        except Exception as e:
            pass

        return messages


def show_notification_badge(count: int) -> str:
    """
    Generate HTML for notification badge

    Args:
        count: Number of notifications

    Returns:
        HTML string for badge
    """
    if count == 0:
        return ""

    return f"""
        <span style="
            background: #EE0000;
            color: white;
            border-radius: 10px;
            padding: 0.15rem 0.5rem;
            font-size: 0.75rem;
            font-weight: 700;
            margin-left: 0.5rem;
        ">{count}</span>
    """


def show_notification_panel():
    """Display notification panel in sidebar"""
    if not hasattr(st.session_state, 'user_id'):
        return

    notifications = NotificationCenter.get_notification_counts(
        st.session_state.user_id,
        st.session_state.role
    )

    if notifications['total'] > 0:
        st.markdown(f"""
            <div style="
                background: rgba(238, 0, 0, 0.1);
                border-left: 4px solid #EE0000;
                padding: 0.75rem;
                margin: 1rem 0;
                border-radius: 4px;
            ">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <span style="font-weight: 600; color: white;">
                        🔔 Notifications
                    </span>
                    <span style="
                        background: #EE0000;
                        color: white;
                        border-radius: 50%;
                        width: 24px;
                        height: 24px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 0.85rem;
                        font-weight: 700;
                    ">{notifications['total']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Show detailed notifications
        messages = NotificationCenter.get_notification_messages(
            st.session_state.user_id,
            st.session_state.role
        )

        for msg in messages:
            st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    padding: 0.5rem;
                    margin: 0.5rem 0;
                    border-radius: 4px;
                    font-size: 0.85rem;
                    color: white;
                ">
                    <div style="font-weight: 600;">{msg['icon']} {msg['title']}</div>
                    <div style="opacity: 0.9; margin-top: 0.25rem;">{msg['message']}</div>
                </div>
            """, unsafe_allow_html=True)
