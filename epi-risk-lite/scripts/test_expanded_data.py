#!/usr/bin/env python3
"""
Test Expanded Data Script

This script tests the expanded knowledge base to ensure it works correctly with the API.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.engine.scorer import RiskScorer
from app.engine.mapper import map_variants_to_tags
from app.engine.pathways import get_drug_info, get_alternatives

def test_expanded_data():
    """Test the expanded knowledge base."""
    print("🧪 Testing Expanded Knowledge Base")
    print("=" * 40)
    
    # Load expanded knowledge base
    data_dir = Path(__file__).parent.parent / "app" / "engine" / "data"
    expanded_kb_path = data_dir / "expanded_knowledge_base.json"
    
    if not expanded_kb_path.exists():
        print("❌ Expanded knowledge base not found!")
        return False
    
    with open(expanded_kb_path, 'r') as f:
        expanded_kb = json.load(f)
    
    print(f"✅ Loaded expanded knowledge base")
    print(f"   - Drugs: {len(expanded_kb['drug_gene_map'])}")
    print(f"   - Variants: {len(expanded_kb['allele_proxies'])}")
    print(f"   - Star alleles: {len(expanded_kb['star_allele_proxies'])}")
    print(f"   - Alternatives: {len(expanded_kb['alternatives'])}")
    print()
    
    # Test 1: Drug-gene mapping
    print("🔬 Test 1: Drug-gene mapping")
    test_drugs = ["codeine", "clopidogrel", "warfarin", "simvastatin", "tamoxifen"]
    
    for drug in test_drugs:
        # Find drug by name
        drug_info = None
        for rxnorm, info in expanded_kb['drug_gene_map'].items():
            if info['name'].lower() == drug.lower():
                drug_info = info
                break
        
        if drug_info:
            print(f"   ✅ {drug}: {drug_info['genes']}")
        else:
            print(f"   ❌ {drug}: Not found")
    
    print()
    
    # Test 2: Variant mapping
    print("🧬 Test 2: Variant mapping")
    test_variants = [
        {"rsid": "rs3892097", "genotype": "AA"},  # CYP2D6_loss
        {"rsid": "rs4244285", "genotype": "AA"},  # CYP2C19_loss
        {"rsid": "rs776746", "genotype": "TT"},   # CYP3A4_rs776746_TT
        {"rsid": "rs9923231", "genotype": "TT"},  # VKORC1_low_dose
    ]
    
    for variant in test_variants:
        tags = map_variants_to_tags([variant])
        if tags:
            print(f"   ✅ {variant['rsid']}:{variant['genotype']} → {list(tags)}")
        else:
            print(f"   ❌ {variant['rsid']}:{variant['genotype']} → No mapping")
    
    print()
    
    # Test 3: Star allele mapping
    print("⭐ Test 3: Star allele mapping")
    test_star_alleles = [
        {"gene": "CYP2D6", "star": "*4/*4"},
        {"gene": "CYP2C19", "star": "*2/*2"},
        {"gene": "CYP2C9", "star": "*3/*3"},
    ]
    
    for star_allele in test_star_alleles:
        tags = map_variants_to_tags([star_allele])
        if tags:
            print(f"   ✅ {star_allele['gene']} {star_allele['star']} → {list(tags)}")
        else:
            print(f"   ❌ {star_allele['gene']} {star_allele['star']} → No mapping")
    
    print()
    
    # Test 4: Risk scoring with expanded data
    print("📊 Test 4: Risk scoring with expanded data")
    
    # Initialize scorer
    scorer = RiskScorer()
    
    # Test cases
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
            "name": "HLA-B risk (abacavir)",
            "variants": [
                {"rsid": "rs2395029", "genotype": "GG"}
            ],
            "medication": "abacavir"
        }
    ]
    
    for test_case in test_cases:
        print(f"   Testing: {test_case['name']}")
        
        try:
            # Map variants to tags
            tags = map_variants_to_tags(test_case['variants'])
            
            # Get drug genes
            drug_info = get_drug_info(test_case['medication'])
            drug_genes = drug_info['genes'] if drug_info else []
            
            # Filter tags to drug pathway
            pathway_tags = {tag for tag in tags if any(gene in tag for gene in drug_genes)}
            
            # Score
            score, label, rationales = scorer.score_deterministic(
                pathway_tags, 
                {gene: [tag for tag in pathway_tags if gene in tag] for gene in drug_genes},
                test_case['medication']
            )
            
            print(f"      Score: {score:.2f} ({label})")
            print(f"      Tags: {list(pathway_tags)}")
            print(f"      Rationales: {len(rationales)}")
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
        
        print()
    
    # Test 5: Alternatives
    print("💊 Test 5: Alternative medications")
    test_medications = ["codeine", "clopidogrel", "warfarin", "simvastatin"]
    
    for med in test_medications:
        alternatives = get_alternatives(med)
        if alternatives:
            print(f"   ✅ {med}: {[alt['name'] for alt in alternatives]}")
        else:
            print(f"   ❌ {med}: No alternatives found")
    
    print()
    print("🎉 Expanded data testing completed!")
    return True

if __name__ == "__main__":
    test_expanded_data()
