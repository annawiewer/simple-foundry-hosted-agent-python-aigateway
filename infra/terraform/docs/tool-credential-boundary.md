# ToolServer and credential boundary

An explicit-credential [tool lifecycle runner](toolchain.md) now implements
ToolServer creation/rotation, GET-only inspection and Foundry Toolbox creation.
**These paths are source-tested, not live-accepted.** Terraform itself still
owns only the RemoteTool connection and selected grants; an explicitly
configured connection does not create its remote server or prove invocation.
The separate project Tools User grant, enabled by default in the application
root, is authorization
configuration only, not an exception to this boundary.

## Selected 2025 contract

The [official CLI installer pinned at b2204cf4](https://github.com/Azure/aigateway/blob/b2204cf4a32f2d69e07fc475cee7c6056a28e711/cli/install.ps1)
identifies release `1.0.0b22` and wheel SHA-256
`3363ee0efde6ec22f445fd11f2b6b625867c1ab49b8ab76108f6e1bfa920060a`.
Its inspected 2025 ToolServer serializer uses `displayName` and dictionary-of-list
credential headers, matching the [Bicep request](../../main.bicep).
Its GET schema exposes **`properties.mcpEndpointUrl`**, not the November
`gatewayEndpoints[]` contract described below. The runner preserves that returned
MCP URL rather than constructing a sample path.

The official CLI custom implementation documents that ToolServer creation does
not enforce `If-None-Match`. This runner therefore requires explicit exclusive
ownership, checks the exact missing-resource response and refuses existing
names. This is not atomic creation. Rotation sends a fresh specific ETag only
after matching the receipt and complete nonsecret configuration. Neither schema
inspection nor mocks prove service-side conditional enforcement.

The Foundry path follows the pinned
[Toolbox v1 client](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/extensions/azure.ai.toolboxes/internal/pkg/azure/foundry_toolsets_client.go)
and [versioned endpoint construction](https://github.com/Azure/azure-dev/blob/1273b0ddd9a04b09352f67632a6f1e3952fc5df0/cli/azd/extensions/azure.ai.toolboxes/internal/cmd/toolbox_show.go).
It uses direct requests rather than `azd ai toolbox create`, avoiding the latter's
automatic role-assignment and environment-write behavior. It never writes the
Terraform-owned RemoteTool connection.

## Earlier contract findings and limits

The November 4-5, 2026 investigations compared the upstream credential hook
with the published standalone gateway contracts. The distinction matters before
porting a resource body or reusing an existing hook:

| Source or check | Finding and limit |
|---|---|
| [Pinned September OpenAPI](https://github.com/Azure/azure-rest-api-specs/blob/28237674e0ed814213f8e2b85ebcb4cc46d3e0fb/specification/apimanagement/resource-manager/Microsoft.ApiManagement/AIGateway/preview/2026-09-01-preview/openapi.json) | The `2026-09-01-preview` document has four top-level gateway paths, without a ToolServer schema. Its omission is not proof that the service lacks child routes. |
| [Pinned ToolServer TypeSpec](https://github.com/Azure/azure-rest-api-specs/blob/28237674e0ed814213f8e2b85ebcb4cc46d3e0fb/specification/apimanagement/resource-manager/Microsoft.ApiManagement/AIGateway/AIGatewayToolServer.tsp) and [November OpenAPI](https://github.com/Azure/azure-rest-api-specs/blob/28237674e0ed814213f8e2b85ebcb4cc46d3e0fb/specification/apimanagement/resource-manager/Microsoft.ApiManagement/AIGateway/stable/2026-11-01/openapi.json) | The published ToolServer resource is introduced at `2026-11-01`. It uses a `name` wire property and header objects with `name`/`values`; secret values are create/update-only. This is not the same body contract as the older hook. |
| Read-only collection probes in the fresh authorized deployment | September 2026 and September 2025 requests returned HTTP 200 with empty collections. November 2026 returned HTTP 400, `MissingOrIncorrectVersionParameter`. This proves only those dated read outcomes in that target, not a write contract, runtime endpoint, secret handling or availability everywhere. |
| [Existing upstream PowerShell hook](../../scripts/configure-ai-gateway.ps1) | It obtains the active local GitHub CLI credential and writes a complete older-format ToolServer body, then configures azd/Toolbox and saves a runtime key. It is not a Terraform adapter and is not run by this contribution. |

The published November contract also exposes a read-only
`gatewayEndpoints[]` collection with the invocation `url` and API kind. Select
the qualified MCP endpoint from the service response; do not copy a sample path
or assume its case. Header values are create/update-only in that schema and
are retrieved separately with `listSecrets`; ordinary GET is not sufficient
to establish header drift or credential preservation. Whether a write omitting
values preserves them remains unaccepted. A schema alone is not approval to
retrieve or upload any real credential.

No API/provider upgrade, ToolServer write, GitHub credential retrieval/upload,
`listSecrets` request or Toolbox creation was performed for these checks.
Do not silently substitute the newer published schema into the tested preview
deployment, or infer a usable MCP URL from an empty collection response.

## Tool role qualification

On November 5, 2026, a subscription-scoped, read-only role-definition GET
confirmed **AI Gateway Tools User**
`dce03f8d-857f-4e40-a90d-67770fa6ecd2` as a built-in role. It returned no management
actions and these data actions:

- `Microsoft.ApiManagement/service/workspaces/toolServers/*`
- `Microsoft.ApiManagement/aigateways/tools/*`

This confirms definition availability in that qualified target, not all
subscriptions, a role assignment, propagation or an intended-identity tool call.
No assignment or inference was made during the lookup. Receipts remain outside
the contribution.

`enable_foundry_gateway_tool_access` grants this role only to the existing
Foundry project identity, at this gateway's exact scope. It defaults to true in
the application root and can be disabled independently. The root owns it;
standalone modules/examples do not add it. The gateway module's caller map still
grants Models User only. The broader AI Gateway User role is not substituted.
Narrower ToolServer-level scope requires a separately established resource
identity; a runtime URL alone is not that identity.

## Implemented ownership and remaining acceptance

The whole-resource runner is the ownership boundary. Terraform must not create
a ToolServer stub that a hook subsequently overwrites. Owner markers, durable
nonsecret receipts and strict readback prevent implicit adoption; they do not
replace Azure authorization or guarantee protection against a competing writer.

The runner must receive an explicitly selected credential; deployment approval
does not select a personal GitHub login for cloud storage. Never infer consent
from an existing `gh` login, read its token automatically, put a token in tfvars,
or save a secret-bearing request in logs, output artifacts, state or plans.
Use repository-restricted, read-only permissions; an `X-MCP-Readonly` header is
not a substitute for credential least privilege.

Before calling the live implementation accepted:

- Establish the exact API, whole request body and service-returned runtime URL.
- Preserve the entire intended ToolServer policy and endpoint configuration
  during creation and credential rotation, with conditional concurrency checks.
- Verify that ordinary reads and all persisted local/cloud diagnostics omit
  credentials; an offline redaction test alone is insufficient.
- Prove intended-identity allow/deny, actual read-only tool invocation and the
  Foundry Toolbox reference separately from role/connection creation.

Offline tests cover request bodies, failure/rotation/inspection behavior,
redaction and handoffs, not those live gates. See the [evidence map](evidence-map.md).
