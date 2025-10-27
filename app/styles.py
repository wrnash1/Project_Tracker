"""
Custom CSS styles for Verizon Tracker
Modern, clean design with Verizon branding
"""

def get_custom_css():
    """Return custom CSS for the application"""
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* Main container styling */
    .main {
        padding: 2rem;
    }

    /* Header styling */
    h1 {
        color: #000000;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    h2 {
        color: #000000;
        font-weight: 600;
        font-size: 1.75rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    h3 {
        color: #333333;
        font-weight: 600;
        font-size: 1.25rem;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    /* Verizon Red accent line under main title */
    .vz-title-accent {
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #EE0000 0%, #CD040B 100%);
        margin: 0.5rem 0 1.5rem 0;
        border-radius: 2px;
    }

    /* Card styling */
    .vz-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #E5E5E5;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .vz-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }

    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F8F8 100%);
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 4px solid #EE0000;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #000000;
        line-height: 1;
        margin-bottom: 0.25rem;
    }

    .metric-label {
        font-size: 0.875rem;
        color: #666666;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #EE0000 0%, #CD040B 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.625rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 6px rgba(238, 0, 0, 0.2);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #CD040B 0%, #A00309 100%);
        box-shadow: 0 4px 12px rgba(238, 0, 0, 0.3);
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Secondary button */
    .stButton > button[kind="secondary"] {
        background: white;
        color: #EE0000;
        border: 2px solid #EE0000;
        box-shadow: none;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #FFF5F5;
        border-color: #CD040B;
    }

    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1.5px solid #D0D0D0;
        padding: 0.625rem 0.875rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #EE0000;
        box-shadow: 0 0 0 3px rgba(238, 0, 0, 0.1);
    }

    /* Data editor / table styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000 0%, #1A1A1A 100%);
        padding: 2rem 1rem;
    }

    [data-testid="stSidebar"] .element-container {
        color: white;
    }

    /* Sidebar text */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: white !important;
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .status-active {
        background: #E8F5E9;
        color: #2E7D32;
    }

    .status-hold {
        background: #FFF3E0;
        color: #E65100;
    }

    .status-completed {
        background: #E3F2FD;
        color: #1565C0;
    }

    .status-cancelled {
        background: #FFEBEE;
        color: #C62828;
    }

    /* Alert/Message styling */
    .stAlert {
        border-radius: 8px;
        border-left-width: 4px;
    }

    /* Success message */
    .stSuccess {
        background: #E8F5E9;
        color: #2E7D32;
        border-left-color: #4CAF50;
    }

    /* Error message */
    .stError {
        background: #FFEBEE;
        color: #C62828;
        border-left-color: #EE0000;
    }

    /* Warning message */
    .stWarning {
        background: #FFF3E0;
        color: #E65100;
        border-left-color: #FF9800;
    }

    /* Info message */
    .stInfo {
        background: #E3F2FD;
        color: #1565C0;
        border-left-color: #2196F3;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: #F8F8F8;
        border-radius: 8px;
        border: 1px solid #E5E5E5;
        font-weight: 600;
        padding: 1rem;
    }

    .streamlit-expanderHeader:hover {
        background: #F0F0F0;
        border-color: #EE0000;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        border-bottom: 2px solid #E5E5E5;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #666666;
        border-radius: 8px 8px 0 0;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #F5F5F5;
        color: #000000;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        color: #EE0000;
        border-bottom: 3px solid #EE0000;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #EE0000 !important;
    }

    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #E5E5E5;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #F5F5F5;
    }

    ::-webkit-scrollbar-thumb {
        background: #D0D0D0;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #EE0000;
    }

    /* Login page specific */
    .login-container {
        max-width: 400px;
        margin: 4rem auto;
        padding: 2.5rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    }

    .login-logo {
        text-align: center;
        margin-bottom: 2rem;
    }

    .login-title {
        text-align: center;
        font-size: 1.75rem;
        font-weight: 700;
        color: #000000;
        margin-bottom: 0.5rem;
    }

    .login-subtitle {
        text-align: center;
        color: #666666;
        margin-bottom: 2rem;
    }
    </style>
    """


def apply_verizon_theme():
    """Apply the Verizon theme to the Streamlit app"""
    import streamlit as st
    st.markdown(get_custom_css(), unsafe_allow_html=True)
