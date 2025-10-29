"""
Database module for Verizon Tracker
Handles all database operations for master and local databases
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Directory paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOCAL_DRIVE = DATA_DIR / "LOCAL_DRIVE"
G_DRIVE = DATA_DIR / "G_DRIVE"
SYNC_INBOX = G_DRIVE / "SYNC_INBOX"
ARCHIVE = G_DRIVE / "ARCHIVE"

# Ensure directories exist
for directory in [DATA_DIR, LOCAL_DRIVE, G_DRIVE, SYNC_INBOX, ARCHIVE]:
    directory.mkdir(parents=True, exist_ok=True)


class Database:
    """Base database class with common operations"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def execute(self, query: str, params: tuple = ()):
        """Execute a query and commit"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetchall(self, query: str, params: tuple = ()):
        """Fetch all results from a query"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def fetchone(self, query: str, params: tuple = ()):
        """Fetch one result from a query"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()


class MasterUsersDB(Database):
    """Master users database - stores all user credentials and roles"""

    def __init__(self):
        db_path = G_DRIVE / "master_users.db"
        super().__init__(str(db_path))

    def initialize_schema(self):
        """Create users table"""
        self.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL CHECK(role IN ('Sr. Project Manager', 'Principal Engineer', 'Associate Director', 'Director')),
                reports_to_id INTEGER,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reports_to_id) REFERENCES users(user_id)
            )
        """)

    def create_default_users(self):
        """Create default admin user if no users exist"""
        result = self.fetchone("SELECT COUNT(*) as count FROM users")
        if result['count'] == 0:
            import bcrypt
            # Create default admin user
            password = "admin123"  # Change this in production!
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            self.execute("""
                INSERT INTO users (username, password_hash, full_name, email, role)
                VALUES (?, ?, ?, ?, ?)
            """, ("admin", hashed.decode('utf-8'), "Admin User", "admin@verizon.com", "Associate Director"))

            # Create a test PM user
            password = "pm123"
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.execute("""
                INSERT INTO users (username, password_hash, full_name, email, role, reports_to_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("pmuser", hashed.decode('utf-8'), "PM User", "pm@verizon.com", "Sr. Project Manager", 1))


class MasterProjectsDB(Database):
    """Master projects database - central repository for all project data"""

    def __init__(self):
        db_path = G_DRIVE / "master_projects.db"
        super().__init__(str(db_path))

    def initialize_schema(self):
        """Create all master tables"""

        # Programs table
        self.execute("""
            CREATE TABLE IF NOT EXISTS programs (
                program_id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Project types table
        self.execute("""
            CREATE TABLE IF NOT EXISTS project_types (
                type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Main projects table
        self.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ccr_nfid TEXT UNIQUE NOT NULL,
                program_id INTEGER,
                project_type_id INTEGER,
                pm_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'On Hold', 'Completed', 'Cancelled')),
                phase TEXT,
                notes TEXT,

                -- Legacy Oracle fields
                nfid TEXT,
                customer TEXT,
                clli TEXT,
                rft_date DATE,
                system_type TEXT,
                current_queue TEXT,
                site_address TEXT,

                -- Scorecard reporting fields
                project_start_date DATE,
                project_complete_date DATE,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (program_id) REFERENCES programs(program_id),
                FOREIGN KEY (project_type_id) REFERENCES project_types(type_id),
                FOREIGN KEY (pm_id) REFERENCES users(user_id)
            )
        """)

        # Project dependencies
        self.execute("""
            CREATE TABLE IF NOT EXISTS project_dependencies (
                dependency_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                depends_on_project_id INTEGER NOT NULL,
                dependency_type TEXT DEFAULT 'Finish-to-Start',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(project_id),
                FOREIGN KEY (depends_on_project_id) REFERENCES projects(project_id)
            )
        """)

        # Project contacts (team members)
        self.execute("""
            CREATE TABLE IF NOT EXISTS project_contacts (
                contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                contact_name TEXT NOT NULL,
                contact_role TEXT NOT NULL,
                contact_email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)

        # Work packages (milestones/tasks)
        self.execute("""
            CREATE TABLE IF NOT EXISTS work_packages (
                package_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                due_date DATE,
                status TEXT DEFAULT 'Not Started' CHECK(status IN ('Not Started', 'In Progress', 'Completed', 'Blocked')),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)

        # KPI snapshots
        self.execute("""
            CREATE TABLE IF NOT EXISTS kpi_snapshots (
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                snapshot_date DATE NOT NULL,
                budget_status TEXT,
                schedule_status TEXT,
                on_time_percent REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)

        # AI Knowledge Base
        self.execute("""
            CREATE TABLE IF NOT EXISTS ai_knowledge_base (
                kb_id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_name TEXT NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User Activity Log
        self.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                activity_description TEXT NOT NULL,
                related_project_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (related_project_id) REFERENCES projects(project_id)
            )
        """)

        # AI Feedback
        self.execute("""
            CREATE TABLE IF NOT EXISTS ai_feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                rating INTEGER CHECK(rating IN (-1, 1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

    def create_default_data(self):
        """Create default programs and project types"""

        # Default programs
        programs = [
            ("5G Rollout", "National 5G network expansion"),
            ("Network Modernization", "Legacy system upgrades"),
            ("BAU Operations", "Business as usual maintenance")
        ]

        for name, desc in programs:
            try:
                self.execute(
                    "INSERT INTO programs (program_name, description) VALUES (?, ?)",
                    (name, desc)
                )
            except sqlite3.IntegrityError:
                pass  # Already exists

        # Default project types
        types = [
            ("BAR", "Build and Run projects"),
            ("Circuit", "Circuit installation and testing"),
            ("BAU Rev", "Business as usual revenue generating"),
            ("BAU Non-Rev", "Business as usual non-revenue"),
            ("Decom", "Decommissioning projects")
        ]

        for name, desc in types:
            try:
                self.execute(
                    "INSERT INTO project_types (type_name, description) VALUES (?, ?)",
                    (name, desc)
                )
            except sqlite3.IntegrityError:
                pass  # Already exists


class LocalProjectsDB(Database):
    """Local user database - mirrors master structure with sync tracking"""

    def __init__(self, user_id: int):
        db_path = LOCAL_DRIVE / f"my_projects_{user_id}.db"
        super().__init__(str(db_path))
        self.user_id = user_id

    def initialize_schema(self):
        """Create local tables with sync_status fields"""

        # Local projects table
        self.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                local_id INTEGER PRIMARY KEY AUTOINCREMENT,
                master_project_id INTEGER,
                name TEXT NOT NULL,
                ccr_nfid TEXT UNIQUE NOT NULL,
                program_id INTEGER,
                project_type_id INTEGER,
                pm_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Active',
                phase TEXT,
                notes TEXT,

                -- Legacy Oracle fields
                nfid TEXT,
                customer TEXT,
                clli TEXT,
                rft_date DATE,
                system_type TEXT,
                current_queue TEXT,
                site_address TEXT,

                -- Scorecard reporting fields
                project_start_date DATE,
                project_complete_date DATE,

                sync_status TEXT DEFAULT 'new' CHECK(sync_status IN ('new', 'updated', 'synced')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Local KPI snapshots
        self.execute("""
            CREATE TABLE IF NOT EXISTS kpi_snapshots (
                local_snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                master_snapshot_id INTEGER,
                local_project_id INTEGER NOT NULL,
                snapshot_date DATE NOT NULL,
                budget_status TEXT,
                schedule_status TEXT,
                on_time_percent REAL,
                notes TEXT,
                sync_status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (local_project_id) REFERENCES projects(local_id)
            )
        """)

        # Local project dependencies
        self.execute("""
            CREATE TABLE IF NOT EXISTS project_dependencies (
                local_dependency_id INTEGER PRIMARY KEY AUTOINCREMENT,
                master_dependency_id INTEGER,
                local_project_id INTEGER NOT NULL,
                depends_on_local_project_id INTEGER NOT NULL,
                dependency_type TEXT DEFAULT 'Finish-to-Start',
                notes TEXT,
                sync_status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (local_project_id) REFERENCES projects(local_id),
                FOREIGN KEY (depends_on_local_project_id) REFERENCES projects(local_id)
            )
        """)

        # Local work packages
        self.execute("""
            CREATE TABLE IF NOT EXISTS work_packages (
                local_package_id INTEGER PRIMARY KEY AUTOINCREMENT,
                master_package_id INTEGER,
                local_project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                due_date DATE,
                status TEXT DEFAULT 'Not Started',
                notes TEXT,
                sync_status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (local_project_id) REFERENCES projects(local_id)
            )
        """)

        # Local project contacts
        self.execute("""
            CREATE TABLE IF NOT EXISTS project_contacts (
                local_contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                master_contact_id INTEGER,
                local_project_id INTEGER NOT NULL,
                contact_name TEXT NOT NULL,
                contact_role TEXT NOT NULL,
                contact_email TEXT,
                sync_status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (local_project_id) REFERENCES projects(local_id)
            )
        """)


class ConfigDB(Database):
    """Configuration database for application settings"""

    def __init__(self):
        db_path = G_DRIVE / "config.db"
        super().__init__(str(db_path))

    def initialize_schema(self):
        """Create config table"""
        self.execute("""
            CREATE TABLE IF NOT EXISTS config_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def create_default_config(self):
        """Create default configuration settings"""
        defaults = [
            ("ai_model_name", "all-MiniLM-L6-v2", "Sentence transformer model for AI"),
            ("kpi_threshold_green", "90", "KPI percentage for green status"),
            ("kpi_threshold_yellow", "70", "KPI percentage for yellow status"),
            ("business_days_per_week", "5", "Number of business days per week"),
            ("app_version", "1.0.0", "Application version")
        ]

        for key, value, desc in defaults:
            try:
                self.execute(
                    "INSERT INTO config_settings (setting_key, setting_value, description) VALUES (?, ?, ?)",
                    (key, value, desc)
                )
            except sqlite3.IntegrityError:
                pass  # Already exists

    def get_config(self, key: str) -> Optional[str]:
        """Get a configuration value"""
        result = self.fetchone("SELECT setting_value FROM config_settings WHERE setting_key = ?", (key,))
        return result['setting_value'] if result else None

    def set_config(self, key: str, value: str):
        """Set a configuration value"""
        self.execute("""
            INSERT OR REPLACE INTO config_settings (setting_key, setting_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))


def initialize_all_databases():
    """Initialize all databases with their schemas and default data"""

    # Master Users DB
    users_db = MasterUsersDB()
    users_db.connect()
    users_db.initialize_schema()
    users_db.create_default_users()
    users_db.close()

    # Master Projects DB
    projects_db = MasterProjectsDB()
    projects_db.connect()
    projects_db.initialize_schema()
    projects_db.create_default_data()
    projects_db.close()

    # Config DB
    config_db = ConfigDB()
    config_db.connect()
    config_db.initialize_schema()
    config_db.create_default_config()
    config_db.close()

    print(" All databases initialized successfully!")


if __name__ == "__main__":
    # Run this to initialize databases
    initialize_all_databases()
