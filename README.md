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

The library release workflow requires an exact Git tag and a reviewed public
trust anchor at `security/release/ed25519-public.pem` (or the explicit
`trusted_public_key` input). A candidate's own pinned and vendored tools remain
part of its local quality gate, but release authority never executes them.
Instead, this workflow builds the renderer/signer from the separate immutable
`spice-framework/development` commit
`963bb6676069b0d4217bf22401e30482e3d05575` and the verifier from the separate
immutable `spice-framework/toolchain` commit
`a83d9b58034cfa1487828fd2b44d28115d987a81`, offline and without shared Go
caches. Each caller must create two protected environments:

- `release-signing` owns the required
  `SPICE_LIBRARY_RELEASE_SIGNING_KEY` environment secret and grants no write
  permission;
- `release-publish` approves publication and contains no private key or other
  release secret.

The signing key must be generated and retained by the repository owner outside
GitHub and committed source. The reusable workflow validates without secrets,
signs with `contents:read`, independently verifies using only the public anchor,
and gives `contents:write` only to the final publishing job. That job receives
only the independently verified five-artifact set.

Candidate-owned checks execute only in the uncredentialed validation job. The
trusted planning, signing, verification, and publishing jobs use fresh candidate
checkouts strictly as inert source/Git input; they never run a candidate-selected
`go tool`, Make target, script, generated binary, or vendored implementation.
Every phase also requires the tagged commit to be an ancestor of fetched
`origin/main`. The public anchor must be a clean repository-relative path to an
exact `100644` blob in that commit, contain no symlink component, and match its
committed bytes. Publication resolves lightweight and annotated remote tags
immediately before and after creating the release and requires both targets to
remain the exact workflow commit.
Changing either trusted tool commit is a security-sensitive workflow change and
requires callers to review and pin the resulting `.github` commit.

Callers pin this repository by immutable commit, grant the reusable call a
`contents:write` ceiling so its final job can publish, and pass no secrets:

```yaml
permissions: {}

jobs:
  release:
    permissions:
      contents: write
    uses: spice-framework/.github/.github/workflows/library-release.yml@<40-character-commit>
    with:
      module: github.com/spice-framework/<repository>
```

Before enabling the caller, maintainers must create both environments, limit
them to release tags, and configure trusted required reviewers. GitHub cannot
raise permissions inside a called workflow, so omitting the caller's
`contents:write` ceiling prevents publication; it does not give the validation,
signing, or verification jobs write access.
