"""Normalization utilities for genetic variant data."""
import re
from typing import Dict, List, Optional, Any


def normalize_column_name(name: str) -> str:
    """Normalize column names to lowercase and strip whitespace."""
    return str(name).lower().strip().replace(" ", "_")


def infer_column_mapping(columns: List[str]) -> Dict[str, str]:
    """
    Infer semantic meaning of columns from their names.
    
    Returns dict mapping semantic name to actual column name.
    """
    normalized = {normalize_column_name(c): c for c in columns}
    mapping = {}
    
    # rsID / SNP
    for key in ["rsid", "snp", "rs_id", "variant_id"]:
        if key in normalized:
            mapping["rsid"] = normalized[key]
            break
    
    # Genotype / Call
    for key in ["genotype", "call", "gt", "alleles", "result"]:
        if key in normalized:
            mapping["genotype"] = normalized[key]
            break
    
    # Gene
    for key in ["gene", "gene_symbol", "gene_name"]:
        if key in normalized:
            mapping["gene"] = normalized[key]
            break
    
    # Variant name
    for key in ["variant", "variant_name", "hgvs"]:
        if key in normalized:
            mapping["variant"] = normalized[key]
            break
    
    # Star allele
    for key in ["star", "star_allele", "diplotype", "haplotype"]:
        if key in normalized:
            mapping["star"] = normalized[key]
            break
    
    # Allele 1
    for key in ["allele1", "allele_1", "a1"]:
        if key in normalized:
            mapping["allele1"] = normalized[key]
            break
    
    # Allele 2
    for key in ["allele2", "allele_2", "a2"]:
        if key in normalized:
            mapping["allele2"] = normalized[key]
            break
    
    # Zygosity
    for key in ["zyg", "zygosity", "het_hom"]:
        if key in normalized:
            mapping["zygosity"] = normalized[key]
            break
    
    return mapping


def normalize_genotype(genotype: str) -> str:
    """
    Normalize genotype string.
    
    - Remove delimiters (/, |, ,)
    - Uppercase
    - Sort alleles alphabetically
    
    Examples:
        A/G -> AG
        g/a -> AG
        T|C -> CT
    """
    if not genotype or str(genotype).lower() in ["nan", "none", ""]:
        return ""
    
    # Remove common delimiters
    clean = str(genotype).replace("/", "").replace("|", "").replace(",", "").replace(" ", "")
    clean = clean.upper().strip()
    
    # Sort alleles alphabetically for consistency
    if len(clean) == 2 and clean.isalpha():
        return "".join(sorted(clean))
    
    return clean


def combine_alleles(allele1: str, allele2: str, zygosity: Optional[str] = None) -> str:
    """
    Combine two alleles into a normalized genotype.
    
    Args:
        allele1: First allele
        allele2: Second allele
        zygosity: Optional zygosity hint (hom/het)
    """
    a1 = str(allele1).upper().strip() if allele1 else ""
    a2 = str(allele2).upper().strip() if allele2 else ""
    
    if not a1 or not a2:
        return ""
    
    # If zygosity indicates homozygous and alleles differ, use first allele twice
    if zygosity and "hom" in str(zygosity).lower() and a1 != a2:
        a2 = a1
    
    # Sort for consistency
    return "".join(sorted([a1, a2]))


def parse_star_allele(text: str) -> Optional[Dict[str, str]]:
    """
    Parse star allele notation.
    
    Examples:
        CYP2D6*4/*4 -> {gene: "CYP2D6", allele1: "*4", allele2: "*4"}
        CYP2C19*2/*1 -> {gene: "CYP2C19", allele1: "*1", allele2: "*2"}
    """
    if not text:
        return None
    
    # Pattern: GENE*N/*M
    pattern = r"([A-Z0-9]+)\*(\d+[A-Z]*)/\*(\d+[A-Z]*)"
    match = re.search(pattern, str(text).upper())
    
    if match:
        gene, a1, a2 = match.groups()
        # Sort alleles for consistency
        alleles = sorted([f"*{a1}", f"*{a2}"])
        return {
            "gene": gene,
            "allele1": alleles[0],
            "allele2": alleles[1],
            "star": f"{alleles[0]}/{alleles[1]}"
        }
    
    return None


def clean_table_text(text: str) -> str:
    """Clean text extracted from tables (remove footnotes, extra whitespace, etc)."""
    if not text:
        return ""
    
    # Remove superscript numbers and footnote markers
    text = re.sub(r"[\u2070-\u209F\u00B0-\u00BE]+", "", text)
    
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def normalize_variant_row(row: Dict[str, Any], column_mapping: Dict[str, str]) -> Optional[Dict[str, str]]:
    """
    Normalize a single row into standard variant format.
    
    Returns:
        Dict with keys: rsid, genotype, gene, star (as applicable)
    """
    result = {}
    
    # Extract mapped values
    rsid = row.get(column_mapping.get("rsid", ""), None) if "rsid" in column_mapping else None
    genotype = row.get(column_mapping.get("genotype", ""), None) if "genotype" in column_mapping else None
    gene = row.get(column_mapping.get("gene", ""), None) if "gene" in column_mapping else None
    star = row.get(column_mapping.get("star", ""), None) if "star" in column_mapping else None
    allele1 = row.get(column_mapping.get("allele1", ""), None) if "allele1" in column_mapping else None
    allele2 = row.get(column_mapping.get("allele2", ""), None) if "allele2" in column_mapping else None
    zygosity = row.get(column_mapping.get("zygosity", ""), None) if "zygosity" in column_mapping else None
    
    # Handle star alleles
    if star:
        parsed = parse_star_allele(str(star))
        if parsed:
            return {
                "gene": parsed["gene"],
                "star": parsed["star"]
            }
    
    # Handle gene + star in separate columns
    if gene and star and "*" in str(star):
        return {
            "gene": str(gene).upper().strip(),
            "star": str(star).strip()
        }
    
    # Handle rsID + genotype
    if rsid and genotype:
        rsid_clean = str(rsid).strip()
        genotype_clean = normalize_genotype(genotype)
        
        if rsid_clean and genotype_clean:
            result["rsid"] = rsid_clean
            result["genotype"] = genotype_clean
            return result
    
    # Handle rsID + alleles
    if rsid and allele1 and allele2:
        rsid_clean = str(rsid).strip()
        genotype_clean = combine_alleles(allele1, allele2, zygosity)
        
        if rsid_clean and genotype_clean:
            result["rsid"] = rsid_clean
            result["genotype"] = genotype_clean
            return result
    
    # Handle genotype in a single column that includes rsID
    if genotype and not rsid:
        # Check if genotype column contains rsID
        genotype_str = str(genotype)
        if "rs" in genotype_str.lower():
            parts = genotype_str.split()
            for part in parts:
                if part.lower().startswith("rs"):
                    rsid = part
                    # Remaining might be genotype
                    genotype = genotype_str.replace(part, "").strip()
                    break
            
            if rsid:
                result["rsid"] = rsid
                result["genotype"] = normalize_genotype(genotype)
                return result if result["genotype"] else None
    
    return None if not result else result

