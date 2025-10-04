"""PDF parser for genetic variant files using camelot and pdfplumber."""
import io
from typing import List, Dict, Optional
import pandas as pd

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

from .normalize import (
    infer_column_mapping,
    normalize_variant_row,
    clean_table_text
)


def parse_pdf(file_content: bytes, filename: str = "") -> List[Dict[str, str]]:
    """
    Parse PDF file into normalized variant list.
    
    Tries multiple extraction methods:
    1. Camelot with lattice flavor (structured tables)
    2. Camelot with stream flavor (less structured)
    3. pdfplumber (fallback)
    
    Args:
        file_content: Raw PDF file bytes
        filename: Original filename (optional)
    
    Returns:
        List of variant dicts
    """
    # Save to temporary file for camelot (it requires file path)
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        # Try camelot first
        if CAMELOT_AVAILABLE:
            variants = _parse_with_camelot(tmp_path, "lattice")
            if variants:
                return variants
            
            variants = _parse_with_camelot(tmp_path, "stream")
            if variants:
                return variants
        
        # Fallback to pdfplumber
        if PDFPLUMBER_AVAILABLE:
            variants = _parse_with_pdfplumber(file_content)
            if variants:
                return variants
        
        raise ValueError(
            "Could not extract variant tables from PDF. "
            "Ensure the PDF contains structured tables with variant data."
        )
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _parse_with_camelot(pdf_path: str, flavor: str = "lattice") -> List[Dict[str, str]]:
    """Parse PDF using camelot library."""
    if not CAMELOT_AVAILABLE:
        return []
    
    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor=flavor)
        
        if not tables:
            return []
        
        # Try to find the table with variant data
        for table in tables:
            df = table.df
            
            if df.empty or len(df) < 2:
                continue
            
            # Use first row as headers
            df.columns = df.iloc[0]
            df = df[1:]
            
            # Clean column names
            df.columns = [clean_table_text(str(c)) for c in df.columns]
            
            # Check if this looks like a variant table
            column_mapping = infer_column_mapping(df.columns.tolist())
            
            if column_mapping:
                variants = []
                for _, row in df.iterrows():
                    row_dict = {k: clean_table_text(str(v)) for k, v in row.to_dict().items()}
                    variant = normalize_variant_row(row_dict, column_mapping)
                    if variant:
                        variants.append(variant)
                
                if variants:
                    return variants
        
    except Exception as e:
        # Camelot can fail in various ways; log but continue to next method
        pass
    
    return []


def _parse_with_pdfplumber(file_content: bytes) -> List[Dict[str, str]]:
    """Parse PDF using pdfplumber library."""
    if not PDFPLUMBER_AVAILABLE:
        return []
    
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # First row as headers
                    headers = [clean_table_text(str(h)) for h in table[0]]
                    rows = table[1:]
                    
                    # Create dataframe
                    df = pd.DataFrame(rows, columns=headers)
                    
                    # Clean all cells
                    for col in df.columns:
                        df[col] = df[col].apply(lambda x: clean_table_text(str(x)) if x else "")
                    
                    # Check if this is a variant table
                    column_mapping = infer_column_mapping(df.columns.tolist())
                    
                    if column_mapping:
                        variants = []
                        for _, row in df.iterrows():
                            variant = normalize_variant_row(row.to_dict(), column_mapping)
                            if variant:
                                variants.append(variant)
                        
                        if variants:
                            return variants
    except Exception as e:
        pass
    
    return []

