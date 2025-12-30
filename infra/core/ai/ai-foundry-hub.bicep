# AI Foundry Hub with Model Router
resource "azurerm_machine_learning_workspace" "ai_hub" {
  name                = var.hub_name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "Hub"
  
  identity {
    type = "SystemAssigned"
  }
  
  storage_account_id      = var.storage_account_id
  key_vault_id            = var.key_vault_id
  application_insights_id = var.application_insights_id
  
  public_network_access_enabled = true
  
  tags = var.tags
}

# AI Project under the Hub
resource "azurerm_machine_learning_workspace" "ai_project" {
  name                = var.project_name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "Project"
  
  identity {
    type = "SystemAssigned"
  }
  
  workspace_id = azurerm_machine_learning_workspace.ai_hub.id
  
  public_network_access_enabled = true
  
  tags = var.tags
}

# Azure OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  name                = "${var.hub_name}-openai"
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "OpenAI"
  sku_name            = "S0"
  
  custom_subdomain_name = "${var.hub_name}-openai"
  
  public_network_access_enabled = true
  
  tags = var.tags
}

# Model Router Deployment
resource "azurerm_cognitive_deployment" "model_router" {
  name               = "model-router"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  
  model {
    format  = "OpenAI"
    name    = "model-router"
    version = var.model_router_version
  }
  
  sku {
    name     = "GlobalStandard"
    capacity = 1
  }
  
  version_upgrade_option = "NoAutoUpgrade"
}

output "hub_id" {
  value = azurerm_machine_learning_workspace.ai_hub.id
}

output "project_id" {
  value = azurerm_machine_learning_workspace.ai_project.id
}

output "project_endpoint" {
  value = azurerm_machine_learning_workspace.ai_project.workspace_url
}

output "openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}

output "model_router_deployment_name" {
  value = azurerm_cognitive_deployment.model_router.name
}
