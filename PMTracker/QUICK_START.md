# PM Project Tracker - Quick Start Guide

## Installation & Setup (5 Minutes)

### 1. Prerequisites
- Python 3.11+ installed
- Oracle Client libraries (for database access)
- Windows 10/11 or Linux

### 2. Install Dependencies
```bash
cd /home/wrnash1/Developer/Project_Tracker/PMTracker
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configure Database
First run will create config at `~/.PMTracker/config/config.ini`

Edit the config or use the Settings UI:
- Oracle Host: `f1btpap-scan.verizon.com/NARPROD`
- Oracle User: `splunkveep_nar`
- Oracle Password: [Enter via Settings dialog - will be encrypted]

### 4. Run the Application
```bash
python src/main.py
```

The application will:
1. Start FastAPI backend on port 8000
2. Open PyWebView window
3. Check for updates
4. Load the dashboard

---

## First Time Usage

### Step 1: View Projects
1. Click "Projects" tab
2. Projects will load from Oracle GS database
3. Use search/filter to find specific projects

### Step 2: Create a Task
1. Click "Tasks" tab
2. Click "Add Task" button
3. Fill in task details
4. Click "Create Task"

### Step 3: Run ML Prediction
1. Click "ML Insights" tab
2. Select a project from dropdown
3. Click "Run Prediction"
4. View delay prediction and risk classification

### Step 4: Generate Report
1. Click "Reports" tab
2. Select report type (Project Summary, CCR Analysis, Budget Variance)
3. Choose format (PDF or Excel)
4. Click "Generate Report"
5. Report will download automatically

---

## Common Tasks

### Search for a Project
```
1. Click search icon in header
2. Enter project number or name
3. Results display in Projects tab
```

### View Gantt Chart
```
1. Go to Gantt Chart tab
2. Select project from dropdown
3. Chart displays CCRs and orders as tasks
```

### Add Project Note
```
1. Go to Notes tab
2. Select project
3. Click "Add Note"
4. Enter title, content, and tags
5. Save
```

### Share ML Insights
```
1. Run ML prediction for a project
2. Click "Share Insights"
3. Choose Slack, Webex, or Email
4. Data copied to clipboard and app opens
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Search projects |
| Ctrl+R | Refresh current tab |
| Ctrl+N | New (task/note depending on tab) |
| Ctrl+G | Go to Gantt chart |
| Esc | Close modal |

---

## Tips & Tricks

### Performance
- **Faster Loading**: Use filters to limit project data
- **Smooth Scrolling**: Clear cache if UI becomes sluggish
- **Quick Access**: Bookmark frequently used projects

### Reports
- **Batch Reports**: Select multiple projects for combined reports
- **Scheduled Reports**: Set up daily/weekly reports via Settings
- **Custom Templates**: Modify report templates in code

### ML Predictions
- **Better Accuracy**: Retrain models monthly with latest data
- **Confidence Scores**: Higher confidence = more reliable prediction
- **Contributing Factors**: Review factors to understand predictions

### Integrations
- **Slack**: Use #project-updates channel for team visibility
- **Webex**: Schedule follow-up meetings from prediction results
- **Google Sheets**: Export data for further analysis

---

## Troubleshooting

### "Oracle connection failed"
**Solution**:
1. Check VPN connection
2. Verify Oracle Client is installed
3. Check credentials in Settings

### "ML model not found"
**Solution**:
1. Models auto-generate on first use
2. Or manually train: ML tab → Retrain Models
3. Requires 100+ completed projects

### "Report generation failed"
**Solution**:
1. Check disk space
2. Verify write permissions to temp folder
3. Try different format (PDF vs Excel)

### "Application won't start"
**Solution**:
1. Check Python version (3.11+)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check port 8000 is not in use

---

## Building Executable

### Windows
```cmd
cd scripts
build.bat
```
Executable: `dist\PMTracker\PMTracker.exe`

### Linux/Mac
```bash
cd scripts
chmod +x build.sh
./build.sh
```
Executable: `dist/PMTracker/PMTracker`

---

## Getting Help

### In-App Help
- Click Settings icon → Help
- View API documentation: http://127.0.0.1:8000/docs

### Documentation
- README.md - Full documentation
- PROJECT_SUMMARY.md - Technical details
- This file - Quick reference

### Support
- Check logs: `~/.PMTracker/logs/`
- Contact: [Internal Verizon Support]

---

## Next Steps

Once comfortable with basics:
1. ⚙️ Customize dashboard widgets
2. 📊 Create custom reports
3. 🤖 Explore ML insights for all projects
4. 📝 Build project documentation with Notes
5. 🔔 Set up Slack/Webex notifications
6. 📈 Track project health scores
7. 🚀 Deploy to team via G: drive

---

## Quick Reference - File Locations

| Item | Location |
|------|----------|
| Config | `~/.PMTracker/config/config.ini` |
| Database | `~/.PMTracker/config/pmtracker.db` |
| Logs | `~/.PMTracker/logs/` |
| ML Models | `resources/models/` |
| Reports | Downloads folder |
| Encryption Key | `~/.PMTracker/config/key.key` |

---

## Quick Reference - API Endpoints

**Base URL**: `http://127.0.0.1:8000`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/projects/` | GET | List projects |
| `/api/projects/{num}` | GET | Project details |
| `/api/notes/` | POST | Create note |
| `/api/tasks/` | GET/POST | Manage tasks |
| `/api/gantt/{num}` | GET | Gantt data |
| `/api/reports/generate` | POST | Generate report |
| `/api/ml/predict-delay/{num}` | GET | Predict delay |
| `/api/tts/speak` | POST | Text-to-speech |

---

**Happy Tracking!** 🚀

For detailed information, see README.md and PROJECT_SUMMARY.md
