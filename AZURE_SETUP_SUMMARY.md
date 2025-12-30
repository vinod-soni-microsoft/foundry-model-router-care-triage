# Azure Infrastructure Setup - Summary

## ✅ Completed Tasks

All Azure infrastructure has been successfully set up with the following:

### 1. Directory Structure Created
```
infra/
├── main.bicep                      # Main deployment (subscription scope)
├── main.parameters.json            # Deployment parameters
├── abbreviations.json              # Resource naming conventions
├── app/
│   └── ai-foundry.bicep           # AI Foundry Hub, Project, Model Router, AI Agent
└── core/
    ├── ai/
    │   ├── ai-agent.bicep         # AI Agent configuration
    │   └── ai-foundry-hub.bicep   # Hub and Project setup
    ├── monitor/
    │   └── monitoring.bicep       # Application Insights & Log Analytics
    ├── search/
    │   └── search-services.bicep  # Azure AI Search
    ├── security/
    │   └── keyvault.bicep         # Key Vault
    └── storage/
        └── storage-account.bicep  # Storage Account

.azure/                             # Azure Developer CLI config
```

### 2. Resource Groups (3 Dedicated Groups)
All resources deploy to **Sweden Central** region:

1. **AI Resources RG** (`rg-{env}-ai-{token}`)
   - AI Foundry Hub
   - AI Foundry Project  
   - Azure OpenAI account
   - Model Router deployment (2025-11-18)
   - AI Agent (care-triage-agent)
   - Application Insights

2. **Data Resources RG** (`rg-{env}-data-{token}`)
   - Azure AI Search (Basic tier)
   - Storage Account (Standard LRS)

3. **Security Resources RG** (`rg-{env}-security-{token}`)
   - Azure Key Vault (RBAC-enabled)

### 3. Model Router Configuration
- **Version**: 2025-11-18 (as requested)
- **SKU**: GlobalStandard with capacity 1
- **Deployment Name**: model-router
- **Upgrade Policy**: NoAutoUpgrade (manual control)
- **Format**: OpenAI compatible

### 4. AI Agent Configuration
- **Name**: care-triage-agent
- **Base Model**: Connected to Model Router deployment
- **Integration**: Configured in AI Foundry Project
- **Description**: Care Triage AI Agent using Model Router

### 5. Azure Developer CLI (azd) Setup
- ✅ `azure.yaml` - Service definitions and deployment hooks
- ✅ `main.bicep` - Infrastructure as Code
- ✅ `main.parameters.json` - Parameterized deployment
- ✅ Postprovision hooks - Auto-updates backend/.env

### 6. Documentation Created
- ✅ `DEPLOYMENT.md` - Complete deployment guide (9,000+ words)
- ✅ `AZURE_QUICK_REF.md` - Quick reference for common tasks
- ✅ `infra/README.md` - Infrastructure documentation
- ✅ `.azure/README.md` - Azure config documentation

### 7. Security & Access
- ✅ RBAC-enabled Key Vault
- ✅ Soft delete and purge protection
- ✅ Role assignments for user (Azure AI Developer, Cognitive Services User)
- ✅ System-assigned managed identities
- ✅ Secure defaults (HTTPS only, minimal public access)

## 🚀 Next Steps to Deploy

### Step 1: Prerequisites
Install required tools:
```bash
# Install Azure Developer CLI
winget install microsoft.azd

# Install Azure CLI  
winget install microsoft.azurecli

# Verify installations
azd version
az version
```

### Step 2: Authenticate
```bash
# Login to Azure
azd auth login
az login

# Set your subscription (if multiple)
az account set --subscription "<your-subscription-id>"
```

### Step 3: Configure Environment
```bash
# Navigate to project directory
cd c:\foundry-model-router-care-triage

# Set your principal ID for role assignments
azd env set AZURE_PRINCIPAL_ID $(az ad signed-in-user show --query id -o tsv)

# Set environment name (or use default from azd init)
azd env set AZURE_ENV_NAME dev

# Confirm location is Sweden Central
azd env set AZURE_LOCATION swedencentral
```

### Step 4: Deploy Infrastructure
```bash
# Deploy all Azure resources
azd provision

# This takes ~10-15 minutes and will:
# - Create 3 resource groups in Sweden Central
# - Deploy AI Foundry Hub and Project
# - Deploy Model Router (2025-11-18 version)
# - Create AI Agent configured with Model Router
# - Deploy supporting services (Key Vault, Storage, Search, etc.)
# - Assign necessary role permissions
# - Auto-update backend/.env with connection strings
```

### Step 5: Verify Deployment
```bash
# View all deployed resources
azd env get-values

# You should see outputs like:
# FOUNDRY_ENDPOINT=https://...inference.ai.azure.com
# FOUNDRY_DEPLOYMENT_NAME=model-router
# AI_AGENT_NAME=care-triage-agent
# AI_HUB_NAME=aihub-xxxxx
# AI_PROJECT_NAME=aiproj-xxxxx
```

### Step 6: Get API Keys
```bash
# Get OpenAI API key
$rgName = azd env get-value AI_RESOURCE_GROUP_NAME
$openAIName = "$(azd env get-value AI_HUB_NAME)-openai"
az cognitiveservices account keys list `
  --name $openAIName `
  --resource-group $rgName `
  --query key1 -o tsv

# Get Search API key
$dataRg = azd env get-value DATA_RESOURCE_GROUP_NAME
$searchName = azd env get-value AZURE_SEARCH_NAME
az search admin-key show `
  --resource-group $dataRg `
  --service-name $searchName `
  --query primaryKey -o tsv
```

