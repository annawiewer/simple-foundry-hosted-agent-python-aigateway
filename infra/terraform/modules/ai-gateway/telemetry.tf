resource "azapi_resource" "telemetry_exporter" {
  # This preview type is not yet present in AzAPI's bundled schema.
  schema_validation_enabled = false
  type                      = "${local.gateway_type}/workspaces/telemetryExporters@${local.gateway_telemetry_api_version}"
  name                      = "appinsights"
  parent_id                 = local.gateway_workspace_id
  body = {

    properties = {
      kind           = "ApplicationInsights"
      payloadCapture = false
      applicationInsights = {
        connectionString = try(azapi_resource.insights.output.properties.ConnectionString, null)
        resourceId       = azapi_resource.insights.id
      }
    }
  }
  lifecycle {
    precondition {
      condition     = try(length(trimspace(azapi_resource.insights.output.properties.ConnectionString)) > 0, false)
      error_message = "The ApplicationInsights exporter requires the returned gateway Insights ConnectionString; incomplete exporters are rejected."
    }
  }
  depends_on = [azapi_resource.role_assignment]
}
