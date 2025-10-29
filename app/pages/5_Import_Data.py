"""
Import Data - Bulk import projects from Excel/CSV files
"""

import streamlit as st
import pandas as pd
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vtrack import auth
from src.vtrack.database import MasterProjectsDB, MasterUsersDB
from app.styles import apply_verizon_theme
from app import sidebar

st.set_page_config(page_title="Import Data", page_icon="📤", layout="wide")
apply_verizon_theme()
auth.require_role(['Associate Director'])
sidebar.show_sidebar()

st.markdown("""
    <h1>📤 Import Data</h1>
    <div class="vz-title-accent"></div>
    <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Bulk import projects from Excel or CSV files
    </p>
""", unsafe_allow_html=True)

# === INSTRUCTIONS ===
st.markdown("### 📋 Import Instructions")

with st.expander("ℹ️ How to Import Data", expanded=True):
    st.markdown("""
    **Step 1: Prepare Your File**
    - Supported formats: CSV (.csv) or Excel (.xlsx)
    - Required columns: `name`, `ccr_nfid`, `pm_id`, `status`
    - Optional columns: `customer`, `clli`, `site_address`, `phase`, `notes`, etc.
    
    **Step 2: Required Column Mapping**
    - **name**: Project name (text)
    - **ccr_nfid**: Unique identifier (text)
    - **pm_id**: Project Manager user ID (number) - see User ID list below
    - **status**: Must be one of: Active, On Hold, Completed, Cancelled
    
    **Step 3: Optional Columns**
    - program_id, project_type_id, customer, clli, site_address, phase, notes
    - nfid, system_type, current_queue, rft_date
    - project_start_date, project_complete_date
    
    **Step 4: Upload and Review**
    - Upload your file below
    - Review the preview
    - Click "Import Projects" to add to database
    """)

# === USER ID REFERENCE ===
st.markdown("### 👥 User ID Reference")

users_db = MasterUsersDB()
users_db.connect()
users = users_db.fetchall("SELECT user_id, username, full_name, role FROM users WHERE active = 1")
users_db.close()

if users:
    users_df = pd.DataFrame([dict(u) for u in users])
    st.dataframe(
        users_df[['user_id', 'username', 'full_name', 'role']],
        hide_index=True,
        use_container_width=True,
        column_config={
            "user_id": "User ID",
            "username": "Username",
            "full_name": "Full Name",
            "role": "Role"
        }
    )

# === DOWNLOAD TEMPLATE ===
st.markdown("---")
st.markdown("### 📥 Download Template")

template_data = {
    'name': ['Sample Project 1', 'Sample Project 2'],
    'ccr_nfid': ['CCR-001', 'CCR-002'],
    'pm_id': [2, 2],  # pmuser ID
    'status': ['Active', 'Active'],
    'customer': ['Customer A', 'Customer B'],
    'clli': ['SITE01', 'SITE02'],
    'site_address': ['123 Main St', '456 Oak Ave'],
    'phase': ['Planning', 'Execution'],
    'notes': ['Sample note 1', 'Sample note 2']
}

template_df = pd.DataFrame(template_data)

col_t1, col_t2, col_t3 = st.columns([2, 1, 2])

with col_t2:
    # CSV Template
    csv_template = template_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV Template",
        data=csv_template,
        file_name="vtrack_import_template.csv",
        mime="text/csv",
        use_container_width=True
    )

# === FILE UPLOAD ===
st.markdown("---")
st.markdown("### 📤 Upload File")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=['csv', 'xlsx'],
    help="Select a CSV or Excel file containing project data"
)

