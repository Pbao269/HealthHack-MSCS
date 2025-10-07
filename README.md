# HealthHack MSCS (Multi-scope Clinical Support)

A comprehensive clinical decision support platform for healthcare professionals, designed to improve patient care through evidence-based decision making and personalized medicine.

Demo: https://www.youtube.com/watch?v=BRFQOMtIXYw&t=24s

## 🏥 **Platform Overview**

HealthHack MSCS is a modular clinical support system that provides healthcare professionals with advanced tools for:

- **Pharmacogenomics**: Personalized medication recommendations based on genetic data
- **Clinical Decision Support**: Evidence-based guidelines and risk assessments
- **Patient Monitoring**: Real-time health tracking and alerts
- **Workflow Automation**: Streamlined clinical processes

## 🧬 **Components**

### Epi-Risk Lite
**Clinical decision support for epistatic risk scoring in pharmacogenomics**

- **Location**: `/epi-risk-lite/`
- **Purpose**: Screen patient genomic data for harmful epistatic interactions
- **Technology**: Python, FastAPI, XGBoost, Docker, Llama V3.3 (later in the pipeline)
- **Coverage**: 50+ medications, 50+ genes, 200+ variants

**Key Features**:
- Multi-format file parsing (CSV, PDF)
- Deterministic and ML-based risk scoring
- Clinical rationales with evidence
- Alternative medication suggestions
- RESTful API with auto-generated documentation
