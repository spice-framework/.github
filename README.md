# Spice Framework organization infrastructure

Unified documentation: [spiceframework.dev/project](https://spiceframework.dev/project/).

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
- Reusable keyless Go-module release: [`.github/workflows/go-module-release.yml`](.github/workflows/go-module-release.yml)
- Reusable keyless Go-distribution release: [`.github/workflows/go-distribution-release.yml`](.github/workflows/go-distribution-release.yml)
- Reusable documentation source validation: [`.github/workflows/docs-source.yml`](.github/workflows/docs-source.yml)

Third-party actions are pinned to immutable commits. Repository-specific gates
remain responsible for product integration, generated freshness, real-service,
editor UI, compatibility, and release evidence.

Documentation contributors pin `docs-source.yml` by full commit and supply a
full immutable `spice-framework/docs` commit. The uncredentialed job validates
the source-owned `spice-docs.json`, overlays the caller commit on the reviewed
ecosystem snapshot, builds the complete static portal, and retains bounded
preview evidence. Source repositories contribute Markdown and declared assets;
the portal never executes source-owned build hooks.

Reusable workflows expose one stable `Required CI` result after all matrix and
offline jobs finish. Checkout credentials are never persisted, so verification
jobs cannot accidentally reuse the workflow token for Git mutations.

The reusable Go matrix is also the real macOS execution boundary: its
`macos-latest` job runs tidy, vet, shuffled tests, race tests, and a trimpath
build. Local `GOOS=darwin` cross-compilation is useful compile evidence but does
not replace that runner for race, process, signal, terminal, or runtime claims.
If hosted jobs are queued by the organization billing/policy state, they remain
an unfinished nonblocking mirror; repository-owned local verification is still
the delivery gate and nobody may report the queued jobs as passed.

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
job has no secrets or release authority. It first bootstraps the candidate's
exact pinned public tool graph through `proxy.golang.org` and the public
checksum database into isolated caches, verifies that the checkout remained
clean, and then runs `verify-release` with `GOPROXY=off`, `GOSUMDB=off`, and
private-module exceptions explicitly cleared. The trusted planning,
signing, verification, and publishing jobs use fresh candidate
checkouts strictly as inert source/Git input; they never run a candidate-selected
`go tool`, Make target, script, generated binary, or vendored implementation.
Every phase also requires the tagged commit to be an ancestor of fetched
`origin/main`. The public anchor must be a clean repository-relative path to an
exact `100644` blob in that commit, contain no symlink component, and match its
committed bytes. Publication resolves lightweight and annotated remote tags
immediately before and after creating the release and requires both targets to
remain the exact workflow commit and the direct tag object to remain unchanged.
Tags containing a canonical semantic-version prerelease suffix are published
as GitHub prereleases, so previews never replace the latest stable release.
The publishing CLI is explicitly bound to the caller repository even though the
workflow's candidate checkout uses a non-root path.
Changing either trusted tool commit is a security-sensitive workflow change and
requires callers to review and pin the resulting `.github` commit.

Generic Go modules use a separate keyless release contract. The candidate gate
has no signing or publication authority. Its public-proxy tool bootstrap is
separate from its offline, fail-closed repository verification. An immutable organization renderer
creates deterministic source, SBOM, metadata, and checksum artifacts; an
independently implemented toolchain verifier authenticates those bytes before
a protected `release-attestation` job mints a short-lived GitHub OIDC identity.
The verifier materializes the exact Git archive in private storage, authenticates
dependencies through the public Go checksum service, proves regenerated vendor
contents and an offline build, then creates a new four-file output directory.
Renderer output is never uploaded under the verified artifact name or handed
directly to attestation.
That job creates Sigstore-backed SLSA provenance with narrowly scoped artifact
metadata authority and has no repository write permission. A following job
verifies the portable bundle against the exact
caller repository, source commit/ref, GitHub issuer, and this reusable workflow
before a separate protected `release-publish` job receives `contents:write`.
The verifier selects the signer with the fully qualified reusable-workflow path
and its immutable commit. It deliberately does not also pass a signer-repository
selector because `gh attestation verify` treats repository and workflow signer
selectors as mutually exclusive; the workflow path already fixes the
`spice-framework/.github` repository.
No long-lived signing key or caller secret exists in this path.

`go-module-release.yml` pins the reviewed renderer at development commit
`ed7e58a7493a44ba60df881b9bf9b24edcbc99ee` and its independently implemented
verifier at toolchain commit
`01478163ce5282f9b71d7da19016f721b911f909`. Changing either pin and its
regression assertion is one security-sensitive governance change. The module
workflow remains fixed to `go-module-v1`.

Binary distributions use the separate `go-distribution-release.yml` workflow.
It pins the same reviewed commits but invokes the profile-specific central
distribution renderer and independent distribution verifier. The closed
`go-distribution-v1` policy currently authenticates six target archives,
release metadata, an SPDX SBOM, and checksums. Before keyless attestation, an
authority-free matrix checks out the exact candidate commit and executes its
installed-byte acceptance target against only that verifier-owned nine-subject
directory on `ubuntu-24.04` and `windows-2025`. The Windows leg explicitly
acknowledges its disposable hosted-runner boundary. This matrix has only
`contents:read`, receives no secret or protected environment, runs with module
network access disabled, and must leave the candidate checkout clean.
Attestation depends on both independent verification and both execution legs.
This distribution-only execution proof never broadens the module or starter
release contracts.

Each caller pins this repository by full commit and grants only the
ceiling that the called workflow narrows per job:

```yaml
permissions: {}

jobs:
  release:
    permissions:
      contents: write
      id-token: write
      attestations: write
      artifact-metadata: write
    uses: spice-framework/.github/.github/workflows/go-module-release.yml@<40-character-commit>
    with:
      module: github.com/spice-framework/<repository>
      workflow_commit: <same-40-character-commit>
```

Distribution callers use the same permission ceiling and inputs but select
`go-distribution-release.yml` in `uses`. The caller passes no secrets and must
not use `secrets: inherit`. Before
enablement, maintainers create protected `release-attestation` and
`release-publish` environments, restrict them to release tags, require trusted
reviewers, and keep both environments secret-free.

All ten active starter repositories now pin this workflow at immutable commit
`9ae80e32f64b29697acd9ebe629468850b4ae9f2`. Their copied release commands and
private release packages have been retired. Each caller has a distinct
committed Ed25519 public anchor, a corresponding repository Actions secret,
separate protected signing and publication approvals, and release-tag creation
and immutability rules. These facts establish the common release architecture;
they do not imply that every tagged preview run and independent downloaded-
artifact audit has completed.

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

Repository ownership is intentionally split. `spice` owns runtime and public
SDK contracts; `toolchain` owns the compiler, generator, CLI, LSP, release
verifier, and performance budgets; editor integrations, reference
applications, starters, development tooling, and organization workflows live
in their own independently gated repositories. The public organization profile
lists the current boundaries without treating compatibility pins as moving
repository-head versions.

The Go workflow applies unchanged to `spice-agent`,
`spice-agent-provider-openai`, `spice-agent-tools-coding`, `spice-agent-tui`,
and `spice-agent-coding`. Their exact 2026-08-06 Phase 0 source commits, selected
module pins, dependency-ordered local command, and macOS evidence limits are
recorded in the development repository's
[`spice-agent-phase-0.md`](https://github.com/spice-framework/development/blob/main/docs/spice-agent-phase-0.md).
That compatibility snapshot links to, but does not duplicate, the canonical
Spice Agent implementation ledger.
