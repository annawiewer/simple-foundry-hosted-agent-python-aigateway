mock_provider "azapi" {
  override_during = plan
  mock_resource "azapi_resource" {
    defaults = {
      id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/agents/providers/Microsoft.Insights/components/monitoring"
      output = {
        properties = {
          ConnectionString = "synthetic-only-not-a-credential"
          primaryEndpoints = { blob = "https://storage.example.invalid/" }
          loginServer      = "registry.example.invalid"
        }
      }
    }
  }
}
override_resource {
  target          = azapi_resource.agents
  override_during = plan
  values          = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/agents/providers/Microsoft.CognitiveServices/accounts/agents" }
}
override_resource {
  target          = azapi_resource.project
  override_during = plan
  values          = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/agents/providers/Microsoft.CognitiveServices/accounts/agents/projects/project" }
}
override_resource {
  target          = azapi_resource.storage
  override_during = plan
  values = {
    id     = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/agents/providers/Microsoft.Storage/storageAccounts/storage"
    output = { properties = { primaryEndpoints = { blob = "https://storage.example.invalid/" } } }
  }
}
override_resource {
  target          = azapi_resource.registry
  override_during = plan
  values = {
    id     = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/agents/providers/Microsoft.ContainerRegistry/registries/registry"
    output = { properties = { loginServer = "registry.example.invalid" } }
  }
}
variables {
  subscription_id   = "00000000-0000-0000-0000-000000000001"
  resource_group_id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/agents"
  name              = "agents-fixture"
  location          = "eastus2"
  names             = { project = "project-fixture", storage = "storagefixture", registry = "registryfixture" }
}
run "agents_module" {
  command = plan
  module { source = "./modules/foundry-agents" }
  assert {
    condition     = output.project_endpoint == "https://agents-fixture.services.ai.azure.com/api/projects/project-fixture" && output.container_registry_endpoint == "registry.example.invalid"
    error_message = "Agent support must publish its project and registry handoff without claiming a deployed application."
  }
  assert {
    condition     = azapi_resource.project_insights_connection.body.properties.authType == "ApiKey" && length(azapi_resource.role_assignment) == 5 && output.monitoring_connection_id == null
    error_message = "Monitoring integration must remain absent from the retained default support graph."
  }
}

run "agents_monitoring_integration" {
  command = plan
  module { source = "./modules/foundry-agents" }
  variables { enable_monitoring_integration = true }
  assert {
    condition = (
      length(azapi_resource.role_assignment) == 7 &&
      azapi_resource.project_insights_connection.parent_id == azapi_resource.project.id &&
      azapi_resource.project_insights_connection.body.properties.authType == "ProjectManagedIdentity" &&
      !contains(keys(azapi_resource.project_insights_connection.body.properties), "credentials") &&
      output.monitoring_connection_id == azapi_resource.project_insights_connection.id &&
      azapi_resource.role_assignment["monitoring-account"].body.properties.principalId == azapi_resource.agents.identity[0].principal_id &&
      azapi_resource.role_assignment["monitoring-project"].body.properties.principalId == azapi_resource.project.identity[0].principal_id &&
      alltrue([for key in ["monitoring-account", "monitoring-project"] :
        azapi_resource.role_assignment[key].parent_id == azapi_resource.insights.id &&
        azapi_resource.role_assignment[key].body.properties.roleDefinitionId == "/subscriptions/00000000-0000-0000-0000-000000000001/providers/Microsoft.Authorization/roleDefinitions/3913510d-42f4-4e42-8a64-420c390055eb"
      ])
    )
    error_message = "Monitoring opt-in must change only the existing connection body and add two exact Insights grants, without a second Terraform connection owner."
  }
}
run "agents_disabled_backend_network" {
  command = plan
  module { source = "./modules/foundry-agents" }
  variables {
    public_network_access            = "Disabled"
    monitoring_public_network_access = "Disabled"
  }
  assert {
    condition = (
      azapi_resource.agents.body.properties.networkAcls.defaultAction == "Deny" &&
      azapi_resource.storage.body.properties.networkAcls.defaultAction == "Deny" &&
      azapi_resource.storage.body.properties.networkAcls.bypass == "AzureServices" &&
      azapi_resource.registry.body.properties.publicNetworkAccess == "Disabled" &&
      azapi_resource.logs.body.properties.publicNetworkAccessForIngestion == "Disabled" &&
      azapi_resource.insights.body.properties.publicNetworkAccessForQuery == "Disabled"
    )
    error_message = "Explicit backend disablement must cover owned support and monitoring without inventing private connectivity."
  }
}

run "agents_storage_enabled_override" {
  command = plan
  module { source = "./modules/foundry-agents" }
  variables {
    public_network_access         = "Disabled"
    storage_public_network_access = "Enabled"
  }
  assert {
    condition = (
      azapi_resource.storage.body.properties.publicNetworkAccess == "Enabled" &&
      azapi_resource.storage.body.properties.networkAcls.defaultAction == "Allow" &&
      !can(azapi_resource.storage.body.properties.networkAcls.resourceAccessRules) &&
      azapi_resource.agents.body.properties.publicNetworkAccess == "Disabled" &&
      azapi_resource.agents.body.properties.networkAcls.defaultAction == "Deny" &&
      azapi_resource.registry.body.properties.publicNetworkAccess == "Disabled" &&
      !can(azapi_resource.logs.body.properties.publicNetworkAccessForIngestion) &&
      !can(azapi_resource.insights.body.properties.publicNetworkAccessForQuery)
    )
    error_message = "An explicit Storage override must take precedence over the shared backend switch without changing unrelated support/monitoring."
  }
}

run "reject_storage_network_enum" {
  command = plan
  module { source = "./modules/foundry-agents" }
  variables { storage_public_network_access = "Private" }
  expect_failures = [var.storage_public_network_access]
}
