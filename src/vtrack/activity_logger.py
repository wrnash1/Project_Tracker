"""
Activity Logger for Verizon Tracker
Logs user activities for timeline and audit purposes
"""

from datetime import datetime
from typing import Optional
from .database import MasterProjectsDB
import streamlit as st


class ActivityLogger:
    """Log user activities to database"""

    @staticmethod
    def log_activity(activity_type: str, description: str, project_id: Optional[int] = None):
        """
        Log a user activity

        Args:
            activity_type: Type of activity (e.g., 'login', 'create_project', 'sync', etc.)
            description: Human-readable description
            project_id: Optional related project ID
        """
        try:
            # Get user_id from session state
            if not hasattr(st.session_state, 'user_id'):
                return  # No user logged in

            user_id = st.session_state.user_id

            # Log to database
            db = MasterProjectsDB()
            db.connect()

            db.execute("""
                INSERT INTO user_activity (user_id, activity_type, activity_description, related_project_id)
                VALUES (?, ?, ?, ?)
            """, (user_id, activity_type, description, project_id))

            db.close()

        except Exception as e:
            # Silent fail - don't disrupt user experience
            pass

    @staticmethod
    def get_recent_activities(user_id: int, limit: int = 10):
        """
        Get recent activities for a user

        Args:
            user_id: User ID to fetch activities for
            limit: Maximum number of activities to return

        Returns:
            List of activity records
        """
        try:
            db = MasterProjectsDB()
            db.connect()

            activities = db.fetchall("""
                SELECT
                    ua.activity_id,
                    ua.activity_type,
                    ua.activity_description,
                    ua.related_project_id,
                    ua.created_at,
                    p.name as project_name
                FROM user_activity ua
                LEFT JOIN projects p ON ua.related_project_id = p.project_id
                WHERE ua.user_id = ?
                ORDER BY ua.created_at DESC
                LIMIT ?
            """, (user_id, limit))

            db.close()

            return activities

        except Exception as e:
            return []

    @staticmethod
    def get_team_activities(limit: int = 20):
        """
        Get recent activities for entire team (admin view)

        Args:
            limit: Maximum number of activities to return

        Returns:
            List of activity records with user info
        """
        try:
            from .database import MasterUsersDB

            projects_db = MasterProjectsDB()
            projects_db.connect()

            users_db = MasterUsersDB()
            users_db.connect()

            # Get activities with user and project names
            activities = projects_db.fetchall("""
                SELECT
                    ua.activity_id,
                    ua.user_id,
                    ua.activity_type,
                    ua.activity_description,
                    ua.related_project_id,
                    ua.created_at,
                    p.name as project_name
                FROM user_activity ua
                LEFT JOIN projects p ON ua.related_project_id = p.project_id
                ORDER BY ua.created_at DESC
                LIMIT ?
            """, (limit,))

            # Enrich with user names
            result = []
            for activity in activities:
                user = users_db.fetchone("SELECT full_name FROM users WHERE user_id = ?", (activity['user_id'],))
                activity_dict = dict(activity)
                activity_dict['user_name'] = user['full_name'] if user else 'Unknown User'
                result.append(activity_dict)

            projects_db.close()
            users_db.close()

            return result

        except Exception as e:
            return []


# Convenience functions for common activities
def log_login():
    """Log user login"""
    ActivityLogger.log_activity('login', f"{st.session_state.full_name} logged in")


def log_logout():
    """Log user logout"""
    ActivityLogger.log_activity('logout', f"{st.session_state.full_name} logged out")


def log_project_created(project_name: str, project_id: int):
    """Log project creation"""
    ActivityLogger.log_activity('create_project', f"Created project: {project_name}", project_id)


def log_project_updated(project_name: str, project_id: int):
    """Log project update"""
    ActivityLogger.log_activity('update_project', f"Updated project: {project_name}", project_id)


def log_sync(items_synced: int):
    """Log data sync"""
    ActivityLogger.log_activity('sync', f"Synced {items_synced} items to master database")


def log_kpi_snapshot(project_name: str, project_id: int):
    """Log KPI snapshot"""
    ActivityLogger.log_activity('kpi_snapshot', f"Created KPI snapshot for: {project_name}", project_id)


def log_import(items_imported: int):
    """Log data import"""
    ActivityLogger.log_activity('import', f"Imported {items_imported} projects from file")


def log_export(export_type: str):
    """Log data export"""
    ActivityLogger.log_activity('export', f"Exported data as {export_type}")
