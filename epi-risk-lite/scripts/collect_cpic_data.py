#!/usr/bin/env python3
"""
CPIC Guidelines Data Collection Script

This script collects data from CPIC guidelines to expand the Epi-Risk Lite knowledge base.
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

class CPICCollector:
    """Collects data from CPIC guidelines and processes it for Epi-Risk Lite."""
    
    def __init__(self, output_dir: Path = Path("../app/engine/data")):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Epi-Risk-Lite/1.0 (https://github.com/your-repo/epi-risk-lite)'
        })
    
    def get_cpic_guidelines(self) -> List[Dict]:
        """Scrape CPIC guidelines from their website."""
        logger.info("Collecting CPIC guidelines...")
        
        # CPIC guidelines page
        url = "https://cpicpgx.org/guidelines/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            guidelines = []
            
            # Find guideline links
            guideline_links = soup.find_all('a', href=re.compile(r'/guidelines/'))
            
            for link in guideline_links:
                guideline_url = f"https://cpicpgx.org{link['href']}"
                guideline_name = link.get_text(strip=True)
                
                # Extract drug and gene from guideline name
                # Format: "Drug Name - Gene Name"
                if ' - ' in guideline_name:
                    drug_name, gene_name = guideline_name.split(' - ', 1)
                    guidelines.append({
                        'name': guideline_name,
                        'drug': drug_name.strip(),
                        'gene': gene_name.strip(),
                        'url': guideline_url
                    })
            
            logger.info(f"Found {len(guidelines)} CPIC guidelines")
            return guidelines
            
        except Exception as e:
            logger.error(f"Error collecting CPIC guidelines: {e}")
            return []
    
    def get_guideline_details(self, guideline_url: str) -> Dict:
        """Get detailed information from a specific guideline page."""
        try:
            response = self.session.get(guideline_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract key information
            details = {
                'url': guideline_url,
                'title': '',
                'drug': '',
                'gene': '',
                'phenotypes': [],
                'recommendations': [],
                'evidence_level': '',
                'last_updated': ''
            }
            
            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                details['title'] = title_elem.get_text(strip=True)
            
            # Extract drug and gene from title
            if ' - ' in details['title']:
                drug, gene = details['title'].split(' - ', 1)
                details['drug'] = drug.strip()
                details['gene'] = gene.strip()
            
            # Extract phenotypes and recommendations
            # Look for tables with phenotype information
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        phenotype = cells[0].get_text(strip=True)
                        recommendation = cells[1].get_text(strip=True)
                        
                        if phenotype and recommendation:
                            details['phenotypes'].append({
                                'phenotype': phenotype,
                                'recommendation': recommendation
                            })
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting guideline details from {guideline_url}: {e}")
            return {}
    
    def process_guidelines(self, guidelines: List[Dict]) -> Dict:
        """Process CPIC guidelines into our format."""
        logger.info("Processing CPIC guidelines...")
        
        processed_guidelines = {
            'epistasis_pairs': {},
            'single_tags': {},
            'drug_gene_pairs': {},
            'recommendations': {}
        }
        
        for guideline in guidelines:
            drug = guideline['drug'].lower()
            gene = guideline['gene']
            
            # Get detailed information
            details = self.get_guideline_details(guideline['url'])
            
            if not details.get('drug') or not details.get('gene'):
                continue
            
            # Process phenotypes and recommendations
            for item in details.get('phenotypes', []):
                phenotype = item['phenotype']
                recommendation = item['recommendation']
                
                # Map phenotype to functional tag
                if 'poor metabolizer' in phenotype.lower() or 'pm' in phenotype.lower():
                    tag = f"{gene}_loss"
                elif 'intermediate metabolizer' in phenotype.lower() or 'im' in phenotype.lower():
                    tag = f"{gene}_reduced"
                elif 'ultrarapid metabolizer' in phenotype.lower() or 'um' in phenotype.lower():
                    tag = f"{gene}_ultrarapid"
                elif 'extensive metabolizer' in phenotype.lower() or 'em' in phenotype.lower():
                    tag = f"{gene}_normal"
                else:
                    tag = f"{gene}_{phenotype.lower().replace(' ', '_')}"
                
                # Add to single tags
                processed_guidelines['single_tags'][tag] = {
                    'weight': self._get_weight_from_recommendation(recommendation),
                    'evidence': [f"CPIC guideline: {recommendation}"],
                    'drugs': [drug]
                }
                
                # Add to drug-gene pairs
                pair_key = f"{drug}_{gene}"
                if pair_key not in processed_guidelines['drug_gene_pairs']:
                    processed_guidelines['drug_gene_pairs'][pair_key] = {
                        'drug': drug,
                        'gene': gene,
                        'phenotypes': []
                    }
                
                processed_guidelines['drug_gene_pairs'][pair_key]['phenotypes'].append({
                    'phenotype': phenotype,
                    'tag': tag,
                    'recommendation': recommendation
                })
        
        return processed_guidelines
    
    def _get_weight_from_recommendation(self, recommendation: str) -> float:
        """Extract weight from recommendation text."""
        recommendation_lower = recommendation.lower()
        
        if 'avoid' in recommendation_lower or 'contraindicated' in recommendation_lower:
            return 0.50  # High risk
        elif 'reduce dose' in recommendation_lower or 'decrease' in recommendation_lower:
            return 0.35  # Moderate risk
        elif 'monitor' in recommendation_lower or 'caution' in recommendation_lower:
            return 0.20  # Low risk
        elif 'normal' in recommendation_lower or 'standard' in recommendation_lower:
            return 0.05  # Very low risk
        else:
            return 0.15  # Default moderate risk
    
    def get_drug_gene_mapping(self, guidelines: List[Dict]) -> Dict:
        """Create drug-gene mapping from CPIC guidelines."""
        logger.info("Creating drug-gene mapping from CPIC guidelines...")
        
        drug_gene_map = {}
        
        for guideline in guidelines:
            drug = guideline['drug'].lower()
            gene = guideline['gene']
            
            if drug not in drug_gene_map:
                drug_gene_map[drug] = {
                    'name': drug,
                    'genes': [],
                    'source': 'CPIC'
                }
            
            if gene not in drug_gene_map[drug]['genes']:
                drug_gene_map[drug]['genes'].append(gene)
        
        return drug_gene_map
    
    def save_data(self, data: Dict, filename: str):
        """Save processed data to JSON file."""
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved data to {output_path}")
    
    def collect_all_data(self):
        """Collect all data from CPIC and process it."""
        logger.info("Starting CPIC data collection...")
        
        # Get guidelines
        guidelines = self.get_cpic_guidelines()
        
        # Process guidelines
        processed_guidelines = self.process_guidelines(guidelines)
        drug_gene_map = self.get_drug_gene_mapping(guidelines)
        
        # Save processed data
        self.save_data(processed_guidelines, "cpic_guidelines.json")
        self.save_data(drug_gene_map, "cpic_drug_gene_map.json")
        
        # Save raw guidelines for reference
        self.save_data(guidelines, "cpic_raw_guidelines.json")
        
        logger.info("CPIC data collection completed!")

def main():
    """Main function to run the data collection."""
    collector = CPICCollector()
    collector.collect_all_data()

if __name__ == "__main__":
    main()
