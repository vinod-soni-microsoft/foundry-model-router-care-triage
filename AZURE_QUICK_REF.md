# Azure Deployment Quick Reference

## Prerequisites Checklist

- [ ] Azure subscription with appropriate permissions
- [ ] Azure Developer CLI (azd) installed
- [ ] Azure CLI installed and authenticated
- [ ] Node.js 20+ installed
- [ ] Python 3.11+ installed

## Quick Start Commands

```bash
# 1. Authenticate
azd auth login
az login

# 2. Set principal ID
azd env set AZURE_PRINCIPAL_ID $(az ad signed-in-user show --query id -o tsv)

# 3. Initialize environment (first time)
azd init

# 4. Deploy everything
azd provision

# 5. View deployed resources
azd env get-values
```

## Deployed Resources

### Resource Groups (3 total)
- `rg-{env}-ai-{token}` - AI Foundry, Model Router, AI Agent
- `rg-{env}-data-{token}` - Azure AI Search, Storage
- `rg-{env}-security-{token}` - Key Vault

### Key Resources
- **AI Foundry Hub** - Central AI resource hub
- **AI Foundry Project** - Project workspace
- **Model Router** - Version 2025-11-18, GlobalStandard SKU
- **AI Agent** - care-triage-agent (uses Model Router)
- **Azure OpenAI** - S0 tier
- **Azure AI Search** - Basic tier
- **Key Vault** - For secrets
- **Storage Account** - LRS tier
- **Application Insights** - For monitoring

## Important Endpoints

After deployment, get endpoints:

```bash
# Foundry endpoint
azd env get-value FOUNDRY_ENDPOINT

# OpenAI endpoint
azd env get-value AZURE_OPENAI_ENDPOINT

# Search endpoint
azd env get-value AZURE_SEARCH_ENDPOINT

# AI Agent name
azd env get-value AI_AGENT_NAME
```

## Common Tasks

### View All Resources
```bash
azd env get-values
```

### Get Resource Group Names
```bash
azd env get-value AI_RESOURCE_GROUP_NAME
azd env get-value DATA_RESOURCE_GROUP_NAME
azd env get-value SECURITY_RESOURCE_GROUP_NAME
```

### Get API Keys
```bash
# OpenAI key
az cognitiveservices account keys list \
  --name $(azd env get-value AI_HUB_NAME)-openai \
  --resource-group $(azd env get-value AI_RESOURCE_GROUP_NAME) \
  --query key1 -o tsv

# Search key
az search admin-key show \
  --resource-group $(azd env get-value DATA_RESOURCE_GROUP_NAME) \
  --service-name $(azd env get-value AZURE_SEARCH_NAME) \
  --query primaryKey -o tsv
```

### Update Infrastructure
```bash
# Make changes to infra/*.bicep files
# Then run:
azd provision
```

### Delete All Resources
```bash
azd down
```

## Running Locally After Deployment

```bash
# Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate.ps1
python app.py

# Terminal 2 - Frontend  
cd frontend
npm run dev

# Open browser
start http://localhost:5173
```

## Troubleshooting

### Check Deployment Status
```bash
azd provision --debug
```

### Verify Providers
```bash
az provider register --namespace Microsoft.MachineLearningServices
az provider register --namespace Microsoft.CognitiveServices
az provider register --namespace Microsoft.Search
az provider register --namespace Microsoft.KeyVault
```

### Check Role Assignments
```bash
az role assignment list \
  --assignee $(azd env get-value AZURE_PRINCIPAL_ID) \
  --resource-group $(azd env get-value AI_RESOURCE_GROUP_NAME)
```

## File Locations

- **Infrastructure**: `infra/` directory
- **Main Bicep**: `infra/main.bicep`
- **Parameters**: `infra/main.parameters.json`
- **AI Foundry Module**: `infra/app/ai-foundry.bicep`
- **Deployment Guide**: `DEPLOYMENT.md`
- **Environment Config**: `.azure/.env`

## Cost Estimates

- AI Foundry Hub & Project: ~$0
- Model Router: Pay-per-use
- Azure OpenAI: ~$0 + usage
- AI Search Basic: ~$75/month
- Storage LRS: ~$20/month
- Key Vault: ~$0.03/10k ops
- App Insights: ~$2.30/GB

**Estimated Total**: ~$95/month + AI usage

## Support Resources

- **Full Guide**: See `DEPLOYMENT.md`
- **Infrastructure Docs**: See `infra/README.md`
- **Azure AI Foundry Portal**: https://ai.azure.com
- **Azure Portal**: https://portal.azure.com

## Important Notes

1. **Region**: All resources deploy to Sweden Central
2. **Model Router Version**: 2025-11-18 (NoAutoUpgrade)
3. **AI Agent**: Automatically configured with Model Router
4. **Secrets**: Update backend/.env after deployment
5. **Costs**: Monitor usage in Azure Cost Management
