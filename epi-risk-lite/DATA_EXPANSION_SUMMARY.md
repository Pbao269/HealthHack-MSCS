# Epi-Risk Lite Data Expansion - Complete Implementation

## 🎯 **Overview**

I've created a comprehensive data expansion system to populate the Epi-Risk Lite knowledge base with credible online resources. This will expand support from **7 medications** to **50+ medications** and from **10+ genes** to **50+ genes**.

## 📚 **Credible Data Sources Identified**

### 1. **PharmGKB (Pharmacogenomics Knowledge Base)**
- **URL**: https://www.pharmgkb.org/
- **API**: https://api.pharmgkb.org/v1
- **Data Available**:
  - Drug-gene interactions
  - Clinical annotations
  - Variant annotations
  - Dosing guidelines
- **Format**: JSON via REST API
- **Coverage**: 1000+ drugs, 100+ genes, 1000+ variants

### 2. **CPIC (Clinical Pharmacogenetics Implementation Consortium)**
- **URL**: https://cpicpgx.org/
- **Data Available**:
  - Evidence-based guidelines for drug-gene pairs
  - Phenotype-based dosing recommendations
  - Clinical significance levels
- **Format**: Web scraping from guidelines pages
- **Coverage**: 50+ drug-gene pairs with clinical guidelines

### 3. **FDA Table of Pharmacogenomic Biomarkers**
- **URL**: https://www.fda.gov/drugs/science-and-research-drugs/table-pharmacogenomic-biomarkers-drug-labeling
- **Data Available**:
  - FDA-approved drug labels with pharmacogenomic information
  - Clinical significance levels
  - Biomarker-drug associations
- **Format**: Web scraping from HTML tables
- **Coverage**: 200+ drug-biomarker pairs

### 4. **RxNorm (National Library of Medicine)**
- **URL**: https://www.nlm.nih.gov/research/umls/rxnorm/
- **Data Available**:
  - Standardized drug nomenclature
  - Drug relationships and hierarchies
  - Ingredient mappings
- **Format**: RRF files, API
- **Coverage**: 100,000+ drug concepts

### 5. **Additional Sources**
- **PharmVar**: Star allele nomenclature
- **dbSNP**: Genetic variant database
- **DrugBank**: Drug target information
- **ClinVar**: Clinical variant interpretations

## 🛠 **Implementation Created**

### Data Collection Scripts
I've created 4 Python scripts in `/scripts/` directory:

#### 1. `collect_pharmgkb_data.py`
- **Purpose**: Download drug-gene interactions and variant annotations
- **Method**: REST API calls to PharmGKB
- **Output**: 
  - `pharmgkb_drug_gene_map.json`
  - `pharmgkb_allele_proxies.json`
  - `pharmgkb_raw_data.json`

#### 2. `collect_cpic_data.py`
- **Purpose**: Scrape CPIC guidelines for drug-gene pairs
- **Method**: Web scraping with BeautifulSoup
- **Output**:
  - `cpic_guidelines.json`
  - `cpic_drug_gene_map.json`
  - `cpic_raw_guidelines.json`

#### 3. `collect_fda_data.py`
- **Purpose**: Extract FDA pharmacogenomic biomarkers table
- **Method**: Web scraping FDA website
- **Output**:
  - `fda_biomarkers.json`
  - `fda_drug_gene_map.json`
  - `fda_guidelines.json`
  - `fda_raw_biomarkers.json`

#### 4. `integrate_data.py`
- **Purpose**: Combine all data sources into unified knowledge base
- **Method**: Data merging, deduplication, and validation
- **Output**:
  - `expanded_drug_gene_map.json`
  - `expanded_allele_proxies.json`
  - `expanded_guidelines.json`
  - `expanded_alternatives.json`
  - `expanded_knowledge_base.json`

### Supporting Files
- `requirements.txt`: Dependencies for data collection
- `README.md`: Comprehensive documentation
- `example_usage.py`: Demo of expanded capabilities
- `data_expansion_plan.md`: Detailed implementation plan

## 📊 **Expected Data Expansion**

### Current State
- **Drugs**: 7 medications
- **Genes**: 10+ pharmacogenes
- **Variants**: 20+ genetic variants
- **Interactions**: 50+ drug-gene interactions

### Target State (After Expansion)
- **Drugs**: 50+ medications (7x increase)
- **Genes**: 50+ pharmacogenes (5x increase)
- **Variants**: 200+ genetic variants (10x increase)
- **Interactions**: 500+ drug-gene interactions (10x increase)

### High-Priority Medications to Add
1. **Anticoagulants**: Warfarin, dabigatran, rivaroxaban
2. **Antiplatelets**: Clopidogrel, prasugrel, ticagrelor
3. **Statins**: Simvastatin, atorvastatin, rosuvastatin
4. **Antidepressants**: Fluoxetine, sertraline, amitriptyline
5. **Antipsychotics**: Clozapine, risperidone, olanzapine
6. **Immunosuppressants**: Azathioprine, mercaptopurine, tacrolimus
7. **Chemotherapy**: 5-fluorouracil, irinotecan, tamoxifen
8. **Cardiovascular**: Metoprolol, carvedilol, amlodipine

