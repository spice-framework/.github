# Spice Framework organization infrastructure

This special `.github` repository provides the public organization profile,
default community health files, issue and pull-request templates, and reusable
least-privilege verification workflows for Spice repositories.

- Organization profile: [`profile/README.md`](profile/README.md)
- Governance: [`GOVERNANCE.md`](GOVERNANCE.md)
- Contribution contract: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Security reporting: [`SECURITY.md`](SECURITY.md)
- Reusable Go gate: [`.github/workflows/go-verify.yml`](.github/workflows/go-verify.yml)
- Reusable Gradle gate: [`.github/workflows/gradle-verify.yml`](.github/workflows/gradle-verify.yml)

Third-party actions are pinned to immutable commits. Repository-specific gates
remain responsible for product integration, generated freshness, real-service,
editor UI, compatibility, and release evidence.
