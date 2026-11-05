mock_provider "azapi" {
  override_during = plan
  mock_resource "azapi_resource" {
    defaults = {
      id     = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/models/providers/Microsoft.CognitiveServices/accounts/models"
      output = { properties = { endpoint = "https://models.example.invalid/" } }
    }
  }
}
variables {
  subscription_id   = "00000000-0000-0000-0000-000000000001"
  resource_group_id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/models"
  name              = "models-fixture"
  location          = "eastus2"
  model_deployments = jsondecode(file("model-profile.json")).model_deployments
}
run "models_module" {
  command = plan
  module { source = "./modules/foundry-models" }
  assert {
    condition     = toset(keys(output.backend.deployment_ids)) == toset(keys(var.model_deployments)) && output.backend.endpoint == "https://models.example.invalid/"
    error_message = "Models module must publish stable logical deployment keys and selected endpoint."
  }
}
run "reject_fractional_capacity" {
  command = plan
  module { source = "./modules/foundry-models" }
  variables {
    model_deployments = { bad = { model_name = "synthetic", model_version = "1", capacity = 1.5, token_limit = 10 } }
  }
  expect_failures = [var.model_deployments]
}
run "reject_empty_model_profile" {
  command = plan
  module { source = "./modules/foundry-models" }
  variables { model_deployments = {} }
  expect_failures = [var.model_deployments]
}

run "models_gateway_safety_metadata" {
  command = plan
  module { source = "./modules/foundry-models" }
  variables {
    model_deployments = {
      for key, model in jsondecode(file("model-profile.json")).model_deployments :
      key => merge(model, { content_safety_severity = "Medium" })
    }
  }
  assert {
    condition = alltrue([for deployment in azapi_resource.model_deployment :
      deployment.body.properties.raiPolicyName == "Microsoft.DefaultV2" &&
      !can(deployment.body.properties.policies)
    ])
    error_message = "Gateway safety metadata must not change the backend filter or add gateway policies to Cognitive Services deployments."
  }
}

run "reject_invalid_model_safety" {
  command = plan
  module { source = "./modules/foundry-models" }
  variables {
    model_deployments = {
      for key, model in jsondecode(file("model-profile.json")).model_deployments :
      key => merge(model, { content_safety_severity = "medium" })
    }
  }
  expect_failures = [var.model_deployments]
}

run "reject_zero_request_limit" {
  command = plan
  module { source = "./modules/foundry-models" }
  variables {
    model_deployments = {
      for key, model in jsondecode(file("model-profile.json")).model_deployments :
      key => merge(model, { request_limit = 0 })
    }
  }
  expect_failures = [var.model_deployments]
}

run "reject_fractional_request_limit" {
  command = plan
  module { source = "./modules/foundry-models" }
  variables {
    model_deployments = {
      for key, model in jsondecode(file("model-profile.json")).model_deployments :
      key => merge(model, { request_limit = 1.5 })
    }
  }
  expect_failures = [var.model_deployments]
}