### High-Priority Genes to Add
1. **Phase I Enzymes**: CYP1A2, CYP2B6, CYP2C8, CYP2C9, CYP2C19, CYP2D6, CYP3A4, CYP3A5
2. **Phase II Enzymes**: UGT1A1, UGT2B7, UGT2B15, SULT1A1, COMT, TPMT, NAT2
3. **Transporters**: ABCB1, ABCC2, ABCG2, SLCO1B1, SLCO1B3, SLC22A1
4. **Receptors**: OPRM1, ADRB1, ADRB2, DRD2, HTR2A, VKORC1
5. **Other**: HLA-B, HLA-A, TPMT, DPYD, G6PD

## 🚀 **How to Use**

### Quick Start
```bash
# 1. Install dependencies
cd scripts
pip install -r requirements.txt

# 2. Run data collection
python collect_pharmgkb_data.py
python collect_cpic_data.py
python collect_fda_data.py

# 3. Integrate data
python integrate_data.py

# 4. Update application
cp ../app/engine/data/expanded_*.json ../app/engine/data/

# 5. Restart application
cd ..
uvicorn app.main:app --reload
```

### Expected Runtime
- **PharmGKB collection**: 5-10 minutes
- **CPIC collection**: 10-15 minutes
- **FDA collection**: 5-10 minutes
- **Data integration**: 2-5 minutes
- **Total**: 20-40 minutes

## 📈 **Data Quality Assurance**

### Validation Checks
- **Cross-validation** between sources
- **Duplicate detection** and removal
- **Data completeness** verification
- **Format consistency** checks
- **Expert review** of critical interactions

### Quality Metrics
- **Coverage**: Number of drugs/genes/variants
- **Accuracy**: Expert-validated interactions
- **Completeness**: Missing data identification
- **Consistency**: Format standardization

## 🔄 **Maintenance Plan**

### Regular Updates
- **Monthly**: PharmGKB updates
- **Quarterly**: CPIC guideline updates
- **Annually**: Complete knowledge base review

### Version Control
- **Git tags** for knowledge base versions
- **Change logs** for each update
- **Backup** of previous versions

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

## 🔍 **Technical Details**

### Data Processing Pipeline
1. **Download** raw data from sources
2. **Parse** and clean data
3. **Map** to our schema
4. **Validate** data quality
5. **Merge** with existing knowledge base
6. **Test** with sample queries

### Schema Mapping
- **Drug names** → RxNorm codes
- **Gene symbols** → Standardized nomenclature
- **Variants** → Functional consequences
- **Interactions** → Clinical significance levels

### Error Handling
- **API rate limiting** with retry logic
- **Website changes** with fallback parsing
- **Data validation** with error reporting
- **Graceful degradation** for missing data

## 📋 **File Structure**

```
scripts/
├── collect_pharmgkb_data.py    # PharmGKB data collection
├── collect_cpic_data.py        # CPIC guidelines collection
├── collect_fda_data.py         # FDA biomarkers collection
├── integrate_data.py           # Data integration
├── example_usage.py            # Usage demonstration
├── requirements.txt            # Dependencies
└── README.md                   # Documentation

app/engine/data/
├── expanded_drug_gene_map.json      # 50+ drugs
├── expanded_allele_proxies.json     # 200+ variants
├── expanded_guidelines.json         # Clinical evidence
├── expanded_alternatives.json       # Alternative medications
└── expanded_knowledge_base.json     # Complete knowledge base
```

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

## 🎉 **Benefits of Expansion**

### For Clinicians
- **Broader coverage** of commonly prescribed medications
- **More accurate** risk assessments
- **Better alternatives** for high-risk patients
- **Evidence-based** clinical decision support

### For Researchers
- **Comprehensive** pharmacogenomics database
- **Structured** data for analysis
- **Extensible** framework for new data
- **Validated** clinical interactions

### For Patients
- **Personalized** medication recommendations
- **Reduced** adverse drug reactions
- **Improved** treatment outcomes
- **Better** quality of care

## 📞 **Support**

For issues with data collection:
1. Check logs for error messages
2. Verify network connectivity
3. Update dependencies
4. Check source website changes

## 🎯 **Next Steps**

1. **Run the data collection scripts** to populate the knowledge base
2. **Test the expanded application** with sample data
3. **Validate the results** with clinical experts
4. **Deploy the updated system** for production use
5. **Set up regular updates** to keep data current

---

**Status**: ✅ Ready for implementation  
**Priority**: High  
**Timeline**: 2-4 weeks for full expansion  
**Last Updated**: October 4, 2025
