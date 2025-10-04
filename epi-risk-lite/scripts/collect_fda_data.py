#!/usr/bin/env python3
"""
FDA Pharmacogenomic Biomarkers Data Collection Script

This script collects data from the FDA Table of Pharmacogenomic Biomarkers to expand the Epi-Risk Lite knowledge base.
"""

import requests
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import re
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FDACollector:
    """Collects data from FDA pharmacogenomic biomarkers table."""
    
    def __init__(self, output_dir: Path = Path("../app/engine/data")):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Epi-Risk-Lite/1.0 (https://github.com/your-repo/epi-risk-lite)'
        })
    
    def get_fda_biomarkers_table(self) -> List[Dict]:
        """Scrape FDA Table of Pharmacogenomic Biomarkers."""
        logger.info("Collecting FDA pharmacogenomic biomarkers...")
        
        # FDA Table of Pharmacogenomic Biomarkers URL
        url = "https://www.fda.gov/drugs/science-and-research-drugs/table-pharmacogenomic-biomarkers-drug-labeling"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            biomarkers = []
            
            # Find the main table
            table = soup.find('table')
            if not table:
                logger.error("Could not find FDA biomarkers table")
                return []
            
            # Extract table headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            logger.info(f"Found table headers: {headers}")
            
            # Extract table data
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:  # Ensure we have enough columns
                    row_data = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            row_data[headers[i]] = cell.get_text(strip=True)
                    
                    # Only process rows with drug information
                    if row_data.get('Drug') and row_data.get('Biomarker'):
                        biomarkers.append(row_data)
            
            logger.info(f"Extracted {len(biomarkers)} biomarker entries")
            return biomarkers
            
        except Exception as e:
            logger.error(f"Error collecting FDA biomarkers: {e}")
            return []
    
    def process_biomarkers(self, biomarkers: List[Dict]) -> Dict:
        """Process FDA biomarkers into our format."""
        logger.info("Processing FDA biomarkers...")
        
        processed_data = {
            'drug_biomarkers': {},
            'biomarker_genes': {},
            'clinical_significance': {},
            'drug_gene_map': {}
        }
        
        for biomarker in biomarkers:
            drug_name = biomarker.get('Drug', '').strip()
            biomarker_name = biomarker.get('Biomarker', '').strip()
            indication = biomarker.get('Indication', '').strip()
            significance = biomarker.get('Clinical Significance', '').strip()
            
            if not drug_name or not biomarker_name:
                continue
            
            # Normalize drug name
            drug_normalized = drug_name.lower().strip()
            
            # Extract gene symbols from biomarker name
            # Common patterns: "CYP2D6", "UGT1A1*28", "HLA-B*1502"
            gene_match = re.search(r'([A-Z0-9]+)(?:\*[0-9A-Z]+)?', biomarker_name)
            if gene_match:
                gene_symbol = gene_match.group(1)
            else:
                # Try to extract from indication or other fields
                gene_match = re.search(r'([A-Z0-9]+)', biomarker_name)
                gene_symbol = gene_match.group(1) if gene_match else biomarker_name
            
            # Create drug-biomarker entry
            if drug_normalized not in processed_data['drug_biomarkers']:
                processed_data['drug_biomarkers'][drug_normalized] = {
                    'name': drug_normalized,
                    'biomarkers': [],
                    'genes': [],
                    'source': 'FDA'
                }
            
            # Add biomarker
            processed_data['drug_biomarkers'][drug_normalized]['biomarkers'].append({
                'biomarker': biomarker_name,
                'gene': gene_symbol,
                'indication': indication,
                'significance': significance
            })
            
            # Add gene if not already present
            if gene_symbol not in processed_data['drug_biomarkers'][drug_normalized]['genes']:
                processed_data['drug_biomarkers'][drug_normalized]['genes'].append(gene_symbol)
            
            # Create gene entry
            if gene_symbol not in processed_data['biomarker_genes']:
                processed_data['biomarker_genes'][gene_symbol] = {
                    'gene': gene_symbol,
                    'biomarkers': [],
                    'drugs': []
                }
            
            processed_data['biomarker_genes'][gene_symbol]['biomarkers'].append({
                'biomarker': biomarker_name,
                'drug': drug_normalized,
                'indication': indication,
                'significance': significance
            })
            
            if drug_normalized not in processed_data['biomarker_genes'][gene_symbol]['drugs']:
                processed_data['biomarker_genes'][gene_symbol]['drugs'].append(drug_normalized)
            
            # Map clinical significance to weights
            significance_weight = self._get_significance_weight(significance)
            processed_data['clinical_significance'][f"{drug_normalized}_{gene_symbol}"] = {
                'drug': drug_normalized,
                'gene': gene_symbol,
                'significance': significance,
                'weight': significance_weight,
                'evidence': [f"FDA drug labeling: {significance}"]
            }
        
        return processed_data
    
    def _get_significance_weight(self, significance: str) -> float:
        """Map clinical significance to risk weight."""
        significance_lower = significance.lower()
        
        if 'contraindicated' in significance_lower or 'avoid' in significance_lower:
            return 0.50  # High risk
        elif 'warning' in significance_lower or 'caution' in significance_lower:
            return 0.35  # Moderate risk
        elif 'monitor' in significance_lower or 'adjust' in significance_lower:
            return 0.20  # Low risk
        elif 'response' in significance_lower or 'efficacy' in significance_lower:
            return 0.15  # Efficacy-related
        else:
            return 0.10  # Default low risk
    
    def create_drug_gene_map(self, processed_data: Dict) -> Dict:
        """Create drug-gene mapping from FDA data."""
        logger.info("Creating drug-gene mapping from FDA data...")
        
        drug_gene_map = {}
        
        for drug, data in processed_data['drug_biomarkers'].items():
            drug_gene_map[drug] = {
                'name': drug,
                'genes': data['genes'],
                'biomarkers': data['biomarkers'],
                'source': 'FDA'
            }
        
        return drug_gene_map
    
    def create_guidelines(self, processed_data: Dict) -> Dict:
        """Create guidelines from FDA biomarker data."""
        logger.info("Creating guidelines from FDA data...")
        
        guidelines = {
            'single_tags': {},
            'epistasis_pairs': {},
            'fda_biomarkers': {}
        }
        
        # Process clinical significance data
        for key, data in processed_data['clinical_significance'].items():
            drug = data['drug']
            gene = data['gene']
            significance = data['significance']
            weight = data['weight']
            
            # Create functional tag based on significance
            if 'contraindicated' in significance.lower():
                tag = f"{gene}_contraindicated"
            elif 'warning' in significance.lower():
                tag = f"{gene}_warning"
            elif 'monitor' in significance.lower():
                tag = f"{gene}_monitor"
            else:
                tag = f"{gene}_fda_biomarker"
            
            guidelines['single_tags'][tag] = {
                'weight': weight,
                'evidence': data['evidence'],
                'drugs': [drug],
                'source': 'FDA'
            }
            
            # Add to FDA biomarkers
            guidelines['fda_biomarkers'][key] = {
                'drug': drug,
                'gene': gene,
                'tag': tag,
                'significance': significance,
                'weight': weight
            }
        
        return guidelines
    
    def save_data(self, data: Dict, filename: str):
        """Save processed data to JSON file."""
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved data to {output_path}")
    
    def collect_all_data(self):
        """Collect all data from FDA and process it."""
        logger.info("Starting FDA data collection...")
        
        # Get biomarkers table
        biomarkers = self.get_fda_biomarkers_table()
        
        if not biomarkers:
            logger.error("No biomarkers data collected")
            return
        
        # Process biomarkers
        processed_data = self.process_biomarkers(biomarkers)
        drug_gene_map = self.create_drug_gene_map(processed_data)
        guidelines = self.create_guidelines(processed_data)
        
        # Save processed data
        self.save_data(processed_data, "fda_biomarkers.json")
        self.save_data(drug_gene_map, "fda_drug_gene_map.json")
        self.save_data(guidelines, "fda_guidelines.json")
        
        # Save raw data for reference
        self.save_data(biomarkers, "fda_raw_biomarkers.json")
        
        logger.info("FDA data collection completed!")

def main():
    """Main function to run the data collection."""
    collector = FDACollector()
    collector.collect_all_data()

if __name__ == "__main__":
    main()
