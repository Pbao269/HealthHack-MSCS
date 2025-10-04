"""Tests for PDF parser."""
import pytest
from app.parsers.pdf_parser import CAMELOT_AVAILABLE, PDFPLUMBER_AVAILABLE


def test_camelot_available():
    """Check if camelot is available."""
    # This is just a sanity check
    assert isinstance(CAMELOT_AVAILABLE, bool)


def test_pdfplumber_available():
    """Check if pdfplumber is available."""
    # This is just a sanity check
    assert isinstance(PDFPLUMBER_AVAILABLE, bool)


# Note: Full PDF parsing tests would require sample PDF files
# For MVP, we'll test with integration tests instead

