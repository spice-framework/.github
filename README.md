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
- Reusable signed library release: [`.github/workflows/library-release.yml`](.github/workflows/library-release.yml)

Third-party actions are pinned to immutable commits. Repository-specific gates
remain responsible for product integration, generated freshness, real-service,
editor UI, compatibility, and release evidence.

Reusable workflows expose one stable `Required CI` result after all matrix and
offline jobs finish. Checkout credentials are never persisted, so verification
jobs cannot accidentally reuse the workflow token for Git mutations.

The library release workflow requires an exact Git tag, the caller's pinned
and vendored central signer and independent verifier tools, a reviewed public
trust anchor in the repository, and an external Ed25519 private-key secret. It
publishes only after the independent verifier authenticates all five artifacts.
