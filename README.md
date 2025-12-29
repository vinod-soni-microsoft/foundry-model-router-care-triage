# Care Triage - Foundry Model Router Demo

A lightweight clinic triage assistant that intelligently routes healthcare queries using Microsoft Foundry Model Router. The system classifies requests by intent (Admin/Clinical/Vision), applies PHI redaction and guardrails, and provides comprehensive observability.

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │  Vite React TypeScript
│   (Chat UI) │  - Message input
└──────┬──────┘  - Image upload
       │         - Telemetry display
       │ HTTP
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│                                     │
│  ┌─────────────────────────────┐  │
│  │  1. PHI Redaction           │  │
│  │  2. Safety Guardrails       │  │
│  │  3. Intent Detection        │  │
│  │  4. Model Selection         │  │
│  │  5. Response Generation     │  │
│  │  6. Observability Logging   │  │
│  └─────────────────────────────┘  │
└──────┬──────────────────┬──────────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌─────────────────┐
│   Foundry    │   │  Azure AI       │
│ Model Router │   │  Search (RAG)   │
│              │   │  Medical KB     │
└──────────────┘   └─────────────────┘
```

## ✨ Features

### Core Capabilities
- **Intent Detection**: Automatically classifies queries as Admin, Clinical, or Vision
- **PHI Redaction**: Detects and redacts Protected Health Information (phone, email, SSN, names, etc.)
- **Safety Guardrails**: Blocks prohibited content, flags emergencies, adds disclaimers
- **Model Router**: Uses Foundry Model Router with 3 modes (Balanced/Cost/Quality)
- **Clinical RAG**: Retrieves vetted medical knowledge with citations
- **Vision Analysis**: Processes medical images with educational descriptions
- **Observability**: Comprehensive logging of routing decisions, model selection, tokens, and latency

### Frontend
- Clean chat interface with message history
- Image upload for vision analysis
- Routing mode selector (⚖️ Balanced / 💰 Cost / ⭐ Quality)
- Real-time telemetry display
- Citation display for RAG responses
- Safety warnings and disclaimers

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Azure OpenAI or Microsoft Foundry access
- (Optional) Azure AI Search for RAG

### 1. Clone and Setup

```bash
git clone <your-repo>
cd foundry-model-router-care-triage
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (see Configuration section)

# Run backend
python app.py
```

Backend runs on: http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs on: http://localhost:5173

## ⚙️ Configuration

### Backend Environment Variables (.env)

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Microsoft Foundry Model Router Configuration
FOUNDRY_ENDPOINT=https://your-foundry-endpoint.ai.azure.com
FOUNDRY_API_KEY=your-foundry-api-key
FOUNDRY_DEPLOYMENT_NAME=model-router

# Azure AI Search Configuration (Optional - for RAG)
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
SEARCH_KEY=your-search-admin-key
SEARCH_INDEX_NAME=medical-kb

# Application Settings
LOG_LEVEL=INFO
```

### Foundry Model Router Deployment

1. **Create Model Router in Microsoft Foundry**:
   - Navigate to Microsoft Foundry (formerly Azure AI Foundry)
   - Create a new Model Router deployment
   - Configure routing preferences for cost/quality/balanced modes
   - Note the endpoint URL and deployment name

2. **Configure Model Deployments**:
   - Ensure you have the following deployments available:
     - `model-router`: Foundry Model Router
     - `gpt-35-turbo`: Admin/cost-effective queries
     - `gpt-4`: Clinical/high-quality queries
     - `gpt-4-vision`: Vision-capable model for images

3. **Update Environment Variables**:
   - Set `FOUNDRY_ENDPOINT` to your Foundry resource endpoint
   - Set `FOUNDRY_API_KEY` to your API key
   - Set `FOUNDRY_DEPLOYMENT_NAME` to your router deployment name

### Azure AI Search Setup (Optional - for RAG)

1. Create an Azure AI Search service
2. Create an index named `medical-kb` with fields:
   - `content` (text)
   - `title` (text)
   - `source` (text)
   - `category` (text)
