"""
Search functionality for Verizon Tracker
Global search across projects, users, and activities
"""

from typing import List, Dict
from .database import MasterProjectsDB, MasterUsersDB, LocalProjectsDB
import streamlit as st


class GlobalSearch:
    """Perform global searches across the application"""

    @staticmethod
    def search_projects(query: str, user_id: int, role: str, limit: int = 10) -> List[Dict]:
        """
        Search projects by name, CCR/NFID, customer, or description

        Args:
            query: Search query string
            user_id: Current user ID
            role: Current user role
            limit: Maximum results to return

        Returns:
            List of matching project dictionaries
        """
        if not query or len(query) < 2:
            return []

        try:
            query_pattern = f"%{query}%"

            if role == "Sr. Project Manager":
                # Search in local database
                db = LocalProjectsDB(user_id)
                db.connect()

                results = db.fetchall("""
                    SELECT
                        project_id,
                        name,
                        ccr_nfid,
                        customer,
                        status,
                        site_address,
                        'local' as source
                    FROM projects
                    WHERE (
                        name LIKE ? OR
                        ccr_nfid LIKE ? OR
                        customer LIKE ? OR
                        site_address LIKE ?
                    )
                    AND pm_id = ?
                    ORDER BY name
                    LIMIT ?
                """, (query_pattern, query_pattern, query_pattern, query_pattern, user_id, limit))

                db.close()
            else:
                # Search in master database
                db = MasterProjectsDB()
                db.connect()

                results = db.fetchall("""
                    SELECT
                        project_id,
                        name,
                        ccr_nfid,
                        customer,
                        status,
                        site_address,
                        'master' as source
                    FROM projects
                    WHERE (
                        name LIKE ? OR
                        ccr_nfid LIKE ? OR
                        customer LIKE ? OR
                        site_address LIKE ?
                    )
                    ORDER BY name
                    LIMIT ?
                """, (query_pattern, query_pattern, query_pattern, query_pattern, limit))

                db.close()

            return [dict(row) for row in results]

        except Exception as e:
            return []

    @staticmethod
    def search_users(query: str, limit: int = 10) -> List[Dict]:
        """
        Search users by name or username

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching user dictionaries
        """
        if not query or len(query) < 2:
            return []

        try:
            query_pattern = f"%{query}%"

            db = MasterUsersDB()
            db.connect()

            results = db.fetchall("""
                SELECT
                    user_id,
                    username,
                    full_name,
                    email,
                    role
                FROM users
                WHERE (
                    full_name LIKE ? OR
                    username LIKE ? OR
                    email LIKE ?
                )
                AND active = 1
                ORDER BY full_name
                LIMIT ?
            """, (query_pattern, query_pattern, query_pattern, limit))

            db.close()

            return [dict(row) for row in results]

        except Exception as e:
            return []

    @staticmethod
    def get_recent_projects(user_id: int, role: str, limit: int = 5) -> List[Dict]:
        """
        Get recently accessed/modified projects

        Args:
            user_id: Current user ID
            role: Current user role
            limit: Maximum results to return

        Returns:
            List of recent project dictionaries
        """
        try:
            if role == "Sr. Project Manager":
                # Get from local database
                db = LocalProjectsDB(user_id)
                db.connect()

                results = db.fetchall("""
                    SELECT
                        p.project_id,
                        p.name,
                        p.ccr_nfid,
                        p.status,
                        p.customer,
                        p.updated_at
                    FROM projects p
                    WHERE p.pm_id = ?
                    ORDER BY p.updated_at DESC
                    LIMIT ?
                """, (user_id, limit))

                db.close()
            else:
                # Get from master database
                db = MasterProjectsDB()
                db.connect()

                # Get recent activities to find recently accessed projects
                results = db.fetchall("""
                    SELECT DISTINCT
                        p.project_id,
                        p.name,
                        p.ccr_nfid,
                        p.status,
                        p.customer,
                        p.updated_at
                    FROM projects p
                    WHERE p.updated_at IS NOT NULL
                    ORDER BY p.updated_at DESC
                    LIMIT ?
                """, (limit,))

                db.close()

            return [dict(row) for row in results]

        except Exception as e:
            return []

    @staticmethod
    def get_quick_stats_for_search() -> Dict:
        """
        Get quick statistics for search suggestions

        Returns:
            Dictionary with various counts
        """
        try:
            db = MasterProjectsDB()
            db.connect()

            stats = {
                'total_projects': 0,
                'active_projects': 0,
                'total_programs': 0
            }

            # Total projects
            result = db.fetchone("SELECT COUNT(*) as count FROM projects", ())
            stats['total_projects'] = result['count'] if result else 0

            # Active projects
            result = db.fetchone("SELECT COUNT(*) as count FROM projects WHERE status = 'Active'", ())
            stats['active_projects'] = result['count'] if result else 0

            # Total programs
            result = db.fetchone("SELECT COUNT(*) as count FROM programs", ())
            stats['total_programs'] = result['count'] if result else 0

            db.close()

            return stats

        except Exception as e:
            return {'total_projects': 0, 'active_projects': 0, 'total_programs': 0}


