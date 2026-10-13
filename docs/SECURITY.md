# Security and safety posture

## Current enforceable controls
- Research mode only, no order dispatch or critical-infrastructure integration.
- Distinct ingest, reviewer A, reviewer B and planner credentials. Two reviewers required before activation.
- Database-backed durable datasets and stored simulation results.
- Pydantic forbid-extra validation, physical units, finite coefficients, numerical feasibility verification and a bounded request size.
- Read-only container filesystem, non-root runtime user, no externally published PostgreSQL port in local compose.
- No secrets or private signing keys committed to the repository. Public statistical ingestion allowlists specific World Bank indicators and countries.
- GitHub pull request review and Actions CI as code-change quality gates.

## Known limitations (do NOT use as a production security claim)
- Shared bearer tokens are suitable for limited local prototypes only. No enterprise SSO/MFA, per-user attribution, rotation or revocation interface.
- The new PostgreSQL control plane has no append-only independent audit log, no signatures for facility submissions, no HSM-backed verification, no double-entry physical reconciliation, no field audit channel and no national-data authorization model yet.
- ORM create_all is not a managed migration system; high-availability, backups, periodic restore tests, tenant isolation, quotas, monitoring and incident response are not installed.
- An authorized reviewer can approve fictional or incorrect data. Formal provenance verification and anti-fraud sampling are future work.
- No vulnerability audit, penetration test or threat-model signoff has been completed.
- Access to PostgreSQL must be TLS enforced for hosted deployments, endpoints behind an HTTPS reverse proxy and private-network access controls, with external rate limits and WAF.
- Static UI uses tokens in memory; avoid untrusted extensions on operational workstations.
- GitHub Actions is a non-confidential ephemeral execution environment, never a security boundary for national private data.

## Mandatory gates before a production pilot

Independent threat-model review, external pentest, security patches, dependency scans with pinned lockfiles and signed images, SSO/MFA, service identity with mTLS, tamper-evident externally anchored logs, per-region access policy, dataset classification/consent/legal review, encrypted backups with restore drill, incident-runbooks, key compromise recovery, approval integrity tests, independent numerical audits and explicit prohibition on direct actuator commands.
