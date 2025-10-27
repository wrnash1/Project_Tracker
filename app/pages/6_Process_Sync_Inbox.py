"""
Process Sync Inbox - Admin tool to merge synced data into master database
"""

import streamlit as st
import pandas as pd
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vtrack import auth
from src.vtrack.database import MasterProjectsDB, SYNC_INBOX, ARCHIVE
from app.styles import apply_verizon_theme
from app import sidebar

st.set_page_config(page_title="Process Sync Inbox", page_icon="⚙️", layout="wide")
apply_verizon_theme()
auth.require_role(['Associate Director'])
sidebar.show_sidebar()

st.markdown("""
    <h1>⚙️ Process Sync Inbox</h1>
    <div class="vz-title-accent"></div>
    <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Review and merge pending synchronizations from project managers
    </p>
""", unsafe_allow_html=True)

# Get list of pending sync files
SYNC_INBOX.mkdir(parents=True, exist_ok=True)
ARCHIVE.mkdir(parents=True, exist_ok=True)

sync_files = sorted(SYNC_INBOX.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

# Summary metrics
st.markdown("### 📊 Inbox Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(sync_files)}</div>
            <div class="metric-label">Pending Syncs</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    archive_files = list(ARCHIVE.glob("*.json"))
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(archive_files)}</div>
            <div class="metric-label">Processed</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    total_items = 0
    for sync_file in sync_files:
        with open(sync_file, 'r') as f:
            data = json.load(f)
            total_items += len(data.get('projects', []))
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_items}</div>
            <div class="metric-label">Total Items</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Process all button
