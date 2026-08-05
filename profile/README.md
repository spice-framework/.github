# Spice Framework

Spice is a Go-native application framework for modular production services.
It pursues the practical developer outcomes of Spring Boot and Spring Modulith
through valid Go source, compile-time validation, deterministic generated Go,
explicit dependencies, and a small runtime.

## Repositories

- [`spice`](https://github.com/spice-framework/spice) owns the framework runtime,
  compiler, command-line tools, examples, and current editor integrations.
- [`development`](https://github.com/spice-framework/development) owns
  cross-repository workspace, compatibility, and coordinated verification
  tooling.
- [`.github`](https://github.com/spice-framework/.github) owns organization
  governance and reusable verification workflows.

Editor integrations, reference applications, and external-service starters
will appear here only after each one has an independent gate and a clean-room
consumer. A planned repository is not advertised as released functionality.

## Engineering principles

- Application annotations remain valid Go comments; ordinary Go tooling keeps
  working without an editor plugin.
- Generated behavior is committed, inspectable Go and requires no compiler at
  runtime.
- Dependency injection is compile-time, typed, explicit, and reflection-free.
- Core stays standard-library-first; integrations remain isolated and opt in.
- Security defaults fail closed, generation is non-destructive, and normal
  analysis never downloads dependencies.
- Compatibility and maturity are evidence-backed rather than inferred from an
  API name or roadmap entry.

Spice is pre-1.0. See each repository's compatibility declaration before
depending on it, and use private vulnerability reporting for security issues.
