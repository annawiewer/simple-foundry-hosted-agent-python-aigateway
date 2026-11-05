# Gateway with existing models

Runnable fresh root for [ai-gateway](../../modules/ai-gateway/README.md), owning
one new group, gateway, monitoring, provider/catalog/aliases and optionally the
gateway's scoped backend grant. It **does not create, import, update or delete
the referenced model account/deployments**. When grant management is enabled,
it does create a role assignment on that external account.

Follow the [canonical offline/preparation route](../../docs/architecture.md#offline-and-deployment-preparation),
setting `$TerraformRoot = 'infra\terraform\examples\existing-models'`. Copy and
edit [`terraform.tfvars.example`](terraform.tfvars.example), including:

- Real `subscription_id` and qualified `location` (gateway and monitoring).
- Fresh `environment_name` (default `existing-models`) and isolated state.
- Non-null `backend = { account_id, endpoint, deployment_ids }`. The account
  must be in the same subscription; the endpoint must be HTTPS; IDs must match
  `<account_id>/deployments/<key>`.

By default this example uses the bundled [model profile](../../model-profile.json)
and its aliases: deployment keys `gpt-latest`, `gpt-6-sol`, `gpt-mini-latest`,
with corresponding compatible model versions, formats and endpoints.
For another profile, supply `model_deployments` metadata and compatible
`model_aliases` together. Null selects the bundled defaults for each map,
not per-deployment fallback aliases. Deployment metadata keys must exactly
match `backend.deployment_ids`. Descriptor validation checks IDs/keys, **not
live model compatibility or safety binding**.

`manage_backend_role_assignment = true` (default) lets Terraform own the
account-scoped grant. False requires an external owner to have granted access
to the actual new gateway identity before provider use; no pregrant bootstrap
or readiness/propagation check is supplied. Never give both owners the same
assignment. Registration alone does not establish inference authorization.

Outputs: `gateway_id`, `gateway_endpoint`, `gateway_monitoring`,
`model_alias_configuration`. No key value, agent resources, RemoteTool or
ToolServer is returned/created. See [evidence limits](../../docs/evidence-map.md).