if len(sync_files) > 0:
    st.markdown("### 🚀 Quick Actions")
    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_b:
        if st.button("⚡ Process All Syncs", use_container_width=True, type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            projects_db = MasterProjectsDB()
            projects_db.connect()
            
            total_processed = 0
            total_files = len(sync_files)
            
            for idx, sync_file in enumerate(sync_files):
                status_text.text(f"Processing {sync_file.name}...")
                
                try:
                    with open(sync_file, 'r') as f:
                        data = json.load(f)
                    
                    # Process projects
                    for project in data.get('projects', []):
                        try:
                            # Check if project exists by ccr_nfid
                            existing = projects_db.fetchone(
                                "SELECT project_id FROM projects WHERE ccr_nfid = ?",
                                (project['ccr_nfid'],)
                            )
                            
                            if existing:
                                # Update existing project
                                projects_db.execute("""
                                    UPDATE projects SET
                                        name = ?, status = ?, phase = ?, notes = ?,
                                        customer = ?, clli = ?, site_address = ?,
                                        current_queue = ?, system_type = ?,
                                        updated_at = CURRENT_TIMESTAMP
                                    WHERE ccr_nfid = ?
                                """, (
                                    project['name'], project['status'], project.get('phase'),
                                    project.get('notes'), project.get('customer'),
                                    project.get('clli'), project.get('site_address'),
                                    project.get('current_queue'), project.get('system_type'),
                                    project['ccr_nfid']
                                ))
                            else:
                                # Insert new project
                                projects_db.execute("""
                                    INSERT INTO projects (
                                        name, ccr_nfid, program_id, project_type_id, pm_id,
                                        status, phase, notes, nfid, customer, clli,
                                        rft_date, system_type, current_queue, site_address,
                                        project_start_date, project_complete_date
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    project['name'], project['ccr_nfid'],
                                    project.get('program_id'), project.get('project_type_id'),
                                    project['pm_id'], project['status'], project.get('phase'),
                                    project.get('notes'), project.get('nfid'),
                                    project.get('customer'), project.get('clli'),
                                    project.get('rft_date'), project.get('system_type'),
                                    project.get('current_queue'), project.get('site_address'),
                                    project.get('project_start_date'), project.get('project_complete_date')
                                ))
                            
                            total_processed += 1
                        except Exception as e:
                            st.warning(f"Error processing project {project.get('name')}: {e}")
                    
                    # Move to archive
                    archive_path = ARCHIVE / sync_file.name
                    sync_file.rename(archive_path)
                    
                except Exception as e:
                    st.error(f"Error processing file {sync_file.name}: {e}")
                
                progress_bar.progress((idx + 1) / total_files)
            
            projects_db.close()
            status_text.empty()
            progress_bar.empty()
            
            st.success(f"✅ Processed {total_files} sync files with {total_processed} projects!")
            st.balloons()
            st.rerun()

    st.markdown("---")

# Display pending sync files
if len(sync_files) > 0:
    st.markdown("### 📦 Pending Sync Files")
    
    for sync_file in sync_files:
        # Read sync file
        with open(sync_file, 'r') as f:
            data = json.load(f)
        
        username = data.get('username', 'Unknown')
        timestamp = data.get('sync_timestamp', 'Unknown')
        num_projects = len(data.get('projects', []))
        num_kpis = len(data.get('kpi_snapshots', []))
        num_deps = len(data.get('project_dependencies', []))
        num_contacts = len(data.get('project_contacts', []))
        
        total_items = num_projects + num_kpis + num_deps + num_contacts
        
        with st.expander(f"📄 {sync_file.name} - {username} ({total_items} items)", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                    **Sync Details:**
                    - **User:** {username}
                    - **Timestamp:** {timestamp}
                    - **Projects:** {num_projects}
                    - **KPI Snapshots:** {num_kpis}
                    - **Dependencies:** {num_deps}
                    - **Contacts:** {num_contacts}
                """)
                
                # Show project names
                if num_projects > 0:
                    st.markdown("**Projects in this sync:**")
                    for project in data['projects'][:5]:  # Show first 5
                        st.markdown(f"- {project['name']} ({project['ccr_nfid']}) - {project['status']}")
                    if num_projects > 5:
                        st.markdown(f"*...and {num_projects - 5} more*")
            
            with col2:
                # Process this file button
                if st.button(f"✅ Process", key=f"process_{sync_file.name}"):
                    projects_db = MasterProjectsDB()
                    projects_db.connect()
                    
                    processed_count = 0
                    
                    try:
                        # Process projects
                        for project in data.get('projects', []):
                            try:
                                existing = projects_db.fetchone(
                                    "SELECT project_id FROM projects WHERE ccr_nfid = ?",
                                    (project['ccr_nfid'],)
                                )
                                
                                if existing:
                                    projects_db.execute("""
                                        UPDATE projects SET
                                            name = ?, status = ?, phase = ?, notes = ?,
                                            customer = ?, clli = ?, site_address = ?,
                                            current_queue = ?, system_type = ?,
                                            updated_at = CURRENT_TIMESTAMP
                                        WHERE ccr_nfid = ?
                                    """, (
                                        project['name'], project['status'], project.get('phase'),
                                        project.get('notes'), project.get('customer'),
                                        project.get('clli'), project.get('site_address'),
                                        project.get('current_queue'), project.get('system_type'),
                                        project['ccr_nfid']
                                    ))
                                else:
                                    projects_db.execute("""
                                        INSERT INTO projects (
                                            name, ccr_nfid, program_id, project_type_id, pm_id,
                                            status, phase, notes, nfid, customer, clli,
                                            rft_date, system_type, current_queue, site_address,
                                            project_start_date, project_complete_date
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        project['name'], project['ccr_nfid'],
                                        project.get('program_id'), project.get('project_type_id'),
                                        project['pm_id'], project['status'], project.get('phase'),
                                        project.get('notes'), project.get('nfid'),
                                        project.get('customer'), project.get('clli'),
                                        project.get('rft_date'), project.get('system_type'),
                                        project.get('current_queue'), project.get('site_address'),
                                        project.get('project_start_date'), project.get('project_complete_date')
                                    ))
                                
                                processed_count += 1
                            except Exception as e:
                                st.warning(f"Error: {e}")
                        
                        # Move to archive
                        archive_path = ARCHIVE / sync_file.name
                        sync_file.rename(archive_path)
                        
                        projects_db.close()
                        
                        st.success(f"✅ Processed {processed_count} projects!")
                        st.rerun()
                        
                    except Exception as e:
                        projects_db.close()
                        st.error(f"Error: {e}")
                
                # View JSON button
                if st.button(f"👁️ View JSON", key=f"view_{sync_file.name}"):
                    st.json(data)

else:
    st.success("✅ Inbox is empty! No pending syncs to process.")
    st.info("💡 When project managers sync their data, files will appear here for you to review and merge.")

# Archive section
st.markdown("---")
st.markdown("### 📚 Recently Processed")

if len(archive_files) > 0:
    st.markdown(f"**Last 10 processed syncs:**")
    
    recent_archives = sorted(archive_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]
    
    for archive_file in recent_archives:
        mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
        st.markdown(f"- ✓ {archive_file.name} - Processed at {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.info("No processed syncs yet.")
