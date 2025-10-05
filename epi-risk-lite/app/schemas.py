"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Variant(BaseModel):
    """A genetic variant."""
    rsid: Optional[str] = Field(None, description="rsID (e.g., rs3892097)")
    genotype: Optional[str] = Field(None, description="Genotype (e.g., AA)")
    gene: Optional[str] = Field(None, description="Gene symbol (e.g., CYP2D6)")
    star: Optional[str] = Field(None, description="Star allele (e.g., *4/*4)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"rsid": "rs3892097", "genotype": "AA"},
                {"gene": "CYP2D6", "star": "*4/*4"}
            ]
        }
    }


class ScoreRequest(BaseModel):
    """Request body for /v1/score endpoint."""
    variants: List[Variant] = Field(..., description="List of genetic variants")
    medication_name: Optional[str] = Field(None, description="Medication name (e.g., codeine)")
    rxnorm: Optional[str] = Field(None, description="RxNorm code")
    context: Optional[Dict[str, Any]] = Field(None, description="Patient context (age, sex, ancestry)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "variants": [
                    {"rsid": "rs3892097", "genotype": "AA"},
                    {"gene": "CYP2D6", "star": "*4/*4"}
                ],
                "medication_name": "codeine",
                "context": {"age": 45, "sex": "M", "ancestry": "EUR"}
            }]
        }
    }


class Rationale(BaseModel):
    """Explanation for risk assessment."""
    type: str = Field(..., description="Type: epistasis_pair | single_tag | pathway_burden")
    pair: Optional[List[str]] = Field(None, description="Tag pair for epistasis")
    tag: Optional[str] = Field(None, description="Single tag")
    pathway: Optional[str] = Field(None, description="Pathway name")
    genes: Optional[List[str]] = Field(None, description="Affected genes")
    evidence: List[str] = Field(default_factory=list, description="Clinical evidence")


class Alternative(BaseModel):
    """Alternative medication suggestion."""
    rxnorm: str = Field(..., description="RxNorm code")
    name: str = Field(..., description="Medication name")
    note: str = Field(..., description="Reason for alternative")
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Risk score for this alternative")
    risk_label: Optional[str] = Field(None, description="Risk category for this alternative")
    safety_status: Optional[str] = Field(None, description="Safety status: SAFE | CAUTION_REQUIRED | NOT_RECOMMENDED")
    safety_warnings: List[str] = Field(default_factory=list, description="Safety warnings for this alternative")
    pathway_genes: Optional[List[str]] = Field(None, description="Genes involved in this alternative's metabolism")


class ValidatedAlternatives(BaseModel):
    """Validated alternatives categorized by safety."""
    safe_alternatives: List[Alternative] = Field(default_factory=list, description="Safe alternatives for this patient")
    caution_required: List[Alternative] = Field(default_factory=list, description="Alternatives requiring caution")
    not_recommended: List[Alternative] = Field(default_factory=list, description="Alternatives not recommended for this patient")
    no_safe_alternatives: bool = Field(False, description="Whether no safe alternatives are available")


class ScoreResponse(BaseModel):
    """Response from score endpoints."""
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score [0-1]")
    risk_label: str = Field(..., description="Risk category: low | moderate | high")
    rationales: List[Rationale] = Field(default_factory=list, description="Explanations")
    suggested_alternatives: ValidatedAlternatives = Field(..., description="Validated alternative medications")
    trace_id: str = Field(..., description="Request trace ID")
    model_version: str = Field(..., description="Model version")
    knowledge_version: str = Field(..., description="Knowledge base version")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "risk_score": 0.75,
                "risk_label": "high",
                "rationales": [
                    {
                        "type": "epistasis_pair",
                        "pair": ["CYP2D6_loss", "CYP3A4_rs776746_TT"],
                        "genes": ["CYP2D6", "CYP3A4"],
                        "evidence": ["Combined loss impairs codeine activation significantly"]
                    }
                ],
                "suggested_alternatives": {
                    "safe_alternatives": [
                        {
                            "rxnorm": "7052",
                            "name": "morphine",
                            "note": "does not require CYP2D6 activation",
                            "risk_score": 0.15,
                            "risk_label": "low",
                            "safety_status": "SAFE",
                            "safety_warnings": [],
                            "pathway_genes": ["UGT2B7"]
                        }
                    ],
                    "caution_required": [
                        {
                            "rxnorm": "7804",
                            "name": "oxycodone",
                            "note": "metabolized primarily by CYP3A4",
                            "risk_score": 0.45,
                            "risk_label": "moderate",
                            "safety_status": "CAUTION_REQUIRED",
                            "safety_warnings": ["Patient has CYP3A4_reduced - monitor for drug accumulation"],
                            "pathway_genes": ["CYP3A4", "CYP2D6"]
                        }
                    ],
                    "not_recommended": [],
                    "no_safe_alternatives": False
                },
                "trace_id": "uuid-here",
                "model_version": "rules-0.1.0",
                "knowledge_version": "rules-20250104"
            }]
        }
    }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    model_available: bool = Field(..., description="Whether ML model is loaded")


class VersionResponse(BaseModel):
    """Version information response."""
    api_version: str = Field(..., description="API version")
    model_version: str = Field(..., description="Current model version")
    knowledge_version: str = Field(..., description="Knowledge base version")

