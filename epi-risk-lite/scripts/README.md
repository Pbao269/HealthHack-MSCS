# Epi-Risk Lite Data Expansion Scripts

This directory contains scripts to collect and integrate data from credible online sources to expand the Epi-Risk Lite knowledge base.

## 🎯 **Purpose**

Expand the knowledge base from:
- **7 medications** → **50+ medications**
- **10+ genes** → **50+ genes** 
- **20+ variants** → **200+ variants**

## 📚 **Data Sources**

### 1. **PharmGKB (Pharmacogenomics Knowledge Base)**
- **URL**: https://www.pharmgkb.org/
- **API**: https://api.pharmgkb.org/v1
- **Data**: Drug-gene interactions, clinical annotations, variant annotations
- **Script**: `collect_pharmgkb_data.py`

### 2. **CPIC (Clinical Pharmacogenetics Implementation Consortium)**
- **URL**: https://cpicpgx.org/
- **Data**: Evidence-based guidelines for drug-gene pairs
- **Script**: `collect_cpic_data.py`

### 3. **FDA Table of Pharmacogenomic Biomarkers**
- **URL**: https://www.fda.gov/drugs/science-and-research-drugs/table-pharmacogenomic-biomarkers-drug-labeling
- **Data**: FDA-approved drug labels with pharmacogenomic information
- **Script**: `collect_fda_data.py`

### 4. **Data Integration**
- **Script**: `integrate_data.py`
- **Purpose**: Combine data from all sources into unified knowledge base

## 🚀 **Quick Start**

### 1. Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### 2. Run Data Collection

```bash
# Collect PharmGKB data
python collect_pharmgkb_data.py

# Collect CPIC data
python collect_cpic_data.py

# Collect FDA data
python collect_fda_data.py
```

### 3. Integrate Data

```bash
# Integrate all collected data
python integrate_data.py
```

### 4. Update Application

```bash
# Copy expanded data to application
cp ../app/engine/data/expanded_*.json ../app/engine/data/

# Restart application to use new data
cd ..
uvicorn app.main:app --reload
```

## 📊 **Expected Results**

After running all scripts, you should have:

### New Files Created
```
app/engine/data/
├── expanded_drug_gene_map.json      # 50+ drugs
├── expanded_allele_proxies.json     # 200+ variants
├── expanded_guidelines.json         # Clinical evidence
├── expanded_alternatives.json       # Alternative medications
└── expanded_knowledge_base.json     # Complete knowledge base
```

### Data Sources
- **PharmGKB**: Drug-gene interactions, clinical annotations
- **CPIC**: Evidence-based guidelines
- **FDA**: Pharmacogenomic biomarkers
- **Existing**: Current knowledge base

## 🔧 **Script Details**

### `collect_pharmgkb_data.py`
- **Purpose**: Download drug-gene interactions and variant annotations
- **API**: Uses PharmGKB REST API
- **Output**: `pharmgkb_drug_gene_map.json`, `pharmgkb_allele_proxies.json`

### `collect_cpic_data.py`
- **Purpose**: Scrape CPIC guidelines for drug-gene pairs
- **Method**: Web scraping with BeautifulSoup
- **Output**: `cpic_guidelines.json`, `cpic_drug_gene_map.json`

### `collect_fda_data.py`
- **Purpose**: Extract FDA pharmacogenomic biomarkers table
- **Method**: Web scraping FDA website
- **Output**: `fda_biomarkers.json`, `fda_drug_gene_map.json`

### `integrate_data.py`
- **Purpose**: Combine all data sources into unified knowledge base
- **Method**: Data merging and deduplication
- **Output**: `expanded_*.json` files

## 📈 **Data Expansion Goals**

### Medications (7 → 50+)
- **High Priority**: Warfarin, clopidogrel, statins, antidepressants, antipsychotics
- **Medium Priority**: Chemotherapy drugs, immunosuppressants, cardiovascular drugs
- **Low Priority**: Rare disease drugs, experimental compounds

