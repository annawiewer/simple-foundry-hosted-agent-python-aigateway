# Validation and acceptance

**Status: November 7, 2026. One end-to-end on-demand hosted digest is accepted.**
Terraform infrastructure, hosted agent, AI Gateway/model, three real GitHub
tools and correlated agent/gateway telemetry were verified together on the
selected `2025-09-01-preview` gateway API. Recurring execution, full credential
lifecycle and teardown remain separate qualifications. The recorded results
below distinguish implementation, offline validation and live acceptance.

## Acceptance matrix

| Area | Established evidence | Boundary / not established by this check |
|---|---|---|
| Terraform offline suite | Recorded November 7 canonical run: 85 native mocked plans with semantic checks of the same plans, 143 Python tests, five locked root validations, formatting and PowerShell syntax. The 25 adapter handoffs are checks within those plans, not additional runs. | Azure availability, successful provisioning or runtime behavior. Default ownership remains 37 resources and 11 scoped roles; adding the optional map does not change empty-map behavior. |
| Application/container CI | Shared application tests, Bicep/hook checks, frozen image build and mocked container smoke passed at the published toolchain checkpoint `0cc1b7b`. Check each later commit's own CI result. | Real Toolbox discovery, hosted image execution or intended-identity authorization. |
| Integrated application infrastructure | The selected-API deployment's authoritative state contains 40 managed resources and 12 scoped roles after native telemetry and RemoteTool setup. The project lists its owned registry connection; ACR authentication-as-ARM is enabled and admin credentials are disabled. The accepted application used the [explicit project-local registry choice](architecture.md#project-local-registry-compatibility). | This does not qualify every region or registry mode. The two operational runtime grants are outside that state; no import/state rewrite was performed. Omitted readback fields, including catalog `apiFormat`, are not independently verified. |
| Agent and gateway telemetry | Correlated agent and native-gateway traces linked the accepted response to both intended model requests and all three real GitHub backend HTTP-200 calls. | Delivery was proven for this deployment, not Portal-dashboard behavior, all-signal completeness or exporter migration. |
| Native telemetry source | Two-stage managed ingestion, OTLP endpoints, gateway-identity DCR publishing, a bounded GET-only helper and native/legacy/pending mock plans. See the [usage and migration boundary](native-telemetry.md). | Configuration alone remains insufficient; the preceding row provides separate delivery evidence for this deployment. Exporter migration and other target/endpoint combinations remain unqualified. |
| Model content-safety source | Same-run mock assertions cover the exact four-category body, omission and coexistence with other policies. The bundled root selects Medium; explicit profiles allow Low/Medium/High or null. Standalone defaults and backend Microsoft.DefaultV2 are unchanged. See [configuration and opt-outs](../README.md#model-content-safety). | Mocks do not prove service acceptance or enforcement; the selected-API readback below is narrower than complete policy/runtime qualification. |
| Selected-2025 model readback | A November 7 disposable-model check returned all four requested Medium safety severities. Model creation, removal and absence were verified. | Requested-body qualification remains incomplete, including omitted `apiFormat`. This was not a runtime safety-enforcement or MCP-safety test. |
| Selected-2025 ToolServer control plane | An isolated November 7 check created, updated, read and deleted a ToolServer using public Learn MCP and synthetic nonsecret headers. Nonsecret configuration, stable endpoint identity, known null header placeholders on ordinary GET and deletion were verified. | Not real credential rotation, secret-value storage/delivery, server-side atomic conditional semantics or runtime safety enforcement. This isolated check did not invoke substantive tools or certify the production runner's full lifecycle. |
| GitHub toolchain source | Explicit-credential whole-resource runner, Terraform-owned RemoteTool handoff, direct Foundry Toolbox creation and GET-only inspection. Forty-five mocked tests cover creation/rotation, concurrency stops, interrupted writes, redaction, version retention and nonsecret outputs. See the [usage and ownership limits](toolchain.md). | The accepted hosted run separately proves real Toolbox/tool consumption. It does not certify effective least privilege, secret omission in every cache/cloud diagnostic, live rotation/revocation or competing-writer behavior. Creation is not atomic. |
| Application-flow source | The [guided app-only path](application-flow.md) binds applied handoffs, copies only shared build/runtime files, disables automatic role repair and gates agent/schedule operations independently. Fifty-five tests cover both registry sharing choices, exact ownership, CLI/context/drift guards, process-only key delivery and single-attempt receipts. | Live acceptance used azd 1.37.2 and extensions 1.0.0 with an immutable prebuilt image and the explicit platform-default ACR path. Other build/registry paths and recurring execution remain unqualified. |
| Actual-agent runtime grants | Exact-principal readback verified Models User at this gateway and Monitoring Metrics Publisher at this agent Insights component. The opt-in [`hosted_agent_principals` handoff](application-flow.md#3-bind-the-deployed-agent-identity) represents these same scoped roles repeatably in source. | The accepted environment's two operational grants remain external to its authoritative state. Source support and import instructions are not completed adoption; no direct agent Tools User or broad Contributor grant was added. Tenant authorization remains separate. |
| November 7 hosted digest | One on-demand run returned a completed, truthful digest. `list_pull_requests`, `list_issues` and `actions_list` all succeeded with empty result sets; independent GitHub checks agreed. Both intended gateway/model requests and all GitHub backend calls returned HTTP 200, with correlated agent/gateway telemetry. | Not recurring execution, populated-result UX coverage, negative authorization or adversarial policy enforcement. No schedule was enabled. |
| Full application lifecycle | The core infrastructure-to-digest journey is demonstrated with separate infrastructure, tool and application owners; the default Bicep path is unchanged. | Scheduled routines, complete credential rotation/recovery and teardown remain separate work. No unattended Terraform `azd up` wrapper is supplied. |

Storage public access `Disabled` does not provide private connectivity or
establish hosted-agent readiness.

The shared host's local package-download TLS failure remains unresolved.
The working acceptance path used an Azure-built immutable image; no TLS trust,
proxy or shared-host security bypass was introduced. That local build
limitation is not a blocker to the demonstrated cloud-hosted path.

## Run the checks

Use the [canonical offline/preparation route](architecture.md#offline-and-deployment-preparation).
[`Test-Offline.ps1`](../scripts/Test-Offline.ps1) initializes with backend disabled
and read-only locks, then checks formatting, validation, structure, native plans,
semantic resource relationships, Python contracts and PowerShell syntax.
It does not deploy or require Azure credentials; uncached providers need network
access. Passing tests describe their assertions, not missing parity features.

| Test owner | Responsibility |
|---|---|
| [`root.tftest.hcl`](../tests/root.tftest.hcl) | Composition, aliases, input guards, full-root defaults, safety settings and opt-in hosted-identity roles with independent switches and exclusive ownership |
| [`gateway.tftest.hcl`](../tests/gateway.tftest.hcl) | Standalone gateway, frontend, exporter destination, callers and safety enum rejection |
| [`telemetry.tftest.hcl`](../tests/telemetry.tftest.hcl) | Native readiness, scoped publisher/exporter and rejection of stale or mismatched handoffs |
| [`models.tftest.hcl`](../tests/models.tftest.hcl) | Model profile, deployment guards and gateway-only safety metadata without changing the backend filter |
| [`agents.tftest.hcl`](../tests/agents.tftest.hcl) | Independent support resources, network inputs and monitoring connection |
| [`examples.tftest.hcl`](../tests/examples.tftest.hcl) | Four standalone roots, external-pregrant configuration and existing-model safety opt-in |
| [`examples-telemetry.tftest.hcl`](../tests/examples-telemetry.tftest.hcl) | Native handoff forwarding through both gateway-bearing examples |
| [`check_contracts.py`](../tests/check_contracts.py) | API bodies, exact grants, routes, sole ownership and dependency edges |
| [`test_environment_adapter.py`](../tests/test_environment_adapter.py) | Nonsecret allow-list, Responses compatibility and resource/endpoint relationships |
| [`test_live_readback.py`](../tests/test_live_readback.py) | GET-only scope, omissions, safe receipts and no overwrite |
| [`test_telemetry_readiness.py`](../tests/test_telemetry_readiness.py) | Readiness polling, CLI/ARM context, endpoint validation, bounds, redaction and explicit no-overwrite handoffs |
| [`test_toolchain.py`](../tests/test_toolchain.py) | Explicit ownership/credentials, complete request bodies, conditional rotation, uncertain outcomes, Toolbox versions, redaction and isolated handoffs |
| [`test_application_flow.py`](../tests/test_application_flow.py) | Offline snapshot generation, context-bound handoffs, app-only manifests, independent deployment gates, installed versions, isolated credentials, drift detection and single-attempt receipts |

## Remaining qualification boundaries

The on-demand milestone does not establish the broader guarantees below.
Each requires separate, explicitly scoped authorization and validation:

- Recurring schedule activation/execution, release changes, recovery and teardown.
- Real credential rotation/revocation, diagnostics-wide secret handling,
  negative authorization and adversarial governance enforcement.
- Other regions, build/registry modes, exporter migration and explicit
  adoption of pre-existing grants into the authoritative state.

Use [read-only field qualification](live-readback.md) alongside a current
ordinary plan, not as a substitute for runtime tests. Omitted properties remain
unknown; successful inference does not make them independently verified.
See [ownership and differences](architecture.md#preserved-contracts-and-deliberate-differences)
and the [tool/credential boundary](tool-credential-boundary.md) before deployment.
