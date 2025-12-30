# ✅ Deployment Complete - Care Triage with Model Router

## Deployment Summary

Successfully deployed all Azure resources to **Sweden Central** region using Azure Developer CLI (azd).

**Deployment Date:** December 29, 2025  
**Environment:** care-triage-prod  
**Resource Token:** veiwwlix6ozgs  
**Subscription:** ME-MngEnvMCAP797853-vinodsoni-1 (4aa3a068-9553-4d3b-be35-5f6660a6253b)

---

## 📦 Deployed Resources

### Resource Groups
1. **rg-care-triage-prod-ai-veiwwlix6ozgs** - AI and ML services
2. **rg-care-triage-prod-data-veiwwlix6ozgs** - Data and search services
3. **rg-care-triage-prod-security-veiwwlix6ozgs** - Security and secrets

### AI Services
- **AI Hub:** aihveiwwlix6ozgs
  - Type: Azure AI Foundry Hub
  - Location: Sweden Central
  - Network: Isolation Disabled (for easier access)

- **AI Project:** aipveiwwlix6ozgs
  - Type: Azure AI Foundry Project
  - Discovery URL: https://swedencentral.api.azureml.ms/discovery
  - Linked to AI Hub

- **Azure OpenAI:** aihveiwwlix6ozgs-openai
  - Endpoint: https://aihveiwwlix6ozgs-openai.openai.azure.com/
  - Authentication: Azure AD (Entra ID)
  - Deployment: model-router (version 2025-11-18)
  - SKU: GlobalStandard
  - Upgrade Policy: NoAutoUpgrade

### Data Services
- **Azure AI Search:** srchveiwwlix6ozgs
  - Endpoint: https://srchveiwwlix6ozgs.search.windows.net
  - Purpose: RAG (Retrieval-Augmented Generation)
  - Index: medical-kb

- **Storage Account:** stveiwwlix6ozgs
  - Purpose: AI Hub data storage
  - Location: Sweden Central

### Security & Monitoring
- **Key Vault:** kvveiwwlix6ozgs
  - Endpoint: https://kvveiwwlix6ozgs.vault.azure.net/
  - Purpose: Secure key storage

- **Application Insights:** appiveiwwlix6ozgs
  - Purpose: Application monitoring and telemetry

- **Log Analytics:** logveiwwlix6ozgs
  - Purpose: Log aggregation and analysis

---

## 🔐 Access & Permissions

### Role Assignments Created
1. **Azure AI Developer** - Assigned to your user (admin@MngEnvMCAP797853.onmicrosoft.com)
   - Scope: AI Hub (aihveiwwlix6ozgs)
   - Allows full AI Foundry access

2. **Cognitive Services User** - Assigned to your user
   - Scope: Azure OpenAI (aihveiwwlix6ozgs-openai)
   - Allows model inference calls

3. **Storage Blob Data Contributor** - Assigned to AI Hub managed identity
   - Scope: Storage Account (stveiwwlix6ozgs)
   - Allows AI Hub to read/write data

---

## 🔑 Configuration Values

All values have been updated in `backend/.env`:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://aihveiwwlix6ozgs-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=FdIy...EFvz
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Microsoft Foundry Model Router Configuration
FOUNDRY_ENDPOINT=https://swedencentral.api.azureml.ms/discovery
FOUNDRY_API_KEY=FdIy...EFvz
FOUNDRY_DEPLOYMENT_NAME=model-router

# Azure AI Search Configuration
SEARCH_ENDPOINT=https://srchveiwwlix6ozgs.search.windows.net
SEARCH_KEY=SjYT...kQT
SEARCH_INDEX_NAME=medical-kb
```

---

## 🎯 Next Steps

### 1. Create AI Agent (Manual Step)

The AI Agent must be created manually in the Azure AI Foundry portal:

1. Navigate to **Azure AI Foundry Studio**: https://ai.azure.com
2. Select your project: **aipveiwwlix6ozgs**
3. Go to **Agents** section
4. Click **Create new agent**
5. Configure:
   - **Name:** care-triage-agent
   - **Base Model:** model-router (from deployment)
   - **Description:** AI agent for care triage using Model Router
   - **Instructions:** Customize based on your triage logic

### 2. Test the Application

Start the backend server:
```bash
cd backend
.venv\Scripts\activate  # Activate virtual environment
python app.py
```

Start the frontend:
```bash
cd frontend
npm run dev
```

Access the application at: http://localhost:5173

### 3. Verify Model Router

Test that the Model Router is working:
```python
from foundry_client import FoundryClient
import os
from dotenv import load_dotenv

