# ToolServer and credential boundary

ToolServer, Toolbox and GitHub credential delivery are **not implemented or
accepted** by this Terraform contribution. An explicitly configured RemoteTool
connection is only a reference; it does not create its remote server, populate
credentials, establish a Toolbox or prove tool invocation.
The separate default-off project Tools User grant is authorization
configuration only, not an exception to this boundary.

## Contract findings

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
Foundry project identity, at this gateway's exact scope. It is independently
default-off. The root owns it; the gateway module's explicit caller map still
grants Models User only. The broader AI Gateway User role is not substituted.
Narrower ToolServer-level scope requires a separately established resource
identity; a runtime URL alone is not that identity.

## Required ownership for a future implementation

A separately reviewed whole-resource runner is the conservative ownership
boundary until write-only state exclusion, GET behavior, conditional updates
and rotation are accepted for the selected API. Terraform must not create a
ToolServer stub that a hook subsequently overwrites.

The runner must receive an explicitly selected credential; deployment approval
does not select a personal GitHub login for cloud storage. Never infer consent
from an existing `gh` login, read its token automatically, put a token in tfvars,
or save a secret-bearing request in logs, output artifacts, state or plans.
Use repository-restricted, read-only permissions; an `X-MCP-Readonly` header is
not a substitute for credential least privilege.

Before calling a future implementation accepted:

- Establish the exact API, whole request body and service-returned runtime URL.
- Preserve the entire intended ToolServer policy and endpoint configuration
  during creation and credential rotation, with conditional concurrency checks.
- Verify that ordinary reads and all persisted local/cloud diagnostics omit
  credentials; an offline redaction test alone is insufficient.
- Prove intended-identity allow/deny, actual read-only tool invocation and the
  Foundry Toolbox reference separately from role/connection creation.

No current green check in the [evidence map](evidence-map.md) covers these gates.
