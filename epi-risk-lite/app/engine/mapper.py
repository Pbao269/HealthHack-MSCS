"""Map genetic variants to functional tags."""
import json
from pathlib import Path
from typing import List, Dict, Set

# Load knowledge bases
DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "allele_proxies.json") as f:
    ALLELE_PROXIES = json.load(f)

with open(DATA_DIR / "star_allele_proxies.json") as f:
    STAR_ALLELE_PROXIES = json.load(f)


def map_variants_to_tags(variants: List[Dict[str, str]]) -> tuple[Set[str], Dict[str, List[str]]]:
    """
    Map variants to functional tags.
    
    Args:
        variants: List of variant dicts with keys: rsid, genotype, gene, star
    
    Returns:
        (tags, gene_to_tags) where:
        - tags: Set of functional tag strings
        - gene_to_tags: Dict mapping gene name to list of tags affecting that gene
    """
    tags = set()
    gene_to_tags = {}
    
    for variant in variants:
        # Handle rsID + genotype
        if "rsid" in variant and "genotype" in variant:
            rsid = variant["rsid"]
            genotype = variant["genotype"]
            
            # Look up in allele proxies
            key = f"{rsid}:{genotype}"
            if key in ALLELE_PROXIES:
                tag = ALLELE_PROXIES[key]
                tags.add(tag)
                
                # Extract gene from tag (e.g., CYP2D6_loss -> CYP2D6)
                gene = extract_gene_from_tag(tag)
                if gene:
                    if gene not in gene_to_tags:
                        gene_to_tags[gene] = []
                    gene_to_tags[gene].append(tag)
        
        # Handle star alleles
        if "gene" in variant and "star" in variant:
            gene = variant["gene"]
            star = variant["star"]
            
            # Parse star allele (e.g., *4/*4 -> [*4, *4])
            alleles = parse_star_diplotype(star)
            
            for allele in alleles:
                key = f"{gene}{allele}"
                if key in STAR_ALLELE_PROXIES:
                    tag = STAR_ALLELE_PROXIES[key]
                    tags.add(tag)
                    
                    if gene not in gene_to_tags:
                        gene_to_tags[gene] = []
                    if tag not in gene_to_tags[gene]:
                        gene_to_tags[gene].append(tag)
    
    return tags, gene_to_tags


def extract_gene_from_tag(tag: str) -> str:
    """
    Extract gene symbol from functional tag.
    
    Examples:
        CYP2D6_loss -> CYP2D6
        CYP3A4_rs776746_TT -> CYP3A4
        SLCO1B1_reduced -> SLCO1B1
    """
    # Gene symbols typically start with capital letters and may include numbers
    # but end before an underscore
    parts = tag.split("_")
    if parts:
        return parts[0]
    return ""


def parse_star_diplotype(star: str) -> List[str]:
    """
    Parse star diplotype into individual alleles.
    
    Examples:
        *4/*4 -> [*4, *4]
        *2/*1 -> [*1, *2]
        *17 -> [*17]
    """
    if "/" in star:
        alleles = star.split("/")
        # Ensure each allele starts with *
        return [a if a.startswith("*") else f"*{a}" for a in alleles]
    else:
        # Single allele
        return [star if star.startswith("*") else f"*{star}"]

