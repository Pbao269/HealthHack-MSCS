#!/bin/bash

# Epi-Risk Lite Docker Runner Script
# Run from repository root: ./scripts/docker_epi_risk.sh

set -e

echo "🐳 Starting Epi-Risk Lite with Docker..."
echo "========================================"

# Check if we're in the right directory
if [ ! -d "epi-risk-lite" ]; then
    echo "❌ Error: epi-risk-lite directory not found"
    echo "Please run this script from the repository root"
    exit 1
fi

# Change to epi-risk-lite directory
cd epi-risk-lite

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting Epi-Risk Lite..."
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

docker-compose up
