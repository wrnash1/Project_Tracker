"""
Project Templates Page
Manage and use project templates
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vtrack import auth
from src.vtrack.templates import ProjectTemplate, show_template_selector, show_template_creation_form
from app.styles import apply_verizon_theme

# Page config
st.set_page_config(
    page_title="Project Templates - Verizon Tracker",
    page_icon="📋",
    layout="wide"
)

# Apply theme
apply_verizon_theme()

# Require authentication
auth.require_auth()

# Show sidebar
from app import sidebar
sidebar.show_sidebar()

# Main content
st.markdown("""
    <h1>📋 Project Templates</h1>
    <div class="vz-title-accent"></div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="vz-card" style="margin-bottom: 2rem;">
        <p style="margin: 0;">
            Create reusable project templates to speed up project creation.
            Templates store common field values that can be applied to new projects.
        </p>
    </div>
""", unsafe_allow_html=True)

# Tabs for different template operations
tab1, tab2, tab3 = st.tabs(["📚 Browse Templates", "➕ Create Template", "📊 Template Stats"])

with tab1:
    st.markdown("## Available Templates")

    def on_template_selected(template):
        st.session_state.selected_template = template
        st.success(f"Template '{template['template_name']}' selected! Use it when creating a new project.")

    show_template_selector(on_template_selected)

    # Show selected template details
    if hasattr(st.session_state, 'selected_template') and st.session_state.selected_template:
        st.markdown("---")
        st.markdown("### 📋 Selected Template Details")

        template = st.session_state.selected_template

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
                <div class="vz-card">
                    <h4>{template['template_name']}</h4>
                    <p><strong>Description:</strong> {template.get('description', 'N/A')}</p>
                    <p><strong>Created:</strong> {template.get('created_at', 'Unknown')}</p>
                    <p><strong>Fields:</strong> {len(template.get('fields', {}))}</p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("**Template Fields:**")
            if template.get('fields'):
                for field, value in template['fields'].items():
                    if value is not None:
                        st.markdown(f"- **{field.replace('_', ' ').title()}:** {value}")
            else:
                st.info("No fields defined in this template.")

        if st.button("🗑️ Clear Selection"):
            del st.session_state.selected_template
            st.rerun()

with tab2:
    show_template_creation_form()

with tab3:
    st.markdown("## Template Statistics")

    templates = ProjectTemplate.get_all_templates()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #673AB7;">{len(templates)}</div>
                <div class="metric-label">Total Templates</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        # Count templates with descriptions
        with_desc = sum(1 for t in templates if t.get('description'))
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #4CAF50;">{with_desc}</div>
                <div class="metric-label">With Descriptions</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        # Average fields per template
        if templates:
            avg_fields = sum(len(t.get('fields', {})) for t in templates) / len(templates)
        else:
            avg_fields = 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #2196F3;">{avg_fields:.1f}</div>
                <div class="metric-label">Avg Fields/Template</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        # Most recent
        if templates:
            most_recent = templates[0].get('created_at', 'N/A')[:10]
        else:
            most_recent = 'N/A'
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #FF9800; font-size: 1.2rem;">{most_recent}</div>
                <div class="metric-label">Most Recent</div>
            </div>
        """, unsafe_allow_html=True)

    if templates:
        st.markdown("---")
        st.markdown("### 📊 Templates List")

        # Create a simple table
        import pandas as pd

        template_data = []
        for t in templates:
            template_data.append({
                'Name': t['template_name'],
                'Description': t.get('description', 'N/A')[:50],
                'Fields': len(t.get('fields', {})),
                'Created': t.get('created_at', 'Unknown')[:10]
            })

        df = pd.DataFrame(template_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# Tips section
st.markdown("---")
st.markdown("### 💡 Tips for Using Templates")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="vz-card">
            <h4>🎯 Best Practices</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>Create templates for common project types</li>
                <li>Use descriptive names</li>
                <li>Add detailed descriptions</li>
                <li>Update templates regularly</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="vz-card">
            <h4>⚡ Quick Actions</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>Select a template from Browse tab</li>
                <li>Go to New Project page</li>
                <li>Template values auto-fill</li>
                <li>Modify as needed and save</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="vz-card">
            <h4>🔧 Template Fields</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>Program and Project Type</li>
                <li>Customer and Location</li>
                <li>Circuit and System Info</li>
                <li>Budget and WBS codes</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
