# Care Triage - Foundry Model Router

## 🎯 Overview

A complete, production-ready healthcare triage assistant demonstrating Microsoft Foundry Model Router capabilities. Routes queries by intent (Admin/Clinical/Vision), applies PHI redaction and safety guardrails, and provides comprehensive observability.

## ✨ Key Features

- **🔀 Intelligent Routing**: Foundry Model Router with Balanced/Cost/Quality modes
- **🔒 PHI Protection**: Automatic redaction of sensitive health information
- **🛡️ Safety Guardrails**: Emergency detection, prohibited content blocking
- **📚 Clinical RAG**: Azure AI Search integration with vetted medical knowledge
- **👁️ Vision Analysis**: Medical image processing with educational descriptions
- **📊 Full Observability**: Real-time telemetry (model, tokens, latency, routing logic)
- **⚡ Fast Setup**: Automated scripts for quick deployment

## 🚀 Quick Start

### Windows
```cmd
setup.bat
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

Then:
1. Edit `backend/.env` with your Azure credentials
2. Start backend: `cd backend && python app.py`
3. Start frontend: `cd frontend && npm run dev`
4. Open http://localhost:5173

## 📖 Documentation

- **[README.md](README.md)**: Complete documentation
- **[SETUP.md](SETUP.md)**: Detailed setup instructions
- **[API Docs](http://localhost:8000/docs)**: Auto-generated API documentation (when backend is running)

## 🧪 Testing

```bash
cd backend
pytest tests/ -v --cov=.
```

## 🏗️ Architecture

```
Frontend (React) → FastAPI → Foundry Model Router
                           ↓
                    Azure AI Search (RAG)
                           ↓
                    Azure OpenAI (Vision/Direct)
```

## 📦 What's Included

- ✅ Complete FastAPI backend with modular design
- ✅ React TypeScript frontend with modern UI
- ✅ Comprehensive test suite (pytest)
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ PHI redaction engine
- ✅ Safety guardrails system
- ✅ RAG pipeline for clinical knowledge
- ✅ Vision model integration
- ✅ Full observability and logging
- ✅ Detailed documentation

## 🛠️ Tech Stack

**Backend**: Python 3.11, FastAPI, Azure OpenAI SDK, Azure AI Search
**Frontend**: React 18, TypeScript, Vite
**Testing**: pytest, pytest-cov
**CI/CD**: GitHub Actions

## 🎓 Demo Prompts

**Admin**: "Schedule an appointment for next week"
**Clinical**: "What are flu symptoms?"
**Vision**: Upload an X-ray + "Describe this image"
**PHI Test**: "My phone is 555-123-4567" (will be redacted)
**Emergency**: "Severe chest pain" (triggers 911 warning)

## ⚠️ Important Notes

- **Demo Only**: Not for actual clinical use
- **HIPAA Compliance**: Requires additional measures for production
- **Azure Costs**: Monitor your Azure resource usage
- **Rate Limits**: Configure appropriate rate limiting for production

## 📝 License

For demonstration purposes. Consult legal/compliance teams before production use.

## 🤝 Contributing

PRs welcome! See [SETUP.md](SETUP.md) for development workflow.

---

**Built with ❤️ for healthcare innovation using Microsoft Foundry**
