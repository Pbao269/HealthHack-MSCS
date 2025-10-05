#!/usr/bin/env python3
"""
Test New Drug Coverage

This script tests the API with newly added drugs to validate expanded coverage.
"""

import requests
import json
from typing import Dict, List

def test_drug_scenario(drug_name: str, variants: List[Dict], expected_risk: str = None):
    """Test a drug scenario and return results."""
    print(f"\n🧬 Testing: {drug_name}")
    print(f"   Variants: {variants}")
    
    try:
        response = requests.post("http://localhost:8000/v1/score", json={
            "variants": variants,
            "medication_name": drug_name
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Score: {result['risk_score']:.2f} ({result['risk_label']})")
            print(f"   📋 Rationales: {len(result['rationales'])}")
            print(f"   💊 Alternatives: {len(result['suggested_alternatives'])}")
            
            # Show specific rationales
            for rationale in result['rationales']:
                if rationale['type'] == 'single_tag':
                    print(f"      - {rationale['tag']}: {rationale['evidence'][0] if rationale['evidence'] else 'No evidence'}")
                elif rationale['type'] == 'epistasis_pair':
                    print(f"      - {rationale['pair'][0]} + {rationale['pair'][1]}: {rationale['evidence'][0] if rationale['evidence'] else 'No evidence'}")
            
            # Show alternatives
            if result['suggested_alternatives']:
                alt_names = [alt['name'] for alt in result['suggested_alternatives'][:3]]
                print(f"      - Alternatives: {', '.join(alt_names)}")
            
            return True
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Run comprehensive new drug tests."""
    print("🧪 TESTING NEW DRUG COVERAGE")
    print("=" * 50)
    
    # Test cases for newly added drugs
    test_cases = [
        # High-risk scenarios
        {
            "drug": "fluoxetine",
            "variants": [{"rsid": "rs1065852", "genotype": "AA"}],  # CYP2D6 loss
            "description": "CYP2D6 poor metabolizer + fluoxetine"
        },
        {
            "drug": "metoprolol",
            "variants": [{"rsid": "rs1065852", "genotype": "AA"}],  # CYP2D6 loss
            "description": "CYP2D6 poor metabolizer + metoprolol"
        },
        {
            "drug": "omeprazole",
            "variants": [{"rsid": "rs4244285", "genotype": "AA"}],  # CYP2C19 loss
            "description": "CYP2C19 poor metabolizer + omeprazole"
        },
        {
            "drug": "abacavir",
            "variants": [{"gene": "HLA-B", "star": "*5701/*5701"}],
            "description": "HLA-B*5701 homozygous + abacavir"
        },
        
        # Moderate-risk scenarios
        {
            "drug": "fluoxetine",
            "variants": [{"rsid": "rs4244285", "genotype": "AG"}],  # CYP2C19 intermediate
            "description": "CYP2C19 intermediate metabolizer + fluoxetine"
        },
        {
            "drug": "metoprolol",
            "variants": [{"rsid": "rs1065852", "genotype": "AG"}],  # CYP2D6 intermediate
            "description": "CYP2D6 intermediate metabolizer + metoprolol"
        },
        
        # Star allele scenarios
        {
            "drug": "codeine",
            "variants": [{"gene": "CYP2D6", "star": "*4/*4"}],
            "description": "CYP2D6*4/*4 + codeine"
        },
        {
            "drug": "warfarin",
            "variants": [{"gene": "CYP2C9", "star": "*2/*3"}],
            "description": "CYP2C9*2/*3 + warfarin"
        },
        
        # Complex scenarios
        {
            "drug": "codeine",
            "variants": [
                {"rsid": "rs1065852", "genotype": "AA"},  # CYP2D6 loss
                {"rsid": "rs776746", "genotype": "TT"}    # CYP3A4 variant
            ],
            "description": "CYP2D6 loss + CYP3A4 variant + codeine"
        },
        {
            "drug": "clopidogrel",
            "variants": [
                {"rsid": "rs4244285", "genotype": "AA"},  # CYP2C19 loss
                {"rsid": "rs1045642", "genotype": "CC"}   # ABCB1 variant
            ],
            "description": "CYP2C19 loss + ABCB1 variant + clopidogrel"
        }
    ]
    
    # Run tests
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}/{total} ---")
        print(f"📝 {test_case['description']}")
        
        if test_drug_scenario(test_case['drug'], test_case['variants']):
            passed += 1
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"✅ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"❌ Failed: {total-passed}/{total} ({(total-passed)/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! New drug coverage is working correctly.")
    else:
        print(f"\n⚠️  {total-passed} tests failed. Check API logs for details.")
    
    return passed == total

if __name__ == "__main__":
    main()
