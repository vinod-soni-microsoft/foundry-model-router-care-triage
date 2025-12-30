using './main.bicep'

param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'care-triage')
param location = readEnvironmentVariable('AZURE_LOCATION', 'swedencentral')
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')
param modelRouterVersion = '2025-11-18'
