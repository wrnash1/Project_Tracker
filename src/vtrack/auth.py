"""
Authentication module for Verizon Tracker
Handles user login, logout, and session management
"""

import bcrypt
import streamlit as st
from typing import Optional, Dict
from .database import MasterUsersDB, LocalProjectsDB


def hash_password(password: str) -> str:
    """Hash a password for storing"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user and return user data if successful
    Returns None if authentication fails
    """
    users_db = MasterUsersDB()
    users_db.connect()

    user = users_db.fetchone(
        "SELECT * FROM users WHERE username = ? AND active = 1",
        (username,)
    )

    users_db.close()

    if user and verify_password(password, user['password_hash']):
        return dict(user)

    return None


def initialize_session_state():
    """Initialize session state variables for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if 'user' not in st.session_state:
        st.session_state.user = None

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    if 'username' not in st.session_state:
        st.session_state.username = None

    if 'full_name' not in st.session_state:
        st.session_state.full_name = None

    if 'role' not in st.session_state:
        st.session_state.role = None

    if 'local_db' not in st.session_state:
        st.session_state.local_db = None


def login(username: str, password: str) -> bool:
    """
    Login a user and set session state
    Returns True if successful, False otherwise
    """
    user = authenticate_user(username, password)

    if user:
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.user_id = user['user_id']
        st.session_state.username = user['username']
        st.session_state.full_name = user['full_name']
        st.session_state.role = user['role']

        # Initialize local database for this user
        local_db = LocalProjectsDB(user['user_id'])
        local_db.connect()
        local_db.initialize_schema()
        st.session_state.local_db = local_db

        return True

    return False


def logout():
    """Logout the current user and clear session state"""
    # Close local database connection if it exists
    if st.session_state.get('local_db'):
        try:
            st.session_state.local_db.close()
        except:
            pass

    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Reinitialize
    initialize_session_state()


def require_auth():
    """
    Decorator/helper function to require authentication
    Redirects to login if not authenticated
    """
    initialize_session_state()

    if not st.session_state.authenticated:
        st.warning("Please log in to access this page.")
        st.stop()


def require_role(allowed_roles: list):
    """
    Check if current user has one of the allowed roles
    If not, display error and stop
    """
    require_auth()

    if st.session_state.role not in allowed_roles:
        st.error(f"Access denied. This page requires one of these roles: {', '.join(allowed_roles)}")
        st.stop()


def get_current_user() -> Optional[Dict]:
    """Get the currently logged in user's data"""
    return st.session_state.get('user')


def is_admin() -> bool:
    """Check if current user is an admin (Associate Director)"""
    return st.session_state.get('role') == 'Associate Director'


def is_pm() -> bool:
    """Check if current user is a Project Manager"""
    return st.session_state.get('role') == 'Sr. Project Manager'
