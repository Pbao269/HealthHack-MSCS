"""Deterministic rule-based scoring."""
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple

DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "guidelines.json") as f:
    GUIDELINES = json.load(f)


def score_deterministic(
    tags: Set[str],
    gene_to_tags: Dict[str, List[str]],
    drug_name: str
) -> Tuple[float, str, List[Dict]]:
    """
    Compute deterministic risk score and generate rationales.
    
    Args:
        tags: Set of functional tags
        gene_to_tags: Dict mapping genes to their tags
        drug_name: Medication name
    
    Returns:
        (score, label, rationales) where:
        - score: float in [0, 1]
        - label: "low" | "moderate" | "high"
        - rationales: List of explanation dicts
    """
    base_score = 0.05
    tag_sum = 0.0
    pair_sum = 0.0
    pathway_burden = 0.0
    
    rationales = []
    
    # Single tag weights
    single_tags_config = GUIDELINES.get("single_tags", {})
    for tag in tags:
        if tag in single_tags_config:
            weight = single_tags_config[tag]["weight"]
            evidence = single_tags_config[tag]["evidence"]
            tag_sum += weight
            
            # Only add rationale for significant tags (weight >= 0.15)
            if weight >= 0.15:
                rationales.append({
                    "type": "single_tag",
                    "tag": tag,
                    "evidence": evidence
                })
    
    # Pairwise interaction weights
    pairs_config = GUIDELINES.get("epistasis_pairs", {})
    tags_list = list(tags)
    
    for i, tag1 in enumerate(tags_list):
        for tag2 in tags_list[i+1:]:
            # Try both orderings
            key1 = f"{tag1}+{tag2}"
            key2 = f"{tag2}+{tag1}"
            
            pair_info = pairs_config.get(key1) or pairs_config.get(key2)
            
            if pair_info:
                # Check if this pair is relevant for the drug
                pair_drugs = pair_info.get("drugs", [])
                if not pair_drugs or drug_name.lower() in [d.lower() for d in pair_drugs]:
                    weight = pair_info["weight"]
                    evidence = pair_info["evidence"]
                    pair_sum += weight
                    
                    from .mapper import extract_gene_from_tag
                    genes = [extract_gene_from_tag(tag1), extract_gene_from_tag(tag2)]
                    
                    rationales.append({
                        "type": "epistasis_pair",
                        "pair": [tag1, tag2],
                        "genes": genes,
                        "evidence": evidence
                    })
    
    # Pathway burden: multiple genes in pathway affected
    affected_genes = [gene for gene, gene_tags in gene_to_tags.items() if any(
        tag in single_tags_config and "loss" in tag.lower() or "reduced" in tag.lower()
        for tag in gene_tags
    )]
    
    if len(affected_genes) >= 2:
        pathway_burden = GUIDELINES.get("pathway_burden", {}).get("weight", 0.20)
        rationales.append({
            "type": "pathway_burden",
            "genes": affected_genes,
            "evidence": GUIDELINES.get("pathway_burden", {}).get("evidence", [])
        })
    
    # Compute final score
    score = min(1.0, max(0.0, base_score + tag_sum + pair_sum + pathway_burden))
    
    # Determine label
    if score < 0.33:
        label = "low"
    elif score < 0.66:
        label = "moderate"
    else:
        label = "high"
    
    return score, label, rationales

