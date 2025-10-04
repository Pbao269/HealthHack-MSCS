"""Model I/O utilities for loading and saving trained models."""
import joblib
import json
from pathlib import Path
from typing import Optional, Tuple, Any, Dict
from datetime import datetime


def save_model(
    model: Any,
    metadata: Dict,
    output_dir: Path,
    timestamp: Optional[str] = None
) -> Path:
    """
    Save trained model and metadata.
    
    Args:
        model: Trained model object
        metadata: Model metadata dict
        output_dir: Base output directory
        timestamp: Optional timestamp string (defaults to now)
    
    Returns:
        Path to saved model directory
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    model_dir = output_dir / timestamp
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    joblib.dump(model, model_dir / "model.joblib")
    
    # Save metadata
    with open(model_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Update latest symlink
    latest_link = output_dir / "latest"
    if latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(timestamp, target_is_directory=True)
    
    return model_dir


def load_model(model_dir: Path) -> Tuple[Any, Dict]:
    """
    Load model and metadata from directory.
    
    Args:
        model_dir: Path to model directory
    
    Returns:
        (model, metadata)
    """
    model_path = model_dir / "model.joblib"
    metadata_path = model_dir / "metadata.json"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    model = joblib.load(model_path)
    
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)
    
    return model, metadata


def load_latest_model(base_dir: Path) -> Tuple[Optional[Any], Dict]:
    """
    Load the latest trained model.
    
    Args:
        base_dir: Base models directory
    
    Returns:
        (model, metadata) or (None, {}) if no model exists
    """
    latest_link = base_dir / "latest"
    
    if not latest_link.exists():
        return None, {}
    
    try:
        return load_model(latest_link)
    except Exception:
        return None, {}

