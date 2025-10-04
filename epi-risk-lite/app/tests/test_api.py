"""Tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/healthz")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_get_version():
    """Test version endpoint."""
    response = client.get("/version")
    
    assert response.status_code == 200
    data = response.json()
    assert "api_version" in data
    assert "model_version" in data
    assert "knowledge_version" in data


def test_score_variants():
    """Test scoring with variant data."""
    request_data = {
        "variants": [
            {"rsid": "rs3892097", "genotype": "AA"},
            {"rsid": "rs776746", "genotype": "TT"}
        ],
        "medication_name": "codeine"
    }
    
    response = client.post("/v1/score", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "risk_score" in data
    assert "risk_label" in data
    assert "rationales" in data
    assert "trace_id" in data
    assert 0.0 <= data["risk_score"] <= 1.0
    assert data["risk_label"] in ["low", "moderate", "high"]


def test_score_variants_invalid_drug():
    """Test scoring with unknown medication."""
    request_data = {
        "variants": [
            {"rsid": "rs3892097", "genotype": "AA"}
        ],
        "medication_name": "unknown_drug_xyz"
    }
    
    response = client.post("/v1/score", json=request_data)
    
    assert response.status_code == 400


def test_score_file_csv():
    """Test scoring with CSV file upload."""
    csv_content = b"""rsid,genotype
rs3892097,AA
rs1065852,GG
"""
    
    response = client.post(
        "/v1/score-file",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"medication_name": "codeine"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "risk_score" in data
    assert "risk_label" in data


def test_score_variants_with_star_alleles():
    """Test scoring with star alleles."""
    request_data = {
        "variants": [
            {"gene": "CYP2D6", "star": "*4/*4"}
        ],
        "medication_name": "codeine"
    }
    
    response = client.post("/v1/score", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # CYP2D6*4 is a loss-of-function allele
    assert data["risk_score"] > 0.3
    assert len(data["suggested_alternatives"]) > 0


def test_score_with_context():
    """Test scoring with patient context."""
    request_data = {
        "variants": [
            {"rsid": "rs3892097", "genotype": "AA"}
        ],
        "medication_name": "codeine",
        "context": {
            "age": 45,
            "sex": "M",
            "ancestry": "EUR"
        }
    }
    
    response = client.post("/v1/score", json=request_data)
    
    assert response.status_code == 200