def show_search_bar():
    """Display a search bar with autocomplete suggestions"""

    st.markdown("""
        <style>
        .search-container {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .search-result {
            padding: 0.75rem;
            margin: 0.5rem 0;
            background: #F8F8F8;
            border-radius: 8px;
            border-left: 4px solid #EE0000;
            cursor: pointer;
            transition: all 0.2s;
        }
        .search-result:hover {
            background: #F0F0F0;
            transform: translateX(5px);
        }
        .search-result-title {
            font-weight: 600;
            color: #333;
            font-size: 1rem;
        }
        .search-result-meta {
            color: #666;
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }
        .search-badge {
            display: inline-block;
            background: #EE0000;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            margin-left: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Search input
    search_query = st.text_input(
        "🔍 Search Projects",
        placeholder="Search by name, CCR/NFID, customer...",
        key="global_search",
        label_visibility="collapsed"
    )

    if search_query and len(search_query) >= 2:
        # Perform search
        results = GlobalSearch.search_projects(
            search_query,
            st.session_state.user_id,
            st.session_state.role,
            limit=8
        )

        if results:
            st.markdown(f"**Found {len(results)} results:**")

            for result in results:
                status_color = {
                    'Active': '#4CAF50',
                    'On Hold': '#FF9800',
                    'Completed': '#2196F3',
                    'Cancelled': '#F44336'
                }.get(result['status'], '#999')

                st.markdown(f"""
                    <div class="search-result">
                        <div class="search-result-title">
                            {result['name']}
                            <span class="search-badge" style="background: {status_color};">
                                {result['status']}
                            </span>
                        </div>
                        <div class="search-result-meta">
                            📋 {result.get('ccr_nfid', 'N/A')} |
                            👤 {result.get('customer', 'N/A')} |
                            📍 {result.get('site_address', 'N/A')[:50]}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No results found. Try a different search term.")


def show_recent_projects_widget():
    """Display recent projects widget"""

    st.markdown("### 📌 Recent Projects")

    recent = GlobalSearch.get_recent_projects(
        st.session_state.user_id,
        st.session_state.role,
        limit=5
    )

    if recent:
        st.markdown("""
            <style>
            .recent-project {
                background: white;
                border-radius: 8px;
                padding: 0.75rem;
                margin: 0.5rem 0;
                border-left: 4px solid #EE0000;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: all 0.2s;
            }
            .recent-project:hover {
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                transform: translateY(-2px);
            }
            .recent-project-name {
                font-weight: 600;
                color: #333;
                font-size: 0.95rem;
                margin-bottom: 0.25rem;
            }
            .recent-project-info {
                color: #666;
                font-size: 0.85rem;
            }
            .status-badge-small {
                display: inline-block;
                padding: 0.15rem 0.4rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 0.5rem;
            }
            </style>
        """, unsafe_allow_html=True)

        for proj in recent:
            status_color = {
                'Active': '#4CAF50',
                'On Hold': '#FF9800',
                'Completed': '#2196F3',
                'Cancelled': '#F44336'
            }.get(proj['status'], '#999')

            st.markdown(f"""
                <div class="recent-project">
                    <div class="recent-project-name">
                        {proj['name']}
                        <span class="status-badge-small" style="background: {status_color}; color: white;">
                            {proj['status']}
                        </span>
                    </div>
                    <div class="recent-project-info">
                        📋 {proj.get('ccr_nfid', 'N/A')} | 👤 {proj.get('customer', 'N/A')[:30]}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # View all button
        if st.button("📋 View All Projects", use_container_width=True):
            st.switch_page("pages/9_All_Projects.py")
    else:
        st.info("No recent projects to display.")
