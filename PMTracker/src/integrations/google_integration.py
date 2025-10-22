import pyperclip
import webbrowser
from typing import Dict
from datetime import datetime

class GoogleIntegration:
    """Integration with Google Workspace (Drive, Sheets, Calendar) via clipboard"""

    def __init__(self):
        self.drive_url = "https://drive.google.com"
        self.sheets_url = "https://sheets.google.com"
        self.calendar_url = "https://calendar.google.com"
        self.docs_url = "https://docs.google.com"

    def create_project_folder(self, project_name: str) -> bool:
        """Create a Google Drive folder for project"""
        try:
            # Copy project name to clipboard
            pyperclip.copy(project_name)

            # Open Google Drive
            webbrowser.open(f"{self.drive_url}/drive/my-drive")

            return True
        except Exception as e:
            print(f"Failed to create Drive folder: {e}")
            return False

    def export_to_sheets(self, data: Dict, sheet_title: str) -> bool:
        """Export data to Google Sheets (via clipboard)"""
        try:
            # Format data as TSV for easy paste into Sheets
            tsv_data = self._dict_to_tsv(data)

            # Copy to clipboard
            pyperclip.copy(tsv_data)

            # Open Google Sheets
            webbrowser.open(f"{self.sheets_url}/create")

            return True
        except Exception as e:
            print(f"Failed to export to Sheets: {e}")
            return False

    def _dict_to_tsv(self, data: Dict) -> str:
        """Convert dictionary to TSV format"""
        lines = []

        # Headers
        if isinstance(data, dict) and 'headers' in data and 'rows' in data:
            lines.append('\t'.join(data['headers']))
            for row in data['rows']:
                lines.append('\t'.join([str(v) for v in row]))
        else:
            # Simple key-value pairs
            for key, value in data.items():
                lines.append(f"{key}\t{value}")

        return '\n'.join(lines)

    def create_calendar_event(self, title: str, start_date: str, end_date: str, description: str = '') -> bool:
        """Create a Google Calendar event"""
        try:
            event_details = f"""
Title: {title}
Start: {start_date}
End: {end_date}
Description: {description}
            """.strip()

            # Copy event details to clipboard
            pyperclip.copy(event_details)

            # Open Google Calendar
            webbrowser.open(f"{self.calendar_url}/render")

            return True
        except Exception as e:
            print(f"Failed to create calendar event: {e}")
            return False

    def create_project_doc(self, project_data: Dict) -> bool:
        """Create a Google Doc for project"""
        try:
            doc_content = f"""
Project: {project_data.get('PROJECT_NAME', 'N/A')}
Project Number: {project_data.get('PROJECT_NUMBER', 'N/A')}
PM: {project_data.get('PM_NAME', 'N/A')}
Status: {project_data.get('PROJECT_STATUS', 'N/A')}
Budget: ${project_data.get('BUDGET', 0):,.2f}
Start Date: {project_data.get('START_DATE', 'N/A')}
End Date: {project_data.get('END_DATE', 'N/A')}

=== Project Overview ===


=== Key Milestones ===


=== Risks and Issues ===


=== Action Items ===

            """.strip()

            # Copy doc content to clipboard
            pyperclip.copy(doc_content)

            # Open Google Docs
            webbrowser.open(f"{self.docs_url}/create")

            return True
        except Exception as e:
            print(f"Failed to create project doc: {e}")
            return False

    def share_project_report(self, report_data: Dict) -> bool:
        """Share project report via Google Sheets"""
        try:
            # Format report data
            formatted_data = {
                'headers': ['Metric', 'Value'],
                'rows': [[k, v] for k, v in report_data.items()]
            }

            return self.export_to_sheets(formatted_data, 'Project Report')
        except Exception as e:
            print(f"Failed to share project report: {e}")
            return False
