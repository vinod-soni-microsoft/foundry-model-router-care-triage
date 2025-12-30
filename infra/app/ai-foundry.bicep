param location string
param tags object
param hubName string
param projectName string
param keyVaultId string
param storageAccountId string
param applicationInsightsId string
param modelRouterVersion string
param principalId string

// Azure OpenAI account for the hub
resource openAIAccount 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${hubName}-openai'
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: '${hubName}-openai'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

// AI Foundry Hub
resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: hubName
  location: location
  tags: tags
  kind: 'Hub'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: hubName
    storageAccount: storageAccountId
    keyVault: keyVaultId
    applicationInsights: applicationInsightsId
    publicNetworkAccess: 'Enabled'
    v1LegacyMode: false
    managedNetwork: {
      isolationMode: 'Disabled'
    }
  }
}

// AI Hub connection to OpenAI using managed identity
resource openAIConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-10-01' = {
  parent: aiHub
  name: 'openai-connection'
  properties: {
    category: 'AzureOpenAI'
    authType: 'AAD'
    isSharedToAll: true
    target: openAIAccount.properties.endpoint
    metadata: {
      ApiVersion: '2024-08-01-preview'
      ApiType: 'azure'
      ResourceId: openAIAccount.id
    }
  }
}

// AI Foundry Project
resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: projectName
  location: location
  tags: tags
  kind: 'Project'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: projectName
    hubResourceId: aiHub.id
    publicNetworkAccess: 'Enabled'
  }
}

// Model Router Deployment
resource modelRouterDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: openAIAccount
  name: 'model-router'
  sku: {
    name: 'GlobalStandard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'model-router'
      version: modelRouterVersion
    }
    versionUpgradeOption: 'NoAutoUpgrade'
  }
}

// AI Agent will be configured manually in Azure AI Foundry portal
// Using the Model Router deployment created above

// Role assignments will be created post-deployment to avoid conflicts
// Use: az role assignment create --assignee <principalId> --role "Azure AI Developer" --scope <hubId>
// Use: az role assignment create --assignee <principalId> --role "Cognitive Services User" --scope <openAIId>

output hubName string = aiHub.name
output hubId string = aiHub.id
output hubPrincipalId string = aiHub.identity.principalId
output projectName string = aiProject.name
output projectId string = aiProject.id
output foundryEndpoint string = aiProject.properties.discoveryUrl
output openAIEndpoint string = openAIAccount.properties.endpoint
output modelRouterDeploymentName string = modelRouterDeployment.name
output agentName string = 'care-triage-agent'
