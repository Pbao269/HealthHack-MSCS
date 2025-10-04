#!/usr/bin/env python3
"""
Example Usage of Expanded Knowledge Base

This script demonstrates how to use the expanded knowledge base data.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.engine.scorer import RiskScorer
from app.engine.data import load_expanded_knowledge_base

def load_expanded_knowledge_base():
    """Load the expanded knowledge base."""
    data_dir = Path(__file__).parent.parent.parent / "epi-risk-lite" / "app" / "engine" / "data"
    
    # Try to load expanded data first
    expanded_file = data_dir / "expanded_knowledge_base.json"
    if expanded_file.exists():
        with open(expanded_file, 'r') as f:
            return json.load(f)
    
    # Fall back to individual expanded files
    expanded_data = {}
    expanded_files = [
        'expanded_drug_gene_map.json',
        'expanded_allele_proxies.json',
        'expanded_guidelines.json',
        'expanded_alternatives.json'
    ]
    
    for filename in expanded_files:
        filepath = data_dir / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                expanded_data[filename.replace('expanded_', '').replace('.json', '')] = json.load(f)
    
    return expanded_data

def demonstrate_expanded_capabilities():
    """Demonstrate the expanded capabilities of the knowledge base."""
    print("🧬 Epi-Risk Lite Expanded Knowledge Base Demo")
    print("=" * 50)
    
    # Load expanded knowledge base
    kb = load_expanded_knowledge_base()
    
    if not kb:
        print("❌ Expanded knowledge base not found. Run data collection scripts first.")
        return
    
    # Show statistics
    print("\n📊 Knowledge Base Statistics:")
    if 'metadata' in kb:
        metadata = kb['metadata']
        print(f"  - Total Drugs: {metadata.get('total_drugs', 'Unknown')}")
        print(f"  - Total Genes: {metadata.get('total_genes', 'Unknown')}")
        print(f"  - Total Variants: {metadata.get('total_variants', 'Unknown')}")
        print(f"  - Sources: {', '.join(metadata.get('sources', []))}")
        print(f"  - Last Updated: {metadata.get('last_updated', 'Unknown')}")
    
    # Show sample drugs
    print("\n💊 Sample Drugs in Knowledge Base:")
    drug_gene_map = kb.get('drug_gene_map', {})
    sample_drugs = list(drug_gene_map.items())[:10]
    
    for rxnorm, data in sample_drugs:
        drug_name = data.get('name', 'Unknown')
        genes = data.get('genes', [])
        sources = data.get('sources', [])
        print(f"  - {drug_name} (RxNorm: {rxnorm})")
        print(f"    Genes: {', '.join(genes[:5])}{'...' if len(genes) > 5 else ''}")
        print(f"    Sources: {', '.join(sources)}")
        print()
    
    # Show sample variants
    print("🧬 Sample Variants in Knowledge Base:")
    allele_proxies = kb.get('allele_proxies', {})
    sample_variants = list(allele_proxies.items())[:10]
    
    for variant, tag in sample_variants:
        print(f"  - {variant} → {tag}")
    
    # Show sample guidelines
    print("\n📋 Sample Clinical Guidelines:")
    guidelines = kb.get('guidelines', {})
    single_tags = guidelines.get('single_tags', {})
    sample_tags = list(single_tags.items())[:5]
    
    for tag, data in sample_tags:
        weight = data.get('weight', 0)
        evidence = data.get('evidence', [])
        drugs = data.get('drugs', [])
        print(f"  - {tag} (Weight: {weight})")
        print(f"    Evidence: {evidence[0] if evidence else 'No evidence'}")
        print(f"    Drugs: {', '.join(drugs[:3])}{'...' if len(drugs) > 3 else ''}")
        print()

def demonstrate_risk_scoring():
    """Demonstrate risk scoring with expanded knowledge base."""
    print("\n🎯 Risk Scoring Demo with Expanded Data")
    print("=" * 50)
    
    # Initialize scorer
    scorer = RiskScorer()
    
    # Example 1: Warfarin with CYP2C9 and VKORC1 variants
    print("\nExample 1: Warfarin Risk Assessment")
    print("-" * 40)
    
    warfarin_variants = [
        {"rsid": "rs1799853", "genotype": "CT"},  # CYP2C9*2
        {"rsid": "rs9923231", "genotype": "AA"},  # VKORC1
        {"rsid": "rs1057910", "genotype": "AC"}   # CYP2C9*3
    ]
    
    try:
        result = scorer.score(
            variants=warfarin_variants,
            medication_name="warfarin"
        )
        
        print(f"Risk Score: {result['risk_score']}")
        print(f"Risk Label: {result['risk_label']}")
        print(f"Model Version: {result['model_version']}")
        print("\nRationales:")
        for rationale in result['rationales']:
            print(f"  - {rationale['type']}: {rationale.get('evidence', ['No evidence'])[0]}")
        
        print("\nSuggested Alternatives:")
        for alt in result['suggested_alternatives']:
            print(f"  - {alt['name']}: {alt['note']}")
    
    except Exception as e:
        print(f"Error scoring warfarin: {e}")
    
    # Example 2: Clopidogrel with CYP2C19 variants
    print("\nExample 2: Clopidogrel Risk Assessment")
    print("-" * 40)
    
    clopidogrel_variants = [
        {"rsid": "rs4244285", "genotype": "AA"},  # CYP2C19*2
        {"rsid": "rs776746", "genotype": "TT"}    # CYP3A4
    ]
    
    try:
        result = scorer.score(
            variants=clopidogrel_variants,
            medication_name="clopidogrel"
        )
        
        print(f"Risk Score: {result['risk_score']}")
        print(f"Risk Label: {result['risk_label']}")
        print(f"Model Version: {result['model_version']}")
        print("\nRationales:")
        for rationale in result['rationales']:
            print(f"  - {rationale['type']}: {rationale.get('evidence', ['No evidence'])[0]}")
        
        print("\nSuggested Alternatives:")
        for alt in result['suggested_alternatives']:
            print(f"  - {alt['name']}: {alt['note']}")
    
    except Exception as e:
        print(f"Error scoring clopidogrel: {e}")

def main():
    """Main function to run the demonstration."""
    demonstrate_expanded_capabilities()
    demonstrate_risk_scoring()
    
    print("\n✅ Demo completed!")
    print("\nTo use the expanded knowledge base:")
    print("1. Run the data collection scripts")
    print("2. Restart the Epi-Risk Lite application")
    print("3. The application will automatically use the expanded data")

if __name__ == "__main__":
    main()
