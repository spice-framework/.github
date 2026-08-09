# Governance

## Scope

The Spice Framework organization maintains the core runtime and public SDK,
the compiler and CLI toolchain, editor integrations, reference applications,
external-service starters, and cross-repository development infrastructure.

## Decision model

The project currently uses a maintainer-led model. The lead maintainer is
responsible for product direction, release decisions, security response, and
appointing additional maintainers. Public contracts or repository boundaries
require an ADR or RFC in the repository that owns the affected contract.

Technical decisions favor:

1. valid and idiomatic Go;
2. deterministic compile-time behavior;
3. explicit dependencies and observable ownership;
4. small, independently versioned repositories;
5. measurable developer experience and operational safety.

The project does not claim consensus when the maintainer has made a decision.
Dissenting alternatives and material tradeoffs should still be recorded.

## Maintainer responsibilities

Maintainers must:

- enforce the owning repository's local verification contract;
- preserve compatibility within the published maturity boundary;
- disclose conflicts of interest;
- coordinate security fixes privately until disclosure is safe;
- require real-system evidence for integrations described as production-ready;
- avoid merging generated, vendored, or release artifacts that are not
  mechanically reproducible.

Cross-repository checks follow the dependency graph in topological waves:
independent ready repositories may run concurrently, but a distribution cannot
be treated as verified before its selected SDK and extension dependencies.
Hosted Actions are a durability and platform mirror. A queued job caused by an
organization billing or policy restriction is unfinished evidence, not a local
delivery blocker and not a green result.

## Releases

Each repository versions its own artifact. Coordinated releases are described
by the compatibility catalog in `spice-framework/development`; matching version
numbers across repositories are not assumed to be compatible. Pre-1.0 APIs may
change only with migration notes and an updated compatibility declaration.

Library repositories use the organization-owned reusable release workflow.
The caller owns its reviewed public trust anchor and user-owned signing key.
The private key exists only as the repository Actions secret
`SPICE_LIBRARY_RELEASE_SIGNING_KEY` and is passed through the reusable workflow's
required one-secret contract; unrelated secrets are never inherited. GitHub
does not expose a caller environment secret to a cross-repository reusable
workflow job. The protected `release-signing` environment therefore remains the
human approval gate but does not own the key. A separate protected
`release-publish` environment controls the only job with `contents:write` and
must contain no private key. The central signer and independently implemented
verifier are built offline from separately checked-out immutable governance
commits, never from candidate source or its vendor tree, and must both accept
the exact tagged commit before publication. Candidate-owned commands may run
only in the earlier uncredentialed validation job; all later phases treat a
fresh candidate checkout as inert input. Updating either trusted tool commit is
a security-sensitive governance change.
Maintainers never commit private keys, generate production keys in automation,
or pass a private key to validation, verification, or publication jobs.

Generic Go-module and Go-distribution releases use separate profile-specific
keyless organization workflows and
never receive the starter release's private-key secret. Candidate-owned checks
run before release authority is introduced. Their pinned public tools are
bootstrapped only in that uncredentialed boundary, after which candidate-owned
release verification runs with Go module resolution disabled. Organization-owned rendering and
independent toolchain verification must both accept the exact tagged commit and
artifact set. Only the protected attestation job receives `id-token:write`,
`attestations:write`, and `artifact-metadata:write`; only the separately
protected publication job receives `contents:write`. The attestation bundle is verified against the exact caller
source identity and reusable workflow before publication. Both environments
are approval gates and contain no secrets.

The existing key-backed library workflow remains the starter release contract.
A generic module or distribution must not use it, and a `starter-*` repository
must not route through either keyless generic profile. Modules and
distributions have distinct reusable workflow identities, central renderers,
independent verifier commands, artifact allowlists, and semantic regression
contracts; neither workflow accepts the other's profile.

Protected-environment approval is intentionally separate from cryptographic
key custody. Reviewers approve the exact tag, commit, public anchor, and trusted
workflow pin; the workflow receives only the named repository secret after that
approval. No approval authorizes a moving branch, a replacement key, or a
candidate-provided signer.

## Changes to governance

Governance changes are public commits in this repository. Material changes
must explain the reason, transition, and effect on existing contributors.
