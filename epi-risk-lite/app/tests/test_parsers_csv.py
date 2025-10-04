"""Tests for CSV parser."""
import pytest
from app.parsers.csv_parser import parse_csv


def test_parse_csv_rsid_genotype():
    """Test parsing CSV with rsid and genotype columns."""
    csv_content = b"""rsid,genotype
rs3892097,AA
rs1065852,GG
rs776746,TT
"""
    
    variants = parse_csv(csv_content)
    
    assert len(variants) == 3
    assert variants[0] == {"rsid": "rs3892097", "genotype": "AA"}
    assert variants[1] == {"rsid": "rs1065852", "genotype": "GG"}
    assert variants[2] == {"rsid": "rs776746", "genotype": "TT"}


def test_parse_csv_with_slash_delimiter():
    """Test parsing genotypes with slash delimiter."""
    csv_content = b"""rsid,genotype
rs3892097,A/A
rs1065852,G/G
rs776746,T/C
"""
    
    variants = parse_csv(csv_content)
    
    assert len(variants) == 3
    assert variants[0]["genotype"] == "AA"
    assert variants[1]["genotype"] == "GG"
    assert variants[2]["genotype"] == "CT"  # Sorted


def test_parse_csv_star_alleles():
    """Test parsing star alleles."""
    csv_content = b"""gene,star
CYP2D6,*4/*4
CYP2C19,*2/*1
"""
    
    variants = parse_csv(csv_content)
    
    assert len(variants) == 2
    assert variants[0]["gene"] == "CYP2D6"
    assert "*4" in variants[0]["star"]
    assert variants[1]["gene"] == "CYP2C19"


def test_parse_csv_with_allele_columns():
    """Test parsing with separate allele columns."""
    csv_content = b"""rsid,allele1,allele2
rs3892097,A,A
rs776746,T,C
"""
    
    variants = parse_csv(csv_content)
    
    assert len(variants) == 2
    assert variants[0]["genotype"] == "AA"
    assert variants[1]["genotype"] == "CT"


def test_parse_csv_case_insensitive_headers():
    """Test that headers are case-insensitive."""
    csv_content = b"""RSID,GENOTYPE
rs3892097,AA
"""
    
    variants = parse_csv(csv_content)
    
    assert len(variants) == 1
    assert variants[0]["rsid"] == "rs3892097"

