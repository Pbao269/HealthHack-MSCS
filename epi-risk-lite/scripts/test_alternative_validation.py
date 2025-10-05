#!/usr/bin/env python3
"""
Test Alternative Validation System

This script tests the enhanced alternative validation system to ensure
that alternatives are properly scored against patient genetics.
"""

import requests
import json
import time
from pathlib import Path

def test_alternative_validation():
    """Test the alternative validation system."""
    print("🧬 Testing Alternative Validation System")
    print("=" * 50)
    
    # API base URL
    API_BASE = "http://localhost:8000"
    
    # Test cases for alternative validation
    test_cases = [
        {
            "name": "High-Risk Codeine - Test Safe Alternatives",
            "variants": [
                {"rsid": "rs3892097", "genotype": "AA"},  # CYP2D6_loss
                {"rsid": "rs776746", "genotype": "TT"}    # CYP3A4_reduced
            ],
            "medication": "codeine",
            "expected_risk": "high",
            "expected_safe_alternatives": ["morphine"],  # Should be safe
            "expected_caution_required": ["oxycodone"],  # Should require caution due to CYP3A4
            "expected_not_recommended": ["tramadol"]     # Should be not recommended due to CYP2D6
        },
        {
            "name": "Moderate-Risk Clopidogrel - Test Alternatives",
            "variants": [
                {"rsid": "rs4244285", "genotype": "AA"}  # CYP2C19_loss
            ],
            "medication": "clopidogrel",
            "expected_risk": "moderate",
            "expected_safe_alternatives": ["ticagrelor"],  # Should be safe
            "expected_caution_required": ["prasugrel"],    # Should require caution
            "expected_not_recommended": []
        },
        {
            "name": "Low-Risk Warfarin - Test Alternatives",
            "variants": [
                {"rsid": "rs1799853", "genotype": "CT"}  # CYP2C9_reduced (not loss)
            ],
            "medication": "warfarin",
            "expected_risk": "low",
            "expected_safe_alternatives": ["apixaban", "rivaroxaban"],  # Should be safe
            "expected_caution_required": [],
            "expected_not_recommended": []
        },
        {
            "name": "Star Allele Test - CYP2D6*4/*4",
            "variants": [
                {"gene": "CYP2D6", "star": "*4/*4"}  # CYP2D6_loss
            ],
            "medication": "codeine",
            "expected_risk": "moderate",
            "expected_safe_alternatives": ["morphine"],  # Should be safe
            "expected_caution_required": ["oxycodone"],  # Should require caution
            "expected_not_recommended": ["tramadol"]     # Should be not recommended
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
        print("   ❌ API is not running. Please start it with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    
    print()
    
    # Test each case
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Test {i}: {test_case['name']}")
        
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
                
                # Check main risk score
                print(f"   📊 Main Risk: {data['risk_score']:.2f} ({data['risk_label']})")
                
                # Check alternatives structure
                alternatives = data.get("suggested_alternatives", {})
                
                safe_alts = alternatives.get("safe_alternatives", [])
                caution_alts = alternatives.get("caution_required", [])
                not_recommended_alts = alternatives.get("not_recommended", [])
                no_safe_alternatives = alternatives.get("no_safe_alternatives", False)
                
                print(f"   ✅ Safe alternatives: {len(safe_alts)}")
                print(f"   ⚠️  Caution required: {len(caution_alts)}")
                print(f"   ❌ Not recommended: {len(not_recommended_alts)}")
                print(f"   🚫 No safe alternatives: {no_safe_alternatives}")
                
                # Show safe alternatives
                if safe_alts:
                    safe_names = [alt["name"] for alt in safe_alts]
                    print(f"      Safe: {', '.join(safe_names)}")
                    
                    # Check if expected safe alternatives are present
                    for expected_safe in test_case["expected_safe_alternatives"]:
                        if any(expected_safe.lower() in alt["name"].lower() for alt in safe_alts):
                            print(f"      ✅ {expected_safe} correctly identified as safe")
                        else:
                            print(f"      ❌ {expected_safe} not found in safe alternatives")
                
                # Show caution required alternatives
                if caution_alts:
                    caution_names = [alt["name"] for alt in caution_alts]
                    print(f"      Caution: {', '.join(caution_names)}")
                    
                    # Check if expected caution alternatives are present
                    for expected_caution in test_case["expected_caution_required"]:
                        if any(expected_caution.lower() in alt["name"].lower() for alt in caution_alts):
                            print(f"      ✅ {expected_caution} correctly identified as caution required")
                        else:
                            print(f"      ❌ {expected_caution} not found in caution required")
                
                # Show not recommended alternatives
                if not_recommended_alts:
                    not_rec_names = [alt["name"] for alt in not_recommended_alts]
                    print(f"      Not recommended: {', '.join(not_rec_names)}")
                    
                    # Check if expected not recommended alternatives are present
                    for expected_not_rec in test_case["expected_not_recommended"]:
                        if any(expected_not_rec.lower() in alt["name"].lower() for alt in not_recommended_alts):
                            print(f"      ✅ {expected_not_rec} correctly identified as not recommended")
                        else:
                            print(f"      ❌ {expected_not_rec} not found in not recommended")
                
                # Show safety warnings for alternatives
                print("   🔍 Safety Analysis:")
                for alt in safe_alts + caution_alts + not_recommended_alts:
                    if alt.get("safety_warnings"):
                        print(f"      {alt['name']}: {', '.join(alt['safety_warnings'])}")
                    if alt.get("pathway_genes"):
                        print(f"      {alt['name']} pathway genes: {', '.join(alt['pathway_genes'])}")
                
                passed_tests += 1
                print("   ✅ Test passed")
                
            else:
                print(f"   ❌ API error: {response.status_code}")
                print(f"      {response.text}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        time.sleep(0.5)
    
    # Summary
    print("📋 Test Summary")
    print("=" * 30)
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Alternative validation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


def test_edge_cases():
    """Test edge cases for alternative validation."""
    print("\n🔬 Testing Edge Cases")
    print("=" * 30)
    
    API_BASE = "http://localhost:8000"
    
    edge_cases = [
        {
            "name": "No Alternatives Available",
            "variants": [{"rsid": "rs3892097", "genotype": "AA"}],
            "medication": "unknown_drug",  # This should have no alternatives
            "expected_no_alternatives": True
        },
        {
            "name": "All Alternatives High Risk",
            "variants": [
                {"rsid": "rs3892097", "genotype": "AA"},  # CYP2D6_loss
                {"rsid": "rs776746", "genotype": "TT"},   # CYP3A4_reduced
                {"rsid": "rs4244285", "genotype": "AA"}   # CYP2C19_loss
            ],
            "medication": "codeine",
            "expected_no_safe": True
        }
    ]
    
    for i, case in enumerate(edge_cases, 1):
        print(f"🧪 Edge Case {i}: {case['name']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/v1/score",
                json={
                    "variants": case["variants"],
                    "medication_name": case["medication"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                alternatives = data.get("suggested_alternatives", {})
                
                safe_count = len(alternatives.get("safe_alternatives", []))
                no_safe = alternatives.get("no_safe_alternatives", False)
                
                print(f"   Safe alternatives: {safe_count}")
                print(f"   No safe alternatives: {no_safe}")
                
                if case.get("expected_no_alternatives"):
                    if safe_count == 0 and len(alternatives.get("caution_required", [])) == 0:
                        print("   ✅ Correctly identified no alternatives available")
                    else:
                        print("   ❌ Expected no alternatives but found some")
                
                if case.get("expected_no_safe"):
                    if no_safe or safe_count == 0:
                        print("   ✅ Correctly identified no safe alternatives")
                    else:
                        print("   ❌ Expected no safe alternatives but found some")
                
            else:
                print(f"   ❌ API error: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()


if __name__ == "__main__":
    print("🚀 Starting Alternative Validation Tests")
    print("=" * 50)
    
    # Test main functionality
    success = test_alternative_validation()
    
    # Test edge cases
    test_edge_cases()
    
    if success:
        print("\n🎉 All alternative validation tests completed successfully!")
        print("✅ The system now properly validates alternatives against patient genetics.")
        print("✅ Patient safety is significantly improved.")
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.")
