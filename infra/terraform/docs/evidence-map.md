# Validation and acceptance

**Status: November 5, 2026. Full Bicep/azd hosted-agent parity is not accepted.**
The public Terraform gateway pin now follows upstream `2025-09-01-preview`.
Earlier live observations used a separately deployed **2026** configuration;
they do not qualify this API change, every region, or a complete application.
Detailed execution receipts remain outside the repository.

## Acceptance matrix

| Area | Established evidence | Not established |
|---|---|---|
| Terraform offline suite | 75 native mocked plans, semantic checks of those same plans, 69 Python tests and five locked root validations. The 20 adapter handoffs are checks within the plans, not additional runs. Full-root defaults, safety overrides/opt-out, minimal integrations, both telemetry stages and the nonsecret tool bootstrap are covered separately. | Azure availability, successful provisioning or runtime behavior. |
| Application/container CI | Shared application tests, Bicep/hook checks, frozen image build and mocked container smoke passed at the published content-safety checkpoint `538e958`. Check each later commit's own CI result. | Real Toolbox discovery, hosted image execution or intended-identity authorization. |
| Earlier live infrastructure | 37 resource GETs, ten exact scoped roles, 250 matching compared leaves and an ordinary exact-input no-change plan. | New 2025 API deployment. Five requested fields were omitted by GET: three catalog `apiFormat` fields, exporter `kind` and registry `credentials`; full requested-body status is `INCOMPLETE`. |
| Local application model client | One bounded Api-Key Responses request through the shared client returned HTTP 200. | Hosted agent, managed-identity invocation, real tools or scheduled routine. |
| Gateway request logs | Four earlier requests were correlated to the expected Application Insights component. | Native OpenTelemetry export, the Portal gateway dashboard or hosted-agent tracing. |
| Native telemetry source | Two-stage managed ingestion, bounded GET-only helper, exact gateway/DCR ownership, native/legacy/pending mock plans and gateway-example forwarding. See the [usage and migration boundary](native-telemetry.md). | A new live native deployment, protected-exporter migration, endpoint-query acceptance, publisher propagation, delivery or dashboard/tracing acceptance. |
| Model content-safety source | Same-run mock assertions cover the exact four-category body, omission and coexistence with other policies. The bundled root selects Medium; explicit profiles allow Low/Medium/High or null. Standalone defaults and backend Microsoft.DefaultV2 are unchanged. See [configuration and opt-outs](../README.md#model-content-safety). | Selected-2025-API write/readback acceptance, enforcement or MCP safety. |
| Earlier content-safety readback | A disposable 2026 model returned all four requested Medium severities; the policy ID was omitted. The disposable model was removed with source preservation confirmed. | Qualification of the current source/API, runtime enforcement or MCP safety. |
| GitHub toolchain source | Explicit-credential whole-resource runner, Terraform-owned RemoteTool handoff, direct Foundry Toolbox creation and GET-only inspection. Thirty new mocked tests cover creation/rotation, concurrency stops, interrupted writes, redaction, version retention and nonsecret outputs. See the [usage and ownership limits](toolchain.md). | Selected-API provisioning, effective GitHub permissions, real credential delivery/rotation, server-side ETag enforcement, secret omission in cloud diagnostics, real MCP invocation or Toolbox consumption. Creation is not atomic. |
| Full application lifecycle | Infrastructure outputs, nonsecret environment/tool handoffs, default application-root access/monitoring/shared registry wiring and explicit opt-outs exist. | Automatic Terraform azd integration, complete live tool/credential acceptance, hosted agent/routine, runtime rotation/recovery and teardown. |

The earlier live environment used an explicit Storage public-access `Disabled`
override to align with inherited policy. That is not private connectivity or
hosted-agent readiness. Separate private-lab results and historical test suites
are not counted as acceptance of this contribution.

## Run the checks

Use the [canonical offline/preparation route](architecture.md#offline-and-deployment-preparation).
[`Test-Offline.ps1`](../scripts/Test-Offline.ps1) initializes with backend disabled
and read-only locks, then checks formatting, validation, structure, native plans,
semantic resource relationships, Python contracts and PowerShell syntax.
It does not deploy or require Azure credentials; uncached providers need network
access. Passing tests describe their assertions, not missing parity features.

| Test owner | Responsibility |
|---|---|
| [`root.tftest.hcl`](../tests/root.tftest.hcl) | Composition, aliases, input guards, full-root defaults, content-safety overrides/opt-out and independent model/tool/monitoring settings |
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

## Remaining acceptance gates

Wire an opt-in Terraform azd route without invoking Bicep writers. Qualify the
credential-explicit tool lifecycle, selected-API content safety,
native OpenTelemetry, the selected full-root wiring and shared registry on a reviewed
target with intended-identity allow/deny, real read-only GitHub tools, hosted
image/agent/routine, governance enforcement, correlated telemetry and repeatable
lifecycle operations.

Use [read-only field qualification](live-readback.md) alongside a current
ordinary plan, not as a substitute for runtime tests. Omitted properties remain
unknown; successful inference does not make them independently verified.
See [ownership and differences](architecture.md#preserved-contracts-and-deliberate-differences)
and the [tool/credential boundary](tool-credential-boundary.md) before deployment.
