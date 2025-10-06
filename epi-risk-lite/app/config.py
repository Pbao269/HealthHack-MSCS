"""Configuration management."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Paths
    model_dir: Path = Path("./models")
    data_dir: Path = Path("./data")
    
    # Logging
    log_level: str = "info"
    
    # API
    api_title: str = "Epi-Risk Lite API"
    api_version: str = "0.1.0"
    api_description: str = "Clinical decision support for epistatic risk scoring"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from environment


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.model_dir.mkdir(parents=True, exist_ok=True)
settings.data_dir.mkdir(parents=True, exist_ok=True)