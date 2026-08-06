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

The uncredentialed candidate-validation job may authenticate the exact
committed module graph through Go's public proxy and checksum database. It has
no secrets or release authority, and private-module exceptions are cleared.
Trusted renderer, signer, and verifier builds remain vendor-only and
network-disabled.

The workflow admits only tagged commits that descend from fetched `origin/main`.
Its public anchor path must be clean and repository-relative, resolve without a
symlink in any component, identify an exact `100644` Git blob in the tagged
commit, and match the checked-out bytes. These workflow checks supplement,
rather than replace, protected environment reviewers and server-side tag rules.
Publication also resolves both lightweight and annotated remote tag forms
immediately before and after release creation and requires the peeled target to
remain the exact workflow commit and the direct tag object to remain unchanged.
The publishing CLI is explicitly scoped to the caller repository.
