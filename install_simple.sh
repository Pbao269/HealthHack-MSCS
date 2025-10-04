#!/bin/bash

# Simple Installation Script for Epi-Risk Lite
# Run from repository root: ./install_simple.sh

set -e

echo "🚀 Simple Installation of Epi-Risk Lite..."
echo "=========================================="

# Check if we're in the right directory
if [ ! -d "epi-risk-lite" ]; then
    echo "❌ Error: epi-risk-lite directory not found"
    echo "Please run this script from the repository root"
    exit 1
fi

cd epi-risk-lite

echo "1. 🧹 Cleaning up..."
rm -rf venv build dist *.egg-info

echo "2. 📦 Creating virtual environment..."
python3 -m venv venv

echo "3. 🔧 Activating virtual environment..."
source venv/bin/activate

echo "4. 📥 Upgrading pip..."
pip install --upgrade pip

echo "5. 📦 Installing from requirements.txt..."
pip install -r requirements.txt

echo "6. 🧪 Testing basic dependencies..."
python test_basic.py

if [ $? -ne 0 ]; then
    echo "❌ Basic dependency test failed. Please check the errors above."
    exit 1
fi

echo "7. 🧪 Testing full installation..."
python test_installation.py

if [ $? -eq 0 ]; then
    echo "✅ Installation successful!"
    echo ""
    echo "🚀 Starting Epi-Risk Lite API..."
    echo "API will be available at: http://localhost:8000"
    echo "API docs at: http://localhost:8000/docs"
    echo "Press Ctrl+C to stop"
    echo ""
    
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo "❌ Installation test failed. Please check the errors above."
    exit 1
fi
