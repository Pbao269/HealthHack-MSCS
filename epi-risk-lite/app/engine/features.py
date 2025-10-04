"""Feature engineering for ML models."""
import numpy as np
from typing import List, Dict, Set
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "guidelines.json") as f:
    GUIDELINES = json.load(f)

with open(DATA_DIR / "drug_gene_map.json") as f:
    DRUG_GENE_MAP = json.load(f)


def build_feature_vector(
    tags: Set[str],
    drug_name: str,
    pathway_genes: List[str]
) -> np.ndarray:
    """
    Build feature vector for ML model.
    
    Features:
    - One-hot encoding of tags
    - Pairwise interactions (within pathway)
    - Drug one-hot encoding
    
    Args:
        tags: Set of functional tags
        drug_name: Medication name
        pathway_genes: Genes in the drug's pathway
    
    Returns:
        Feature vector as numpy array
    """
    features = []
    
    # Get all possible tags from guidelines
    all_tags = set(GUIDELINES.get("single_tags", {}).keys())
    
    # Tag one-hot
    for tag in sorted(all_tags):
        features.append(1.0 if tag in tags else 0.0)
    
    # Pairwise interactions (only within pathway)
    from .mapper import extract_gene_from_tag
    
    pathway_tags = [t for t in tags if extract_gene_from_tag(t) in pathway_genes]
    pathway_tags_sorted = sorted(pathway_tags)
    
    # Generate all possible pairs
    all_possible_pairs = []
    for i, tag1 in enumerate(sorted(all_tags)):
        for tag2 in sorted(all_tags)[i+1:]:
            all_possible_pairs.append((tag1, tag2))
    
    for tag1, tag2 in all_possible_pairs:
        # Check if both tags present and in pathway
        if tag1 in pathway_tags_sorted and tag2 in pathway_tags_sorted:
            features.append(1.0)
        else:
            features.append(0.0)
    
    # Drug one-hot
    all_drugs = set()
    for info in DRUG_GENE_MAP.values():
        all_drugs.add(info["name"])
    
    for drug in sorted(all_drugs):
        features.append(1.0 if drug.lower() == drug_name.lower() else 0.0)
    
    return np.array(features, dtype=np.float32)


def get_feature_names() -> List[str]:
    """Get feature names for interpretability."""
    feature_names = []
    
    # Tag features
    all_tags = sorted(GUIDELINES.get("single_tags", {}).keys())
    feature_names.extend([f"tag_{tag}" for tag in all_tags])
    
    # Pair features
    for i, tag1 in enumerate(all_tags):
        for tag2 in all_tags[i+1:]:
            feature_names.append(f"pair_{tag1}_{tag2}")
    
    # Drug features
    all_drugs = set()
    for info in DRUG_GENE_MAP.values():
        all_drugs.add(info["name"])
    
    feature_names.extend([f"drug_{drug}" for drug in sorted(all_drugs)])
    
    return feature_names

