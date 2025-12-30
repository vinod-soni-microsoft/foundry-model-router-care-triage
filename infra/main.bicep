targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment used to generate a short unique hash for resources')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
@allowed([
  'swedencentral'
])
param location string = 'swedencentral'

@description('Model Router version to deploy')
param modelRouterVersion string = '2025-11-18'

@description('Principal ID of the user executing the deployment')
param principalId string = ''

// Tags that should be applied to all resources
var tags = {
  'azd-env-name': environmentName
  'environment': environmentName
  'managed-by': 'azd'
}

// Generate abbreviations for resource naming
var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

// Resource Group names
var aiResourceGroupName = '${abbrs.resourceGroup}-${environmentName}-ai-${resourceToken}'
var dataResourceGroupName = '${abbrs.resourceGroup}-${environmentName}-data-${resourceToken}'
var securityResourceGroupName = '${abbrs.resourceGroup}-${environmentName}-security-${resourceToken}'

// Create Resource Groups
resource aiResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: aiResourceGroupName
  location: location
  tags: tags
}

resource dataResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: dataResourceGroupName
  location: location
  tags: tags
}

resource securityResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: securityResourceGroupName
  location: location
  tags: tags
}

// Deploy monitoring resources
module monitoring './core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: aiResourceGroup
  params: {
    location: location
    tags: tags
    logAnalyticsName: '${abbrs.logAnalyticsWorkspace}${resourceToken}'
    applicationInsightsName: '${abbrs.applicationInsights}${resourceToken}'
  }
}

// Deploy Key Vault
module keyVault './core/security/keyvault.bicep' = {
  name: 'keyvault'
  scope: securityResourceGroup
  params: {
    location: location
    tags: tags
    name: '${abbrs.keyVault}${resourceToken}'
    principalId: principalId
  }
}

// Deploy Storage Account
module storage './core/storage/storage-account.bicep' = {
  name: 'storage'
  scope: dataResourceGroup
  params: {
    location: location
    tags: tags
    name: '${abbrs.storageAccount}${resourceToken}'
  }
}

// Deploy AI Search
module search './core/search/search-services.bicep' = {
  name: 'search'
  scope: dataResourceGroup
  params: {
    location: location
    tags: tags
    name: '${abbrs.aiSearch}${resourceToken}'
  }
}

// Deploy AI Foundry Hub and Project with Model Router
module aiFoundry './app/ai-foundry.bicep' = {
  name: 'ai-foundry'
  scope: aiResourceGroup
  params: {
    location: location
    tags: tags
    hubName: '${abbrs.aiHub}${resourceToken}'
    projectName: '${abbrs.aiProject}${resourceToken}'
    keyVaultId: keyVault.outputs.id
    storageAccountId: storage.outputs.id
    applicationInsightsId: monitoring.outputs.applicationInsightsId
    modelRouterVersion: modelRouterVersion
    principalId: principalId
  }
}

// Grant AI Hub managed identity access to storage
// Role assignment created on first deploy - commented to avoid conflicts on retry
// module storageRoleAssignment './core/storage/storage-role-assignment.bicep' = {
//   name: 'storage-role-assignment'
//   scope: dataResourceGroup
//   params: {
//     storageAccountName: storage.outputs.name
//     principalId: aiFoundry.outputs.hubPrincipalId
//     principalType: 'ServicePrincipal'
//   }
// }

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_SUBSCRIPTION_ID string = subscription().subscriptionId

output AI_RESOURCE_GROUP_NAME string = aiResourceGroup.name
output DATA_RESOURCE_GROUP_NAME string = dataResourceGroup.name
output SECURITY_RESOURCE_GROUP_NAME string = securityResourceGroup.name

output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.endpoint

output AZURE_STORAGE_ACCOUNT_NAME string = storage.outputs.name
output AZURE_STORAGE_ACCOUNT_ID string = storage.outputs.id

output AZURE_SEARCH_ENDPOINT string = search.outputs.endpoint
output AZURE_SEARCH_NAME string = search.outputs.name

output AI_HUB_NAME string = aiFoundry.outputs.hubName
output AI_HUB_ID string = aiFoundry.outputs.hubId
output AI_PROJECT_NAME string = aiFoundry.outputs.projectName
output AI_PROJECT_ID string = aiFoundry.outputs.projectId

output FOUNDRY_ENDPOINT string = aiFoundry.outputs.foundryEndpoint
output FOUNDRY_DEPLOYMENT_NAME string = aiFoundry.outputs.modelRouterDeploymentName
output AZURE_OPENAI_ENDPOINT string = aiFoundry.outputs.openAIEndpoint

output AI_AGENT_NAME string = aiFoundry.outputs.agentName
