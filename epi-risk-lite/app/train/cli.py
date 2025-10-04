"""CLI for training models."""
import argparse
import pandas as pd
from pathlib import Path

from .pipeline import train_xgboost_model


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Train XGBoost model for Epi-Risk")
    parser.add_argument(
        "--in",
        dest="input_file",
        required=True,
        help="Input training data (CSV or Parquet)"
    )
    parser.add_argument(
        "--out",
        dest="output_dir",
        default="./models",
        help="Output directory for models (default: ./models)"
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Test set fraction (default: 0.2)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)"
    )
    
    args = parser.parse_args()
    
    # Load data
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    if input_path.suffix == ".parquet":
        df = pd.read_parquet(input_path)
    elif input_path.suffix == ".csv":
        df = pd.read_csv(input_path)
    else:
        print(f"Error: Unsupported file type: {input_path.suffix}")
        return 1
    
    print(f"Loaded {len(df)} training samples from {input_path}")
    
    # Train model
    output_dir = Path(args.output_dir)
    model_dir = train_xgboost_model(
        df=df,
        output_dir=output_dir,
        test_size=args.test_size,
        random_state=args.seed
    )
    
    print(f"\nTraining complete! Model saved to: {model_dir}")
    return 0


if __name__ == "__main__":
    exit(main())

