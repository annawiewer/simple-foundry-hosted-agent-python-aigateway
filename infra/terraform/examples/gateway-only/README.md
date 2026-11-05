# Gateway only

Runnable fresh root for [ai-gateway](../../modules/ai-gateway/README.md) without
model or agent dependencies. Owns one new group, gateway/system identity,
runtime-key resource and monitoring/exporter. `backend` remains null: **no
provider, model catalog, aliases, backend grant or callable model is created**.

Follow the [canonical offline/preparation route](../../docs/architecture.md#offline-and-deployment-preparation),
setting `$TerraformRoot = 'infra\terraform\examples\gateway-only'`. Edit the
local copy of [`terraform.tfvars.example`](terraform.tfvars.example):
`subscription_id` and `location` are required; `environment_name` defaults to
`gateway-only`, and `tags` is optional. Gateway and monitoring use `location`.
Use an isolated state/backend key and fresh names, not the full root's state.

Outputs are `gateway_id`, `gateway_endpoint`, `gateway_monitoring` and an empty
`model_alias_configuration`. The key value is not returned. Gateway destruction
is deliberately guarded.

This is not a running digest agent or proof of model/telemetry runtime. See
[historical evidence limits](../../docs/evidence-map.md).
