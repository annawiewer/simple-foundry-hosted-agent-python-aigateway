# foundry-agents

Independent **agent-support infrastructure**, not a deployed hosted agent.
Creates an account/project with system identities, Storage, Premium ACR,
Log Analytics/ApplicationInsights, internal scoped roles and three project
connections. It does not require gateway outputs.

Required inputs: `subscription_id`, `resource_group_id`, `name` (account),
`location`, and `names = { project, storage, registry }`. Caller owns resource
names, group and provider configuration. Optional: `tags`,
`project_display_name`, `project_description`, `public_network_access`,
`storage_public_network_access`, `monitoring_public_network_access`, and
developer principal ID/type.

`enable_monitoring_integration = true` updates the existing owned
`AppInsights` connection to `ProjectManagedIdentity` and adds two Monitoring Metrics
Publisher grants (`3913510d-42f4-4e42-8a64-420c390055eb`), for the existing
account/project identities at this module's exact Insights scope. It defaults
to false; the connection depends on both grants. Account/project keys remain
known before identity creation. The root exposes this as
`enable_foundry_monitoring_integration`.

The connection retains `accounts/projects/connections@2025-06-01`, its original
Terraform address, project parent and name, unshared, with Bicep's managed-identity
body, target and metadata. Provider schema validation is disabled only for this auth
contract, matching Bicep's suppressed type warning; this is not schema proof.
Default false preserves the original ApiKey body and provider validation.
Read-only inspection found the existing connection also exposed through the
account route with matching creation time, auth, target and metadata. This
suggests mirrored backing resources, not a fully specified alias contract;
creating a second same-name account-route owner is deliberately prohibited.
The controlled single-owner update subsequently appeared through both routes
under the original resource IDs. Azure reset both creation timestamps, so a
Terraform in-place plan is not proof of unchanged service-internal backing.
The opt-in omits ApiKey credentials; omission alone does not prove that the
service erases previously stored values. No Insights local-auth setting,
registry sharing, credential hook or application instrumentation is changed.
This does not enforce Entra-only ingestion or prove trace delivery.

`storage_public_network_access` accepts null (inherit `public_network_access`),
`Enabled` or `Disabled`. An explicit value overrides only Storage's public
access and default ACL action, including an explicit `Enabled` with other
backends disabled. It creates no private connectivity and has no gateway
subnet requirement. The configured Storage `AzureServices` bypass remains;
the override is not proof of private-only runtime operation.

The project receives Storage data access, ACR pull access and account-scoped
Cognitive Services roles. Storage and registry connections depend on their
grants. ACR uses a project-managed-identity connection, unshared; AppInsights is
an unshared project-local ApiKey connection unless explicitly opted in above.
These are the current default connection contracts, not a claim of upstream
publisher/sharing/auth equivalence.

Outputs include account/project IDs and principals, project endpoint,
registry ID/endpoint/connection name, Storage name/ID and monitoring IDs.
`monitoring_connection_id` exposes the existing project-owned connection ID only
when the monitoring opt-in is enabled; otherwise it is null.
The project endpoint is constructed from the supplied account/project names;
it is not live endpoint-readiness proof. See [`outputs.tf`](outputs.tf).

No gateway model/tool invocation grants, direct model-backend grants, RemoteTool,
ToolServer, Toolbox, image build, hosted Responses agent or routine are created.
Connection strings occur in managed payloads: protect state and plans even
though published outputs are nonsecret. Public-access overrides do not create
private networking.

Use [agent-support-only](../../examples/agent-support-only/README.md) or the
[composition root](../../README.md), following the
[canonical preparation/state route](../../docs/architecture.md#offline-and-deployment-preparation).
Configuration is not hosted-runtime or tracing-delivery acceptance; see the
[evidence map](../../docs/evidence-map.md).
