import pyperclip
import webbrowser
from typing import Dict, List

class WebexIntegration:
    """Integration with Webex via clipboard and browser automation"""

    def __init__(self):
        self.webex_url = "https://web.webex.com"

    def send_message(self, recipient: str, message: str) -> bool:
        """Send a message via Webex (via clipboard)"""
        try:
            # Copy message to clipboard
            pyperclip.copy(message)

            # Open Webex in browser
            webbrowser.open(self.webex_url)

            return True
        except Exception as e:
            print(f"Webex integration error: {e}")
            return False

    def schedule_meeting(self, topic: str, participants: List[str], duration: int = 60) -> bool:
        """Schedule a Webex meeting (opens Webex scheduler)"""
        try:
            meeting_details = f"""
Meeting Topic: {topic}
Participants: {', '.join(participants)}
Duration: {duration} minutes
            """.strip()

            # Copy meeting details to clipboard
            pyperclip.copy(meeting_details)

            # Open Webex scheduler
            scheduler_url = f"{self.webex_url}/schedule"
            webbrowser.open(scheduler_url)

            return True
        except Exception as e:
            print(f"Failed to schedule meeting: {e}")
            return False

    def notify_project_milestone(self, project_data: Dict, milestone: str) -> bool:
        """Send project milestone notification"""
        try:
            message = f"""
Project Milestone Reached

Project: {project_data.get('PROJECT_NAME', 'N/A')}
Project Number: {project_data.get('PROJECT_NUMBER', 'N/A')}
Milestone: {milestone}
PM: {project_data.get('PM_NAME', 'N/A')}
            """.strip()

            return self.send_message(project_data.get('PM_EMAIL', ''), message)
        except Exception as e:
            print(f"Failed to send milestone notification: {e}")
            return False

    def create_project_space(self, project_name: str, team_members: List[str]) -> bool:
        """Create a Webex space for project (opens Webex)"""
        try:
            space_info = f"""
Space Name: {project_name}
Members: {', '.join(team_members)}
            """.strip()

            pyperclip.copy(space_info)
            webbrowser.open(f"{self.webex_url}/spaces")

            return True
        except Exception as e:
            print(f"Failed to create project space: {e}")
            return False