### Step 7: Update Backend Configuration
The postprovision hook automatically updates `backend/.env` with:
- `FOUNDRY_ENDPOINT`
- `FOUNDRY_DEPLOYMENT_NAME`  
- `AZURE_OPENAI_ENDPOINT`
- `SEARCH_ENDPOINT`

Manually add the API keys:
```bash
# Edit backend/.env and add:
AZURE_OPENAI_API_KEY=<key-from-step-6>
FOUNDRY_API_KEY=<same-as-openai-key>
SEARCH_KEY=<search-key-from-step-6>
```

### Step 8: Run Application
```bash
# Terminal 1: Start backend
cd backend
.\venv\Scripts\Activate.ps1
python app.py

# Terminal 2: Start frontend
cd frontend
npm run dev

# Open browser to http://localhost:5173
```

## 📊 What You Get

### AI Foundry Resources
- **Hub**: Central hub for managing AI resources
- **Project**: Workspace for development and deployment
- **Model Router**: Latest version (2025-11-18) with default settings
- **AI Agent**: Pre-configured agent using Model Router as base model

### Data & Search
- **Azure AI Search**: Basic tier with semantic search enabled
- **Storage Account**: For AI Foundry and application data

### Security & Monitoring
- **Key Vault**: For secure secrets management
- **Application Insights**: For telemetry and monitoring
- **Log Analytics**: For logs aggregation

### Access Control
- You get Azure AI Developer role on the Hub
- You get Cognitive Services User role on OpenAI
- Services use managed identities for inter-service communication

## 💰 Cost Estimation

Monthly costs (Sweden Central region):

| Resource | Tier/SKU | Estimated Cost |
|----------|----------|----------------|
| AI Foundry Hub & Project | - | $0 (management) |
| Model Router | GlobalStandard | Pay-per-token |
| Azure OpenAI | S0 | $0 base + usage |
| AI Search | Basic | ~$75/month |
| Storage Account | Standard LRS | ~$20/month |
| Key Vault | Standard | ~$0.03/10k ops |
| Application Insights | - | ~$2.30/GB |
| **Total** | | **~$95/month + AI usage** |

### Cost Savings Tips
- Use `azd down` when not actively using resources
- Consider AI Search Free tier for development (1 per subscription)
- Monitor usage in Azure Cost Management
- Set up budget alerts

## 🔍 Viewing Your Resources

### Azure Portal
1. Visit https://portal.azure.com
2. Navigate to Resource Groups
3. Find your three resource groups:
   - `rg-{env}-ai-{token}`
   - `rg-{env}-data-{token}`
   - `rg-{env}-security-{token}`

### Azure AI Foundry Portal
1. Visit https://ai.azure.com
2. Select your project: `aiproj-{token}`
3. View Model Router deployment: `model-router`
4. Manage AI Agent: `care-triage-agent`

### Command Line
```bash
# List all environment values
azd env get-values

# List resources in a resource group
az resource list \
  --resource-group $(azd env get-value AI_RESOURCE_GROUP_NAME) \
  --output table
```

## 🛠️ Managing the Deployment

### Update Infrastructure
```bash
# Modify Bicep files in infra/ directory
# Then update deployment:
azd provision
```

### View Deployment Logs
```bash
# Enable debug output
azd provision --debug

# View in Azure Portal
# Subscriptions → Deployments → Find by timestamp
```

### Delete Resources
```bash
# Delete all resources (keeps azd environment)
azd down

# Delete everything including azd config
azd down --purge
```

### Multiple Environments
```bash
# Create separate environments for dev/test/prod
azd env new prod
azd env select prod
azd provision
```

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| `DEPLOYMENT.md` | Comprehensive deployment guide with troubleshooting |
| `AZURE_QUICK_REF.md` | Quick command reference |
| `infra/README.md` | Infrastructure documentation |
| `.azure/README.md` | Azure config documentation |
| This file | Setup summary and next steps |

## ✅ Verification Checklist

After deployment, verify:

- [ ] All three resource groups created in Sweden Central
- [ ] AI Foundry Hub deployed successfully
- [ ] AI Foundry Project created under Hub
- [ ] Model Router deployment (2025-11-18) visible in OpenAI account
- [ ] AI Agent created in the project
- [ ] Azure AI Search service accessible
- [ ] Key Vault created with RBAC enabled
- [ ] Storage account created
- [ ] Application Insights configured
- [ ] Role assignments applied successfully
- [ ] `backend/.env` updated with endpoints
- [ ] API keys retrieved and added to `.env`
- [ ] Backend starts successfully
- [ ] Frontend starts successfully
- [ ] Application accessible at http://localhost:5173

## 🆘 Support

If you encounter issues:

1. **Check the detailed deployment guide**: `DEPLOYMENT.md`
2. **Review infrastructure docs**: `infra/README.md`
3. **Check Azure Portal**: Look for deployment errors
4. **Run with debug**: `azd provision --debug`
5. **Check provider registration**:
   ```bash
   az provider register --namespace Microsoft.MachineLearningServices
   az provider register --namespace Microsoft.CognitiveServices
   ```

## 🎉 You're Ready!

The Azure infrastructure is fully configured and ready to deploy. Simply run:

```bash
azd auth login
azd provision
```

All resources will be created in Sweden Central with the Model Router (2025-11-18) and AI Agent configured as requested!
