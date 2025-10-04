#!/bin/bash

# Epi-Risk Lite Test Script
# Run from repository root: ./scripts/test_epi_risk.sh

set -e

echo "🧪 Testing Epi-Risk Lite..."
echo "============================"

# Check if we're in the right directory
if [ ! -d "epi-risk-lite" ]; then
    echo "❌ Error: epi-risk-lite directory not found"
    echo "Please run this script from the repository root"
    exit 1
fi

# Change to epi-risk-lite directory
cd epi-risk-lite

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -e .
pip install -e ".[dev]"

echo "🧪 Running tests..."
pytest -v

echo "🔍 Running API tests..."
if [ -f "test_api.sh" ]; then
    chmod +x test_api.sh
    ./test_api.sh
else
    echo "⚠️ API test script not found, skipping API tests"
fi

echo "✅ All tests completed!"
