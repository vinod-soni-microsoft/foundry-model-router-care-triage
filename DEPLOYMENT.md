# Deploying Care Triage to Azure with Model Router

This guide explains how to deploy the Care Triage application to Azure using Azure Developer CLI (azd), including the Model Router (2025-11-18 version) and AI Agent in Azure AI Foundry.

## Prerequisites

1. **Azure Subscription** - You need an active Azure subscription
2. **Azure Developer CLI (azd)** - [Install azd](https://aka.ms/azd-install)
3. **Azure CLI** - [Install Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
4. **Node.js 20+** - For frontend development
5. **Python 3.11+** - For backend development

## Architecture Overview

The deployment creates the following Azure resources across three dedicated resource groups:

### AI Resources Resource Group (`rg-<env>-ai-<token>`)
- **AI Foundry Hub** - Central hub for AI resources
- **AI Foundry Project** - Project workspace with Model Router
- **Azure OpenAI Service** - With Model Router deployment (2025-11-18)
- **AI Agent** - Configured to use Model Router as base model
- **Application Insights** - For monitoring and telemetry

### Data Resources Resource Group (`rg-<env>-data-<token>`)
- **Azure AI Search** - For RAG (Retrieval Augmented Generation) functionality
- **Storage Account** - For data storage

### Security Resources Resource Group (`rg-<env>-security-<token>`)
- **Azure Key Vault** - For secrets management

## Deployment Steps

### 1. Authenticate with Azure

```bash
# Login to Azure
azd auth login

# Set your subscription (if you have multiple)
az account set --subscription "<your-subscription-id>"
```

### 2. Initialize the Environment

```bash
# Navigate to the project directory
cd c:\foundry-model-router-care-triage

# Initialize azd (first time only)
azd init

# When prompted:
# - Environment name: dev (or your preferred name)
# - Location: swedencentral (default, required)
```

### 3. Set Environment Variables

```bash
# Set your Azure principal ID for role assignments
azd env set AZURE_PRINCIPAL_ID $(az ad signed-in-user show --query id -o tsv)

# Optionally, set a custom environment name
azd env set AZURE_ENV_NAME dev

# Verify the location is set to swedencentral
azd env set AZURE_LOCATION swedencentral
```

### 4. Deploy Infrastructure and Application

```bash
# Provision all Azure resources
azd provision

# This will:
# 1. Create three resource groups in Sweden Central
# 2. Deploy AI Foundry Hub and Project
# 3. Deploy Model Router (2025-11-18 version)
# 4. Create AI Agent configured with Model Router
# 5. Deploy supporting resources (Key Vault, Storage, Search, etc.)
# 6. Configure role assignments
# 7. Update backend/.env with connection strings
```

### 5. Verify Deployment

After successful deployment, azd will display:

```
Resource Groups:
  AI Resources: rg-dev-ai-xxxxx
  Data Resources: rg-dev-data-xxxxx
  Security Resources: rg-dev-security-xxxxx

AI Foundry:
  Hub: aihub-xxxxx
  Project: aiproj-xxxxx
  Agent: care-triage-agent

Model Router:
  Endpoint: https://....inference.ai.azure.com
  Deployment: model-router
```

### 6. Configure API Keys (if needed)

Check the updated `backend/.env` file:

```bash
cat backend/.env
```

The postprovision hook automatically updates:
- `FOUNDRY_ENDPOINT`
- `FOUNDRY_DEPLOYMENT_NAME`
- `AZURE_OPENAI_ENDPOINT`
- `SEARCH_ENDPOINT`

You may need to manually add API keys:

```bash
# Get the Azure OpenAI key
az cognitiveservices account keys list \
  --name <openai-account-name> \
  --resource-group <ai-resource-group-name> \
  --query key1 -o tsv

# Get the Search key
az search admin-key show \
  --resource-group <data-resource-group-name> \
  --service-name <search-service-name> \
  --query primaryKey -o tsv
```

Update `backend/.env`:
```env
AZURE_OPENAI_API_KEY=<your-key>
FOUNDRY_API_KEY=<your-key>
SEARCH_KEY=<your-key>
```

### 7. Run the Application Locally

```bash
# Terminal 1: Start backend
cd backend
.\venv\Scripts\Activate.ps1
python app.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Visit http://localhost:5173

## Azure Resource Details

### Model Router Configuration

The Model Router deployment uses:
- **Version**: 2025-11-18 (as specified)
- **SKU**: GlobalStandard with capacity 1
- **Upgrade Option**: NoAutoUpgrade (manual control)
- **Format**: OpenAI

### AI Agent Configuration

The AI Agent is created in the AI Foundry Project with:
- **Name**: care-triage-agent
- **Base Model**: Model Router deployment
- **Description**: Care Triage AI Agent using Model Router
- **Integration**: Connected to the project's Model Router endpoint

### Role Assignments

The deployment automatically assigns:
- **Azure AI Developer** role on the AI Hub (for you)
- **Cognitive Services User** role on Azure OpenAI (for you)
- System-assigned managed identities for services

## Managing the Deployment

### View All Resources

```bash
# Show all environment values
azd env get-values

# List resources in a resource group
az resource list --resource-group <resource-group-name> -o table
```

### Access AI Foundry Portal

```bash
# Get the AI Foundry project URL
azd env get-values | findstr FOUNDRY_ENDPOINT
```

Visit [Azure AI Foundry](https://ai.azure.com) to:
- View your AI Hub and Project
- Manage the AI Agent
- Monitor Model Router usage
- Configure additional deployments

### Monitor Usage

```bash
# View Application Insights metrics
az monitor app-insights metrics show \
  --app <app-insights-name> \
  --resource-group <ai-resource-group-name> \
  --metrics requests/count

# Check Model Router deployment status
az cognitiveservices account deployment list \
  --name <openai-account-name> \
  --resource-group <ai-resource-group-name>
```

### Update Infrastructure

If you need to modify the infrastructure:

```bash
# Edit infra/main.bicep or infra/app/ai-foundry.bicep

# Re-provision (incremental update)
azd provision
```

### Tear Down Resources

```bash
# Delete all Azure resources
azd down

# This will:
# 1. Delete all three resource groups
# 2. Remove all resources (cannot be undone)
# 3. Keep the local environment configuration
```

To completely remove everything including local config:

```bash
azd down --purge
```

## Cost Management

Estimated monthly costs for the deployed resources:

- **AI Foundry Hub & Project**: ~$0 (management plane)
- **Model Router (GlobalStandard)**: Pay-per-token pricing
- **Azure OpenAI S0**: ~$0 base + usage
- **AI Search Basic**: ~$75/month
- **Storage Account LRS**: ~$20/month
- **Key Vault**: ~$0.03/10k operations
- **Application Insights**: ~$2.30/GB

**Total**: ~$95/month + AI usage costs

To minimize costs:
- Use `azd down` when not using the resources
- Monitor usage in Azure Cost Management
- Consider scaling down AI Search to Free tier for development

## Troubleshooting

### Deployment Fails

```bash
# Check detailed logs
azd provision --debug

# Verify subscription has required providers
az provider list --query "[?registrationState=='NotRegistered']" -o table

# Register missing providers
az provider register --namespace Microsoft.MachineLearningServices
az provider register --namespace Microsoft.CognitiveServices
az provider register --namespace Microsoft.Search
```

### Model Router Not Available

If Model Router 2025-11-18 is not available in Sweden Central:

1. Check available models:
```bash
az cognitiveservices account list-models \
  --name <openai-account-name> \
  --resource-group <resource-group-name>
```

2. Update `infra/main.bicep`:
```bicep
param modelRouterVersion string = 'latest-available-version'
```

3. Re-provision:
```bash
azd provision
```

### Role Assignment Issues

If you don't have permissions to assign roles:

1. Ask your subscription administrator to run:
```bash
az role assignment create \
  --assignee <your-principal-id> \
  --role "User Access Administrator" \
  --scope /subscriptions/<subscription-id>
```

2. Or manually assign roles after deployment

### Backend Connection Issues

If the backend can't connect to Azure services:

1. Verify environment variables:
```bash
azd env get-values
```

2. Check network connectivity:
```bash
curl https://<your-openai-account>.openai.azure.com
```

3. Verify role assignments in Azure Portal

## Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Model Router Documentation](https://learn.microsoft.com/azure/ai-services/openai/how-to/model-router)
- [Azure Developer CLI (azd) Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)

## Support

For issues related to:
- **Infrastructure**: Check Bicep files in `infra/` directory
- **Azure services**: Review Azure Portal and service-specific logs
- **Application**: See main README.md and application logs
