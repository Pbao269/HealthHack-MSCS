"""CSV parser for genetic variant files."""
import pandas as pd
from typing import List, Dict, Optional
import io

from .normalize import (
    infer_column_mapping,
    normalize_variant_row,
    parse_star_allele
)


def parse_csv(file_content: bytes, filename: str = "") -> List[Dict[str, str]]:
    """
    Parse CSV file into normalized variant list.
    
    Args:
        file_content: Raw CSV file bytes
        filename: Original filename (optional, for debugging)
    
    Returns:
        List of variant dicts with keys: rsid, genotype, gene, star
    """
    # Try different encodings
    for encoding in ["utf-8", "latin-1", "iso-8859-1"]:
        try:
            df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Could not decode CSV file with common encodings")
    
    if df.empty:
        return []
    
    # Infer column mappings
    column_mapping = infer_column_mapping(df.columns.tolist())
    
    if not column_mapping:
        raise ValueError(
            f"Could not identify variant columns. Found columns: {list(df.columns)}"
        )
    
    variants = []
    
    for idx, row in df.iterrows():
        # Skip rows with all NaN
        if row.isna().all():
            continue
        
        variant = normalize_variant_row(row.to_dict(), column_mapping)
        
        if variant:
            variants.append(variant)
    
    return variants


def parse_csv_with_star_alleles(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Helper to parse CSV that primarily contains star alleles.
    
    Expected format:
        gene, star OR gene, diplotype
    """
    variants = []
    
    # Look for gene column
    gene_col = None
    star_col = None
    
    for col in df.columns:
        col_lower = col.lower().strip()
        if col_lower in ["gene", "gene_symbol"]:
            gene_col = col
        if col_lower in ["star", "star_allele", "diplotype", "haplotype", "alleles"]:
            star_col = col
    
    if not gene_col or not star_col:
        return []
    
    for _, row in df.iterrows():
        gene = row.get(gene_col, "")
        star = row.get(star_col, "")
        
        if not gene or not star:
            continue
        
        gene_str = str(gene).upper().strip()
        star_str = str(star).strip()
        
        # Try to parse as star allele
        parsed = parse_star_allele(f"{gene_str}{star_str}")
        
        if parsed:
            variants.append({
                "gene": parsed["gene"],
                "star": parsed["star"]
            })
        elif "*" in star_str:
            # Already in good format
            variants.append({
                "gene": gene_str,
                "star": star_str
            })
    
    return variants

