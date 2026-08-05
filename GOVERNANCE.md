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

## Releases

Each repository versions its own artifact. Coordinated releases are described
by the compatibility catalog in `spice-framework/development`; matching version
numbers across repositories are not assumed to be compatible. Pre-1.0 APIs may
change only with migration notes and an updated compatibility declaration.

## Changes to governance

Governance changes are public commits in this repository. Material changes
must explain the reason, transition, and effect on existing contributors.
