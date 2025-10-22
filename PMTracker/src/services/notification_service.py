from typing import List, Dict
from datetime import datetime
from core.sqlite_manager import SQLiteManager
from integrations.slack_integration import SlackIntegration
from integrations.webex_integration import WebexIntegration

class NotificationService:
    """Service for managing notifications and alerts"""

    def __init__(self):
        self.sqlite_mgr = SQLiteManager()
        self.slack = SlackIntegration()
        self.webex = WebexIntegration()

    def create_notification(self, notification_type: str, title: str, message: str,
                          recipients: List[str] = None, priority: str = 'medium') -> int:
        """Create a new notification"""
        try:
            with self.sqlite_mgr as db:
                # Create notifications table if not exists
                db.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        notification_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        priority TEXT DEFAULT 'medium',
                        recipients TEXT,
                        status TEXT DEFAULT 'pending',
                        sent_date TIMESTAMP,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                db.connection.commit()

                # Insert notification
                query = """
                    INSERT INTO notifications (notification_type, title, message, priority, recipients)
                    VALUES (?, ?, ?, ?, ?)
                """
                recipients_str = ','.join(recipients) if recipients else ''
                db.execute_update(query, (notification_type, title, message, priority, recipients_str))

                return db.cursor.lastrowid
        except Exception as e:
            print(f"Error creating notification: {e}")
            return 0

    def send_notification(self, notification_id: int, channel: str = 'slack') -> bool:
        """Send a notification via specified channel"""
        try:
            with self.sqlite_mgr as db:
                # Get notification
                result = db.execute_query(
                    "SELECT * FROM notifications WHERE id = ?",
                    (notification_id,)
                )

                if not result:
                    return False

                notification = result[0]
                message = f"{notification['title']}\n\n{notification['message']}"

                # Send via channel
                success = False
                if channel == 'slack':
                    success = self.slack.send_message('project-alerts', message)
                elif channel == 'webex':
                    recipients = notification['recipients'].split(',') if notification['recipients'] else []
                    if recipients:
                        success = self.webex.send_message(recipients[0], message)

                # Update status
                if success:
                    db.execute_update(
                        "UPDATE notifications SET status = 'sent', sent_date = CURRENT_TIMESTAMP WHERE id = ?",
                        (notification_id,)
                    )

                return success
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False

    def get_pending_notifications(self) -> List[Dict]:
        """Get all pending notifications"""
        try:
            with self.sqlite_mgr as db:
                return db.execute_query(
                    "SELECT * FROM notifications WHERE status = 'pending' ORDER BY priority DESC, created_date ASC"
                )
        except Exception as e:
            print(f"Error getting notifications: {e}")
            return []

    def notify_project_risk(self, project_number: str, risk_level: str, factors: Dict) -> bool:
        """Send notification for high-risk projects"""
        if risk_level not in ['High', 'Critical']:
            return False

        title = f"⚠️ {risk_level} Risk Alert: Project {project_number}"
        message = f"""
Project {project_number} has been classified as {risk_level} risk.

Contributing Factors:
{self._format_factors(factors)}

Immediate action recommended.
        """.strip()

        notification_id = self.create_notification(
            'risk_alert',
            title,
            message,
            priority='high' if risk_level == 'High' else 'critical'
        )

        return self.send_notification(notification_id, 'slack')

    def notify_delay_prediction(self, project_number: str, predicted_days: int, confidence: float) -> bool:
        """Send notification for predicted delays"""
        if predicted_days < 30:  # Only notify for significant delays
            return False

        title = f"📅 Delay Prediction: Project {project_number}"
        message = f"""
Project {project_number} is predicted to experience a delay of {predicted_days} days.

Confidence: {confidence * 100:.1f}%

Please review the project timeline and resource allocation.
        """.strip()

        notification_id = self.create_notification(
            'delay_alert',
            title,
            message,
            priority='medium'
        )

        return self.send_notification(notification_id, 'slack')

    def notify_budget_variance(self, project_number: str, variance: float, percentage: float) -> bool:
        """Send notification for budget issues"""
        if abs(percentage) < 10:  # Only notify for >10% variance
            return False

        if variance < 0:
            title = f"💰 Budget Overrun: Project {project_number}"
            message = f"Project is over budget by ${abs(variance):,.2f} ({abs(percentage):.1f}%)"
        else:
            title = f"💰 Budget Update: Project {project_number}"
            message = f"Project is under budget by ${variance:,.2f} ({percentage:.1f}%)"

        notification_id = self.create_notification(
            'budget_alert',
            title,
            message,
            priority='high' if variance < 0 else 'low'
        )

        return self.send_notification(notification_id, 'slack')

    def _format_factors(self, factors: Dict) -> str:
        """Format contributing factors for notification"""
        lines = []
        for key, value in factors.items():
            key_formatted = key.replace('_', ' ').title()
            if isinstance(value, float):
                value_formatted = f"{value * 100:.1f}%"
            else:
                value_formatted = str(value)
            lines.append(f"  • {key_formatted}: {value_formatted}")
        return '\n'.join(lines)

    def schedule_daily_digest(self, recipients: List[str]) -> bool:
        """Schedule daily project digest"""
        title = "📊 Daily Project Digest"
        message = "Daily summary of project status will be sent at 9 AM daily."

        notification_id = self.create_notification(
            'daily_digest',
            title,
            message,
            recipients=recipients,
            priority='low'
        )

        # In production, this would set up a scheduled task
        return notification_id > 0

    def get_notification_history(self, limit: int = 50) -> List[Dict]:
        """Get notification history"""
        try:
            with self.sqlite_mgr as db:
                return db.execute_query(
                    "SELECT * FROM notifications ORDER BY created_date DESC LIMIT ?",
                    (limit,)
                )
        except Exception as e:
            print(f"Error getting notification history: {e}")
            return []
