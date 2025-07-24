#!/bin/bash

# Quick start script for YouTube AI Monitor
echo "🚀 YouTube AI Monitor - Quick Start"
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

# Run setup
echo "📦 Running setup..."
python3 setup.py

# Check if setup was successful
if [ -f ".env" ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "🔧 IMPORTANT: Edit .env file and add your YouTube API key"
    echo "   YOUTUBE_API_KEY=your_actual_api_key_here"
    echo ""
    echo "🎯 Quick Commands:"
    echo "   Test API:              python3 src/youtube_api.py"
    echo "   Find videos (once):    python3 src/monitor.py --once"
    echo "   Start dashboard:       python3 src/dashboard.py"
    echo "   Start monitoring:      python3 src/monitor.py"
    echo ""
    echo "🌐 Dashboard: http://localhost:5000"
else
    echo "❌ Setup failed. Please check errors above."
fi
