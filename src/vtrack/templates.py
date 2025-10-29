"""
Project Templates System for Verizon Tracker
Save and reuse project configurations
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from .database import G_DRIVE, MasterProjectsDB
import streamlit as st


# Templates directory
TEMPLATES_DIR = G_DRIVE / "project_templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


class ProjectTemplate:
    """Manage project templates"""

    @staticmethod
    def create_template_from_project(project: Dict, template_name: str, description: str = "") -> bool:
        """
        Create a template from an existing project

        Args:
            project: Project dictionary
            template_name: Name for the template
            description: Optional description

        Returns:
            Success boolean
        """
        try:
            # Fields to save in template
            template_fields = [
                'program_id', 'project_type_id', 'phase',
                'customer', 'system_type', 'current_queue',
                'clli', 'site_address', 'city', 'state', 'zip_code',
                'circuit_id', 'circuit_type', 'bandwidth',
                'project_priority', 'contract_value',
                'scorecard_week1_q', 'scorecard_week2_q', 'scorecard_week3_q', 'scorecard_week4_q',
                'wbs_code', 'budget_amount'
            ]

            template_data = {
                'template_name': template_name,
                'description': description,
                'created_by': st.session_state.user_id if hasattr(st.session_state, 'user_id') else None,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'fields': {}
            }

            # Copy relevant fields
            for field in template_fields:
                if field in project and project[field] is not None:
                    template_data['fields'][field] = project[field]

            # Save to file
            filename = f"{template_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            filepath = TEMPLATES_DIR / filename

            with open(filepath, 'w') as f:
                json.dump(template_data, f, indent=2)

            return True

        except Exception as e:
            return False

    @staticmethod
    def get_all_templates() -> List[Dict]:
        """
        Get all available templates

        Returns:
            List of template dictionaries
        """
        try:
            templates = []

            for template_file in TEMPLATES_DIR.glob("*.json"):
                try:
                    with open(template_file, 'r') as f:
                        template = json.load(f)
                        template['file_path'] = str(template_file)
                        template['file_name'] = template_file.name
                        templates.append(template)
                except:
                    continue

            # Sort by created_at descending
            templates.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            return templates

        except Exception as e:
            return []

    @staticmethod
    def load_template(template_file: str) -> Optional[Dict]:
        """
        Load a specific template

        Args:
            template_file: Template filename

        Returns:
            Template dictionary or None
        """
        try:
            filepath = TEMPLATES_DIR / template_file

            with open(filepath, 'r') as f:
                return json.load(f)

        except Exception as e:
            return None

    @staticmethod
    def delete_template(template_file: str) -> bool:
        """
        Delete a template

        Args:
            template_file: Template filename

        Returns:
            Success boolean
        """
        try:
            filepath = TEMPLATES_DIR / template_file
            filepath.unlink()
            return True

        except Exception as e:
            return False

    @staticmethod
    def apply_template_to_project(template: Dict, project_data: Dict) -> Dict:
        """
        Apply template fields to project data

        Args:
            template: Template dictionary
            project_data: Project data dictionary

        Returns:
            Updated project data
        """
        if 'fields' in template:
            for field, value in template['fields'].items():
                if field not in project_data or project_data[field] is None:
                    project_data[field] = value

        return project_data


def show_template_selector(on_select_callback):
    """Display template selector UI"""

    templates = ProjectTemplate.get_all_templates()

    if templates:
        st.markdown("### 📋 Available Templates")

        for template in templates:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"""
                        <div style="
                            background: white;
                            padding: 1rem;
                            border-radius: 8px;
                            border-left: 4px solid #EE0000;
                            margin-bottom: 0.5rem;
                        ">
                            <div style="font-weight: 600; color: #333; font-size: 1rem;">
                                {template['template_name']}
                            </div>
                            <div style="color: #666; font-size: 0.85rem; margin-top: 0.25rem;">
                                {template.get('description', 'No description')}
                            </div>
                            <div style="color: #999; font-size: 0.75rem; margin-top: 0.5rem;">
                                Created: {template.get('created_at', 'Unknown')} |
                                Fields: {len(template.get('fields', {}))}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("Use Template", key=f"use_{template['file_name']}", use_container_width=True):
                        if on_select_callback:
                            on_select_callback(template)

                with col3:
                    if st.button("Delete", key=f"del_{template['file_name']}", use_container_width=True, type="secondary"):
                        if ProjectTemplate.delete_template(template['file_name']):
                            st.success("Template deleted!")
                            st.rerun()
    else:
        st.info("No templates available. Create your first template from an existing project!")


def show_template_creation_form():
    """Display form to create new template"""

    st.markdown("### ➕ Create New Template")

    with st.form("create_template_form"):
        template_name = st.text_input("Template Name*", placeholder="e.g., Standard Fiber Installation")
        description = st.text_area("Description", placeholder="Brief description of this template...")

        # Common fields
        st.markdown("**Template Fields:**")

        col1, col2 = st.columns(2)

        with col1:
            program_id = st.number_input("Program ID", min_value=0, value=0)
            project_type_id = st.number_input("Project Type ID", min_value=0, value=0)
            phase = st.text_input("Phase")
            customer = st.text_input("Customer (optional)")
            system_type = st.text_input("System Type")

        with col2:
            current_queue = st.text_input("Current Queue")
            project_priority = st.selectbox("Priority", ["", "High", "Medium", "Low"])
            circuit_type = st.text_input("Circuit Type")
            bandwidth = st.text_input("Bandwidth")
            wbs_code = st.text_input("WBS Code")

        submitted = st.form_submit_button("Create Template", use_container_width=True)

        if submitted:
            if not template_name:
                st.error("Template name is required!")
            else:
                # Create template data
                template_data = {
                    'program_id': program_id if program_id > 0 else None,
                    'project_type_id': project_type_id if project_type_id > 0 else None,
                    'phase': phase if phase else None,
                    'customer': customer if customer else None,
                    'system_type': system_type if system_type else None,
                    'current_queue': current_queue if current_queue else None,
                    'project_priority': project_priority if project_priority else None,
                    'circuit_type': circuit_type if circuit_type else None,
                    'bandwidth': bandwidth if bandwidth else None,
                    'wbs_code': wbs_code if wbs_code else None
                }

                # Create template
                if ProjectTemplate.create_template_from_project(
                    template_data,
                    template_name,
                    description
                ):
                    st.success(f"✅ Template '{template_name}' created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create template. Please try again.")
