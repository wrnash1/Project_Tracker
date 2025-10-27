#!/bin/bash
# Verizon Tracker - Quick Start Script

echo "🚀 Starting Verizon Tracker..."
echo ""

# Check if databases exist, initialize if not
if [ ! -f "data/G_DRIVE/master_users.db" ]; then
    echo "📊 Initializing databases..."
    python3 src/vtrack/database.py
    echo ""
fi

# Start Streamlit
echo "🌐 Launching application on http://localhost:8501"
echo ""
echo "Default Login Credentials:"
echo "  Admin: username: admin, password: admin123"
echo "  PM User: username: pmuser, password: pm123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m streamlit run app/Home.py --server.headless true