if uploaded_file is not None:
    try:
        # Read file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File loaded successfully! Found {len(df)} rows.")
        
        # === PREVIEW DATA ===
        st.markdown("### 👀 Preview Data")
        st.dataframe(df.head(10), use_container_width=True)
        
        # === VALIDATION ===
        st.markdown("### ✓ Validation")
        
        errors = []
        warnings = []
        
        # Check required columns
        required_cols = ['name', 'ccr_nfid', 'pm_id', 'status']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        else:
            # Check for empty required fields
            for col in required_cols:
                if df[col].isna().any():
                    null_count = df[col].isna().sum()
                    errors.append(f"Column '{col}' has {null_count} empty values")
            
            # Validate status values
            if 'status' in df.columns:
                valid_statuses = ['Active', 'On Hold', 'Completed', 'Cancelled']
                invalid_statuses = df[~df['status'].isin(valid_statuses)]['status'].unique()
                if len(invalid_statuses) > 0:
                    errors.append(f"Invalid status values: {', '.join(map(str, invalid_statuses))}")
            
            # Check for duplicate ccr_nfid
            if 'ccr_nfid' in df.columns:
                duplicates = df[df.duplicated(subset=['ccr_nfid'], keep=False)]
                if len(duplicates) > 0:
                    errors.append(f"Found {len(duplicates)} duplicate CCR/NFID values in file")
            
            # Check if pm_id exists
            if 'pm_id' in df.columns:
                user_ids = [u['user_id'] for u in users]
                invalid_pms = df[~df['pm_id'].isin(user_ids)]['pm_id'].unique()
                if len(invalid_pms) > 0:
                    errors.append(f"Invalid PM IDs (user doesn't exist): {', '.join(map(str, invalid_pms))}")
        
        # Display validation results
        if errors:
            st.error("❌ Validation Errors:")
            for error in errors:
                st.markdown(f"- {error}")
        else:
            st.success("✅ All validation checks passed!")
        
        if warnings:
            st.warning("⚠️ Warnings:")
            for warning in warnings:
                st.markdown(f"- {warning}")
        
        # === IMPORT BUTTON ===
        st.markdown("---")
        
        if not errors:
            col_i1, col_i2, col_i3 = st.columns([2, 1, 2])
            
            with col_i2:
                if st.button("🚀 Import Projects", use_container_width=True, type="primary"):
                    projects_db = MasterProjectsDB()
                    projects_db.connect()
                    
                    success_count = 0
                    error_count = 0
                    skipped_count = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, row in df.iterrows():
                        status_text.text(f"Processing row {idx + 1} of {len(df)}...")
                        
                        try:
                            # Check if project already exists
                            existing = projects_db.fetchone(
                                "SELECT project_id FROM projects WHERE ccr_nfid = ?",
                                (row['ccr_nfid'],)
                            )
                            
                            if existing:
                                skipped_count += 1
                                continue
                            
                            # Insert project
                            projects_db.execute("""
                                INSERT INTO projects (
                                    name, ccr_nfid, program_id, project_type_id, pm_id,
                                    status, phase, notes, nfid, customer, clli,
                                    rft_date, system_type, current_queue, site_address,
                                    project_start_date, project_complete_date
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                row['name'],
                                row['ccr_nfid'],
                                row.get('program_id'),
                                row.get('project_type_id'),
                                row['pm_id'],
                                row['status'],
                                row.get('phase'),
                                row.get('notes'),
                                row.get('nfid'),
                                row.get('customer'),
                                row.get('clli'),
                                row.get('rft_date'),
                                row.get('system_type'),
                                row.get('current_queue'),
                                row.get('site_address'),
                                row.get('project_start_date'),
                                row.get('project_complete_date')
                            ))
                            
                            success_count += 1
                            
                        except Exception as e:
                            error_count += 1
                            st.warning(f"Error importing row {idx + 1}: {e}")
                        
                        progress_bar.progress((idx + 1) / len(df))
                    
                    projects_db.close()
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Summary
                    st.success(f"""
                    ✅ Import Complete!
                    - **Imported:** {success_count} projects
                    - **Skipped:** {skipped_count} (already exist)
                    - **Errors:** {error_count}
                    """)
                    
                    if success_count > 0:
                        st.balloons()
        else:
            st.error("⚠️ Fix validation errors before importing.")
            
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.info("Make sure your file is a valid CSV or Excel file with the correct format.")

else:
    st.info("👆 Upload a CSV or Excel file to begin import.")

# === IMPORT HISTORY ===
st.markdown("---")
st.markdown("### 📜 Recent Imports")
st.info("Import history tracking will be added in a future update.")
