# Epi-Risk Lite MVP

A clinical decision support tool that screens patient genomic data for harmful epistatic interactions and provides risk scores for adverse drug reactions.

## Features

- **Multi-format parsing**: Accepts CSV or PDF patient genotype files
- **Functional mapping**: Converts genetic variants to functional tags using rsID/genotype and star-allele proxies
- **Risk scoring**: Deterministic rule-based scoring with optional XGBoost ML model
- **Drug-gene pathways**: Filters variants to relevant drug metabolism genes
- **Clinical rationale**: Provides detailed explanations and alternative medication suggestions

## Quick Start

### Using Docker

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000` (or `http://your-server-ip:8000`)

**Hackathon Note**: CORS is enabled to allow requests from any domain!

### Local Development

```bash
# Install dependencies
pip install -e .

# Run the server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### POST /v1/score-file

Upload a patient genotype file (CSV or PDF) along with medication info:

```bash
curl -X POST "http://localhost:8000/v1/score-file" \
  -F "file=@patient_genotype.csv" \
  -F "medication_name=codeine" \
  -F 'context={"age":45,"sex":"M","ancestry":"EUR"}'
```

**Form fields:**
- `file`: CSV or PDF file with genetic variants
- `medication_name`: Drug name (optional if rxnorm provided)
- `rxnorm`: RxNorm code (optional if medication_name provided)
- `context`: JSON string with patient context (optional)

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
      "evidence": ["Combined loss impairs codeine activation significantly"]
    }
  ],
  "suggested_alternatives": [
    {
      "rxnorm": "7052",
      "name": "morphine",
      "note": "does not require CYP2D6 activation"
    }
  ],
  "trace_id": "uuid-here",
  "model_version": "rules-0.1.0",
  "knowledge_version": "rules-20250104"
}
```

### POST /v1/score

Score with already-normalized variant data:

```bash
curl -X POST "http://localhost:8000/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "variants": [
      {"rsid": "rs3892097", "genotype": "AA"},
      {"gene": "CYP2D6", "star": "*4/*4"}
    ],
    "medication_name": "codeine"
  }'
```

### GET /healthz

Health check endpoint:

```bash
curl http://localhost:8000/healthz
```

### GET /version

Get version information:

```bash
curl http://localhost:8000/version
```

## CSV Format

Accepted CSV headers (case-insensitive):
- `rsid` or `snp`: Variant identifier
- `genotype`, `call`, or `gt`: Allele combination (e.g., "A/G", "AG")
- `gene`: Gene symbol
- `variant`: Variant name
- `allele1`, `allele2`: Individual alleles
- `zyg` or `zygosity`: Homozygous/heterozygous

Example:
```csv
rsid,genotype
rs3892097,AA
rs1065852,GG
```

Or with star alleles:
```csv
gene,star
CYP2D6,*4/*4
CYP2C19,*2/*1
```

## PDF Format

The parser attempts to extract tables from PDF files using:
1. Camelot with lattice flavor (structured tables)
2. Camelot with stream flavor (fallback)
3. pdfplumber (fallback for complex PDFs)

Expected table columns: similar to CSV headers above.

## Training (Optional)

Train an XGBoost model with labeled data:

```bash
# Using the CLI
python -m app.train.cli --in data/train.parquet --out models/

# Or via API
curl -X POST "http://localhost:8000/v1/train-file" \
  -F "file=@training_data.csv"
```

Training data should include:
- `patient_id`: Patient identifier
- `rxnorm`: RxNorm code
- `drug_name`: Medication name
- `variants_json`: JSON string of variant list
- `y`: Binary outcome (0=no adverse event, 1=adverse event)

## Testing

```bash
pytest
```

## Architecture

```
Upload → Parse (CSV/PDF) → Normalize → Map to Tags → 
Filter by Pathway → Score (Rules/ML) → Return JSON
```

## Knowledge Base

The system uses several curated JSON files:
- `allele_proxies.json`: Maps rsID:genotype → functional tags
- `star_allele_proxies.json`: Maps star alleles → functional tags
- `drug_gene_map.json`: Maps drugs → relevant genes
- `alternatives.json`: Alternative medication suggestions
- `guidelines.json`: Clinical evidence and rationales

## License

MIT

