#!/bin/bash

# Data Expansion Runner Script
# Run from repository root: ./scripts/run_data_expansion.sh

set -e

echo "📊 Starting Epi-Risk Lite Data Expansion..."
echo "============================================="

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
pip install -r scripts/requirements.txt

# Change to scripts directory
cd scripts

echo "🔍 Collecting data from PharmGKB..."
python collect_pharmgkb_data.py

echo "📋 Collecting data from CPIC..."
python collect_cpic_data.py

echo "🏛️ Collecting data from FDA..."
python collect_fda_data.py

echo "🔄 Integrating all data..."
python integrate_data.py

echo "✅ Data expansion completed!"
echo ""
echo "📁 Expanded data saved to: epi-risk-lite/app/engine/data/"
echo "🚀 Restart Epi-Risk Lite to use the expanded knowledge base"
echo ""
echo "To restart: ./scripts/run_epi_risk.sh"
