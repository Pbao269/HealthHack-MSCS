# Epi-Risk Lite Data Expansion Plan

## 🎯 **Objective**
Expand the knowledge base in `/app/engine/data/` to support more medications and genes using credible online resources.

## 📚 **Primary Data Sources**

### 1. **PharmGKB (Pharmacogenomics Knowledge Base)**
- **URL**: https://www.pharmgkb.org/
- **Description**: Comprehensive resource for drug-gene interactions, clinical annotations, and dosing guidelines
- **Data Format**: CSV, TSV, JSON via API
- **Key Files**:
  - Drug-gene interactions
  - Clinical annotations
  - Variant annotations
  - Drug labels

### 2. **CPIC (Clinical Pharmacogenetics Implementation Consortium)**
- **URL**: https://cpicpgx.org/
- **Description**: Evidence-based guidelines for drug-gene pairs
- **Data Format**: Guidelines tables, structured data
- **Key Files**:
  - Drug-gene pair guidelines
  - Dosing recommendations
  - Phenotype assignments

### 3. **RxNorm (National Library of Medicine)**
- **URL**: https://www.nlm.nih.gov/research/umls/rxnorm/
- **Description**: Standardized drug nomenclature
- **Data Format**: RRF files, API
- **Key Files**:
  - Drug names and RxNorm codes
  - Drug relationships
  - Ingredient mappings

### 4. **FDA Table of Pharmacogenomic Biomarkers**
- **URL**: https://www.fda.gov/drugs/science-and-research-drugs/table-pharmacogenomic-biomarkers-drug-labeling
- **Description**: FDA-approved drug labels with pharmacogenomic information
- **Data Format**: HTML tables, structured data
- **Key Files**:
  - Drug-biomarker associations
  - Clinical significance levels

### 5. **PharmVar (Pharmacogene Variation Consortium)**
- **URL**: https://www.pharmvar.org/
- **Description**: Standardized pharmacogene variation nomenclature
- **Data Format**: Structured data, API
- **Key Files**:
  - Star allele definitions
  - Gene variant annotations

## 🔧 **Implementation Strategy**

### Phase 1: Data Collection Scripts
Create Python scripts to download and parse data from each source.

### Phase 2: Data Integration
Transform external data to match our JSON schema.

### Phase 3: Knowledge Base Expansion
Update existing JSON files with new data.

### Phase 4: Validation & Testing
Ensure data quality and test with expanded knowledge base.

## 📊 **Target Expansion Goals**

### Medications (Current: 7 → Target: 50+)
- **High Priority**: Warfarin, clopidogrel, statins, antidepressants, antipsychotics
- **Medium Priority**: Chemotherapy drugs, immunosuppressants, cardiovascular drugs
- **Low Priority**: Rare disease drugs, experimental compounds

### Genes (Current: 10+ → Target: 50+)
- **Phase I Enzymes**: CYP1A2, CYP2B6, CYP2C8, CYP2C9, CYP2C19, CYP2D6, CYP3A4, CYP3A5
- **Phase II Enzymes**: UGT1A1, UGT2B7, UGT2B15, SULT1A1, COMT, TPMT, NAT2
- **Transporters**: ABCB1, ABCC2, ABCG2, SLCO1B1, SLCO1B3, SLC22A1
- **Receptors**: OPRM1, ADRB1, ADRB2, DRD2, HTR2A, VKORC1

### Variants (Current: 20+ → Target: 200+)
- **SNPs**: rsIDs with functional consequences
- **Star Alleles**: Comprehensive pharmacogene haplotypes
- **CNVs**: Copy number variations affecting drug metabolism

## 🛠 **Technical Implementation**

### Data Collection Tools
- **APIs**: PharmGKB REST API, RxNorm API
- **Web Scraping**: BeautifulSoup for HTML tables
- **File Downloads**: Direct CSV/TSV downloads
- **Manual Curation**: Expert review of critical data

### Data Processing Pipeline
1. **Download** raw data from sources
2. **Parse** and clean data
3. **Map** to our schema
4. **Validate** data quality
5. **Merge** with existing knowledge base
6. **Test** with sample queries

### Quality Assurance
- **Cross-validation** between sources
- **Expert review** of critical interactions
- **Automated testing** of data integrity
- **Version control** of knowledge base updates

## 📁 **File Structure Updates**

### New Files to Create
```
app/engine/data/
├── expanded_drug_gene_map.json      # 50+ drugs
├── expanded_allele_proxies.json     # 200+ variants
├── expanded_star_allele_proxies.json # 100+ star alleles
├── expanded_alternatives.json       # Alternative medications
├── expanded_guidelines.json         # Clinical evidence
├── drug_categories.json             # Drug classification
├── gene_functions.json              # Gene function descriptions
└── population_frequencies.json      # Allele frequencies by population
```

### Existing Files to Expand
- `drug_gene_map.json`: 7 → 50+ drugs
- `allele_proxies.json`: 20+ → 200+ variants
- `star_allele_proxies.json`: 10+ → 100+ star alleles
- `alternatives.json`: 7 → 50+ drug alternatives
- `guidelines.json`: Expand evidence base

## 🚀 **Quick Start Implementation**

### Step 1: PharmGKB Integration
```python
# Download drug-gene interactions
# Parse clinical annotations
# Extract variant information
```

### Step 2: CPIC Guidelines
```python
# Parse guideline tables
# Extract drug-gene pairs
# Map to our schema
```

### Step 3: RxNorm Integration
```python
# Download drug database
# Map to RxNorm codes
# Standardize drug names
```

### Step 4: FDA Biomarkers
```python
# Scrape FDA table
# Extract biomarker associations
# Map to clinical significance
```

## 📈 **Success Metrics**

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

## 🔄 **Maintenance Plan**

### Regular Updates
- **Monthly**: PharmGKB updates
- **Quarterly**: CPIC guideline updates
- **Annually**: Complete knowledge base review

### Version Control
- **Git tags** for knowledge base versions
- **Change logs** for each update
- **Backup** of previous versions

### Quality Monitoring
- **Automated tests** for data integrity
- **Performance metrics** for scoring accuracy
- **User feedback** on clinical utility

## 📋 **Next Steps**

1. **Create data collection scripts** for each source
2. **Set up automated download pipeline**
3. **Implement data validation framework**
4. **Expand knowledge base incrementally**
5. **Test with expanded dataset**
6. **Deploy updated application**

---

**Status**: Ready for implementation  
**Priority**: High  
**Timeline**: 2-4 weeks for full expansion
