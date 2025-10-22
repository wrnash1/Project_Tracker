import pyperclip
import webbrowser
from typing import Dict

class SlackIntegration:
    """Integration with Slack via clipboard and browser automation"""

    def __init__(self):
        self.slack_workspace_url = "https://verizon.slack.com"

    def send_message(self, channel: str, message: str) -> bool:
        """Send a message to Slack channel (via clipboard)"""
        try:
            # Copy message to clipboard
            pyperclip.copy(message)

            # Open Slack channel in browser
            channel_url = f"{self.slack_workspace_url}/channels/{channel}"
            webbrowser.open(channel_url)

            return True
        except Exception as e:
            print(f"Slack integration error: {e}")
            return False

    def share_project_update(self, project_data: Dict, channel: str = "project-updates") -> bool:
        """Share project update to Slack"""
        try:
            message = self._format_project_update(project_data)
            return self.send_message(channel, message)
        except Exception as e:
            print(f"Failed to share project update: {e}")
            return False

    def _format_project_update(self, project_data: Dict) -> str:
        """Format project data for Slack message"""
        return f"""
Project Update: {project_data.get('PROJECT_NAME', 'N/A')}

Project Number: {project_data.get('PROJECT_NUMBER', 'N/A')}
Status: {project_data.get('PROJECT_STATUS', 'N/A')}
PM: {project_data.get('PM_NAME', 'N/A')}
Budget: ${project_data.get('BUDGET', 0):,.2f}
        """.strip()

    def notify_delay_prediction(self, project_number: str, delay_days: int, risk_level: str) -> bool:
        """Notify about ML delay prediction"""
        try:
            message = f"""
ML Prediction Alert - Project {project_number}

Predicted Delay: {delay_days} days
Risk Level: {risk_level}

Please review the project timeline.
            """.strip()

            return self.send_message("project-alerts", message)
        except Exception as e:
            print(f"Failed to send delay notification: {e}")
            return False
