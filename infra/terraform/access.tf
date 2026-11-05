locals {
  foundry_gateway_callers = var.enable_foundry_gateway_model_access ? {
    account = module.foundry_agents.account_principal_id
    project = module.foundry_agents.project_principal_id
  } : {}
  foundry_gateway_tool_callers = var.enable_foundry_gateway_tool_access ? {
    project = module.foundry_agents.project_principal_id
  } : {}
  gateway_models_user_role_id = "a6b68e3d-a1f0-4c60-8678-237c050cf4ea"
  gateway_tools_user_role_id  = "dce03f8d-857f-4e40-a90d-67770fa6ecd2"
}

resource "azapi_resource" "foundry_gateway_tool_access" {
  for_each  = local.foundry_gateway_tool_callers
  type      = "Microsoft.Authorization/roleAssignments@2022-04-01"
  name      = uuidv5("url", "${module.ai_gateway.gateway_id}/${each.value}/${local.gateway_tools_user_role_id}")
  parent_id = module.ai_gateway.gateway_id
  body = {
    properties = {
      principalId      = each.value
      principalType    = "ServicePrincipal"
      roleDefinitionId = "/subscriptions/${var.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/${local.gateway_tools_user_role_id}"
    }
  }
}

resource "azapi_resource" "foundry_gateway_model_access" {
  for_each  = local.foundry_gateway_callers
  type      = "Microsoft.Authorization/roleAssignments@2022-04-01"
  name      = uuidv5("url", "${module.ai_gateway.gateway_id}/${each.value}/${local.gateway_models_user_role_id}")
  parent_id = module.ai_gateway.gateway_id
  body = {
    properties = {
      principalId      = each.value
      principalType    = "ServicePrincipal"
      roleDefinitionId = "/subscriptions/${var.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/${local.gateway_models_user_role_id}"
    }
  }
  lifecycle {
    precondition {
      condition = !contains(
        [for caller in values(var.gateway_access_principals) : lower(caller.principal_id)],
        lower(each.value)
      )
      error_message = "Use either enable_foundry_gateway_model_access or gateway_access_principals for the same Foundry identity, not both owners."
    }
  }
}
