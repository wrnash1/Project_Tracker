# Verizon Tracker

A secure, local-first Project Management Tool for Verizon, designed to replace legacy spreadsheet-based tracking systems with a modern, high-performance desktop application.

## Overview

Verizon Tracker provides:
- **Role-based dashboards** for Project Managers, Admins, Engineers, and Directors
- **Local-first architecture** using SQLite for fast, secure data management
- **Automated KPI reporting** with monthly scorecards and interval tracking
- **Project dependency management** for complex project relationships
- **AI-powered assistant** for intelligent insights and knowledge base queries
- **Modern, Verizon-branded UI** built with Streamlit and custom CSS

## Features

### ✅ Currently Implemented (MVP v1.0.0)

- **Authentication System**: Secure login with role-based access control
- **My Dashboard**: Project Manager view with editable project list
- **New Project**: Form to create new projects with all legacy Oracle fields
- **KPI Snapshots**: Take point-in-time snapshots of project metrics
- **Project Dependencies**: Define and track project relationships
- **Data Synchronization**: ⭐ Push local changes to master database via sync inbox
- **All Projects View**: ⭐ Advanced filtering, search, and export to CSV
- **Admin Panel**: ⭐ User management, system configuration, and database info
- **Modern UI**: Verizon-themed interface with custom CSS styling
- **Database Architecture**: Complete schema for users, projects, KPIs, dependencies, and AI features
- **Export Functionality**: ⭐ Download projects as CSV with filters applied

### 🚧 Coming Soon

- **Team Dashboard**: Admin view of all projects across team members
- **Import Data**: Bulk import from Excel/CSV spreadsheets
- **Process Sync Inbox**: Admin tool to merge synced data
- **Reports & Analytics**: Advanced reporting dashboards and scorecards with charts
- **AI Assistant**: Chatbot with knowledge base and feedback mechanism
- **Work Packages**: Milestone and task management for projects
- **Project Contacts**: Team member tracking per project

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**:
   ```bash
   cd /home/wrnash1/development/Project_Tracker
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize databases**:
   ```bash
   python src/vtrack/database.py
   ```

5. **Run the application**:
   ```bash
   streamlit run app/Home.py
   ```

6. **Access the application**:
   - Open your browser to `http://localhost:8501`
   - Login with default credentials:
     - **Admin**: username: `admin`, password: `admin123`
     - **PM User**: username: `pmuser`, password: `pm123`

## Project Structure

```
Project_Tracker/
├── app/
│   ├── Home.py                 # Main entry point & login page
│   ├── sidebar.py              # Sidebar navigation component
│   ├── styles.py               # Custom CSS styling
│   └── pages/                  # Multi-page app structure
│       ├── 1_My_Dashboard.py   # PM dashboard
│       ├── 2_New_Project.py    # Create new projects
│       ├── 3_Sync_Data.py      # Sync to master DB
│       ├── 4_Team_Dashboard.py # Admin team view
│       ├── 5_Import_Data.py    # Bulk import
│       ├── 6_Process_Sync_Inbox.py  # Process syncs
│       ├── 7_Admin_Panel.py    # Admin controls
│       ├── 8_Reports.py        # Analytics & reports
│       ├── 9_All_Projects.py   # View all projects
│       └── 10_AI_Assistant.py  # AI chatbot
├── src/
│   └── vtrack/
│       ├── __init__.py
│       ├── database.py         # Database schemas & operations
│       ├── auth.py             # Authentication & session management
│       ├── sync.py             # Sync logic (future)
│       └── reports.py          # Reporting functions (future)
├── data/                       # Created at runtime
│   ├── LOCAL_DRIVE/            # Local user databases
│   └── G_DRIVE/                # Shared master databases
│       ├── SYNC_INBOX/         # Pending syncs
│       ├── ARCHIVE/            # Processed syncs
│       ├── AI_Knowledge_Base/  # AI documents
│       └── AI_Feedback/        # AI feedback data
├── .streamlit/
│   └── config.toml             # Verizon theme configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Architecture

### Local-First Design

- Each user has a **local database** (`my_projects_USERID.db`) stored on their machine
- Changes are tracked with `sync_status` (new, updated, synced)
- **Sync inbox model** safely consolidates data without corruption
- **Master databases** on shared network drive (simulated as `G_DRIVE`)

### Database Schema

1. **master_users.db**: User credentials, roles, and reporting hierarchy
2. **master_projects.db**: Central repository for all project data
3. **config.db**: Application configuration and business rules
4. **my_projects_USERID.db**: Local user database with sync tracking

### User Roles

- **Sr. Project Manager**: Manage projects, take KPIs, sync data
- **Principal Engineer**: Read-only view of all projects, access reports
- **Associate Director**: Admin controls, user management, sync processing
- **Director**: High-level portfolio dashboard, read-only access

## Technology Stack

- **Python 3.10+**: Core language
- **Streamlit**: Web UI framework
- **SQLite**: Local and master databases
- **Pandas**: Data manipulation and import
- **bcrypt**: Password hashing
- **Sentence Transformers**: AI embeddings (future)
- **FAISS**: Vector similarity search (future)

## Development

### Adding New Features

1. Create new pages in `app/pages/`
2. Add business logic in `src/vtrack/`
3. Update database schema in `src/vtrack/database.py`
4. Update sidebar navigation in `app/sidebar.py`
5. Test with different user roles

### Running Tests

```bash
# Coming soon
pytest tests/
```

### Code Style

- Follow PEP 8 guidelines
- Use docstrings for functions and classes
- Keep functions focused and modular
- Add comments for complex logic

## Security

- **No cloud dependencies**: All data stays within Verizon network
- **Bcrypt password hashing**: Secure credential storage
- **Role-based access control**: Users only see what they're authorized to see
- **Local-first**: No external API calls or internet requirements
- **Session management**: Secure Streamlit session state

## Future Enhancements

### Phase 5: Project Details Page
- Manage work packages (milestones/tasks)
- Manage project contacts (team members)
- Link from dashboard to detailed project view

### Phase 6: Advanced Reporting
- Monthly scorecard with project counts and intervals
- Visual program tracker (like UT Market Update PDF)
- Business day calculations for KPIs

### Phase 7: Branding & Templates
- Enhanced Verizon logo integration
- Role-based form defaults
- Reusable project templates

### Phase 8: Packaging
- PyInstaller build to standalone .exe
- One-click installation
- Bundled dependencies

## Troubleshooting

### Database Initialization Failed
```bash
# Manually initialize databases
python src/vtrack/database.py
```

### Module Not Found Errors
```bash
# Ensure you're in the virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Run on different port
streamlit run app/Home.py --server.port 8502
```

## Support & Contribution

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: See `/docs` folder (coming soon)
- **Team Collaboration**: Use feature branches and pull requests

## License

© 2025 Verizon Communications. Internal use only.

## Version History

- **v1.0.0** (Current) - MVP with authentication, dashboard, and project creation
- **v0.9.0** - Initial setup and architecture

---

**Built with ❤️ for Verizon Project Management Teams**
