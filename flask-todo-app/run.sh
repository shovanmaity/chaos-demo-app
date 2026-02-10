#!/bin/bash

# Run script for In-Memory Todo App
# This script activates the virtual environment and starts the Flask application

set -e

echo "📝 Starting In-Memory Todo App..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup.sh"
    echo ""
    exit 1
fi

# Check if Flask is installed
if ! venv/bin/python -c "import flask" 2>/dev/null; then
    echo "❌ Error: Dependencies not installed"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup.sh"
    echo ""
    exit 1
fi

# Run the application
echo "🚀 Launching Flask application..."
echo ""
venv/bin/python app.py
