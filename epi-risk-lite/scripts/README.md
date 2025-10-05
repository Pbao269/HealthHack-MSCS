# Epi-Risk Lite Scripts

This directory contains testing and analysis scripts for the Epi-Risk Lite application.

## ⚠️ **IMPORTANT NOTE**

**Data collection scripts are currently disabled** due to:
- API authentication requirements (PharmGKB)
- Web scraping unreliability (CPIC, FDA)
- Terms of service restrictions

These scripts are kept for **reference only** and are excluded from CI/CD pipelines.

## 📊 **Current Data Coverage**

Our manually curated knowledge base includes:
- **34 medications** with pharmacogenomic data
- **26 genes** across multiple pathways
- **88 genetic variants** with functional consequences
- **181 star alleles** with clinical significance
- **25 alternative medication sets**
- **22 functional tags** for scoring
- **10 epistasis pairs** for complex interactions

## 🧪 **Working Scripts**

### 1. **API Testing Scripts**
- **`end_to_end_test.py`** - Comprehensive API endpoint testing
- **`test_api_with_expanded_data.py`** - API testing with new data
- **`test_expanded_data.py`** - Data validation testing

### 2. **Analysis Scripts**
- **`final_coverage_analysis.py`** - Coverage analysis and reporting
- **`validation_test_cases.md`** - Test case documentation

### 3. **Reference Scripts (Non-Working)**
- **`collect_pharmgkb_data.py`** - PharmGKB data collection (API auth issues)
- **`collect_cpic_data.py`** - CPIC data collection (web scraping issues)
- **`collect_fda_data.py`** - FDA data collection (web scraping issues)
- **`integrate_data.py`** - Data integration (depends on collectors)

## 🚀 **Quick Start**

### 1. Run API Tests

```bash
cd epi-risk-lite/scripts

# Test API endpoints
python end_to_end_test.py

# Test with expanded data
python test_api_with_expanded_data.py

# Run coverage analysis
python final_coverage_analysis.py
```

### 2. Test New Drug Coverage

```bash
# Test specific drug scenarios
python test_expanded_data.py
```

## 📋 **Test Cases**

The `validation_test_cases.md` file contains comprehensive test cases covering:

### **High-Risk Scenarios**
- **TMPT + Thiopurines** (severe myelosuppression)
- **DPYD + Fluoropyrimidines** (severe toxicity)
- **CYP2D6 + Codeine** (respiratory depression)
- **HLA-B*5701 + Abacavir** (hypersensitivity)

### **Moderate-Risk Scenarios**
- **CYP2C19 + Clopidogrel** (reduced efficacy)
- **SLCO1B1 + Simvastatin** (myopathy)
- **VKORC1 + Warfarin** (bleeding risk)

### **New Drug Coverage**
- **Fluoxetine** (CYP2D6, CYP2C19)
- **Metoprolol** (CYP2D6, ADRB1)
- **Omeprazole** (CYP2C19, CYP3A4)
- **Abacavir** (HLA-B*5701)

## 🔧 **Script Details**

### **Working Scripts**

#### `end_to_end_test.py`
- Tests all API endpoints (`/v1/score`, `/v1/score-file`, `/healthz`, `/version`)
- Validates response schemas and data types
- Tests error handling and edge cases
- Generates comprehensive test reports

#### `test_api_with_expanded_data.py`
- Tests API with the new comprehensive data
- Validates drug-gene mappings
- Tests functional tag generation
- Verifies scoring accuracy

#### `final_coverage_analysis.py`
- Analyzes current data coverage
- Compares against research benchmarks
- Identifies gaps and missing scenarios
- Generates coverage reports

### **Reference Scripts (Non-Working)**

#### `collect_pharmgkb_data.py`
- **Issue**: Requires API key authentication
- **Purpose**: Collect drug-gene interactions from PharmGKB
- **Status**: Disabled, kept for reference

#### `collect_cpic_data.py`
- **Issue**: Web scraping unreliable, anti-bot protection
- **Purpose**: Collect CPIC guidelines
- **Status**: Disabled, kept for reference

#### `collect_fda_data.py`
- **Issue**: Complex website structure, dynamic content
- **Purpose**: Collect FDA pharmacogenomic biomarkers
- **Status**: Disabled, kept for reference

## 📈 **Expected Test Results**

When running the working scripts, you should see:

### **API Tests**
- ✅ All endpoints responding correctly
- ✅ Proper error handling
- ✅ Valid response schemas
- ✅ Correct scoring calculations

### **Coverage Analysis**
- **34 medications** covered
- **26 genes** in knowledge base
- **88 variants** with functional consequences
- **High-risk scenarios** properly identified

### **New Drug Testing**
- **Fluoxetine**: CYP2D6/CYP2C19 interactions
- **Metoprolol**: CYP2D6/ADRB1 interactions
- **Omeprazole**: CYP2C19/CYP3A4 interactions
- **Abacavir**: HLA-B*5701 hypersensitivity

## 🚨 **Troubleshooting**

### **Common Issues**

1. **API not running**
   ```bash
   # Start API first
   cd epi-risk-lite
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Import errors**
   ```bash
   # Install dependencies
   pip install -e .
   pip install -e ".[dev]"
   ```

3. **Data not found**
   ```bash
   # Ensure data files exist
   ls app/engine/data/*.json
   ```

## 📚 **References**

- **PharmGKB**: https://www.pharmgkb.org/
- **CPIC**: https://cpicpgx.org/
- **FDA Biomarkers**: https://www.fda.gov/drugs/science-and-research-drugs/table-pharmacogenomic-biomarkers-drug-labeling
- **API Documentation**: http://localhost:8000/docs