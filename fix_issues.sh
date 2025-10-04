#!/bin/bash

# Fix Issues Script for Epi-Risk Lite
# Run from repository root: ./fix_issues.sh

set -e

echo "🔧 Fixing Epi-Risk Lite Issues..."
echo "================================="

# Check if we're in the right directory
if [ ! -d "epi-risk-lite" ]; then
    echo "❌ Error: epi-risk-lite directory not found"
    echo "Please run this script from the repository root"
    exit 1
fi

cd epi-risk-lite

echo "1. 🧹 Cleaning up previous installations..."
# Remove any existing virtual environment
if [ -d "venv" ]; then
    echo "   Removing existing virtual environment..."
    rm -rf venv
fi

# Remove any build artifacts
if [ -d "build" ]; then
    echo "   Removing build artifacts..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "   Removing dist artifacts..."
    rm -rf dist
fi

if [ -d "*.egg-info" ]; then
    echo "   Removing egg-info artifacts..."
    rm -rf *.egg-info
fi

echo "2. 📦 Creating fresh virtual environment..."
python3 -m venv venv

echo "3. 🔧 Activating virtual environment..."
source venv/bin/activate

echo "4. 📥 Upgrading pip..."
pip install --upgrade pip

echo "5. 📦 Installing dependencies..."
pip install -e .

echo "6. 📦 Installing dev dependencies..."
pip install -e ".[dev]"

echo "7. 🧪 Testing basic dependencies..."
python test_basic.py

if [ $? -ne 0 ]; then
    echo "❌ Basic dependency test failed. Installing missing dependencies..."
    pip install pandas numpy fastapi joblib
fi

echo "8. 🧪 Testing full installation..."
python test_installation.py

if [ $? -eq 0 ]; then
    echo "✅ Installation test passed!"
else
    echo "❌ Installation test failed. Please check the errors above."
    exit 1
fi

echo "6. 🚀 Starting Epi-Risk Lite API..."
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
