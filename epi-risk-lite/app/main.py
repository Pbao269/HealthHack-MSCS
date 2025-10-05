"""FastAPI application for Epi-Risk Lite."""
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging

from .config import settings
from .schemas import (
    ScoreRequest, ScoreResponse, HealthResponse, VersionResponse,
    Rationale, Alternative, ValidatedAlternatives
)
from .engine.scorer import RiskScorer
from .parsers.csv_parser import parse_csv
from .parsers.pdf_parser import parse_pdf

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)

# Add CORS middleware (open for hackathon - any domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scorer
scorer = RiskScorer(model_dir=settings.model_dir)


@app.get("/")
async def root():
    """Root endpoint with API information and links."""
    return {
        "message": "Epi-Risk Lite API",
        "description": "Pharmacogenomic risk assessment API for medication safety",
        "version": settings.api_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/healthz",
        "version_info": "/version",
        "endpoints": {
            "score_file": "POST /v1/score-file",
            "score_variants": "POST /v1/score", 
            "train_model": "POST /v1/train-file",
            "health_check": "GET /healthz",
            "version": "GET /version"
        }
    }


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        model_available=scorer.model is not None
    )


@app.get("/version", response_model=VersionResponse)
async def get_version():
    """Get version information."""
    return VersionResponse(
        api_version=settings.api_version,
        model_version=scorer.model_version,
        knowledge_version="rules-20250104"
    )


@app.post("/v1/score-file", response_model=ScoreResponse)
async def score_file(
    file: UploadFile = File(..., description="Patient genotype file (CSV or PDF)"),
    medication_name: Optional[str] = Form(None, description="Medication name"),
    rxnorm: Optional[str] = Form(None, description="RxNorm code"),
    context: Optional[str] = Form(None, description="Patient context as JSON string")
):
    """
    Score risk from uploaded genotype file.
    
    Accepts CSV or PDF files with genetic variant data.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Determine file type
        filename = file.filename or ""
        content_type = file.content_type or ""
        
        # Parse file
        variants = []
        if filename.lower().endswith(".csv") or "csv" in content_type.lower():
            logger.info(f"Parsing CSV file: {filename}")
            variants = parse_csv(content, filename)
        elif filename.lower().endswith(".pdf") or "pdf" in content_type.lower():
            logger.info(f"Parsing PDF file: {filename}")
            variants = parse_pdf(content, filename)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Expected CSV or PDF, got: {filename}"
            )
        
        if not variants:
            raise HTTPException(
                status_code=400,
                detail="No variants could be extracted from file. Please check file format."
            )
        
        logger.info(f"Extracted {len(variants)} variants from file")
        
        # Parse context if provided
        context_dict = None
        if context:
            try:
                context_dict = json.loads(context)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Context must be valid JSON string"
                )
        
        # Score
        result = scorer.score(
            variants=variants,
            medication_name=medication_name,
            rxnorm=rxnorm,
            context=context_dict
        )
        
        # Convert to response model
        return _format_score_response(result)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/v1/score", response_model=ScoreResponse)
async def score_variants(request: ScoreRequest):
    """
    Score risk from normalized variant data.
    
    Accepts already-parsed genetic variants in JSON format.
    """
    try:
        # Convert Pydantic models to dicts
        variants = [v.model_dump(exclude_none=True) for v in request.variants]
        
        if not variants:
            raise HTTPException(
                status_code=400,
                detail="No variants provided"
            )
        
        # Score
        result = scorer.score(
            variants=variants,
            medication_name=request.medication_name,
            rxnorm=request.rxnorm,
            context=request.context
        )
        
        # Convert to response model
        return _format_score_response(result)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error scoring variants: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/v1/train-file")
async def train_model(
    file: UploadFile = File(..., description="Training data (CSV or Parquet)")
):
    """
    Train XGBoost model from labeled data.
    
    Expected columns: patient_id, rxnorm, drug_name, variants_json, y
    """
    try:
        from .train.pipeline import train_xgboost_model
        
        content = await file.read()
        
        # Determine file type
        filename = file.filename or ""
        
        if filename.lower().endswith(".parquet"):
            import pandas as pd
            import io
            df = pd.read_parquet(io.BytesIO(content))
        elif filename.lower().endswith(".csv"):
            import pandas as pd
            import io
            df = pd.read_csv(io.BytesIO(content))
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Expected CSV or Parquet."
            )
        
        # Train model
        model_dir = train_xgboost_model(df, settings.model_dir)
        
        # Reload scorer with new model
        global scorer
        scorer = RiskScorer(model_dir=settings.model_dir)
        
        return {
            "status": "success",
            "message": f"Model trained and saved to {model_dir}",
            "model_version": scorer.model_version
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error training model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")


def _format_score_response(result: dict) -> ScoreResponse:
    """Convert scorer result dict to ScoreResponse."""
    rationales = [
        Rationale(**r) for r in result.get("rationales", [])
    ]
    
    # Handle the new validated alternatives structure
    suggested_alternatives_data = result.get("suggested_alternatives", {})
    
    # Convert alternatives to Pydantic models
    def convert_alternatives(alt_list):
        return [Alternative(**alt) for alt in alt_list]
    
    validated_alternatives = ValidatedAlternatives(
        safe_alternatives=convert_alternatives(suggested_alternatives_data.get("safe_alternatives", [])),
        caution_required=convert_alternatives(suggested_alternatives_data.get("caution_required", [])),
        not_recommended=convert_alternatives(suggested_alternatives_data.get("not_recommended", [])),
        no_safe_alternatives=suggested_alternatives_data.get("no_safe_alternatives", False)
    )
    
    return ScoreResponse(
        risk_score=result["risk_score"],
        risk_label=result["risk_label"],
        rationales=rationales,
        suggested_alternatives=validated_alternatives,
        trace_id=result["trace_id"],
        model_version=result["model_version"],
        knowledge_version=result["knowledge_version"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

