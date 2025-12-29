# Care Triage - Setup Instructions

## Prerequisites

- **Python 3.11+**: Check with `python --version`
- **Node.js 20+**: Check with `node --version`
- **pip**: Python package installer
- **npm**: Node package manager
- **Git**: Version control

## Azure Resources Required

### 1. Azure OpenAI Service
- Create an Azure OpenAI resource in Azure Portal
- Deploy models:
  - `gpt-35-turbo` (for admin queries)
  - `gpt-4` (for clinical queries)
  - `gpt-4-vision` (for image analysis)

### 2. Microsoft Foundry Model Router
- Access Microsoft Foundry portal (formerly Azure AI Foundry)
- Create a new Model Router deployment
- Configure routing preferences:
  - **Balanced**: Mix of cost and quality
  - **Cost**: Prefer faster, cheaper models
  - **Quality**: Prefer higher-quality models
- Note the endpoint and API key

### 3. Azure AI Search (Optional - for RAG)
- Create Azure AI Search service
- Create index named `medical-kb`
- Schema:
  ```json
  {
    "fields": [
      {"name": "id", "type": "Edm.String", "key": true},
      {"name": "content", "type": "Edm.String", "searchable": true},
      {"name": "title", "type": "Edm.String", "searchable": true},
      {"name": "source", "type": "Edm.String"},
      {"name": "category", "type": "Edm.String", "filterable": true}
    ]
  }
  ```
- Populate with vetted medical documents

## Installation Steps

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd foundry-model-router-care-triage
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit .env with your Azure credentials
# Use your favorite text editor:
notepad .env  # Windows
nano .env     # Linux/Mac
```

### Step 3: Configure Environment Variables

Edit `backend/.env` and fill in:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Foundry Model Router
FOUNDRY_ENDPOINT=https://<your-foundry>.ai.azure.com
FOUNDRY_API_KEY=<your-foundry-key>
FOUNDRY_DEPLOYMENT_NAME=model-router

# Azure AI Search (Optional)
SEARCH_ENDPOINT=https://<your-search>.search.windows.net
SEARCH_KEY=<your-search-key>
SEARCH_INDEX_NAME=medical-kb
```

### Step 4: Test Backend

```bash
# Run tests
pytest tests/ -v

# Start backend server
python app.py
```

Backend should start on http://localhost:8000

Test health endpoint:
```bash
curl http://localhost:8000/
```

### Step 5: Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend should start on http://localhost:5173

### Step 6: Verify Setup

1. Open browser to http://localhost:5173
2. You should see the Care Triage chat interface
3. Try a test message: "What are your office hours?"
4. Verify you get a response with telemetry displayed

## Deployment to Production

### Backend Deployment (Azure App Service)

```bash
# Create App Service
az webapp create --name care-triage-api --resource-group <rg> --plan <plan> --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set --name care-triage-api --resource-group <rg> --settings \
  AZURE_OPENAI_ENDPOINT="<value>" \
  AZURE_OPENAI_API_KEY="<value>" \
  FOUNDRY_ENDPOINT="<value>" \
  FOUNDRY_API_KEY="<value>"

# Deploy
cd backend
zip -r deploy.zip . -x "venv/*" "tests/*" "__pycache__/*" "*.pyc"
az webapp deployment source config-zip --name care-triage-api --resource-group <rg> --src deploy.zip
```

### Frontend Deployment (Azure Static Web Apps)

```bash
# Build frontend
cd frontend
npm run build

# Deploy to Static Web Apps
az staticwebapp create --name care-triage-ui --resource-group <rg> --location eastus2

# Configure API endpoint
# Update frontend API URL to point to deployed backend
```

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=.

# Frontend tests (if added)
cd frontend
npm test
```

### Code Formatting

```bash
# Python
cd backend
black .
flake8 .

# TypeScript
cd frontend
npm run lint
```

### Making Changes

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Run tests: `pytest tests/`
4. Commit: `git commit -m "Description"`
5. Push: `git push origin feature/my-feature`
6. Create Pull Request

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: CORS errors in browser

**Solution**: Verify backend is running and frontend is configured correctly
- Check `backend/app.py` CORS configuration includes frontend URL
- Confirm backend running on http://localhost:8000
- Check browser console for specific error

### Issue: "Authentication failed" errors

**Solution**: Verify Azure credentials
- Check `.env` file has correct values (no quotes, no spaces)
- Verify API keys are valid in Azure Portal
- Ensure resource endpoints are correct

### Issue: Frontend won't build

**Solution**: Clear cache and reinstall
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue: Model Router errors

**Solution**: Verify Foundry setup
- Confirm Model Router deployment is active
- Check deployment name matches `FOUNDRY_DEPLOYMENT_NAME`
- Verify endpoint URL format is correct
- Test endpoint with curl:
```bash
curl -X POST "<FOUNDRY_ENDPOINT>/openai/deployments/<DEPLOYMENT>/chat/completions?api-version=2024-02-15-preview" \
  -H "Content-Type: application/json" \
  -H "api-key: <KEY>" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

## Additional Configuration

### Enable Detailed Logging

Edit `backend/router_observability.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    ...
)
```

### Customize Intent Keywords

Edit `backend/intent_detector.py` to add domain-specific keywords:
```python
CLINICAL_KEYWORDS = [
    "symptom", "diagnosis", ...
    "your-custom-keyword"
]
```

### Adjust PHI Patterns

Edit `backend/phi_redactor.py` to customize PHI detection patterns.

### Configure Model Deployments

Edit `backend/model_selector.py` to match your deployment names:
```python
MODELS = {
    "admin": {"deployment": "your-gpt35-deployment"},
    "clinical": {"deployment": "your-gpt4-deployment"},
    ...
}
```

## Support

For issues or questions:
1. Check logs: `backend/router.log`
2. Review README.md troubleshooting section
3. Check Azure Portal for service health
4. Open GitHub issue with error details

## Next Steps

1. **Populate RAG Knowledge Base**: Add medical documents to Azure AI Search
2. **Customize Disclaimers**: Update `guardrails.py` for your use case
3. **Add Authentication**: Implement user authentication
4. **Enable Monitoring**: Set up Application Insights
5. **Security Hardening**: Review and implement additional security measures

---

**Last Updated**: December 2025
