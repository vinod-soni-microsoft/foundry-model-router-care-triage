param projectName string
param agentName string
param modelDeploymentName string
param openAIEndpoint string
param description string = 'AI Agent for healthcare triage'

// AI Agent configuration (to be created manually or via SDK)
// The agent should be configured in Azure AI Foundry portal to use the Model Router deployment

output agentName string = agentName
output agentDescription string = description
output agentProjectName string = projectName
output agentModelDeployment string = modelDeploymentName
output agentStatus string = 'ready-to-configure'
