"""
Backup and Restore System for Verizon Tracker
Create and restore database backups
"""

import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from .database import DATA_DIR, G_DRIVE, LOCAL_DRIVE
import streamlit as st


# Backup directory
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


class BackupManager:
    """Manage database backups"""

    @staticmethod
    def create_backup(backup_name: str = None, include_local: bool = False) -> tuple[bool, str, str]:
        """
        Create a full backup of all databases

        Args:
            backup_name: Optional name for backup, otherwise uses timestamp
            include_local: Whether to include local databases

        Returns:
            (success, message, backup_path)
        """
        try:
            # Generate backup name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if not backup_name:
                backup_name = f"backup_{timestamp}"
            else:
                backup_name = f"{backup_name}_{timestamp}"

            # Create backup folder
            backup_folder = BACKUP_DIR / backup_name
            backup_folder.mkdir(parents=True, exist_ok=True)

            # Backup metadata
            metadata = {
                'backup_name': backup_name,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'created_by': st.session_state.user_id if hasattr(st.session_state, 'user_id') else None,
                'include_local': include_local,
                'files_backed_up': []
            }

            # Backup G_DRIVE databases
            for db_file in G_DRIVE.glob("*.db"):
                dest = backup_folder / "master" / db_file.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(db_file, dest)
                metadata['files_backed_up'].append(f"master/{db_file.name}")

            # Optionally backup local databases
            if include_local:
                for db_file in LOCAL_DRIVE.glob("*.db"):
                    dest = backup_folder / "local" / db_file.name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(db_file, dest)
                    metadata['files_backed_up'].append(f"local/{db_file.name}")

            # Backup project templates
            from .database import G_DRIVE
            templates_dir = G_DRIVE / "project_templates"
            if templates_dir.exists():
                dest_templates = backup_folder / "templates"
                shutil.copytree(templates_dir, dest_templates, dirs_exist_ok=True)
                metadata['files_backed_up'].append("templates/*")

            # Save metadata
            with open(backup_folder / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)

            # Create a summary file
            summary = f"""
Verizon Tracker Backup
=====================
Backup Name: {backup_name}
Created: {metadata['created_at']}
Files Backed Up: {len(metadata['files_backed_up'])}
Include Local DBs: {include_local}

Files:
{chr(10).join('- ' + f for f in metadata['files_backed_up'])}
"""

            with open(backup_folder / "README.txt", 'w') as f:
                f.write(summary)

            return True, f"Backup created successfully: {backup_name}", str(backup_folder)

        except Exception as e:
            return False, f"Backup failed: {str(e)}", ""

    @staticmethod
    def list_backups() -> List[Dict]:
        """
        List all available backups

        Returns:
            List of backup dictionaries with metadata
        """
        try:
            backups = []

            for backup_folder in sorted(BACKUP_DIR.iterdir(), reverse=True):
                if backup_folder.is_dir():
                    metadata_file = backup_folder / "metadata.json"

                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            metadata['backup_path'] = str(backup_folder)
                            metadata['backup_folder_name'] = backup_folder.name

                            # Calculate size
                            total_size = sum(f.stat().st_size for f in backup_folder.rglob('*') if f.is_file())
                            metadata['size_mb'] = round(total_size / (1024 * 1024), 2)

                            backups.append(metadata)
                    else:
                        # Backup without metadata (older format)
                        backups.append({
                            'backup_name': backup_folder.name,
                            'created_at': datetime.fromtimestamp(backup_folder.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                            'backup_path': str(backup_folder),
                            'backup_folder_name': backup_folder.name,
                            'files_backed_up': [],
                            'size_mb': round(sum(f.stat().st_size for f in backup_folder.rglob('*') if f.is_file()) / (1024 * 1024), 2)
                        })

            return backups

        except Exception as e:
            return []

    @staticmethod
    def restore_backup(backup_folder_name: str, restore_local: bool = False) -> tuple[bool, str]:
        """
        Restore a backup

        Args:
            backup_folder_name: Name of backup folder
            restore_local: Whether to restore local databases

        Returns:
            (success, message)
        """
        try:
            backup_folder = BACKUP_DIR / backup_folder_name

            if not backup_folder.exists():
                return False, "Backup not found"

            # Restore master databases
            master_backup = backup_folder / "master"
            if master_backup.exists():
                for db_file in master_backup.glob("*.db"):
                    dest = G_DRIVE / db_file.name
                    # Create backup of current before overwriting
                    if dest.exists():
                        backup_current = dest.parent / f"{dest.stem}_pre_restore_{datetime.now().strftime('%Y%m%d%H%M%S')}.db"
                        shutil.copy2(dest, backup_current)

                    shutil.copy2(db_file, dest)

            # Optionally restore local databases
            if restore_local:
                local_backup = backup_folder / "local"
                if local_backup.exists():
                    for db_file in local_backup.glob("*.db"):
                        dest = LOCAL_DRIVE / db_file.name
                        shutil.copy2(db_file, dest)

            # Restore templates
            templates_backup = backup_folder / "templates"
            if templates_backup.exists():
                templates_dir = G_DRIVE / "project_templates"
                shutil.copytree(templates_backup, templates_dir, dirs_exist_ok=True)

            return True, f"Backup restored successfully from {backup_folder_name}"

        except Exception as e:
            return False, f"Restore failed: {str(e)}"

    @staticmethod
    def delete_backup(backup_folder_name: str) -> tuple[bool, str]:
        """
        Delete a backup

        Args:
            backup_folder_name: Name of backup folder

        Returns:
            (success, message)
        """
        try:
            backup_folder = BACKUP_DIR / backup_folder_name

            if not backup_folder.exists():
                return False, "Backup not found"

            shutil.rmtree(backup_folder)

            return True, f"Backup {backup_folder_name} deleted successfully"

        except Exception as e:
            return False, f"Delete failed: {str(e)}"

    @staticmethod
    def export_backup(backup_folder_name: str) -> Optional[bytes]:
        """
        Export backup as zip file

        Args:
            backup_folder_name: Name of backup folder

        Returns:
            Zip file bytes or None
        """
        try:
            import zipfile
            import io

            backup_folder = BACKUP_DIR / backup_folder_name

            if not backup_folder.exists():
                return None

            # Create zip in memory
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in backup_folder.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(backup_folder)
                        zip_file.write(file_path, arcname)

            zip_buffer.seek(0)
            return zip_buffer.getvalue()

        except Exception as e:
            return None

    @staticmethod
    def get_backup_stats() -> Dict:
        """Get statistics about backups"""
        try:
            backups = BackupManager.list_backups()

            total_size = sum(b.get('size_mb', 0) for b in backups)
            total_backups = len(backups)

            most_recent = backups[0]['created_at'] if backups else 'N/A'

            return {
                'total_backups': total_backups,
                'total_size_mb': round(total_size, 2),
                'most_recent': most_recent,
                'oldest': backups[-1]['created_at'] if backups else 'N/A'
            }

        except:
            return {
                'total_backups': 0,
                'total_size_mb': 0,
                'most_recent': 'N/A',
                'oldest': 'N/A'
            }
