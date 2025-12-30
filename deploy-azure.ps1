#!/usr/bin/env pwsh
# Azure Deployment Script for Care Triage with Model Router

Write-Host "🏥 Care Triage - Azure Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check azd
if (!(Get-Command azd -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Azure Developer CLI (azd) not found" -ForegroundColor Red
    Write-Host "   Install: winget install microsoft.azd" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Azure Developer CLI (azd) found" -ForegroundColor Green

# Check az
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Azure CLI (az) not found" -ForegroundColor Red
    Write-Host "   Install: winget install microsoft.azurecli" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Azure CLI (az) found" -ForegroundColor Green

Write-Host ""
Write-Host "This script will:" -ForegroundColor Cyan
Write-Host "  1. Authenticate with Azure" -ForegroundColor White
Write-Host "  2. Set your principal ID for role assignments" -ForegroundColor White
Write-Host "  3. Configure environment settings" -ForegroundColor White
Write-Host "  4. Deploy all Azure resources to Sweden Central" -ForegroundColor White
Write-Host "  5. Update backend/.env with connection strings" -ForegroundColor White
Write-Host ""
Write-Host "Resources to be created:" -ForegroundColor Cyan
Write-Host "  • AI Foundry Hub & Project" -ForegroundColor White
Write-Host "  • Model Router (2025-11-18 version)" -ForegroundColor White
Write-Host "  • AI Agent (care-triage-agent)" -ForegroundColor White
Write-Host "  • Azure OpenAI Service" -ForegroundColor White
Write-Host "  • Azure AI Search" -ForegroundColor White
Write-Host "  • Key Vault" -ForegroundColor White
Write-Host "  • Storage Account" -ForegroundColor White
Write-Host "  • Application Insights" -ForegroundColor White
Write-Host ""
Write-Host "All resources will be deployed to Sweden Central region." -ForegroundColor Yellow
Write-Host ""

$continue = Read-Host "Continue with deployment? (y/N)"
if ($continue -ne 'y' -and $continue -ne 'Y') {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Authenticating with Azure..." -ForegroundColor Cyan

# Check if already logged in to azd
$azdLoginCheck = azd auth login --check-status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Logging in to Azure Developer CLI..." -ForegroundColor Yellow
    azd auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to login to azd" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Authenticated with azd" -ForegroundColor Green

# Check if already logged in to az
$azLoginCheck = az account show 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Logging in to Azure CLI..." -ForegroundColor Yellow
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to login to az" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Authenticated with Azure CLI" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Setting up environment..." -ForegroundColor Cyan

# Get principal ID
Write-Host "Retrieving your principal ID..." -ForegroundColor Yellow
$principalId = az ad signed-in-user show --query id -o tsv
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($principalId)) {
    Write-Host "❌ Failed to retrieve principal ID" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Principal ID: $principalId" -ForegroundColor Green

# Set environment variables
Write-Host "Configuring environment variables..." -ForegroundColor Yellow
azd env set AZURE_PRINCIPAL_ID $principalId
azd env set AZURE_LOCATION swedencentral

# Check if environment name is set
$envName = azd env get-value AZURE_ENV_NAME 2>&1
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($envName)) {
    $envName = "dev"
    azd env set AZURE_ENV_NAME $envName
    Write-Host "✅ Using environment name: $envName" -ForegroundColor Green
} else {
    Write-Host "✅ Environment name: $envName" -ForegroundColor Green
}

Write-Host "✅ Location: swedencentral" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Deploying Azure infrastructure..." -ForegroundColor Cyan
Write-Host "This will take approximately 10-15 minutes..." -ForegroundColor Yellow
Write-Host ""

azd provision

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "  1. Check Azure Portal for detailed error messages" -ForegroundColor White
    Write-Host "  2. Verify you have Contributor role on the subscription" -ForegroundColor White
    Write-Host "  3. Run 'azd provision --debug' for detailed logs" -ForegroundColor White
    Write-Host "  4. Check DEPLOYMENT.md for common issues" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host ""

# Display deployment information
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Information" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$foundryEndpoint = azd env get-value FOUNDRY_ENDPOINT 2>$null
$deploymentName = azd env get-value FOUNDRY_DEPLOYMENT_NAME 2>$null
$agentName = azd env get-value AI_AGENT_NAME 2>$null
$aiHubName = azd env get-value AI_HUB_NAME 2>$null
$aiProjectName = azd env get-value AI_PROJECT_NAME 2>$null
$aiRg = azd env get-value AI_RESOURCE_GROUP_NAME 2>$null
$dataRg = azd env get-value DATA_RESOURCE_GROUP_NAME 2>$null
$securityRg = azd env get-value SECURITY_RESOURCE_GROUP_NAME 2>$null

Write-Host "Resource Groups:" -ForegroundColor Yellow
Write-Host "  AI Resources:      $aiRg" -ForegroundColor White
Write-Host "  Data Resources:    $dataRg" -ForegroundColor White
Write-Host "  Security Resources: $securityRg" -ForegroundColor White
Write-Host ""

Write-Host "AI Foundry:" -ForegroundColor Yellow
Write-Host "  Hub:        $aiHubName" -ForegroundColor White
Write-Host "  Project:    $aiProjectName" -ForegroundColor White
Write-Host "  AI Agent:   $agentName" -ForegroundColor White
Write-Host ""

Write-Host "Model Router:" -ForegroundColor Yellow
Write-Host "  Endpoint:   $foundryEndpoint" -ForegroundColor White
Write-Host "  Deployment: $deploymentName" -ForegroundColor White
Write-Host "  Version:    2025-11-18" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Get your API keys:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   # OpenAI API Key:" -ForegroundColor White
Write-Host "   az cognitiveservices account keys list ``" -ForegroundColor Gray
Write-Host "     --name ${aiHubName}-openai ``" -ForegroundColor Gray
Write-Host "     --resource-group $aiRg ``" -ForegroundColor Gray
Write-Host "     --query key1 -o tsv" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Search API Key:" -ForegroundColor White
$searchName = azd env get-value AZURE_SEARCH_NAME 2>$null
Write-Host "   az search admin-key show ``" -ForegroundColor Gray
Write-Host "     --resource-group $dataRg ``" -ForegroundColor Gray
Write-Host "     --service-name $searchName ``" -ForegroundColor Gray
Write-Host "     --query primaryKey -o tsv" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Update backend/.env with the API keys" -ForegroundColor Yellow
Write-Host ""

Write-Host "3. Run the application:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   # Terminal 1 - Backend:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Terminal 2 - Frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Open browser:" -ForegroundColor White
Write-Host "   http://localhost:5173" -ForegroundColor Gray
Write-Host ""

Write-Host "4. View resources in Azure Portal:" -ForegroundColor Yellow
Write-Host "   https://portal.azure.com" -ForegroundColor Cyan
Write-Host ""

Write-Host "5. View AI Foundry Portal:" -ForegroundColor Yellow
Write-Host "   https://ai.azure.com" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "For detailed documentation, see:" -ForegroundColor White
Write-Host "  • DEPLOYMENT.md - Complete deployment guide" -ForegroundColor Gray
Write-Host "  • AZURE_QUICK_REF.md - Quick reference" -ForegroundColor Gray
Write-Host "  • AZURE_SETUP_SUMMARY.md - Setup summary" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🎉 Setup complete! Your Azure infrastructure is ready." -ForegroundColor Green
