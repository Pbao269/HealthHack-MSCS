#!/usr/bin/env python3
"""
Data Integration Script

This script integrates data from multiple sources (PharmGKB, CPIC, FDA) to create an expanded knowledge base for Epi-Risk Lite.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Set
import logging
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIntegrator:
    """Integrates data from multiple pharmacogenomics sources."""
    
    def __init__(self, data_dir: Path = Path("app/engine/data")):
        self.data_dir = data_dir
        self.output_dir = data_dir
        
        # Load existing data
        self.existing_data = self._load_existing_data()
        
        # Load new data
        self.new_data = self._load_new_data()
    
    def _load_existing_data(self) -> Dict:
        """Load existing knowledge base data."""
        existing_files = [
            'drug_gene_map.json',
            'allele_proxies.json',
            'star_allele_proxies.json',
            'alternatives.json',
            'guidelines.json'
        ]
        
        existing_data = {}
        for filename in existing_files:
            filepath = self.data_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    existing_data[filename.replace('.json', '')] = json.load(f)
                logger.info(f"Loaded existing {filename}")
            else:
                logger.warning(f"Existing file not found: {filename}")
        
        return existing_data
    
    def _load_new_data(self) -> Dict:
        """Load newly collected data."""
        new_files = [
            'pharmgkb_drug_gene_map.json',
            'pharmgkb_allele_proxies.json',
            'cpic_guidelines.json',
            'cpic_drug_gene_map.json',
            'fda_biomarkers.json',
            'fda_drug_gene_map.json',
            'fda_guidelines.json'
        ]
        
        new_data = {}
        for filename in new_files:
            filepath = self.data_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    new_data[filename.replace('.json', '')] = json.load(f)
                logger.info(f"Loaded new {filename}")
            else:
                logger.warning(f"New file not found: {filename}")
        
        return new_data
    
    def integrate_drug_gene_maps(self) -> Dict:
        """Integrate drug-gene mappings from all sources."""
        logger.info("Integrating drug-gene mappings...")
        
        integrated_map = {}
        
        # Start with existing data
        if 'drug_gene_map' in self.existing_data:
            for rxnorm, data in self.existing_data['drug_gene_map'].items():
                integrated_map[rxnorm] = data.copy()
                integrated_map[rxnorm]['sources'] = ['existing']
        
        # Add PharmGKB data
        if 'pharmgkb_drug_gene_map' in self.new_data:
            for drug_name, data in self.new_data['pharmgkb_drug_gene_map'].items():
                # Try to find RxNorm code for this drug
                rxnorm = self._find_rxnorm_for_drug(drug_name)
                if rxnorm:
                    if rxnorm not in integrated_map:
                        integrated_map[rxnorm] = {
                            'name': drug_name,
                            'genes': [],
                            'sources': []
                        }
                    
                    # Merge genes
                    for gene in data.get('genes', []):
                        if gene not in integrated_map[rxnorm]['genes']:
                            integrated_map[rxnorm]['genes'].append(gene)
                    
                    if 'PharmGKB' not in integrated_map[rxnorm]['sources']:
                        integrated_map[rxnorm]['sources'].append('PharmGKB')
        
        # Add CPIC data
        if 'cpic_drug_gene_map' in self.new_data:
            for drug_name, data in self.new_data['cpic_drug_gene_map'].items():
                rxnorm = self._find_rxnorm_for_drug(drug_name)
                if rxnorm:
                    if rxnorm not in integrated_map:
                        integrated_map[rxnorm] = {
                            'name': drug_name,
                            'genes': [],
                            'sources': []
                        }
                    
                    # Merge genes
                    for gene in data.get('genes', []):
                        if gene not in integrated_map[rxnorm]['genes']:
                            integrated_map[rxnorm]['genes'].append(gene)
                    
                    if 'CPIC' not in integrated_map[rxnorm]['sources']:
                        integrated_map[rxnorm]['sources'].append('CPIC')
        
        # Add FDA data
        if 'fda_drug_gene_map' in self.new_data:
            for drug_name, data in self.new_data['fda_drug_gene_map'].items():
                rxnorm = self._find_rxnorm_for_drug(drug_name)
                if rxnorm:
                    if rxnorm not in integrated_map:
                        integrated_map[rxnorm] = {
                            'name': drug_name,
                            'genes': [],
                            'sources': []
                        }
                    
                    # Merge genes
                    for gene in data.get('genes', []):
                        if gene not in integrated_map[rxnorm]['genes']:
                            integrated_map[rxnorm]['genes'].append(gene)
                    
                    if 'FDA' not in integrated_map[rxnorm]['sources']:
                        integrated_map[rxnorm]['sources'].append('FDA')
        
        logger.info(f"Integrated {len(integrated_map)} drug-gene mappings")
        return integrated_map
    
    def integrate_allele_proxies(self) -> Dict:
        """Integrate allele proxies from all sources."""
        logger.info("Integrating allele proxies...")
        
        integrated_proxies = {}
        
        # Start with existing data
        if 'allele_proxies' in self.existing_data:
            integrated_proxies.update(self.existing_data['allele_proxies'])
        
        # Add PharmGKB data
        if 'pharmgkb_allele_proxies' in self.new_data:
            integrated_proxies.update(self.new_data['pharmgkb_allele_proxies'])
        
        logger.info(f"Integrated {len(integrated_proxies)} allele proxies")
        return integrated_proxies
    
    def integrate_guidelines(self) -> Dict:
        """Integrate guidelines from all sources."""
        logger.info("Integrating guidelines...")
        
        integrated_guidelines = {
            'single_tags': {},
            'epistasis_pairs': {},
            'pathway_burden': {
                'weight': 0.20,
                'evidence': [
                    'Multiple gene impairment in same pathway indicates higher risk',
                    'Redundancy loss increases susceptibility to adverse events'
                ]
            }
        }
        
        # Start with existing data
        if 'guidelines' in self.existing_data:
            existing = self.existing_data['guidelines']
            integrated_guidelines['single_tags'].update(existing.get('single_tags', {}))
            integrated_guidelines['epistasis_pairs'].update(existing.get('epistasis_pairs', {}))
        
        # Add CPIC guidelines
        if 'cpic_guidelines' in self.new_data:
            cpic = self.new_data['cpic_guidelines']
            integrated_guidelines['single_tags'].update(cpic.get('single_tags', {}))
            integrated_guidelines['epistasis_pairs'].update(cpic.get('epistasis_pairs', {}))
        
        # Add FDA guidelines
        if 'fda_guidelines' in self.new_data:
            fda = self.new_data['fda_guidelines']
            integrated_guidelines['single_tags'].update(fda.get('single_tags', {}))
        
        logger.info(f"Integrated {len(integrated_guidelines['single_tags'])} single tags")
        logger.info(f"Integrated {len(integrated_guidelines['epistasis_pairs'])} epistasis pairs")
        return integrated_guidelines
    
    def integrate_alternatives(self) -> Dict:
        """Integrate alternative medications from all sources."""
        logger.info("Integrating alternatives...")
        
        integrated_alternatives = {}
        
        # Start with existing data
        if 'alternatives' in self.existing_data:
            integrated_alternatives.update(self.existing_data['alternatives'])
        
        # Add new alternatives based on drug-gene interactions
        # This would require additional logic to suggest alternatives
        # based on genetic contraindications
        
        logger.info(f"Integrated {len(integrated_alternatives)} alternative medications")
        return integrated_alternatives
    
    def _find_rxnorm_for_drug(self, drug_name: str) -> str:
        """Find RxNorm code for a drug name."""
        # This is a simplified mapping - in practice, you'd use RxNorm API
        drug_mapping = {
            'warfarin': '11289',
            'clopidogrel': '32968',
            'simvastatin': '42331',
            'codeine': '1049630',
            'morphine': '7052',
            'metoprolol': '6809',
            'omeprazole': '8123',
            'fluoxetine': '3295',
            'sertraline': '36567',
            'amitriptyline': '704',
            'carbamazepine': '2387',
            'phenytoin': '8183',
            'tamoxifen': '10379',
            'azathioprine': '1235',
            'mercaptopurine': '6809',
            'thiopurine': '6809'
        }
        
        return drug_mapping.get(drug_name.lower(), None)
    
    def create_expanded_knowledge_base(self) -> Dict:
        """Create the expanded knowledge base."""
        logger.info("Creating expanded knowledge base...")
        
        expanded_kb = {
            'drug_gene_map': self.integrate_drug_gene_maps(),
            'allele_proxies': self.integrate_allele_proxies(),
            'star_allele_proxies': self.existing_data.get('star_allele_proxies', {}),
            'alternatives': self.integrate_alternatives(),
            'guidelines': self.integrate_guidelines(),
            'metadata': {
                'version': 'expanded-1.0',
                'sources': ['existing', 'PharmGKB', 'CPIC', 'FDA'],
                'total_drugs': 0,
                'total_genes': 0,
                'total_variants': 0,
                'last_updated': pd.Timestamp.now().isoformat()
            }
        }
        
        # Calculate statistics
        expanded_kb['metadata']['total_drugs'] = len(expanded_kb['drug_gene_map'])
        expanded_kb['metadata']['total_variants'] = len(expanded_kb['allele_proxies'])
        
        # Count unique genes
        all_genes = set()
        for drug_data in expanded_kb['drug_gene_map'].values():
            all_genes.update(drug_data.get('genes', []))
        expanded_kb['metadata']['total_genes'] = len(all_genes)
        
        logger.info(f"Expanded knowledge base created:")
        logger.info(f"  - Drugs: {expanded_kb['metadata']['total_drugs']}")
        logger.info(f"  - Genes: {expanded_kb['metadata']['total_genes']}")
        logger.info(f"  - Variants: {expanded_kb['metadata']['total_variants']}")
        
        return expanded_kb
    
    def save_expanded_knowledge_base(self, expanded_kb: Dict):
        """Save the expanded knowledge base."""
        logger.info("Saving expanded knowledge base...")
        
        # Save individual files
        for key, data in expanded_kb.items():
            if key != 'metadata':
                filename = f"expanded_{key}.json"
                filepath = self.output_dir / filename
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Saved {filename}")
        
        # Save complete knowledge base
        complete_filepath = self.output_dir / "expanded_knowledge_base.json"
        with open(complete_filepath, 'w') as f:
            json.dump(expanded_kb, f, indent=2)
        logger.info(f"Saved complete knowledge base to {complete_filepath}")
    
    def run_integration(self):
        """Run the complete data integration process."""
        logger.info("Starting data integration process...")
        
        # Create expanded knowledge base
        expanded_kb = self.create_expanded_knowledge_base()
        
        # Save expanded knowledge base
        self.save_expanded_knowledge_base(expanded_kb)
        
        logger.info("Data integration completed!")

def main():
    """Main function to run the data integration."""
    integrator = DataIntegrator()
    integrator.run_integration()

if __name__ == "__main__":
    main()
