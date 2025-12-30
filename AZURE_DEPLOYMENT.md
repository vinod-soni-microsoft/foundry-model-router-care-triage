# Azure Deployment Guide

## Quick Start with Azure Developer CLI (azd)

The fastest way to deploy this application to Azure is using the Azure Developer CLI.

### Prerequisites

1. [Azure Developer CLI (azd)](https://aka.ms/azd-install)
2. [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
3. An Azure subscription
4. Azure account with permissions to create resources

### Step-by-Step Deployment

#### 1. Install Azure Developer CLI

**Windows (PowerShell):**
```powershell
winget install microsoft.azd
```

**macOS/Linux:**
```bash
curl -fsSL https://aka.ms/install-azd.sh | bash
```

#### 2. Login to Azure

```bash
azd auth login
```

This will open a browser window for authentication.

#### 3. Initialize Your Environment

```bash
azd env new
```

When prompted, provide:
- **Environment name**: e.g., `care-triage-dev` (lowercase, alphanumeric with hyphens)

The environment name helps organize your resources and allows multiple deployments.

#### 4. (Optional) Set Azure Subscription

If you have multiple subscriptions:

```bash
# List your subscriptions
az account list --output table

# Set the desired subscription
azd env set AZURE_SUBSCRIPTION_ID <your-subscription-id>
```

#### 5. Deploy Everything with One Command

```bash
azd up
```

This single command will:
- ✅ Provision all Azure resources in Sweden Central
- ✅ Create separate resource groups for AI, Data, and Security resources
- ✅ Deploy Azure AI Foundry Hub and Project
- ✅ Deploy Model Router (2025-11-18 version)
- ✅ Create AI Agent configured with Model Router
- ✅ Set up Azure OpenAI, AI Search, Key Vault, and Storage
- ✅ Configure monitoring and logging
- ✅ Update your local `.env` file with connection details

**Deployment time**: Approximately 10-15 minutes

#### 6. Review Deployment Output

After successful deployment, you'll see:

```
Azure resources deployed successfully!

Resource Groups:
  AI Resources: rg-care-triage-ai-abc123
  Data Resources: rg-care-triage-data-abc123
  Security Resources: rg-care-triage-security-abc123

AI Foundry:
  Hub: aih-abc123
  Project: aip-abc123
  Agent: care-triage-agent

Model Router:
  Endpoint: https://...
  Deployment: model-router
```

#### 7. Get Azure Resource Keys

You'll need to manually retrieve and add API keys to your `.env` file:

```bash
# Get Azure OpenAI API key
az cognitiveservices account keys list \
  --name <openai-account-name> \
  --resource-group <ai-resource-group-name> \
  --query key1 -o tsv

# Get Azure AI Search admin key
az search admin-key show \
  --service-name <search-service-name> \
  --resource-group <data-resource-group-name> \
  --query primaryKey -o tsv
```

Update `backend/.env`:
```env
AZURE_OPENAI_API_KEY=<your-openai-key>
SEARCH_KEY=<your-search-key>
FOUNDRY_API_KEY=<your-openai-key>  # Same as AZURE_OPENAI_API_KEY
```

#### 8. Run the Application Locally

```bash
# Start backend
cd backend
python app.py

# In a new terminal, start frontend
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

## View Azure Resources

### Azure Portal

Visit [Azure Portal](https://portal.azure.com) and navigate to your resource groups:
- `rg-<env>-ai-*` - AI Foundry, OpenAI, Monitoring
- `rg-<env>-data-*` - AI Search, Storage
- `rg-<env>-security-*` - Key Vault

### AI Foundry Portal

Visit [Azure AI Foundry](https://ai.azure.com) to:
- View your AI Project and Hub
- Test the Model Router deployment
- Configure the AI Agent
- Monitor usage and performance

## Check Environment Configuration

```bash
# View all environment variables
azd env get-values

# View specific variable
azd env get-value FOUNDRY_ENDPOINT
azd env get-value AI_PROJECT_NAME
```

## Update Deployment

To update infrastructure or redeploy:

```bash
# Re-provision and deploy
azd up

# Or provision only (no deployment)
azd provision

# Deploy only (no infrastructure changes)
azd deploy
```

## Cleanup Resources

To delete all Azure resources:

```bash
azd down
```

This will:
- Delete all resource groups
- Remove all Azure resources
- Preserve your local environment configuration

To also delete the environment configuration:

```bash
azd down --purge
```

## Troubleshooting

### Model Router Not Available

If Model Router version 2025-11-18 is not available:
1. Check Azure OpenAI service in Azure Portal
2. Try a different region or version
3. Update `modelRouterVersion` parameter in `infra/main.bicepparam`

### Deployment Fails

```bash
# Check deployment logs
azd deploy --debug

# Validate Bicep templates
az bicep build --file infra/main.bicep

# Check Azure activity log
az monitor activity-log list --resource-group <rg-name>
```

### Permission Errors

Ensure your Azure account has:
- Contributor role on the subscription
- Ability to create role assignments
- Ability to create service principals

### Region Capacity Issues

If Sweden Central has capacity issues:
1. Edit `infra/main.bicep`
2. Add more regions to the `@allowed` list
3. Update `location` parameter in `infra/main.bicepparam`
4. Redeploy with `azd up`

## Cost Estimation

Approximate monthly costs (Sweden Central, as of Dec 2024):
- **AI Foundry Hub/Project**: Consumption-based (~$0-50/month for development)
- **Azure OpenAI with Model Router**: ~$100-500/month (depends on usage)
- **AI Search (Basic)**: ~$75/month
- **Storage Account**: ~$5-20/month
- **Key Vault**: ~$5/month
- **Monitoring**: ~$10-30/month

**Total estimated**: ~$195-680/month

Use Azure Cost Management to track actual costs.

## Advanced Configuration

### Custom Environment Variables

```bash
# Set custom environment variable
azd env set CUSTOM_VARIABLE value

# Use in Bicep by adding to main.bicepparam
param customVariable = readEnvironmentVariable('CUSTOM_VARIABLE', 'default-value')
```

### Multiple Environments

Create separate environments for dev, staging, production:

```bash
# Create new environment
azd env new care-triage-prod

# Switch between environments
azd env select care-triage-dev
azd env select care-triage-prod
```

### CI/CD Integration

For automated deployments, see `.github/workflows/` for GitHub Actions examples.

## Support

- **Azure Developer CLI**: https://aka.ms/azd
- **Azure AI Foundry**: https://learn.microsoft.com/azure/ai-studio/
- **Azure OpenAI**: https://learn.microsoft.com/azure/cognitive-services/openai/
- **Bicep**: https://learn.microsoft.com/azure/azure-resource-manager/bicep/

## Next Steps

1. ✅ Configure authentication and authorization
2. ✅ Set up CI/CD pipelines
3. ✅ Configure private endpoints for production
4. ✅ Enable diagnostic logging
5. ✅ Set up alerts and monitoring
6. ✅ Review security best practices
7. ✅ Load medical knowledge base into AI Search
8. ✅ Test Model Router with various scenarios
9. ✅ Configure AI Agent instructions and behavior
10. ✅ Set up backup and disaster recovery
