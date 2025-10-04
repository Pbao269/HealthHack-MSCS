"""Drug-gene pathway mapping."""
import json
from pathlib import Path
from typing import List, Dict, Optional

DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "drug_gene_map.json") as f:
    DRUG_GENE_MAP = json.load(f)

with open(DATA_DIR / "alternatives.json") as f:
    ALTERNATIVES = json.load(f)


def get_drug_info(medication_name: Optional[str] = None, rxnorm: Optional[str] = None) -> Optional[Dict]:
    """
    Get drug information including pathway genes.
    
    Args:
        medication_name: Drug name (e.g., "codeine")
        rxnorm: RxNorm code (e.g., "1049630")
    
    Returns:
        Dict with keys: name, genes, rxnorm
    """
    # Try rxnorm first
    if rxnorm:
        key = f"rxnorm:{rxnorm}"
        if key in DRUG_GENE_MAP:
            info = DRUG_GENE_MAP[key].copy()
            info["rxnorm"] = rxnorm
            return info
    
    # Try medication name
    if medication_name:
        med_lower = medication_name.lower().strip()
        for key, info in DRUG_GENE_MAP.items():
            if info["name"].lower() == med_lower:
                rxnorm_code = key.split(":")[-1] if ":" in key else None
                result = info.copy()
                result["rxnorm"] = rxnorm_code
                return result
    
    return None


def filter_tags_by_pathway(tags: List[str], pathway_genes: List[str]) -> List[str]:
    """
    Filter tags to only those affecting genes in the drug pathway.
    
    Args:
        tags: List of functional tags
        pathway_genes: List of gene symbols relevant to the drug
    
    Returns:
        Filtered list of tags
    """
    from .mapper import extract_gene_from_tag
    
    filtered = []
    pathway_genes_set = {g.upper() for g in pathway_genes}
    
    for tag in tags:
        gene = extract_gene_from_tag(tag)
        if gene.upper() in pathway_genes_set:
            filtered.append(tag)
    
    return filtered


def get_alternatives(medication_name: str) -> List[Dict[str, str]]:
    """
    Get alternative medications with less genetic risk.
    
    Args:
        medication_name: Drug name
    
    Returns:
        List of alternative drug dicts with keys: rxnorm, name, note
    """
    med_lower = medication_name.lower().strip()
    return ALTERNATIVES.get(med_lower, [])

