"""Import Data"""
import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.vtrack import auth
from app.styles import apply_verizon_theme
from app import sidebar

st.set_page_config(page_title="Import Data", layout="wide")
apply_verizon_theme()
auth.require_auth()
sidebar.show_sidebar()

st.markdown('<h1>Import Data</h1><div class="vz-title-accent"></div>', unsafe_allow_html=True)
st.info("🚧 **Coming Soon:** This feature is under development")
