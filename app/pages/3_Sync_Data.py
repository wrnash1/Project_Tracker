"""
Sync Data Page
Push local changes to the sync inbox
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vtrack import auth, sync
from app.styles import apply_verizon_theme
from app import sidebar

st.set_page_config(page_title="Sync Data - Verizon Tracker", page_icon="🔄", layout="wide")
apply_verizon_theme()
auth.require_role(['Sr. Project Manager'])
sidebar.show_sidebar()

st.markdown("""
    <h1>🔄 Sync Data</h1>
    <div class="vz-title-accent"></div>
    <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Push your local changes to the master database
    </p>
""", unsafe_allow_html=True)

# Get local database
local_db = st.session_state.local_db
username = st.session_state.username

# Get pending sync counts
counts = sync.get_pending_sync_counts(local_db)
total_pending = sum(counts.values())

# Display sync status
st.markdown("### 📊 Sync Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{counts.get('projects', 0)}</div>
            <div class="metric-label">Projects</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{counts.get('kpis', 0)}</div>
            <div class="metric-label">KPI Snapshots</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{counts.get('dependencies', 0)}</div>
            <div class="metric-label">Dependencies</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{counts.get('contacts', 0)}</div>
            <div class="metric-label">Contacts</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Show pending changes
if total_pending > 0:
    st.markdown("### 📋 Pending Changes")

    # Show pending projects
    if counts.get('projects', 0) > 0:
        st.markdown("**Projects to Sync:**")
        projects = local_db.fetchall("""
            SELECT name, ccr_nfid, status, sync_status
            FROM projects
            WHERE sync_status IN ('new', 'updated')
        """)
        df = pd.DataFrame([dict(p) for p in projects])
        st.dataframe(df, hide_index=True, use_container_width=True)

    # Show pending KPIs
    if counts.get('kpis', 0) > 0:
        with st.expander(f"📸 KPI Snapshots ({counts['kpis']})", expanded=False):
            kpis = local_db.fetchall("""
                SELECT k.snapshot_date, p.name as project_name, k.budget_status, k.schedule_status
                FROM kpi_snapshots k
                JOIN projects p ON k.local_project_id = p.local_id
                WHERE k.sync_status IN ('new', 'updated')
            """)
            df_kpis = pd.DataFrame([dict(k) for k in kpis])
            st.dataframe(df_kpis, hide_index=True, use_container_width=True)

    # Sync button
    st.markdown("---")
    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_b:
        if st.button("🔄 Sync to Master", use_container_width=True, type="primary"):
            with st.spinner("Syncing data to master database..."):
                success, message, stats = sync.sync_local_to_inbox(local_db, username)

                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    st.info("💡 Your changes have been sent to the sync inbox. An administrator will process them to merge into the master database.")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

    st.markdown("### ℹ️ How Sync Works")
    st.markdown("""
        <div class="vz-card">
            <ol>
                <li><strong>Local Changes:</strong> All your new and updated projects, KPIs, dependencies, and contacts are tracked locally</li>
                <li><strong>Sync to Inbox:</strong> Click "Sync to Master" to create a sync bundle and send it to the shared inbox</li>
                <li><strong>Admin Processing:</strong> An Associate Director will process your sync bundle and merge it into the master database</li>
                <li><strong>Safe & Secure:</strong> This inbox model prevents data corruption and allows for review before merging</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)

else:
    st.success("✅ All changes are synced! You have no pending changes.")
    st.info("💡 Make changes to projects, add KPI snapshots, or create dependencies in 'My Dashboard' to have items to sync.")

# Sync history
st.markdown("---")
st.markdown("### 📜 Recent Syncs")

# Get list of sync files for this user
import os
sync_files = []
if sync.SYNC_INBOX.exists():
    sync_files = [f for f in os.listdir(sync.SYNC_INBOX) if f.startswith(f"sync_{username}_")]
    sync_files.sort(reverse=True)

if sync_files:
    st.markdown(f"**Last 5 sync operations:**")
    for sync_file in sync_files[:5]:
        # Parse filename for timestamp
        parts = sync_file.replace('.json', '').split('_')
        if len(parts) >= 3:
            date_part = parts[2] if len(parts) > 2 else "Unknown"
            time_part = parts[3] if len(parts) > 3 else ""
            st.markdown(f"- 📦 {sync_file} - Waiting for processing")
else:
    st.info("No sync history yet. Create some projects and sync them!")
