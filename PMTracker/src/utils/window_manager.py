import webview
import subprocess
import os
from typing import Dict, Any

class WindowManager:
    """JavaScript API bridge for PyWebView"""

    def __init__(self):
        self.window = None

    def set_window(self, window):
        """Set the window reference"""
        self.window = window

    def minimize(self):
        """Minimize the window"""
        if self.window:
            self.window.minimize()

    def maximize(self):
        """Maximize the window"""
        if self.window:
            self.window.toggle_fullscreen()

    def close(self):
        """Close the window"""
        if self.window:
            self.window.destroy()

    def open_url(self, url: str):
        """Open URL in default browser"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(url)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.run(['xdg-open', url])
        except Exception as e:
            print(f"Error opening URL: {e}")

    def show_notification(self, title: str, message: str):
        """Show desktop notification"""
        try:
            if os.name == 'nt':  # Windows
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5, threaded=True)
        except Exception as e:
            print(f"Error showing notification: {e}")

    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False

    def get_from_clipboard(self) -> str:
        """Get text from clipboard"""
        try:
            import pyperclip
            return pyperclip.paste()
        except Exception as e:
            print(f"Error getting from clipboard: {e}")
            return ''

    def open_file_dialog(self, dialog_type: str = 'open', file_types: tuple = ()) -> str:
        """Open file dialog"""
        try:
            if dialog_type == 'open':
                result = self.window.create_file_dialog(
                    webview.OPEN_DIALOG,
                    file_types=file_types
                )
            elif dialog_type == 'save':
                result = self.window.create_file_dialog(
                    webview.SAVE_DIALOG,
                    file_types=file_types
                )
            elif dialog_type == 'folder':
                result = self.window.create_file_dialog(
                    webview.FOLDER_DIALOG
                )
            return result[0] if result else ''
        except Exception as e:
            print(f"Error opening file dialog: {e}")
            return ''

    def show_alert(self, message: str):
        """Show alert dialog"""
        try:
            if self.window:
                self.window.evaluate_js(f'alert("{message}")')
        except Exception as e:
            print(f"Error showing alert: {e}")

    def confirm(self, message: str) -> bool:
        """Show confirmation dialog"""
        try:
            if self.window:
                result = self.window.evaluate_js(f'confirm("{message}")')
                return result
            return False
        except Exception as e:
            print(f"Error showing confirmation: {e}")
            return False

    def get_app_path(self) -> str:
        """Get application path"""
        return os.path.dirname(os.path.abspath(__file__))

    def get_user_data_path(self) -> str:
        """Get user data directory path"""
        from pathlib import Path
        return str(Path.home() / 'PMTracker')
