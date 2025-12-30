# Azure Infrastructure for Care Triage

This directory contains the Infrastructure as Code (IaC) for deploying the Care Triage application to Azure using Bicep.

## Architecture

The infrastructure is organized into separate resource groups for logical isolation:

### Resource Groups

1. **AI Resource Group** (`rg-{env}-ai-{token}`)
   - AI Foundry Hub and Project
   - Azure OpenAI Service with Model Router deployment
   - AI Agent configuration
   - Monitoring (Log Analytics, Application Insights)

2. **Data Resource Group** (`rg-{env}-data-{token}`)
   - Azure AI Search
   - Storage Account

3. **Security Resource Group** (`rg-{env}-security-{token}`)
   - Azure Key Vault

## Deployment

### Prerequisites

1. **Azure CLI**: Install from https://docs.microsoft.com/cli/azure/install-azure-cli
2. **Azure Developer CLI (azd)**: Install from https://aka.ms/azd-install
3. **Azure Subscription**: With appropriate permissions to create resources

### Deploy with azd

```bash
# Login to Azure
azd auth login

# Initialize environment (first time only)
azd env new

# Set your Azure subscription (if you have multiple)
azd env set AZURE_SUBSCRIPTION_ID <your-subscription-id>

# Provision and deploy all resources
azd up
```

### Manual Deployment

If you prefer to deploy without azd:

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription <subscription-id>

# Get your user principal ID
$principalId = az ad signed-in-user show --query id -o tsv

# Deploy to subscription scope
az deployment sub create \
  --name care-triage-deployment \
  --location swedencentral \
  --template-file infra/main.bicep \
  --parameters infra/main.bicepparam \
  --parameters principalId=$principalId
```

## Model Router Configuration

The deployment creates a Model Router (version 2025-11-18) with default settings:
- **Deployment Name**: `model-router`
- **SKU**: GlobalStandard
- **Capacity**: 1
- **Version Upgrade**: Manual (NoAutoUpgrade)

## AI Agent Configuration

An AI Agent is automatically created in the AI Foundry project with:
- **Name**: `care-triage-agent`
- **Base Model**: Model Router deployment
- **Purpose**: Healthcare triage assistance

## Accessing Resources

After deployment, use these commands to get resource information:

```bash
# Get all environment variables
azd env get-values

# Get specific values
azd env get-value FOUNDRY_ENDPOINT
azd env get-value AI_PROJECT_NAME
```

## Resource Naming

Resources follow Azure naming best practices with abbreviated prefixes:
- `aih-*`: AI Hub
- `aip-*`: AI Project
- `srch-*`: AI Search
- `kv-*`: Key Vault
- `st*`: Storage Account
- `log-*`: Log Analytics
- `appi-*`: Application Insights

All resource names include a unique token based on subscription ID and environment name.

## Region

All resources are deployed to **Sweden Central** region as specified.

## Security

- **RBAC**: Role-Based Access Control is enabled on all resources
- **Key Vault**: Enabled with RBAC authorization, soft delete, and purge protection
- **Managed Identity**: System-assigned identities for AI Hub and Project
- **Network**: Public access enabled (configure private endpoints in production)

## Cost Management

Resources deployed in this configuration:
- AI Foundry Hub and Project (consumption-based)
- Azure OpenAI (S0 tier with Model Router)
- AI Search (Basic tier)
- Storage Account (Standard LRS)
- Key Vault (Standard)
- Log Analytics and Application Insights

Monitor costs in Azure Portal under Cost Management.

## Cleanup

To delete all resources:

```bash
azd down
```

Or manually delete the resource groups:

```bash
az group delete --name rg-{env}-ai-{token}
az group delete --name rg-{env}-data-{token}
az group delete --name rg-{env}-security-{token}
```

## Troubleshooting

### Deployment Failures

1. Check Azure region availability for AI Foundry resources
2. Verify subscription has sufficient quota for Azure OpenAI
3. Ensure principal ID has proper permissions

### Model Router Issues

1. Verify Model Router version (2025-11-18) is available in Sweden Central
2. Check deployment status in Azure Portal
3. Review OpenAI service logs

### AI Agent Configuration

The AI Agent is configured via deployment script. Check deployment script outputs in Azure Portal if agent creation fails.

## Updates

To update infrastructure:

```bash
# Update Bicep files
# Then re-run
azd up
```

The deployment is idempotent and will only update changed resources.
