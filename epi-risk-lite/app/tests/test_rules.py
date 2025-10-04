"""Tests for rule-based scoring."""
import pytest
from app.engine.rules import score_deterministic


def test_score_deterministic_low_risk():
    """Test scoring with low risk tags."""
    tags = {"CYP2D6_normal"}
    gene_to_tags = {"CYP2D6": ["CYP2D6_normal"]}
    
    score, label, rationales = score_deterministic(tags, gene_to_tags, "codeine")
    
    assert 0.0 <= score <= 1.0
    assert label == "low"


def test_score_deterministic_high_risk_single_tag():
    """Test scoring with high-risk single tag."""
    tags = {"CYP2D6_loss"}
    gene_to_tags = {"CYP2D6": ["CYP2D6_loss"]}
    
    score, label, rationales = score_deterministic(tags, gene_to_tags, "codeine")
    
    assert score > 0.3  # Base + tag weight
    assert label in ["moderate", "high"]
    assert any(r["type"] == "single_tag" for r in rationales)


def test_score_deterministic_epistasis():
    """Test scoring with epistatic interaction."""
    tags = {"CYP2D6_loss", "CYP3A4_rs776746_TT"}
    gene_to_tags = {
        "CYP2D6": ["CYP2D6_loss"],
        "CYP3A4": ["CYP3A4_rs776746_TT"]
    }
    
    score, label, rationales = score_deterministic(tags, gene_to_tags, "codeine")
    
    assert score > 0.5  # Should be high due to epistasis
    assert label == "high"
    assert any(r["type"] == "epistasis_pair" for r in rationales)


def test_score_deterministic_pathway_burden():
    """Test pathway burden calculation."""
    tags = {"CYP2C19_loss", "CYP3A4_reduced", "ABCB1_reduced_function"}
    gene_to_tags = {
        "CYP2C19": ["CYP2C19_loss"],
        "CYP3A4": ["CYP3A4_reduced"],
        "ABCB1": ["ABCB1_reduced_function"]
    }
    
    score, label, rationales = score_deterministic(tags, gene_to_tags, "clopidogrel")
    
    # Should have pathway burden bonus
    assert any(r["type"] == "pathway_burden" for r in rationales)

