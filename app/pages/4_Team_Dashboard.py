"""Team Dashboard - Admin view of all projects"""
import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.vtrack import auth
from app.styles import apply_verizon_theme
from app import sidebar

st.set_page_config(page_title="Team Dashboard", page_icon="👥", layout="wide")
apply_verizon_theme()
auth.require_role(['Associate Director', 'Director'])
sidebar.show_sidebar()

st.markdown('<h1>👥 Team Dashboard</h1><div class="vz-title-accent"></div>', unsafe_allow_html=True)
st.info("🚧 **Coming Soon:** View all team projects and manage team resources")
