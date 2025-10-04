"""Unified scoring interface (rules vs ML)."""
from typing import List, Dict, Set, Optional
from pathlib import Path
import uuid

from .mapper import map_variants_to_tags, extract_gene_from_tag
from .pathways import get_drug_info, filter_tags_by_pathway, get_alternatives
from .rules import score_deterministic
from .model_io import load_latest_model


class RiskScorer:
    """Main risk scoring class."""
    
    def __init__(self, model_dir: Optional[Path] = None):
        """
        Initialize scorer.
        
        Args:
            model_dir: Directory containing trained models (optional)
        """
        self.model_dir = model_dir
        self.model = None
        self.model_version = "rules-0.1.0"
        
        # Try to load ML model if available
        if model_dir:
            try:
                self.model, metadata = load_latest_model(model_dir)
                if self.model:
                    self.model_version = metadata.get("version", "xgb-unknown")
            except Exception:
                pass
    
    def score(
        self,
        variants: List[Dict[str, str]],
        medication_name: Optional[str] = None,
        rxnorm: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Score risk for given variants and medication.
        
        Args:
            variants: List of variant dicts
            medication_name: Drug name
            rxnorm: RxNorm code
            context: Optional patient context (age, sex, ancestry)
        
        Returns:
            Score response dict with keys:
            - risk_score: float in [0, 1]
            - risk_label: "low" | "moderate" | "high"
            - rationales: List of explanation dicts
            - suggested_alternatives: List of alternative medications
            - trace_id: UUID for request tracking
            - model_version: Model identifier
            - knowledge_version: Knowledge base version
        """
        trace_id = str(uuid.uuid4())
        
        # Get drug info
        drug_info = get_drug_info(medication_name, rxnorm)
        if not drug_info:
            raise ValueError(
                f"Unknown medication: {medication_name or rxnorm}. "
                f"Please provide a valid medication name or RxNorm code."
            )
        
        drug_name = drug_info["name"]
        pathway_genes = drug_info["genes"]
        
        # Map variants to tags
        all_tags, gene_to_tags = map_variants_to_tags(variants)
        
        # Filter to pathway-relevant tags
        pathway_tags = filter_tags_by_pathway(list(all_tags), pathway_genes)
        pathway_tags_set = set(pathway_tags)
        
        # Filter gene_to_tags to pathway genes
        pathway_gene_to_tags = {
            gene: tags for gene, tags in gene_to_tags.items()
            if gene in pathway_genes
        }
        
        # Score with rules or ML
        if self.model is not None:
            score, label, rationales = self._score_with_ml(
                pathway_tags_set, drug_name, pathway_genes
            )
        else:
            score, label, rationales = score_deterministic(
                pathway_tags_set, pathway_gene_to_tags, drug_name
            )
        
        # Get alternatives
        alternatives = get_alternatives(drug_name)
        
        return {
            "risk_score": round(score, 3),
            "risk_label": label,
            "rationales": rationales,
            "suggested_alternatives": alternatives,
            "trace_id": trace_id,
            "model_version": self.model_version,
            "knowledge_version": "rules-20250104"
        }
    
    def _score_with_ml(
        self,
        tags: Set[str],
        drug_name: str,
        pathway_genes: List[str]
    ) -> tuple:
        """Score using ML model."""
        from .features import build_feature_vector
        
        # Build features
        X = build_feature_vector(tags, drug_name, pathway_genes)
        X = X.reshape(1, -1)
        
        # Predict
        score = float(self.model.predict_proba(X)[0, 1])
        
        # Determine label
        if score < 0.33:
            label = "low"
        elif score < 0.66:
            label = "moderate"
        else:
            label = "high"
        
        # Generate rationales (still use rules-based explanation)
        from .rules import score_deterministic
        _, _, rationales = score_deterministic(tags, {}, drug_name)
        
        return score, label, rationales

