import requests
import os
from pathlib import Path
from core.config_manager import ConfigManager

__version__ = '1.0.0'

def check_for_updates() -> bool:
    """Check if a newer version is available on G: drive"""
    try:
        config = ConfigManager()
        update_url = config.get('Application', 'update_check')

        if update_url == 'false':
            return False

        # Read version file from G: drive
        version_file = Path(update_url)
        if not version_file.exists():
            return False

        with open(version_file, 'r') as f:
            latest_version = f.read().strip()

        # Compare versions
        if _compare_versions(latest_version, __version__) > 0:
            return True

        return False
    except Exception as e:
        print(f"Update check error: {e}")
        return False

def _compare_versions(v1: str, v2: str) -> int:
    """Compare two version strings (returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal)"""
    v1_parts = [int(x) for x in v1.split('.')]
    v2_parts = [int(x) for x in v2.split('.')]

    for i in range(max(len(v1_parts), len(v2_parts))):
        p1 = v1_parts[i] if i < len(v1_parts) else 0
        p2 = v2_parts[i] if i < len(v2_parts) else 0

        if p1 > p2:
            return 1
        elif p1 < p2:
            return -1

    return 0

def download_update(destination: Path) -> bool:
    """Download the latest version from G: drive"""
    try:
        config = ConfigManager()
        update_base = config.get('Application', 'update_url').replace('latest_version.txt', '')
        exe_path = Path(update_base) / 'PMTracker.exe'

        if not exe_path.exists():
            return False

        # Copy new version to destination
        import shutil
        shutil.copy(exe_path, destination)
        return True
    except Exception as e:
        print(f"Update download error: {e}")
        return False
