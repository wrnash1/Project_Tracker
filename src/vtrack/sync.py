"""
Synchronization module for Verizon Tracker
Handles syncing local data to master database via inbox system
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from .database import LocalProjectsDB, SYNC_INBOX, ARCHIVE


def create_sync_bundle(local_db: LocalProjectsDB, username: str) -> Dict[str, Any]:
    """
    Create a sync bundle containing all pending changes from local database
    Returns a dictionary with projects, KPIs, dependencies, and contacts
    """

    bundle = {
        "username": username,
        "sync_timestamp": datetime.now().isoformat(),
        "projects": [],
        "kpi_snapshots": [],
        "project_dependencies": [],
        "project_contacts": []
    }

    # Get all projects that need syncing (new or updated)
    projects = local_db.fetchall("""
        SELECT * FROM projects
        WHERE sync_status IN ('new', 'updated')
    """)

    for project in projects:
        bundle["projects"].append(dict(project))

    # Get KPI snapshots for those projects
    if projects:
        project_ids = [p['local_id'] for p in projects]
        placeholders = ','.join(['?' for _ in project_ids])

        kpis = local_db.fetchall(f"""
            SELECT * FROM kpi_snapshots
            WHERE local_project_id IN ({placeholders})
            AND sync_status IN ('new', 'updated')
        """, tuple(project_ids))

        for kpi in kpis:
            bundle["kpi_snapshots"].append(dict(kpi))

        # Get dependencies
        deps = local_db.fetchall(f"""
            SELECT * FROM project_dependencies
            WHERE local_project_id IN ({placeholders})
            AND sync_status IN ('new', 'updated')
        """, tuple(project_ids))

        for dep in deps:
            bundle["project_dependencies"].append(dict(dep))

        # Get contacts
        contacts = local_db.fetchall(f"""
            SELECT * FROM project_contacts
            WHERE local_project_id IN ({placeholders})
            AND sync_status IN ('new', 'updated')
        """, tuple(project_ids))

        for contact in contacts:
            bundle["project_contacts"].append(dict(contact))

    return bundle


def save_sync_bundle_to_inbox(bundle: Dict[str, Any], username: str) -> str:
    """
    Save sync bundle as JSON file in the sync inbox
    Returns the filename
    """

    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sync_{username}_{timestamp}.json"
    filepath = SYNC_INBOX / filename

    # Ensure inbox directory exists
    SYNC_INBOX.mkdir(parents=True, exist_ok=True)

    # Write JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(bundle, f, indent=2, default=str)

    return filename


def mark_items_as_synced(local_db: LocalProjectsDB):
    """
    Mark all items that were in 'new' or 'updated' status as 'synced'
    """

    tables = [
        'projects',
        'kpi_snapshots',
        'project_dependencies',
        'project_contacts'
    ]

    for table in tables:
        local_db.execute(f"""
            UPDATE {table}
            SET sync_status = 'synced'
            WHERE sync_status IN ('new', 'updated')
        """)


def get_pending_sync_counts(local_db: LocalProjectsDB) -> Dict[str, int]:
    """
    Get counts of items pending sync
    """

    counts = {}

    # Count projects
    result = local_db.fetchone("""
        SELECT COUNT(*) as count FROM projects
        WHERE sync_status IN ('new', 'updated')
    """)
    counts['projects'] = result['count'] if result else 0

    # Count KPIs
    result = local_db.fetchone("""
        SELECT COUNT(*) as count FROM kpi_snapshots
        WHERE sync_status IN ('new', 'updated')
    """)
    counts['kpis'] = result['count'] if result else 0

    # Count dependencies
    result = local_db.fetchone("""
        SELECT COUNT(*) as count FROM project_dependencies
        WHERE sync_status IN ('new', 'updated')
    """)
    counts['dependencies'] = result['count'] if result else 0

    # Count contacts
    result = local_db.fetchone("""
        SELECT COUNT(*) as count FROM project_contacts
        WHERE sync_status IN ('new', 'updated')
    """)
    counts['contacts'] = result['count'] if result else 0

    return counts


def sync_local_to_inbox(local_db: LocalProjectsDB, username: str) -> tuple[bool, str, Dict]:
    """
    Main sync function - creates bundle and saves to inbox
    Returns (success, message, stats)
    """

    try:
        # Get pending counts first
        counts = get_pending_sync_counts(local_db)

        # Check if there's anything to sync
        total = sum(counts.values())
        if total == 0:
            return False, "No pending changes to sync", counts

        # Create sync bundle
        bundle = create_sync_bundle(local_db, username)

        # Save to inbox
        filename = save_sync_bundle_to_inbox(bundle, username)

        # Mark items as synced
        mark_items_as_synced(local_db)

        message = f"Successfully synced {total} items to inbox ({filename})"
        return True, message, counts

    except Exception as e:
        return False, f"Sync failed: {str(e)}", {}
