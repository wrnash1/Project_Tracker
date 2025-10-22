import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from core.config_manager import ConfigManager

class SQLiteManager:
    """Manages SQLite database for user-generated content"""

    def __init__(self):
        self.config = ConfigManager()
        self.db_path = self.config.get_sqlite_path()
        self.connection = None
        self.cursor = None
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with schema"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connect()
        self._create_tables()
        self.disconnect()

    def connect(self):
        """Establish connection to SQLite database"""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def disconnect(self):
        """Close SQLite database connection"""
        if self.connection:
            self.connection.commit()
            self.connection.close()

    def _create_tables(self):
        """Create all necessary tables"""

        # Project Notes
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_number TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                tags TEXT,
                created_by TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User Tasks
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_number TEXT NOT NULL,
                task_name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'Pending',
                priority TEXT DEFAULT 'Medium',
                assigned_to TEXT,
                due_date DATE,
                completed_date TIMESTAMP,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Comments
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_number TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                comment_text TEXT NOT NULL,
                author TEXT NOT NULL,
                mentions TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Saved Filters
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filter_name TEXT NOT NULL,
                filter_criteria TEXT NOT NULL,
                created_by TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Custom Dashboards
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashboards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dashboard_name TEXT NOT NULL,
                layout TEXT NOT NULL,
                widgets TEXT NOT NULL,
                created_by TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Report History
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT NOT NULL,
                report_name TEXT NOT NULL,
                parameters TEXT,
                file_path TEXT,
                created_by TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ML Model Training History
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_training_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_type TEXT NOT NULL,
                accuracy REAL,
                training_samples INTEGER,
                training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_path TEXT
            )
        """)

        self.connection.commit()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a SELECT query and return results as list of dicts"""
        if not self.connection:
            self.connect()

        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            columns = [col[0] for col in self.cursor.description]
            results = []
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        except Exception as e:
            print(f"SQLite query error: {e}")
            return []

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        if not self.connection:
            self.connect()

        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            print(f"SQLite update error: {e}")
            self.connection.rollback()
            return 0

    # Project Notes Methods
    def create_note(self, project_number: str, title: str, content: str, tags: str = '', created_by: str = '') -> int:
        """Create a new project note"""
        query = """
            INSERT INTO project_notes (project_number, title, content, tags, created_by)
            VALUES (?, ?, ?, ?, ?)
        """
        self.execute_update(query, (project_number, title, content, tags, created_by))
        return self.cursor.lastrowid

    def get_notes(self, project_number: str) -> List[Dict]:
        """Get all notes for a project"""
        query = "SELECT * FROM project_notes WHERE project_number = ? ORDER BY created_date DESC"
        return self.execute_query(query, (project_number,))

    def update_note(self, note_id: int, title: str, content: str, tags: str = '') -> int:
        """Update an existing note"""
        query = """
            UPDATE project_notes
            SET title = ?, content = ?, tags = ?, modified_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.execute_update(query, (title, content, tags, note_id))

    def delete_note(self, note_id: int) -> int:
        """Delete a note"""
        query = "DELETE FROM project_notes WHERE id = ?"
        return self.execute_update(query, (note_id,))

    # User Tasks Methods
    def create_task(self, project_number: str, task_name: str, description: str = '',
                    status: str = 'Pending', priority: str = 'Medium',
                    assigned_to: str = '', due_date: str = None) -> int:
        """Create a new user task"""
        query = """
            INSERT INTO user_tasks (project_number, task_name, description, status, priority, assigned_to, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_update(query, (project_number, task_name, description, status, priority, assigned_to, due_date))
        return self.cursor.lastrowid

    def get_tasks(self, project_number: str = None, status: str = None) -> List[Dict]:
        """Get tasks, optionally filtered by project and status"""
        query = "SELECT * FROM user_tasks WHERE 1=1"
        params = []

        if project_number:
            query += " AND project_number = ?"
            params.append(project_number)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY due_date, priority"
        return self.execute_query(query, tuple(params) if params else None)

    def update_task(self, task_id: int, updates: Dict) -> int:
        """Update a task with provided fields"""
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE user_tasks SET {set_clause}, modified_date = CURRENT_TIMESTAMP WHERE id = ?"
        params = tuple(list(updates.values()) + [task_id])
        return self.execute_update(query, params)

    def delete_task(self, task_id: int) -> int:
        """Delete a task"""
        query = "DELETE FROM user_tasks WHERE id = ?"
        return self.execute_update(query, (task_id,))

    # Comments Methods
    def create_comment(self, project_number: str, entity_type: str, entity_id: int,
                      comment_text: str, author: str, mentions: str = '') -> int:
        """Create a new comment"""
        query = """
            INSERT INTO comments (project_number, entity_type, entity_id, comment_text, author, mentions)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.execute_update(query, (project_number, entity_type, entity_id, comment_text, author, mentions))
        return self.cursor.lastrowid

    def get_comments(self, entity_type: str, entity_id: int) -> List[Dict]:
        """Get all comments for an entity"""
        query = "SELECT * FROM comments WHERE entity_type = ? AND entity_id = ? ORDER BY created_date ASC"
        return self.execute_query(query, (entity_type, entity_id))

    # Dashboard Methods
    def save_dashboard(self, dashboard_name: str, layout: str, widgets: str, created_by: str = '') -> int:
        """Save a custom dashboard"""
        query = """
            INSERT INTO dashboards (dashboard_name, layout, widgets, created_by)
            VALUES (?, ?, ?, ?)
        """
        self.execute_update(query, (dashboard_name, layout, widgets, created_by))
        return self.cursor.lastrowid

    def get_dashboards(self, created_by: str = None) -> List[Dict]:
        """Get all dashboards, optionally filtered by creator"""
        if created_by:
            query = "SELECT * FROM dashboards WHERE created_by = ? ORDER BY modified_date DESC"
            return self.execute_query(query, (created_by,))
        else:
            query = "SELECT * FROM dashboards ORDER BY modified_date DESC"
            return self.execute_query(query)

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
