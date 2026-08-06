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
the reusable workflow input). Store the private material only in the protected
`release-signing` environment as `SPICE_LIBRARY_RELEASE_SIGNING_KEY`. Require
trusted-reviewer approval for that environment.

Create a separate protected `release-publish` environment with trusted-reviewer
approval and no secrets. Validation runs before either environment, signing has
only `contents:read`, independent verification receives only signed artifacts
and the public anchor, and publication alone receives `contents:write`. Never
put the private key in an organization or repository secret, pass it through a
`workflow_call`, expose it to verification or publication, or generate a
production key in CI.

The release workflow must not execute a signer or verifier selected by the
tagged candidate. Candidate-owned checks run in a separate uncredentialed job
whose filesystem and outputs are not trusted as release authority. Planning and
signing build `spice-dev` from immutable commit
`963bb6676069b0d4217bf22401e30482e3d05575`; verification builds the independent
verifier from immutable commit
`a83d9b58034cfa1487828fd2b44d28115d987a81`. Both builds use the trusted
repositories' vendor trees, network-disabled Go settings, isolated build/module
caches, and `-trimpath`. Fresh candidate checkouts remain inert inputs after the
uncredentialed validation phase.

The workflow admits only tagged commits that descend from fetched `origin/main`.
Its public anchor path must be clean and repository-relative, resolve without a
symlink in any component, identify an exact `100644` Git blob in the tagged
commit, and match the checked-out bytes. These workflow checks supplement,
rather than replace, protected environment reviewers and server-side tag rules.
Publication also resolves both lightweight and annotated remote tag forms
immediately before and after release creation and requires the peeled target to
remain the exact workflow commit.