load_dotenv()
client = FoundryClient()
response = client.query("What are the symptoms of a heart attack?")
print(response)
```

### 4. Populate Search Index (Optional)

If using RAG features, populate the medical knowledge base:
```bash
# Run your indexing script
python backend/ai/populate_search_index.py
```

---

## 🔗 Useful Links

- **Azure Portal:** https://portal.azure.com
- **AI Foundry Studio:** https://ai.azure.com
- **AI Project:** https://ai.azure.com/resource/projects/aipveiwwlix6ozgs
- **OpenAI Resource:** https://portal.azure.com/#@119c65a0-954b-4fcc-a16a-e7ce5559037d/resource/subscriptions/4aa3a068-9553-4d3b-be35-5f6660a6253b/resourceGroups/rg-care-triage-prod-ai-veiwwlix6ozgs/providers/Microsoft.CognitiveServices/accounts/aihveiwwlix6ozgs-openai

---

## 📊 Deployment Commands Reference

```bash
# View all environment values
azd env get-values

# Refresh/redeploy infrastructure
azd provision

# Deploy application code (if configured)
azd deploy

# Tear down all resources
azd down --force --purge

# Check authentication
azd auth login --check-status

# Switch subscription
az account set --subscription 4aa3a068-9553-4d3b-be35-5f6660a6253b

# Get OpenAI key
az cognitiveservices account keys list --name aihveiwwlix6ozgs-openai \
  --resource-group rg-care-triage-prod-ai-veiwwlix6ozgs --query key1 -o tsv

# Get Search key
az search admin-key show --resource-group rg-care-triage-prod-data-veiwwlix6ozgs \
  --service-name srchveiwwlix6ozgs --query primaryKey -o tsv
```

---

## ⚠️ Important Notes

1. **Model Router Version:** 2025-11-18 (NoAutoUpgrade policy)
   - Will not automatically upgrade to newer versions
   - Manual upgrade required when new versions are available

2. **Authentication:** Using Azure AD (Entra ID) authentication
   - No local auth keys for OpenAI (disableLocalAuth: true)
   - API keys provided for backward compatibility
   - Managed identity used for service-to-service auth

3. **Network Access:** AI Hub isolation is disabled
   - Easier for development and testing
   - For production, consider enabling managed network isolation

4. **Cost Management:**
   - Model Router uses GlobalStandard SKU
   - Azure AI Search on Free tier (if selected)
   - Monitor costs in Azure Portal: Cost Management + Billing

5. **Old Resources Cleaned Up:**
   - Previous environment (care-triage-model-router) resource groups deleted
   - Only care-triage-prod resources remain active

---

## 🐛 Troubleshooting

### Backend won't start
- Ensure virtual environment is activated
- Check `.env` file has all required values
- Verify Python dependencies: `pip install -r requirements.txt`

### Can't access AI Foundry
- Confirm you have "Azure AI Developer" role
- Check you're logged into correct subscription
- Wait a few minutes for role assignments to propagate

### Model Router not responding
- Verify deployment exists: Check Azure Portal
- Test endpoint directly using Azure AI SDK
- Check Application Insights for errors

### Search index not found
- Run indexing script to populate data
- Verify search service name and key in `.env`
- Check index name matches: `medical-kb`

---

## 🎉 Success!

Your Care Triage application with Microsoft Foundry Model Router is now deployed and ready to use!

For questions or issues, refer to:
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Detailed deployment guide
- [AZURE_SETUP_SUMMARY.md](./AZURE_SETUP_SUMMARY.md) - Azure architecture overview
- [README.md](./README.md) - Application documentation