### Genes (10+ → 50+)
- **Phase I Enzymes**: CYP1A2, CYP2B6, CYP2C8, CYP2C9, CYP2C19, CYP2D6, CYP3A4, CYP3A5
- **Phase II Enzymes**: UGT1A1, UGT2B7, UGT2B15, SULT1A1, COMT, TPMT, NAT2
- **Transporters**: ABCB1, ABCC2, ABCG2, SLCO1B1, SLCO1B3, SLC22A1
- **Receptors**: OPRM1, ADRB1, ADRB2, DRD2, HTR2A, VKORC1

### Variants (20+ → 200+)
- **SNPs**: rsIDs with functional consequences
- **Star Alleles**: Comprehensive pharmacogene haplotypes
- **CNVs**: Copy number variations affecting drug metabolism

## 🛠 **Customization**

### Adding New Data Sources

1. **Create new collection script**:
```python
# scripts/collect_new_source.py
class NewSourceCollector:
    def collect_data(self):
        # Implementation
        pass
```

2. **Update integration script**:
```python
# scripts/integrate_data.py
def integrate_new_source_data(self):
    # Add new source integration
    pass
```

### Modifying Data Processing

Edit the processing methods in each collection script to customize how data is transformed and mapped to the Epi-Risk Lite schema.

## 🔍 **Data Quality**

### Validation Checks
- **Cross-validation** between sources
- **Duplicate detection** and removal
- **Data completeness** verification
- **Format consistency** checks

### Quality Metrics
- **Coverage**: Number of drugs/genes/variants
- **Accuracy**: Expert-validated interactions
- **Completeness**: Missing data identification
- **Consistency**: Format standardization

## 📋 **Troubleshooting**

### Common Issues

1. **API Rate Limits**
   - Add delays between requests
   - Use session with proper headers
   - Implement retry logic

2. **Website Changes**
   - Update CSS selectors
   - Modify parsing logic
   - Add error handling

3. **Data Format Issues**
   - Validate JSON structure
   - Check data types
   - Handle missing fields

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 **Maintenance**

### Regular Updates
- **Monthly**: PharmGKB updates
- **Quarterly**: CPIC guideline updates
- **Annually**: Complete knowledge base review

### Version Control
- **Git tags** for knowledge base versions
- **Change logs** for each update
- **Backup** of previous versions

## 📊 **Performance**

### Expected Runtime
- **PharmGKB**: 5-10 minutes
- **CPIC**: 10-15 minutes
- **FDA**: 5-10 minutes
- **Integration**: 2-5 minutes
- **Total**: 20-40 minutes

### Resource Usage
- **Memory**: ~500MB peak
- **Disk**: ~100MB for all data files
- **Network**: ~50MB downloads

## 🚨 **Important Notes**

### Data Licensing
- **PharmGKB**: Open access, cite appropriately
- **CPIC**: Open access, cite guidelines
- **FDA**: Public domain data
- **RxNorm**: Public domain

### Usage Restrictions
- **Rate limiting**: Respect API limits
- **Attribution**: Cite data sources
- **Updates**: Keep data current
- **Validation**: Verify data accuracy

## 📞 **Support**

For issues with data collection:
1. Check logs for error messages
2. Verify network connectivity
3. Update dependencies
4. Check source website changes

## 🎯 **Success Metrics**

### Quantitative Goals
- **Drugs**: 7 → 50+ (7x increase)
- **Genes**: 10+ → 50+ (5x increase)
- **Variants**: 20+ → 200+ (10x increase)
- **Interactions**: 50+ → 500+ (10x increase)

### Qualitative Goals
- **Coverage**: Major drug classes represented
- **Accuracy**: Expert-validated interactions
- **Completeness**: Comprehensive variant coverage
- **Usability**: Clear clinical rationales

---

**Status**: Ready for use  
**Last Updated**: October 4, 2025  
**Version**: 1.0
