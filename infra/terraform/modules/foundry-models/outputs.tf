output "account_id" { value = azapi_resource.models.id }
output "endpoint" { value = azapi_resource.models.output.properties.endpoint }
output "deployment_ids" { value = { for key, deployment in azapi_resource.model_deployment : key => deployment.id } }
output "backend" {
  description = "Typed nonsecret backend descriptor; logical deployment keys remain known during planning."
  value = {
    account_id     = azapi_resource.models.id
    endpoint       = azapi_resource.models.output.properties.endpoint
    deployment_ids = { for key, deployment in azapi_resource.model_deployment : key => deployment.id }
  }
}
