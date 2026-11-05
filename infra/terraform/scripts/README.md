# Offline checks

[`Test-Offline.ps1`](Test-Offline.ps1) is the single credential-free structural
verification entry. Use the
[canonical preparation route](../docs/architecture.md#offline-and-deployment-preparation)
for prerequisites, invocation and the separate Azure-enabled planning boundary.

The runner uses locked, backend-disabled initialization, formatting/validation,
provider-mocked tests and Python contract inspection. Provider downloads may
need registry access. It does not retrieve credentials, deploy resources,
invoke models, repair exporters, configure azd, deploy an agent or certify
runtime/telemetry/lifecycle acceptance. Existing Bicep mutation/recovery hooks
must not be reused against Terraform-owned resources.