3. Populate with vetted medical knowledge documents
4. Update `SEARCH_ENDPOINT`, `SEARCH_KEY`, and `SEARCH_INDEX_NAME` in `.env`

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
pytest tests/ -v --cov=.
```

### Test Coverage
- Intent detection (admin/clinical/vision)
- PHI redaction (phone, email, SSN, names)
- Safety guardrails (prohibited content, emergencies)
- Model selection logic
- Disclaimer addition

## 📊 Demo Prompts

### Administrative Intent
```
"I need to schedule an appointment for next week"
"What are your office hours?"
"Do you accept my insurance?"
```

### Clinical Intent
```
"I have a persistent headache for 3 days"
"What are the symptoms of flu?"
"Is acetaminophen safe during pregnancy?"
```

### Vision Intent
```
Upload an X-ray or medical image with prompt:
"Can you describe what you see in this image?"
"What anatomical structures are visible?"
```

### PHI Redaction Test
```
"My name is John Smith, phone 555-123-4567"
"Contact me at patient@example.com"
"My DOB is 01/15/1980"
```

### Emergency Detection
```
"I'm having severe chest pain"
"Can't breathe properly"
(System will flag as emergency and provide 911 guidance)
```

## 📁 Project Structure

```
foundry-model-router-care-triage/
├── backend/
│   ├── app.py                    # FastAPI application
│   ├── foundry_client.py         # Foundry & Azure OpenAI client
│   ├── intent_detector.py        # Intent classification
│   ├── phi_redactor.py           # PHI detection & redaction
│   ├── guardrails.py             # Safety checks & disclaimers
│   ├── model_selector.py         # Model routing logic
│   ├── router_observability.py   # Telemetry & logging
│   ├── ai/
│   │   └── rag_pipeline.py       # Clinical RAG with Azure AI Search
│   ├── tests/
│   │   ├── test_modules.py       # Unit tests
│   │   └── test_api.py           # API integration tests
│   ├── requirements.txt
│   ├── .env.example
│   └── router.log               # Generated log file
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main React component
│   │   └── App.css              # Styles
│   ├── package.json
│   └── vite.config.ts
├── .github/
│   └── workflows/
│       └── ci.yml               # CI/CD pipeline
├── .gitignore
└── README.md
```

## 🔍 Observability

### Telemetry Captured
- **Intent**: Detected intent (admin/clinical/vision)
- **Model Chosen**: Actual model used (from router or direct)
- **Tokens**: Prompt, completion, and total tokens
- **Latency**: Request processing time (ms)
- **Routing Mode**: User-selected mode (balanced/cost/quality)
- **Rationale**: Explanation of routing decision
- **PHI Detection**: Whether PHI was found and redacted
- **Image Present**: Whether request included image

### Logging
All routing decisions are logged to:
- Console (for development)
- `backend/router.log` (persistent file)

Example log entry:
```json
{
  "timestamp": "2024-12-29T10:30:00.000Z",
  "intent": "clinical",
  "routing_mode": "balanced",
  "model_chosen": "gpt-4",
  "tokens": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  },
  "latency_ms": 1234.56,
  "rationale": "Balanced routing via Model Router",
  "has_phi": false,
  "has_image": false
}
```

## 🛡️ Safety & Compliance

### PHI Protection
- Automatic detection and redaction of:
  - Phone numbers
  - Email addresses
  - Social Security Numbers
  - Medical Record Numbers
  - Dates of birth
  - Physical addresses
  - Patient names

### Safety Guardrails
- **Emergency Detection**: Flags life-threatening situations with 911 guidance
- **Prohibited Content**: Blocks illegal requests (fake prescriptions, etc.)
- **Medical Disclaimers**: Automatically added to clinical and vision responses
- **Non-Diagnostic Language**: Enforced through prompts and disclaimers

### Compliance Note
⚠️ **This is a demonstration tool only**. Not intended for actual clinical use. For production deployment:
- Implement additional HIPAA compliance measures
- Add user authentication and authorization
- Enable audit logging
- Conduct security assessments
- Obtain appropriate certifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow
- Backend tests: `pytest backend/tests/ -v`
- Frontend build: `cd frontend && npm run build`
- Linting: `flake8 backend/` and `black backend/`

## 📝 License

This project is for demonstration purposes. Consult with legal and compliance teams before using in production healthcare environments.

## 🆘 Troubleshooting

### Backend won't start
- Verify all environment variables in `.env`
- Check Python version: `python --version` (should be 3.11+)
- Ensure dependencies installed: `pip install -r requirements.txt`

### Frontend API errors
- Confirm backend is running on http://localhost:8000
- Check CORS settings in `backend/app.py`
- Verify network connectivity

### Foundry Router errors
- Validate `FOUNDRY_ENDPOINT` and `FOUNDRY_API_KEY`
- Confirm Model Router deployment exists and is active
- Check Azure resource quotas

### RAG not working
- Verify Azure AI Search credentials
- Ensure index `medical-kb` exists and is populated
- Check search service is in same region

## 📚 Additional Resources

- [Microsoft Foundry Documentation](https://learn.microsoft.com/azure/ai-services/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure AI Search](https://learn.microsoft.com/azure/search/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite + React](https://vitejs.dev/guide/)

---

**Built with ❤️ for healthcare innovation**
