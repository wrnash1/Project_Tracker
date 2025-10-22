# PM Project Tracker - PyWebView Native Desktop Edition

A comprehensive project tracking application for Verizon Internal Systems, built with PyWebView for native desktop experience.

## Overview

PM Project Tracker is a desktop application that provides project managers with powerful tools to track, analyze, and manage Verizon network deployment projects. It integrates with Oracle databases, provides ML-powered predictions, and offers seamless integrations with Slack, Webex, and Google Workspace.

## Features

- **Dashboard**: Real-time project overview with customizable widgets
- **Project Management**: Track projects from Oracle GS database
- **Gantt Charts**: Visualize project timelines and dependencies
- **ML Predictions**: AI-powered delay prediction and risk classification
- **Reports**: Generate PDF and Excel reports
- **Task Management**: Create and track user tasks
- **Project Notes**: Collaborative notebook for project documentation
- **Integrations**: Slack, Webex, and Google Workspace integration
- **Text-to-Speech**: Accessibility features for report reading
- **Auto-updater**: Automatic updates from G: drive

## Technology Stack

### Backend
- Python 3.11+
- FastAPI 0.104+
- PyWebView 4.4+
- Oracle Database (oracledb 2.0+)
- SQLite (local data)
- TensorFlow/Keras (ML models)

### Frontend
- HTML5/CSS3
- Tailwind CSS
- JavaScript (ES6+)
- Chart.js
- DHTMLX Gantt
- GridStack.js

## Installation

### Prerequisites
- Python 3.11 or higher
- Oracle Client (for database connectivity)
- Windows 10/11 (recommended) or Linux

### Setup

1. **Clone or extract the project**:
   ```bash
   cd PMTracker
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure database connection**:
   - Run the application once to generate default config
   - Edit `%USERPROFILE%\PMTracker\config\config.ini`
   - Add Oracle database password (will be encrypted)

6. **Run the application**:
   ```bash
   python src/main.py
   ```

## Building Executable

### Windows
```bash
cd scripts
build.bat
```

### Linux/Mac
```bash
cd scripts
chmod +x build.sh
./build.sh
```

The executable will be created in `dist/PMTracker/`

## Configuration

Configuration file location: `%USERPROFILE%\PMTracker\config\config.ini`

### Database Settings
- `oracle_host`: Oracle database connection string
- `oracle_user`: Oracle username
- `oracle_password`: Encrypted password (use settings dialog)
- `sqlite_path`: Local SQLite database path

### Application Settings
- `theme`: light or dark
- `auto_save`: Enable auto-save (true/false)
- `tts_enabled`: Enable text-to-speech (true/false)
- `update_check`: Enable update checking (true/false)

### ML Settings
- `delay_model_path`: Path to delay predictor model
- `risk_model_path`: Path to risk classifier model
- `retrain_threshold_days`: Days before retraining (default: 90)

## Usage

### Dashboard
- View project statistics and recent projects
- Quick access to all major features
- Customizable widget layout

### Projects
- Search and filter projects from Oracle database
- View detailed project information
- Access CCRs and provisioning orders
- View project metrics and budget variance

### Gantt Chart
- Visualize project timeline
- Track CCRs and provisioning orders
- Identify critical path

### Reports
- Generate PDF or Excel reports
- Project summary reports
- CCR analysis reports
- Budget variance reports

### Tasks
- Create and manage user tasks
- Assign tasks to team members
- Track task completion

### Notes
- Create project notes and documentation
- Tag and organize notes
- Collaborative note-taking

### ML Insights
- Predict project delays
- Classify project risk levels
- View contributing factors
- Retrain models with latest data

## Integrations

### Slack
- Share project updates
- Send delay alerts
- Automated notifications

### Webex
- Schedule project meetings
- Send milestone notifications
- Create project spaces

### Google Workspace
- Export to Google Sheets
- Create project folders in Drive
- Schedule events in Calendar
- Generate project documents

## Deployment

### G: Drive Deployment
1. Build the executable using build scripts
2. Copy `dist/PMTracker/` to `G:\PMTracker\`
3. Create version file: `G:\PMTracker\latest_version.txt`
4. Users can run `G:\PMTracker\PMTracker.exe`

### Auto-updater
- Application checks for updates on startup
- Compares version with `G:\PMTracker\latest_version.txt`
- Prompts user to download new version if available

## Troubleshooting

### Oracle Connection Issues
- Verify Oracle Client is installed
- Check network connectivity to database
- Verify credentials in config file
- Ensure user has read access to GS tables

### ML Model Errors
- Ensure TensorFlow is installed correctly
- Check model files exist in resources/models/
- Retrain models if accuracy is low
- Verify sufficient training data (100+ projects)

### Performance Issues
- Clear browser cache (Ctrl+Shift+Delete)
- Restart application
- Check database query performance
- Reduce dashboard widgets

## Development

### Project Structure
```
PMTracker/
├── src/
│   ├── main.py                 # Application entry point
│   ├── api/                    # FastAPI routers
│   ├── core/                   # Core managers
│   ├── models/                 # Pydantic models
│   ├── ml/                     # ML models
│   ├── integrations/           # External integrations
│   ├── web_app/                # Frontend assets
│   └── utils/                  # Utilities
├── resources/                  # Application resources
├── config/                     # Configuration files
├── scripts/                    # Build scripts
├── requirements.txt            # Dependencies
├── build.spec                  # PyInstaller spec
└── README.md                   # This file
```

### Running Tests
```bash
pytest tests/
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document functions with docstrings

## Support

For issues or questions:
- Check the troubleshooting section
- Review application logs in `%USERPROFILE%\PMTracker\logs\`
- Contact the development team

## Version

Current Version: 1.0.0

## License

Internal Use Only - Verizon Communications Inc.
