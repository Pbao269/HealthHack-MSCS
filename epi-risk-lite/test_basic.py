#!/usr/bin/env python3
"""
Basic test script to verify core dependencies.
"""

def test_basic_imports():
    """Test basic Python imports."""
    print("🧪 Testing basic imports...")
    
    try:
        import json
        import sys
        from pathlib import Path
        print("✅ Basic Python modules successful")
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_pandas():
    """Test pandas import."""
    print("🧪 Testing pandas...")
    
    try:
        import pandas as pd
        print(f"✅ Pandas imported successfully: {pd.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False

def test_numpy():
    """Test numpy import."""
    print("🧪 Testing numpy...")
    
    try:
        import numpy as np
        print(f"✅ Numpy imported successfully: {np.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Numpy import failed: {e}")
        return False

def test_fastapi():
    """Test FastAPI import."""
    print("🧪 Testing FastAPI...")
    
    try:
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
        return True
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

def test_joblib():
    """Test joblib import."""
    print("🧪 Testing joblib...")
    
    try:
        import joblib
        print(f"✅ Joblib imported successfully: {joblib.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Joblib import failed: {e}")
        return False

def main():
    """Run all basic tests."""
    print("🚀 Basic Dependency Test")
    print("=" * 30)
    
    tests = [
        test_basic_imports,
        test_pandas,
        test_numpy,
        test_fastapi,
        test_joblib
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 30)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic dependencies are working!")
        return 0
    else:
        print("❌ Some dependencies are missing. Please install them.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
