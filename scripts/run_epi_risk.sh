#!/bin/bash

# Epi-Risk Lite Runner Script
# Run from repository root: ./scripts/run_epi_risk.sh

set -e

echo "🧬 Starting Epi-Risk Lite..."
echo "================================"

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

# Start the application
echo "🚀 Starting Epi-Risk Lite API..."
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
