import webview
import threading
from api import create_app
from utils.window_manager import WindowManager
from utils.updater import check_for_updates
from core.config_manager import ConfigManager
import uvicorn

class PMTrackerApp:
    def __init__(self):
        self.window = None
        self.api = None
        self.config = ConfigManager()

    def start_backend(self):
        """Start FastAPI in background thread"""
        app = create_app()
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="error",
            access_log=False
        )

    def run(self):
        """Main application entry point"""
        # Check for updates
        update_available = check_for_updates()

        # Start FastAPI in background thread
        backend_thread = threading.Thread(target=self.start_backend, daemon=True)
        backend_thread.start()

        # Create JavaScript API
        self.api = WindowManager()

        # Create PyWebView window
        self.window = webview.create_window(
            'PM Project Tracker',
            'http://127.0.0.1:8000',
            width=1400,
            height=900,
            resizable=True,
            fullscreen=False,
            min_size=(1024, 768),
            confirm_close=True,
            js_api=self.api
        )

        # Start PyWebView
        webview.start(debug=False, http_server=False)

if __name__ == '__main__':
    app = PMTrackerApp()
    app.run()
