#!/bin/bash

# Test script for Epi-Risk Lite API
# Usage: ./test_api.sh

set -e

API_URL="${API_URL:-http://localhost:8000}"

echo "Testing Epi-Risk Lite API at $API_URL"
echo "========================================"
echo ""

# Health check
echo "1. Testing health check..."
curl -s "$API_URL/healthz" | jq .
echo ""

# Version check
echo "2. Testing version endpoint..."
curl -s "$API_URL/version" | jq .
echo ""

# Score with JSON variants
echo "3. Testing score with JSON variants (codeine)..."
curl -s -X POST "$API_URL/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "variants": [
      {"rsid": "rs3892097", "genotype": "AA"},
      {"rsid": "rs776746", "genotype": "TT"}
    ],
    "medication_name": "codeine"
  }' | jq .
echo ""

# Score with star alleles
echo "4. Testing score with star alleles..."
curl -s -X POST "$API_URL/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "variants": [
      {"gene": "CYP2D6", "star": "*4/*4"}
    ],
    "medication_name": "codeine"
  }' | jq .
echo ""

# Score with CSV file (if sample exists)
if [ -f "data/sample_genotype.csv" ]; then
  echo "5. Testing score with CSV file upload..."
  curl -s -X POST "$API_URL/v1/score-file" \
    -F "file=@data/sample_genotype.csv" \
    -F "medication_name=codeine" | jq .
  echo ""
fi

# Test clopidogrel
echo "6. Testing with clopidogrel (different drug pathway)..."
curl -s -X POST "$API_URL/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "variants": [
      {"rsid": "rs4244285", "genotype": "AA"},
      {"rsid": "rs776746", "genotype": "TT"}
    ],
    "medication_name": "clopidogrel"
  }' | jq .
echo ""

# Test warfarin
echo "7. Testing with warfarin..."
curl -s -X POST "$API_URL/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "variants": [
      {"rsid": "rs1799853", "genotype": "CT"},
      {"rsid": "rs9923231", "genotype": "AA"}
    ],
    "medication_name": "warfarin"
  }' | jq .
echo ""

# Test with context
echo "8. Testing with patient context..."
curl -s -X POST "$API_URL/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "variants": [
      {"rsid": "rs3892097", "genotype": "AA"}
    ],
    "medication_name": "codeine",
    "context": {
      "age": 45,
      "sex": "M",
      "ancestry": "EUR"
    }
  }' | jq .
echo ""

echo "========================================"
echo "All tests completed!"

