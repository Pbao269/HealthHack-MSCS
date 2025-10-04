#!/bin/bash

# Direct Installation Script for Epi-Risk Lite
# Run from repository root: ./install_direct.sh

set -e

echo "🚀 Direct Installation of Epi-Risk Lite..."
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

echo "5. 📦 Installing core dependencies directly..."
pip install fastapi>=0.104.0
pip install uvicorn[standard]>=0.24.0
pip install pydantic>=2.5.0
pip install pydantic-settings>=2.1.0
pip install pandas>=2.1.0
pip install numpy>=1.26.0
pip install camelot-py[cv]>=0.11.0
pip install pdfplumber>=0.10.0
pip install xgboost>=2.0.0
pip install scikit-learn>=1.3.0
pip install joblib>=1.3.0
pip install python-dotenv>=1.0.0
pip install python-multipart>=0.0.6

echo "6. 📦 Installing dev dependencies..."
pip install pytest>=7.4.0
pip install pytest-asyncio>=0.21.0
pip install httpx>=0.25.0

echo "7. 🧪 Testing installation..."
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
