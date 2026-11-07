# foundry-models

Creates a dedicated Foundry model-serving account and deployments. It does not
create a project, gateway, provider/catalog routes or hosted agent.

Required inputs: `subscription_id`, `resource_group_id`, `name`, `location` and
`model_deployments`. The caller owns the group and provider configuration.
Optional inputs: `tags`, `public_network_access` (default `Enabled`) and explicit
developer principal ID/type.

Deployment map keys are stable deployment names. The full shared metadata type
is in [`variables.tf`](variables.tf): required model name/version, capacity and
token limit, with optional model format/SKU/API endpoints/description and policy
metadata. Gateway policy fields travel alongside deployment metadata; this
module does **not** enforce gateway token/cost/request limits or content safety.
It accepts optional `content_safety_severity` (`Low`, `Medium`, `High` or null)
for composition with [ai-gateway](../ai-gateway/README.md); accepting metadata
does not create a gateway policy here.

The model-only account disables local authentication and project management,
matching Bicep; the separate agent account supports projects.
Deployments serialize through an account-scoped AzAPI operation lock and omit
an explicit `raiPolicyName`, matching Bicep. Read back the service's effective
backend policy rather than assuming a policy name or that filtering is disabled.
The operation lock is not a remote state/concurrent-writer lock. Backend filter
configuration is not enforcement proof or gateway/MCP filtering.

Outputs:

- `account_id`, `endpoint`, `deployment_ids` keyed by deployment name.
- `backend = { account_id, endpoint, deployment_ids }`, accepted by
  [ai-gateway](../ai-gateway/README.md). Pass `model_deployments` metadata
  separately; this module never accepts gateway identities.

Use [models-only](../../examples/models-only/README.md) independently, or the
[composition root](../../README.md). Check model availability and quota before
planning a real target. `public_network_access = "Disabled"` does not provision
private connectivity. Existing accounts are not imported through this module;
use the [existing-models example](../../examples/existing-models/README.md).

See the [canonical preparation/state route](../../docs/architecture.md#offline-and-deployment-preparation)
and [historical evidence boundary](../../docs/evidence-map.md).
