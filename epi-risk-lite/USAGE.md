# Epi-Risk Lite Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
cd epi-risk-lite
pip install -e .
```

### 2. Start the Server

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --port 8000

# Option 2: Using Docker
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### 3. View API Documentation

Open your browser to:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Usage

### Upload and Score a CSV File

```bash
curl -X POST "http://localhost:8000/v1/score-file" \
  -F "file=@data/sample_genotype.csv" \
  -F "medication_name=codeine"
```

**Response:**
```json
{
  "risk_score": 0.75,
  "risk_label": "high",
  "rationales": [
    {
      "type": "epistasis_pair",
      "pair": ["CYP2D6_loss", "CYP3A4_rs776746_TT"],
      "genes": ["CYP2D6", "CYP3A4"],
      "evidence": [
        "Combined CYP2D6 and CYP3A4 impairment severely reduces codeine activation",
        "PharmGKB Level 1A: Poor metabolizers at high risk for treatment failure"
      ]
    }
  ],
  "suggested_alternatives": [
    {
      "rxnorm": "7052",
      "name": "morphine",
      "note": "does not require CYP2D6 activation"
    }
  ],
  "trace_id": "a1b2c3d4-e5f6-...",
  "model_version": "rules-0.1.0",
  "knowledge_version": "rules-20250104"
}
```

### Score with JSON Variants

```bash
curl -X POST "http://localhost:8000/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "variants": [
      {"rsid": "rs3892097", "genotype": "AA"},
      {"rsid": "rs776746", "genotype": "TT"}
    ],
    "medication_name": "codeine",
    "context": {"age": 45, "sex": "M", "ancestry": "EUR"}
  }'
```

### Score with Star Alleles

```bash
curl -X POST "http://localhost:8000/v1/score-file" \
  -F "file=@data/sample_star_alleles.csv" \
  -F "medication_name=codeine"
```

### Score with RxNorm Code

```bash
curl -X POST "http://localhost:8000/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "variants": [
      {"gene": "CYP2D6", "star": "*4/*4"}
    ],
    "rxnorm": "1049630"
  }'
```

## Supported Medications

The MVP includes curated data for these medications:

1. **Codeine** (rxnorm:1049630)
   - Pathway genes: CYP2D6, CYP3A4, UGT2B7
   - High-risk interactions: CYP2D6 + CYP3A4 loss

2. **Clopidogrel** (rxnorm:32968)
   - Pathway genes: CYP2C19, CYP3A4, ABCB1
   - High-risk interactions: CYP2C19 + CYP3A4 loss

3. **Warfarin** (rxnorm:11289)
   - Pathway genes: CYP2C9, VKORC1, CYP4F2
   - High-risk interactions: CYP2C9 + VKORC1 variants

4. **Simvastatin** (rxnorm:42331)
   - Pathway genes: SLCO1B1, CYP3A4, CYP3A5, ABCB1
   - High-risk interactions: SLCO1B1 + CYP3A4 reduced

5. **Morphine** (rxnorm:7052)
   - Pathway genes: UGT2B7, OPRM1

6. **Metoprolol** (rxnorm:6809)
   - Pathway genes: CYP2D6, ADRB1

7. **Omeprazole** (rxnorm:8123)
   - Pathway genes: CYP2C19, CYP3A4

## Input File Formats

### CSV Format

**Option 1: rsID + genotype**
```csv
rsid,genotype
rs3892097,AA
rs1065852,GG
rs776746,TT
```

**Option 2: rsID + alleles**
```csv
rsid,allele1,allele2
rs3892097,A,A
rs776746,T,C
```

**Option 3: Star alleles**
```csv
gene,star
CYP2D6,*4/*4
CYP2C19,*2/*1
```

### PDF Format

The parser can extract tables from PDF reports. Expected table structure:

| rsID | Genotype |
|------|----------|
| rs3892097 | A/A |
| rs1065852 | G/G |

Or:

| Gene | Star Allele |
|------|-------------|
| CYP2D6 | *4/*4 |
| CYP2C19 | *2/*1 |

## Training a Custom Model

### Prepare Training Data

Create a CSV or Parquet file with these columns:

- `patient_id`: Patient identifier
- `rxnorm`: RxNorm code for medication
- `drug_name`: Medication name
- `variants_json`: JSON string of variant list
- `y`: Binary outcome (0=no adverse event, 1=adverse event)

Example CSV:
```csv
patient_id,rxnorm,drug_name,variants_json,y
P001,1049630,codeine,"[{\"rsid\":\"rs3892097\",\"genotype\":\"AA\"}]",1
P002,1049630,codeine,"[{\"rsid\":\"rs3892097\",\"genotype\":\"GG\"}]",0
```

### Train via CLI

```bash
python -m app.train.cli --in data/train.csv --out models/
```

### Train via API

```bash
curl -X POST "http://localhost:8000/v1/train-file" \
  -F "file=@data/train.csv"
```

After training, the API will automatically use the new model for scoring.

## Testing

### Run Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_api.py -v
```

### Test Coverage

The test suite includes:
- CSV parser tests
- PDF parser availability checks
- Rule-based scoring tests
- API endpoint tests (health, score, score-file)
- Integration tests with sample data

## Architecture

```
┌─────────────┐
│   Upload    │
│  CSV/PDF    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Parse & Extract │
│    Variants      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Normalize      │
│   Variants       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Map to         │
│   Functional     │
│   Tags           │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Filter to      │
│   Drug Pathway   │
│   Genes          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Score:         │
│   - Rules or     │
│   - ML Model     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Generate       │
│   Rationales &   │
│   Alternatives   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Return JSON    │
│   Response       │
└──────────────────┘
```

## Troubleshooting

### Camelot/PDF Issues

If you encounter issues with PDF parsing:

```bash
# macOS
brew install ghostscript

# Ubuntu/Debian
sudo apt-get install ghostscript python3-tk

# Verify installation
python -c "import camelot; print('Camelot OK')"
```

### Unknown Medication Error

If you get "Unknown medication" error:
- Check that the medication name matches one in `app/engine/data/drug_gene_map.json`
- Use exact spelling (case-insensitive)
- Or use the RxNorm code instead

### No Variants Extracted

If the parser returns "No variants could be extracted":
- Verify the file format matches expected headers
- Check that the CSV/PDF contains recognizable column names (rsid, genotype, gene, star, etc.)
- Try the other file format (CSV vs PDF)

## API Rate Limiting

There is no rate limiting in this MVP. For production:
- Add authentication
- Implement rate limiting per user/API key
- Add request logging and monitoring
- Implement RBAC (Role-Based Access Control)

## Security Note

⚠️ **This is an MVP with no authentication or authorization.** 

For production deployment:
- Add user authentication (OAuth2, JWT)
- Implement RBAC for different user roles
- Add API keys for external integrations
- Enable HTTPS/TLS
- Implement audit logging
- Add PHI/PII data encryption
- Comply with HIPAA requirements

## License

MIT

