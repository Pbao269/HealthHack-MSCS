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
- **Technology**: Python, FastAPI, XGBoost, Docker
- **Status**: ✅ Production Ready
- **Coverage**: 50+ medications, 50+ genes, 200+ variants

**Key Features**:
- Multi-format file parsing (CSV, PDF)
- Deterministic and ML-based risk scoring
- Clinical rationales with evidence
- Alternative medication suggestions
- RESTful API with auto-generated documentation

**Quick Start**:
```bash
cd epi-risk-lite
pip install -e .
uvicorn app.main:app --reload
```

**Documentation**: [Epi-Risk Lite README](epi-risk-lite/README.md)

### Future Components
- **Patient Monitoring Dashboard**: Real-time health tracking
- **Clinical Workflow Automation**: Streamlined processes
- **EHR Integration**: Seamless data exchange
- **Population Health Analytics**: Population-level insights

## 🚀 **Quick Start**

### Prerequisites
- Python 3.11+
- Docker (optional)
- Git

### 🏆 **Hackathon Usage**
This API is configured for hackathon use with:
- **CORS enabled** - Accepts requests from any domain
- **No authentication** - Ready for immediate use
- **RESTful API** - Easy integration with any frontend
- **Swagger UI** - Interactive API documentation

#### **Frontend Integration Example**
```javascript
// JavaScript/React example
const API_BASE = 'http://your-server-ip:8000';

// Score genetic variants
async function scoreVariants(variants, medication) {
  const response = await fetch(`${API_BASE}/v1/score`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      variants: variants,
      medication_name: medication
    })
  });
  
  return await response.json();
}

// Upload CSV file
async function uploadFile(file, medication) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('medication_name', medication);
  
  const response = await fetch(`${API_BASE}/v1/score-file`, {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}
```

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Pbao269/HealthHack-MSCS.git
cd HealthHack-MSCS
```

2. **Set up Epi-Risk Lite**:
```bash
cd epi-risk-lite
pip install -e .
```

3. **Start the application**:
```bash
uvicorn app.main:app --reload --port 8000
```

4. **Access the API**:
- Swagger UI: http://localhost:8000/docs (or http://your-server-ip:8000/docs)
- ReDoc: http://localhost:8000/redoc (or http://your-server-ip:8000/redoc)
- **Hackathon Note**: API accepts requests from any domain (CORS enabled)

### Docker Deployment

```bash
cd epi-risk-lite
docker-compose up --build
```

## 📊 **Data Expansion**

To expand the knowledge base with additional medications and genes:

```bash
cd epi-risk-lite/scripts
pip install -r requirements.txt
python collect_pharmgkb_data.py
python collect_cpic_data.py
python collect_fda_data.py
python integrate_data.py
```

**Sources**: PharmGKB, CPIC, FDA, RxNorm

## 🏗️ **Architecture**

```
HealthHack-MSCS/
├── epi-risk-lite/              # Pharmacogenomics component
│   ├── app/                    # FastAPI application
│   ├── scripts/                # Data collection tools
│   ├── data/                   # Knowledge base
│   └── models/                 # ML models
├── shared/                     # Common utilities (future)
├── docs/                       # Platform documentation (future)
└── deployments/                # Deployment configurations (future)
```

## 🔧 **Development**

### Running Tests
```bash
cd epi-risk-lite
pytest
```

### Data Collection
```bash
cd epi-risk-lite/scripts
python collect_pharmgkb_data.py
python collect_cpic_data.py
python collect_fda_data.py
python integrate_data.py
```

### API Testing
```bash
cd epi-risk-lite
./test_api.sh
```

## 📚 **Documentation**

- [Epi-Risk Lite Documentation](epi-risk-lite/README.md)
- [Data Expansion Guide](epi-risk-lite/scripts/README.md)
- [API Documentation](http://localhost:8000/docs) (when running locally)
- **Hackathon**: API accessible from any domain with CORS enabled
- [Project Summary](epi-risk-lite/PROJECT_SUMMARY.md)

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **PharmGKB**: Pharmacogenomics knowledge base
- **CPIC**: Clinical Pharmacogenetics Implementation Consortium
- **FDA**: Pharmacogenomic biomarkers data
- **RxNorm**: Standardized drug nomenclature

## 📞 **Support**

For questions or issues:
1. Check the component-specific documentation
2. Review the API documentation at `/docs`
3. Open an issue on GitHub
4. Contact the development team

## 🎯 **Roadmap**

### Phase 1: Core Platform (Current)
- ✅ Epi-Risk Lite pharmacogenomics component
- ✅ Data collection and integration tools
- ✅ RESTful API with documentation
- ✅ Docker deployment support

### Phase 2: Expansion (Q2 2025)
- 🔄 Patient monitoring dashboard
- 🔄 Clinical workflow automation
- 🔄 Enhanced ML models
- 🔄 Real-time data processing

### Phase 3: Integration (Q3 2025)
- 📋 EHR system integration
- 📋 Population health analytics
- 📋 Multi-tenant support
- 📋 Advanced security features

### Phase 4: Scale (Q4 2025)
- 📋 Cloud deployment
- 📋 Microservices architecture
- 📋 Advanced analytics
- 📋 Mobile applications

---

**HealthHack MSCS** - Empowering healthcare through intelligent clinical support

**Repository**: [https://github.com/Pbao269/HealthHack-MSCS](https://github.com/Pbao269/HealthHack-MSCS)

**Status**: 🚀 Active Development
