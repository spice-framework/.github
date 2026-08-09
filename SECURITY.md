# Security Policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's private
vulnerability reporting on the affected Spice repository. If repository
routing is unclear, report it privately through
`spice-framework/spice`.

Include affected versions or commits, reproduction steps, expected impact,
and any known mitigations. Maintainers will acknowledge the report, establish
a private remediation plan, coordinate affected repositories, and publish an
advisory when users can safely update.

## Supported versions

Spice is pre-1.0 and does not yet have a generally supported release line.
Security fixes target the latest published preview and the current main branch.
Each repository's release notes will state support changes explicitly.

Security-sensitive areas include annotation and generated-code injection,
module/tool supply chains, secret handling, request binding, authentication and
authorization defaults, module boundary bypasses, external-service clients,
and editor-applied source edits. Security features require negative tests and
documented secure defaults.

## Library signing custody

Each publishing repository must use a maintainer-generated Ed25519 key whose
private half remains user-owned. Commit only the reviewed public PEM at
`security/release/ed25519-public.pem` (or pass its repository-relative path as
the reusable workflow input). Store the private material as the repository
Actions secret `SPICE_LIBRARY_RELEASE_SIGNING_KEY` and map only that named
secret into the reusable workflow. GitHub does not make a caller environment
secret available to a cross-repository reusable workflow job, so the secret
must not be stored only on the environment. Never use `secrets: inherit`.
GitHub secret storage removes the PEM's terminal newline; the protected signing
job normalizes CRLF to LF and restores exactly one terminal newline before the
strict canonical parser reads it.
Require trusted-reviewer approval for the `release-signing` environment that
gates the called signing job.

Create a separate protected `release-publish` environment with trusted-reviewer
approval and no secrets. Validation runs before either environment, signing has
only `contents:read`, independent verification receives only signed artifacts
and the public anchor, and publication alone receives `contents:write`. Never
put the private key in an organization secret, expose it to validation,
verification, or publication, or generate a production key in CI. The explicit
one-secret `workflow_call` mapping is the only supported transfer boundary.

The release workflow must not execute a signer or verifier selected by the
tagged candidate. Candidate-owned checks run in a separate uncredentialed job
whose filesystem and outputs are not trusted as release authority. Planning and
signing build `spice-dev` from immutable commit
`4c308d1b9fda11cb2b045f2e0d9e1616d32d007d`; verification builds the independent
verifier from immutable commit
`71211498297c9ab77cc05c4844db5e64e0170896`. Both builds use the trusted
repositories' vendor trees, network-disabled Go settings, isolated build/module
caches, and `-trimpath`. Fresh candidate checkouts remain inert inputs after the
uncredentialed validation phase.

The uncredentialed candidate-validation job may bootstrap only the exact
candidate-owned pinned public tool graph through Go's proxy and checksum
database. It has no secrets or release authority, uses isolated caches, and
must leave the checkout clean. The following candidate-owned `verify-release`
step reuses those caches with `GOPROXY=off`, `GOSUMDB=off`, and private-module
exceptions cleared. Trusted renderer, signer, and verifier builds remain
vendor-only and network-disabled.

The workflow admits only tagged commits that descend from fetched `origin/main`.
Its public anchor path must be clean and repository-relative, resolve without a
symlink in any component, identify an exact `100644` Git blob in the tagged
commit, and match the checked-out bytes. These workflow checks supplement,
rather than replace, protected environment reviewers and server-side tag rules.
Publication also resolves both lightweight and annotated remote tag forms
immediately before and after release creation and requires the peeled target to
remain the exact workflow commit and the direct tag object to remain unchanged.
The publishing CLI is explicitly scoped to the caller repository.

## Keyless generic Go-module and distribution releases

Generic Go modules and binary distributions use separate GitHub artifact
attestation workflows backed by Sigstore rather than a repository or
organization private key. Each reusable workflow accepts
only the canonical module input and no secrets. The caller's permission ceiling
must include `contents:write`, `id-token:write`, `attestations:write`, and
`artifact-metadata:write`, but the called workflow narrows these capabilities
per job:

- candidate validation, rendering, and independent verification receive only
  `contents:read` and cannot mint an OIDC identity;
- `release-attestation` receives `id-token:write`, `attestations:write`, and
  `artifact-metadata:write`, has no content-write authority, and consumes only
  independently verified bytes;
- bundle verification receives only `contents:read`; and
- `release-publish` alone receives `contents:write`, cannot mint OIDC identity,
  and consumes only the authenticated artifact set.

Rendering and verification are built with Go 1.26.5, `-mod=vendor`, `-trimpath`,
network-disabled module settings, isolated caches, and distinct immutable
organization repository commits. Within this later central trust boundary,
the independently built verifier alone may use the public Go proxy and checksum
database in fresh caches to authenticate the selected graph and reproduce
vendor; it builds the archive-materialized
Git tree offline and never the caller worktree. It then re-lists untrusted
renderer input and copies only its profile's closed artifact set into a new
verifier-owned directory: four files for modules or nine files for the current
six-target distribution policy. Generic modules pass those copied bytes
directly toward attestation. Distributions first pass the verifier-owned
nine-subject directory through a separate installed-byte execution matrix on
fixed Linux and Windows GitHub-hosted runners. That matrix checks out the exact
candidate commit, runs only its documented `verify-release-artifacts` target
with module networking disabled, always requires a clean checkout, and has only
`contents:read`: it receives no secret, protected environment, OIDC identity,
attestation authority, or publication authority. Windows execution additionally
requires the candidate's explicit disposable-runner acknowledgement.
Attestation depends on both the independent verifier and every execution leg.
No bytes produced by candidate execution replace the verifier-owned subjects.
The keyless verifier requires
the public GitHub OIDC issuer, exact caller repository, exact source commit and
tag ref, organization
reusable-workflow path and commit, and a GitHub-hosted runner. The caller must
repeat its immutable `uses` revision through the required `workflow_commit`
input; the signed certificate, not that input by itself, proves the match.
The verifier uses the fully qualified workflow as its signer selector and does
not combine it with `--signer-repo`: current `gh` versions treat those selectors
as mutually exclusive, while the workflow value already fixes the
`spice-framework/.github` repository and workflow path.
Publication resolves both annotated and lightweight remote tags before and
after release creation.

The portable Sigstore bundle is published beside the source archive, SBOM,
release metadata, and checksums so consumers are not limited to a live GitHub
API lookup. Consumers should verify every downloaded artifact with `gh
attestation verify`, the bundle, the expected `spice-framework` repository, the
organization reusable-workflow path, and the immutable workflow commit they
reviewed. Offline consumers must separately acquire a current trusted-root
bundle through GitHub's documented TUF-backed process.

The generic workflow pins separately reviewed renderer and independent-verifier
commits and the semantic regression check requires those exact object IDs.
Changing either pin requires successful local trust-boundary checks, a newly
pinned caller workflow, protected secret-free `release-attestation` and
`release-publish` environments, repository tag immutability, and a public
end-to-end rehearsal. The module and distribution workflows reject each
other's profile, and both reject starters; no profile may bypass its dedicated
contract.

The trust model follows GitHub's documentation for
[artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations),
[OIDC in reusable workflows](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-with-reusable-workflows),
and [offline attestation verification](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline).
