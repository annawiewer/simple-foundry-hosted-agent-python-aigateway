# ToolServer and credential boundary

ToolServer, Toolbox and GitHub credential delivery are **not implemented or
accepted** by this Terraform contribution. An explicitly configured RemoteTool
connection is only a reference; it does not create its remote server, populate
credentials, establish a Toolbox or prove tool invocation.

## Contract findings

The November 4, 2026 investigation compared the upstream credential hook with
the published standalone gateway contracts. The distinction matters before
porting a resource body or reusing an existing hook:

| Source or check | Finding and limit |
|---|---|
| [Pinned September OpenAPI](https://github.com/Azure/azure-rest-api-specs/blob/28237674e0ed814213f8e2b85ebcb4cc46d3e0fb/specification/apimanagement/resource-manager/Microsoft.ApiManagement/AIGateway/preview/2026-09-01-preview/openapi.json) | The `2026-09-01-preview` document has four top-level gateway paths, without a ToolServer schema. Its omission is not proof that the service lacks child routes. |
| [Pinned ToolServer TypeSpec](https://github.com/Azure/azure-rest-api-specs/blob/28237674e0ed814213f8e2b85ebcb4cc46d3e0fb/specification/apimanagement/resource-manager/Microsoft.ApiManagement/AIGateway/AIGatewayToolServer.tsp) and [November OpenAPI](https://github.com/Azure/azure-rest-api-specs/blob/28237674e0ed814213f8e2b85ebcb4cc46d3e0fb/specification/apimanagement/resource-manager/Microsoft.ApiManagement/AIGateway/stable/2026-11-01/openapi.json) | The published ToolServer resource is introduced at `2026-11-01`. It uses a `name` wire property and header objects with `name`/`values`; secret values are create/update-only. This is not the same body contract as the older hook. |
| Read-only collection probes in the fresh authorized deployment | September 2026 and September 2025 requests returned HTTP 200 with empty collections. November 2026 returned HTTP 400, `MissingOrIncorrectVersionParameter`. This proves only those dated read outcomes in that target, not a write contract, runtime endpoint, secret handling or availability everywhere. |
| [Existing upstream PowerShell hook](../../scripts/configure-ai-gateway.ps1) | It obtains the active local GitHub CLI credential and writes a complete older-format ToolServer body, then configures azd/Toolbox and saves a runtime key. It is not a Terraform adapter and is not run by this contribution. |

No API/provider upgrade, ToolServer write, GitHub credential retrieval/upload,
`listSecrets` request or Toolbox creation was performed for these checks.
Do not silently substitute the newer published schema into the tested preview
deployment, or infer a usable MCP URL from an empty collection response.

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
