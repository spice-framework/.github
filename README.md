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
`4c308d1b9fda11cb2b045f2e0d9e1616d32d007d` and the verifier from the separate
immutable `spice-framework/toolchain` commit
`71211498297c9ab77cc05c4844db5e64e0170896`, offline and without shared Go
caches. GitHub does not make a caller environment secret available to a job in
a cross-repository reusable workflow. Each caller therefore stores the key as
the repository Actions secret `SPICE_LIBRARY_RELEASE_SIGNING_KEY` and passes
only that named secret through `workflow_call`. The called signing job remains
behind the caller repository's protected environment approval. Each caller
must create two protected environments:

- `release-signing` approves access to the signing job and grants no write
  permission;
- `release-publish` approves publication and contains no private key or other
  release secret.

The signing key must be generated and retained by the repository owner outside
GitHub and committed source. The reusable workflow validates without secrets,
signs with `contents:read`, independently verifies using only the public anchor,
and gives `contents:write` only to the final publishing job. That job receives
only the independently verified five-artifact set.

Candidate-owned checks execute only in the uncredentialed validation job. That
job has no secrets or release authority and may resolve the exact committed
module graph only through `proxy.golang.org` with the public checksum database;
private-module exceptions are cleared explicitly. The trusted planning,
signing, verification, and publishing jobs use fresh candidate
checkouts strictly as inert source/Git input; they never run a candidate-selected
`go tool`, Make target, script, generated binary, or vendored implementation.
Every phase also requires the tagged commit to be an ancestor of fetched
`origin/main`. The public anchor must be a clean repository-relative path to an
exact `100644` blob in that commit, contain no symlink component, and match its
committed bytes. Publication resolves lightweight and annotated remote tags
immediately before and after creating the release and requires both targets to
remain the exact workflow commit and the direct tag object to remain unchanged.
The publishing CLI is explicitly bound to the caller repository even though the
workflow's candidate checkout uses a non-root path.
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
    secrets:
      SPICE_LIBRARY_RELEASE_SIGNING_KEY: ${{ secrets.SPICE_LIBRARY_RELEASE_SIGNING_KEY }}
```

Before enabling the caller, maintainers must create both environments, limit
them to release tags, configure trusted required reviewers, and create the
repository Actions secret. Pass the one named secret explicitly; never use
`secrets: inherit`. GitHub cannot raise permissions inside a called workflow,
so omitting the caller's `contents:write` ceiling prevents publication; it does
not give the validation, signing, or verification jobs write access.
