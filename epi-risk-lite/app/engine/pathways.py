"""Drug-gene pathway mapping."""
import json
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple

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


def validate_alternatives(
    alternatives: List[Dict[str, str]], 
    patient_variants: List[Dict[str, str]]
) -> Dict[str, List[Dict]]:
    """
    Validate alternatives against patient's genetic profile.
    
    Args:
        alternatives: List of alternative medications
        patient_variants: Patient's genetic variants
    
    Returns:
        Dict with safe_alternatives, caution_required, not_recommended
    """
    from .mapper import map_variants_to_tags, extract_gene_from_tag
    from .rules import score_deterministic
    
    # Map patient variants to functional tags
    patient_tags, gene_to_tags = map_variants_to_tags(patient_variants)
    
    safe_alternatives = []
    caution_required = []
    not_recommended = []
    
    for alt in alternatives:
        # Get drug info for the alternative
        alt_drug_info = get_drug_info(alt["name"])
        if not alt_drug_info:
            # If we don't have drug info, mark as caution required
            caution_alt = {
                **alt,
                "risk_score": 0.5,  # Unknown risk
                "risk_label": "moderate",
                "safety_status": "CAUTION_REQUIRED",
                "safety_warnings": ["Unknown genetic risk profile for this medication"]
            }
            caution_required.append(caution_alt)
            continue
        
        # Get pathway genes for the alternative
        alt_pathway_genes = alt_drug_info["genes"]
        
        # Filter patient tags to alternative's pathway
        alt_pathway_tags = filter_tags_by_pathway(list(patient_tags), alt_pathway_genes)
        alt_pathway_tags_set = set(alt_pathway_tags)
        
        # Filter gene_to_tags to alternative's pathway genes
        alt_gene_to_tags = {
            gene: tags for gene, tags in gene_to_tags.items()
            if gene in alt_pathway_genes
        }
        
        # Score the alternative
        if alt_pathway_tags_set:
            score, label, rationales = score_deterministic(
                alt_pathway_tags_set, alt_gene_to_tags, alt["name"]
            )
        else:
            # No relevant genetic variants for this alternative
            score, label, rationales = 0.05, "low", []
        
        # Categorize based on risk
        enhanced_alt = {
            **alt,
            "risk_score": round(score, 3),
            "risk_label": label,
            "safety_warnings": [r.get("evidence", [""])[0] for r in rationales if r.get("evidence")],
            "pathway_genes": alt_pathway_genes
        }
        
        if label == "low":
            enhanced_alt["safety_status"] = "SAFE"
            safe_alternatives.append(enhanced_alt)
        elif label == "moderate":
            enhanced_alt["safety_status"] = "CAUTION_REQUIRED"
            caution_required.append(enhanced_alt)
        else:  # high risk
            enhanced_alt["safety_status"] = "NOT_RECOMMENDED"
            not_recommended.append(enhanced_alt)
    
    # Sort by risk score (lowest first)
    safe_alternatives.sort(key=lambda x: x["risk_score"])
    caution_required.sort(key=lambda x: x["risk_score"])
    not_recommended.sort(key=lambda x: x["risk_score"])
    
    return {
        "safe_alternatives": safe_alternatives,
        "caution_required": caution_required,
        "not_recommended": not_recommended,
        "no_safe_alternatives": len(safe_alternatives) == 0
    }


def get_safe_alternatives(medication_name: str, patient_variants: List[Dict[str, str]]) -> Dict[str, List[Dict]]:
    """
    Get alternatives that are safe for this specific patient.
    
    Args:
        medication_name: Original medication name
        patient_variants: Patient's genetic variants
    
    Returns:
        Dict with categorized alternatives based on safety
    """
    # Get all alternatives for the medication
    alternatives = get_alternatives(medication_name)
    
    if not alternatives:
        return {
            "safe_alternatives": [],
            "caution_required": [],
            "not_recommended": [],
            "no_safe_alternatives": True
        }
    
    # Validate each alternative against patient genetics
    return validate_alternatives(alternatives, patient_variants)

