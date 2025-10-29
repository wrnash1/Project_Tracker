"""
Project Favorites/Bookmarks System for Verizon Tracker
Allow users to bookmark their favorite projects
"""

import json
from pathlib import Path
from typing import List, Dict
from .database import G_DRIVE
import streamlit as st


# Favorites directory
FAVORITES_DIR = G_DRIVE / "user_favorites"
FAVORITES_DIR.mkdir(parents=True, exist_ok=True)


class FavoritesManager:
    """Manage user project favorites"""

    @staticmethod
    def get_favorites_file(user_id: int) -> Path:
        """Get path to user's favorites file"""
        return FAVORITES_DIR / f"user_{user_id}_favorites.json"

    @staticmethod
    def get_user_favorites(user_id: int) -> List[int]:
        """
        Get list of favorite project IDs for user

        Args:
            user_id: User ID

        Returns:
            List of project IDs
        """
        try:
            favorites_file = FavoritesManager.get_favorites_file(user_id)

            if favorites_file.exists():
                with open(favorites_file, 'r') as f:
                    data = json.load(f)
                    return data.get('project_ids', [])

            return []

        except Exception as e:
            return []

    @staticmethod
    def add_favorite(user_id: int, project_id: int) -> bool:
        """
        Add project to favorites

        Args:
            user_id: User ID
            project_id: Project ID to add

        Returns:
            Success boolean
        """
        try:
            favorites = FavoritesManager.get_user_favorites(user_id)

            if project_id not in favorites:
                favorites.append(project_id)

                favorites_file = FavoritesManager.get_favorites_file(user_id)

                with open(favorites_file, 'w') as f:
                    json.dump({
                        'user_id': user_id,
                        'project_ids': favorites,
                        'updated_at': str(Path(__file__).stat().st_mtime)
                    }, f, indent=2)

                return True

            return False  # Already in favorites

        except Exception as e:
            return False

    @staticmethod
    def remove_favorite(user_id: int, project_id: int) -> bool:
        """
        Remove project from favorites

        Args:
            user_id: User ID
            project_id: Project ID to remove

        Returns:
            Success boolean
        """
        try:
            favorites = FavoritesManager.get_user_favorites(user_id)

            if project_id in favorites:
                favorites.remove(project_id)

                favorites_file = FavoritesManager.get_favorites_file(user_id)

                with open(favorites_file, 'w') as f:
                    json.dump({
                        'user_id': user_id,
                        'project_ids': favorites,
                        'updated_at': str(Path(__file__).stat().st_mtime)
                    }, f, indent=2)

                return True

            return False

        except Exception as e:
            return False

    @staticmethod
    def is_favorite(user_id: int, project_id: int) -> bool:
        """
        Check if project is in user's favorites

        Args:
            user_id: User ID
            project_id: Project ID

        Returns:
            True if favorited
        """
        favorites = FavoritesManager.get_user_favorites(user_id)
        return project_id in favorites

    @staticmethod
    def get_favorite_projects(user_id: int, db) -> List[Dict]:
        """
        Get full project data for user's favorites

        Args:
            user_id: User ID
            db: Database connection

        Returns:
            List of project dictionaries
        """
        try:
            favorites = FavoritesManager.get_user_favorites(user_id)

            if not favorites:
                return []

            # Get projects
            placeholders = ','.join('?' * len(favorites))
            projects = db.fetchall(
                f"SELECT * FROM projects WHERE project_id IN ({placeholders})",
                tuple(favorites)
            )

            return [dict(p) for p in projects]

        except Exception as e:
            return []


def show_favorite_button(project_id: int, user_id: int, size: str = "normal"):
    """Display favorite/unfavorite button"""

    is_fav = FavoritesManager.is_favorite(user_id, project_id)

    if size == "small":
        icon = "⭐" if is_fav else "☆"
        label = ""
        key_suffix = f"_small_{project_id}"
    else:
        icon = "⭐" if is_fav else "☆"
        label = "Unfavorite" if is_fav else "Add to Favorites"
        key_suffix = f"_{project_id}"

    button_label = f"{icon} {label}".strip()

    if st.button(button_label, key=f"fav_btn{key_suffix}", use_container_width=(size != "small")):
        if is_fav:
            if FavoritesManager.remove_favorite(user_id, project_id):
                st.success("Removed from favorites!")
                st.rerun()
        else:
            if FavoritesManager.add_favorite(user_id, project_id):
                st.success("Added to favorites!")
                st.rerun()


def show_favorites_widget():
    """Display favorites widget for Home dashboard"""

    if not hasattr(st.session_state, 'user_id'):
        return

    user_id = st.session_state.user_id
    role = st.session_state.role

    st.markdown("### ⭐ Favorite Projects")

    from src.vtrack.database import LocalProjectsDB, MasterProjectsDB

    # Get database based on role
    if role == "Sr. Project Manager":
        db = LocalProjectsDB(user_id)
    else:
        db = MasterProjectsDB()

    db.connect()

    favorite_projects = FavoritesManager.get_favorite_projects(user_id, db)

    db.close()

    if favorite_projects:
        for proj in favorite_projects[:5]:  # Show top 5
            st.markdown(f"""
                <div class="modern-card" style="padding: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #333; font-size: 0.95rem;">
                                ⭐ {proj['name'][:35]}{'...' if len(proj['name']) > 35 else ''}
                            </div>
                            <div style="font-size: 0.8rem; color: #666; margin-top: 0.25rem;">
                                {proj.get('ccr_nfid', 'N/A')} | {proj['status']}
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.caption(f"Showing {min(5, len(favorite_projects))} of {len(favorite_projects)} favorites")
    else:
        st.info("No favorite projects yet. Star projects to add them here!")
