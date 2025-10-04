#!/usr/bin/env python3
"""
Test script to verify installation works correctly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Test basic imports
        import json
        import pandas as pd
        import numpy as np
        print("✅ Basic imports successful")
        
        # Test FastAPI imports
        from fastapi import FastAPI
        from pydantic import BaseModel
        print("✅ FastAPI imports successful")
        
        # Test app imports
        from app.config import settings
        print("✅ App config import successful")
        
        from app.schemas import ScoreRequest, ScoreResponse
        print("✅ App schemas import successful")
        
        from app.engine.scorer import RiskScorer
        print("✅ Engine scorer import successful")
        
        from app.parsers.csv_parser import parse_csv
        print("✅ CSV parser import successful")
        
        from app.parsers.pdf_parser import parse_pdf
        print("✅ PDF parser import successful")
        
        print("🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_data_loading():
    """Test that data files can be loaded."""
    print("\n📊 Testing data loading...")
    
    try:
        from app.engine.rules import GUIDELINES
        print(f"✅ Guidelines loaded: {len(GUIDELINES.get('single_tags', {}))} single tags")
        
        from app.engine.pathways import DRUG_GENE_MAP
        print(f"✅ Drug-gene map loaded: {len(DRUG_GENE_MAP)} drugs")
        
        from app.engine.mapper import ALLELE_PROXIES
        print(f"✅ Allele proxies loaded: {len(ALLELE_PROXIES)} variants")
        
        print("🎉 All data loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False

def test_scorer():
    """Test that the scorer can be initialized."""
    print("\n🎯 Testing scorer initialization...")
    
    try:
        from app.engine.scorer import RiskScorer
        
        scorer = RiskScorer()
        print(f"✅ Scorer initialized: {scorer.model_version}")
        
        # Test basic scoring
        test_variants = [
            {"rsid": "rs3892097", "genotype": "AA"}
        ]
        
        result = scorer.score(
            variants=test_variants,
            medication_name="codeine"
        )
        
        print(f"✅ Basic scoring works: {result['risk_label']} risk")
        print("🎉 Scorer test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Scorer error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Epi-Risk Lite Installation Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_data_loading,
        test_scorer
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Installation is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
