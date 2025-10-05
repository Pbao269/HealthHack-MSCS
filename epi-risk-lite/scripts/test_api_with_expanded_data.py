#!/usr/bin/env python3
"""
Test API with Expanded Data

This script tests the API with the expanded knowledge base to ensure it works correctly.
"""

import requests
import json
import time
from pathlib import Path

def test_api_with_expanded_data():
    """Test the API with expanded data."""
    print("🧪 Testing API with Expanded Data")
    print("=" * 40)
    
    # API base URL
    API_BASE = "http://localhost:8000"
    
    # Test cases using expanded data
    test_cases = [
        {
            "name": "High-risk codeine (CYP2D6 + CYP3A4 loss)",
            "variants": [
                {"rsid": "rs3892097", "genotype": "AA"},
                {"rsid": "rs776746", "genotype": "TT"}
            ],
            "medication": "codeine"
        },
        {
            "name": "High-risk clopidogrel (CYP2C19 loss)",
            "variants": [
                {"rsid": "rs4244285", "genotype": "AA"}
            ],
            "medication": "clopidogrel"
        },
        {
            "name": "High-risk warfarin (CYP2C9 + VKORC1)",
            "variants": [
                {"rsid": "rs1799853", "genotype": "CC"},
                {"rsid": "rs9923231", "genotype": "TT"}
            ],
            "medication": "warfarin"
        },
        {
            "name": "Star allele test (CYP2D6*4/*4)",
            "variants": [
                {"gene": "CYP2D6", "star": "*4/*4"}
            ],
            "medication": "codeine"
        },
        {
            "name": "HLA-B risk (abacavir)",
            "variants": [
                {"rsid": "rs2395029", "genotype": "GG"}
            ],
            "medication": "abacavir"
        }
    ]
    
    # Test health check first
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/healthz")
        if response.status_code == 200:
            print("   ✅ API is running")
        else:
            print(f"   ❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ API is not running. Please start it with: ./scripts/run_epi_risk.sh")
        return False
    
    print()
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧬 Test {i}: {test_case['name']}")
        
        try:
            # Make API request
            response = requests.post(
                f"{API_BASE}/v1/score",
                json={
                    "variants": test_case["variants"],
                    "medication_name": test_case["medication"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Score: {data['risk_score']:.2f} ({data['risk_label']})")
                print(f"   ✅ Rationales: {len(data['rationales'])}")
                print(f"   ✅ Alternatives: {len(data['suggested_alternatives'])}")
                
                # Show rationales
                for rationale in data['rationales'][:2]:  # Show first 2
                    print(f"      - {rationale['type']}: {rationale.get('tag', rationale.get('pair', 'N/A'))}")
                
                # Show alternatives
                if data['suggested_alternatives']:
                    alt_names = [alt['name'] for alt in data['suggested_alternatives'][:2]]
                    print(f"      - Alternatives: {', '.join(alt_names)}")
                
            else:
                print(f"   ❌ API error: {response.status_code}")
                print(f"      {response.text}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        time.sleep(0.5)  # Rate limiting
    
    # Test file upload
    print("📁 Test: File upload with expanded data")
    
    # Create a test CSV file
    test_csv_content = """rsid,genotype
rs3892097,AA
rs776746,TT
rs4244285,AA"""
    
    test_csv_path = Path("test_expanded_variants.csv")
    with open(test_csv_path, 'w') as f:
        f.write(test_csv_content)
    
    try:
        with open(test_csv_path, 'rb') as f:
            response = requests.post(
                f"{API_BASE}/v1/score-file",
                files={"file": f},
                data={"medication_name": "codeine"}
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ File upload successful")
            print(f"   ✅ Score: {data['risk_score']:.2f} ({data['risk_label']})")
            print(f"   ✅ Rationales: {len(data['rationales'])}")
        else:
            print(f"   ❌ File upload failed: {response.status_code}")
            print(f"      {response.text}")
    
    except Exception as e:
        print(f"   ❌ File upload error: {e}")
    
    finally:
        # Clean up test file
        if test_csv_path.exists():
            test_csv_path.unlink()
    
    print()
    print("🎉 API testing with expanded data completed!")
    return True

if __name__ == "__main__":
    test_api_with_expanded_data()
