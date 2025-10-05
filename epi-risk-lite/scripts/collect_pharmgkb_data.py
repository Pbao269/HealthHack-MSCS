#!/usr/bin/env python3
"""
PharmGKB Data Collection Script

This script downloads and processes data from PharmGKB to expand the Epi-Risk Lite knowledge base.
"""

import requests
import json
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PharmGKB API base URL
PHARMGKB_BASE_URL = "https://api.pharmgkb.org/v1"

class PharmGKBCollector:
    """Collects data from PharmGKB API and processes it for Epi-Risk Lite."""
    
    def __init__(self, output_dir: Path = Path("app/engine/data")):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Epi-Risk-Lite/1.0 (https://github.com/Pbao269/HealthHack-MSCS)'
        })
    
    def get_drug_gene_interactions(self) -> List[Dict]:
        """Download drug-gene interactions from PharmGKB."""
        logger.info("Downloading drug-gene interactions...")
        
        # PharmGKB drug-gene interactions endpoint (updated)
        url = f"{PHARMGKB_BASE_URL}/data/drugGeneInteractions"
        
        try:
            response = self.session.get(url, params={'format': 'json', 'view': 'full'})
            response.raise_for_status()
            data = response.json()
            
            interactions = []
            for item in data.get('data', []):
                interaction = {
                    'drug_id': item.get('drug', {}).get('id'),
                    'drug_name': item.get('drug', {}).get('name'),
                    'gene_id': item.get('gene', {}).get('id'),
                    'gene_symbol': item.get('gene', {}).get('symbol'),
                    'interaction_type': item.get('interactionType'),
                    'evidence_level': item.get('evidenceLevel'),
                    'source': 'PharmGKB'
                }
                interactions.append(interaction)
            
            logger.info(f"Downloaded {len(interactions)} drug-gene interactions")
            return interactions
            
        except Exception as e:
            logger.error(f"Error downloading drug-gene interactions: {e}")
            return []
    
    def get_clinical_annotations(self) -> List[Dict]:
        """Download clinical annotations from PharmGKB."""
        logger.info("Downloading clinical annotations...")
        
        url = f"{PHARMGKB_BASE_URL}/data/clinicalAnnotations"
        
        try:
            response = self.session.get(url, params={'format': 'json', 'view': 'full'})
            response.raise_for_status()
            data = response.json()
            
            annotations = []
            for item in data.get('data', []):
                annotation = {
                    'drug_id': item.get('drug', {}).get('id'),
                    'drug_name': item.get('drug', {}).get('name'),
                    'gene_id': item.get('gene', {}).get('id'),
                    'gene_symbol': item.get('gene', {}).get('symbol'),
                    'variant_id': item.get('variant', {}).get('id'),
                    'variant_name': item.get('variant', {}).get('name'),
                    'phenotype': item.get('phenotype'),
                    'evidence_level': item.get('evidenceLevel'),
                    'clinical_significance': item.get('clinicalSignificance'),
                    'source': 'PharmGKB'
                }
                annotations.append(annotation)
            
            logger.info(f"Downloaded {len(annotations)} clinical annotations")
            return annotations
            
        except Exception as e:
            logger.error(f"Error downloading clinical annotations: {e}")
            return []
    
    def get_variant_annotations(self) -> List[Dict]:
        """Download variant annotations from PharmGKB."""
        logger.info("Downloading variant annotations...")
        
        url = f"{PHARMGKB_BASE_URL}/data/variantAnnotations"
        
        try:
            response = self.session.get(url, params={'format': 'json', 'view': 'full'})
            response.raise_for_status()
            data = response.json()
            
            variants = []
            for item in data.get('data', []):
                variant = {
                    'variant_id': item.get('id'),
                    'variant_name': item.get('name'),
                    'gene_id': item.get('gene', {}).get('id'),
                    'gene_symbol': item.get('gene', {}).get('symbol'),
                    'rsid': item.get('rsId'),
                    'chromosome': item.get('chromosome'),
                    'position': item.get('position'),
                    'reference_allele': item.get('referenceAllele'),
                    'alternate_allele': item.get('alternateAllele'),
                    'functional_consequence': item.get('functionalConsequence'),
                    'source': 'PharmGKB'
                }
                variants.append(variant)
            
            logger.info(f"Downloaded {len(variants)} variant annotations")
            return variants
            
        except Exception as e:
            logger.error(f"Error downloading variant annotations: {e}")
            return []
    
    def process_drug_gene_data(self, interactions: List[Dict]) -> Dict:
        """Process drug-gene interactions into our format."""
        logger.info("Processing drug-gene interactions...")
        
        drug_gene_map = {}
        
        for interaction in interactions:
            drug_name = interaction.get('drug_name', '').lower()
            gene_symbol = interaction.get('gene_symbol', '')
            interaction_type = interaction.get('interaction_type', '')
            evidence_level = interaction.get('evidence_level', '')
            
            if not drug_name or not gene_symbol:
                continue
            
            # Create drug entry if not exists
            if drug_name not in drug_gene_map:
                drug_gene_map[drug_name] = {
                    'name': drug_name,
                    'genes': [],
                    'interactions': [],
                    'source': 'PharmGKB'
                }
            
            # Add gene if not already present
            if gene_symbol not in drug_gene_map[drug_name]['genes']:
                drug_gene_map[drug_name]['genes'].append(gene_symbol)
            
            # Add interaction details
            drug_gene_map[drug_name]['interactions'].append({
                'gene': gene_symbol,
                'type': interaction_type,
                'evidence': evidence_level
            })
        
        return drug_gene_map
    
    def process_variant_data(self, variants: List[Dict]) -> Dict:
        """Process variant annotations into our format."""
        logger.info("Processing variant annotations...")
        
        allele_proxies = {}
        
        for variant in variants:
            rsid = variant.get('rsid', '')
            gene_symbol = variant.get('gene_symbol', '')
            functional_consequence = variant.get('functional_consequence', '')
            ref_allele = variant.get('reference_allele', '')
            alt_allele = variant.get('alternate_allele', '')
            
            if not rsid or not gene_symbol or not functional_consequence:
                continue
            
            # Create genotype combinations
            if ref_allele and alt_allele:
                # Heterozygous
                het_genotype = f"{ref_allele}{alt_allele}"
                # Homozygous reference
                hom_ref_genotype = f"{ref_allele}{ref_allele}"
                # Homozygous alternate
                hom_alt_genotype = f"{alt_allele}{alt_allele}"
                
                # Map to functional tags
                if 'loss' in functional_consequence.lower() or 'decreased' in functional_consequence.lower():
                    tag = f"{gene_symbol}_loss"
                elif 'gain' in functional_consequence.lower() or 'increased' in functional_consequence.lower():
                    tag = f"{gene_symbol}_gain"
                elif 'reduced' in functional_consequence.lower():
                    tag = f"{gene_symbol}_reduced"
                else:
                    tag = f"{gene_symbol}_{functional_consequence.lower()}"
                
                # Add to allele proxies
                allele_proxies[f"{rsid}:{hom_alt_genotype}"] = tag
                allele_proxies[f"{rsid}:{het_genotype}"] = f"{gene_symbol}_intermediate"
                allele_proxies[f"{rsid}:{hom_ref_genotype}"] = f"{gene_symbol}_normal"
        
        return allele_proxies
    
    def save_data(self, data: Dict, filename: str):
        """Save processed data to JSON file."""
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved data to {output_path}")
    
    def collect_all_data(self):
        """Collect all data from PharmGKB and process it."""
        logger.info("Starting PharmGKB data collection...")
        
        # Download raw data
        interactions = self.get_drug_gene_interactions()
        annotations = self.get_clinical_annotations()
        variants = self.get_variant_annotations()
        
        # Process data
        drug_gene_map = self.process_drug_gene_data(interactions)
        allele_proxies = self.process_variant_data(variants)
        
        # Save processed data
        self.save_data(drug_gene_map, "pharmgkb_drug_gene_map.json")
        self.save_data(allele_proxies, "pharmgkb_allele_proxies.json")
        
        # Save raw data for reference
        self.save_data({
            'interactions': interactions,
            'annotations': annotations,
            'variants': variants
        }, "pharmgkb_raw_data.json")
        
        logger.info("PharmGKB data collection completed!")

def main():
    """Main function to run the data collection."""
    collector = PharmGKBCollector()
    collector.collect_all_data()

if __name__ == "__main__":
    main()
