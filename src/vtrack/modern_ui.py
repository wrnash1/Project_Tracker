"""
Modern UI Enhancements for Verizon Tracker
Advanced CSS animations, transitions, and visual effects
"""

import streamlit as st


def inject_modern_css():
    """Inject modern CSS animations and effects"""

    st.markdown("""
        <style>
        /* ===== Modern Animations ===== */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }

        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }

        /* Apply fade-in to main content */
        .main .block-container {
            animation: fadeIn 0.5s ease-out;
        }

        /* ===== Enhanced Cards ===== */
        .modern-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(238, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }

        .modern-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(238, 0, 0, 0.05), transparent);
            transition: left 0.5s;
        }

        .modern-card:hover::before {
            left: 100%;
        }

        .modern-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(238, 0, 0, 0.15);
        }

        /* ===== Glass Morphism Effect ===== */
        .glass-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        /* ===== Modern Buttons ===== */
        .stButton > button {
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(238, 0, 0, 0.3);
        }

        .stButton > button:active {
            transform: translateY(0);
        }

        /* ===== Loading Skeleton ===== */
        .skeleton {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 1000px 100%;
            animation: shimmer 2s infinite;
            border-radius: 8px;
            height: 20px;
            margin: 10px 0;
        }

        /* ===== Progress Bars ===== */
        .modern-progress {
            height: 12px;
            background: #E0E0E0;
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        }

        .modern-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #EE0000, #FF4444);
            border-radius: 12px;
            position: relative;
            overflow: hidden;
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .modern-progress-bar::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 2s infinite;
        }

        /* ===== Badges ===== */
        .modern-badge {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            background: linear-gradient(135deg, #EE0000, #CC0000);
            color: white;
            box-shadow: 0 2px 8px rgba(238, 0, 0, 0.3);
            transition: all 0.3s ease;
        }

        .modern-badge:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(238, 0, 0, 0.4);
        }

        /* ===== Tooltips ===== */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 8px;
            padding: 8px 12px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s, visibility 0.3s;
            font-size: 0.85rem;
            white-space: nowrap;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        /* ===== Modern Tables ===== */
        .dataframe {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        .dataframe thead tr {
            background: linear-gradient(135deg, #EE0000, #CC0000);
            color: white;
        }

        .dataframe tbody tr:hover {
            background: rgba(238, 0, 0, 0.05);
            transition: background 0.2s ease;
        }

        /* ===== Input Fields ===== */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div {
            border-radius: 12px;
            border: 2px solid #E0E0E0;
            transition: all 0.3s ease;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #EE0000;
            box-shadow: 0 0 0 3px rgba(238, 0, 0, 0.1);
        }

        /* ===== Sidebar Enhancements ===== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
        }

        [data-testid="stSidebar"] .element-container {
            animation: slideInRight 0.3s ease-out;
        }

        /* ===== Metric Cards Enhancement ===== */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #EE0000, #FF4444);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* ===== Tab Enhancement ===== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: #f8f9fa;
            padding: 8px;
            border-radius: 12px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #EE0000, #CC0000);
            color: white;
            box-shadow: 0 4px 12px rgba(238, 0, 0, 0.3);
        }

        /* ===== Expander Enhancement ===== */
        .streamlit-expanderHeader {
            border-radius: 12px;
            transition: all 0.3s ease;
            font-weight: 600;
        }

        .streamlit-expanderHeader:hover {
            background: rgba(238, 0, 0, 0.05);
        }

        /* ===== Success/Error Messages ===== */
        .stAlert {
            border-radius: 12px;
            border-left-width: 6px;
            animation: slideInRight 0.3s ease-out;
        }

        /* ===== Loading Spinner ===== */
        .stSpinner > div {
            border-top-color: #EE0000;
        }

        /* ===== Charts Enhancement ===== */
        .js-plotly-plot {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        /* ===== File Uploader ===== */
        [data-testid="stFileUploader"] {
            border-radius: 12px;
            border: 2px dashed #E0E0E0;
            transition: all 0.3s ease;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: #EE0000;
            background: rgba(238, 0, 0, 0.02);
        }

        /* ===== Custom Scrollbar ===== */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #EE0000, #CC0000);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #CC0000;
        }

        /* ===== Floating Action Button ===== */
        .fab {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #EE0000, #CC0000);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
            box-shadow: 0 6px 20px rgba(238, 0, 0, 0.4);
            cursor: pointer;
            transition: all 0.3s ease;
            z-index: 1000;
        }

        .fab:hover {
            transform: scale(1.1) rotate(90deg);
            box-shadow: 0 8px 25px rgba(238, 0, 0, 0.5);
        }

        /* ===== Notification Dot ===== */
        .notification-dot {
            width: 10px;
            height: 10px;
            background: #EE0000;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        /* ===== Grid Layout Enhancement ===== */
        .grid-container {
            display: grid;
            gap: 1rem;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        }

        /* ===== Spotlight Effect ===== */
        .spotlight {
            position: relative;
            overflow: hidden;
        }

        .spotlight::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(238,0,0,0.1) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .spotlight:hover::after {
            opacity: 1;
        }
        </style>
    """, unsafe_allow_html=True)


def create_loading_spinner(text: str = "Loading..."):
    """Create modern loading spinner HTML"""
    return f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem;
        ">
            <div style="
                width: 60px;
                height: 60px;
                border: 6px solid #f3f3f3;
                border-top: 6px solid #EE0000;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            "></div>
            <p style="margin-top: 1rem; color: #666; font-weight: 600;">{text}</p>
        </div>
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
    """


def create_modern_badge(text: str, color: str = "#EE0000"):
    """Create modern badge HTML"""
    return f"""
        <span class="modern-badge" style="background: linear-gradient(135deg, {color}, {color}cc);">
            {text}
        </span>
    """


def create_skeleton_loader(lines: int = 3):
    """Create skeleton loading animation"""
    skeletons = "\n".join([f'<div class="skeleton" style="width: {90-i*10}%;"></div>' for i in range(lines)])
    return f"<div>{skeletons}</div>"


def create_tooltip(text: str, tooltip: str):
    """Create tooltip HTML"""
    return f"""
        <div class="tooltip">
            {text}
            <span class="tooltiptext">{tooltip}</span>
        </div>
    """


def create_progress_bar(value: int, max_value: int = 100, color: str = "#EE0000"):
    """Create modern progress bar"""
    percentage = (value / max_value) * 100

    return f"""
        <div class="modern-progress">
            <div class="modern-progress-bar" style="width: {percentage}%; background: linear-gradient(90deg, {color}, {color}88);"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.85rem; color: #666;">
            <span>{value}</span>
            <span>{percentage:.0f}%</span>
        </div>
    """


def create_notification_badge(count: int):
    """Create notification badge with pulse animation"""
    if count == 0:
        return ""

    return f"""
        <div style="
            position: relative;
            display: inline-block;
            margin-left: 0.5rem;
        ">
            <div class="notification-dot" style="
                position: absolute;
                top: -5px;
                right: -5px;
            "></div>
            <span style="
                background: #EE0000;
                color: white;
                border-radius: 12px;
                padding: 0.2rem 0.6rem;
                font-size: 0.75rem;
                font-weight: 700;
            ">{count}</span>
        </div>
    """
