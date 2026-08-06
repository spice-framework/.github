# Spice Framework

Spice is a Go-native application framework for modular production services.
It pursues the practical developer outcomes of Spring Boot and Spring Modulith
through valid Go source, compile-time validation, deterministic generated Go,
explicit dependencies, and a small runtime.

## Repositories

- [`spice`](https://github.com/spice-framework/spice) owns the framework runtime
  and public SDK contracts.
- [`toolchain`](https://github.com/spice-framework/toolchain) owns the compiler,
  deterministic generator, CLI, LSP, independent library-release verifier, and
  enforced compiler/generator/development-loop performance budgets.
- [`spice-agent`](https://github.com/spice-framework/spice-agent) owns the
  experimental Spice-native agent kernel, public agent SDK, daemon/client
  protocols, runtime-plugin host, and conformance contracts. Its static
  extension graph is the generated Spice bean graph, never a parallel
  container.
- [`spice-agent-provider-openai`](https://github.com/spice-framework/spice-agent-provider-openai),
  [`spice-agent-tools-coding`](https://github.com/spice-framework/spice-agent-tools-coding),
  and [`spice-agent-tui`](https://github.com/spice-framework/spice-agent-tui)
  own independently versioned OpenAI Responses, coding-tool, and terminal UI
  extensions.
- [`spice-agent-coding`](https://github.com/spice-framework/spice-agent-coding)
  is the generated SDK-first reference distribution and end-to-end
  architecture proof; it is not yet advertised as a stable daily-use coding
  product.
- [`petclinic`](https://github.com/spice-framework/petclinic) is the standalone
  Spring Petclinic reference application, with generated in-memory, PostgreSQL,
  and MySQL targets plus explicit minimum/current core and toolchain
  compatibility verification.
- [`commerce`](https://github.com/spice-framework/commerce) is the
  production-shaped modular reference application, with explicit
  minimum/current compatibility verification across generated DI, HTTP,
  security, data, and mail workflows.
- [`zed`](https://github.com/spice-framework/zed) owns the independently
  versioned Zed extension that launches Spice's shared language server.
- [`goland`](https://github.com/spice-framework/goland) owns the independently
  versioned GoLand plugin, including valid-Go annotation editing, zero-width
  concealment, navigation, syntax coloring, package Run/Debug, and installed-IDE
  visual gates on Windows and Linux.
- [`starter-smtp`](https://github.com/spice-framework/starter-smtp),
  [`starter-postgres`](https://github.com/spice-framework/starter-postgres),
  [`starter-mysql`](https://github.com/spice-framework/starter-mysql), and
  [`starter-redis`](https://github.com/spice-framework/starter-redis) own mail,
  relational-data, and cache integrations outside core.
- [`starter-otel`](https://github.com/spice-framework/starter-otel),
  [`starter-oauth2client`](https://github.com/spice-framework/starter-oauth2client),
  and [`starter-oidc`](https://github.com/spice-framework/starter-oidc) own
  observability and OAuth2/OIDC integrations.
- [`starter-websocket`](https://github.com/spice-framework/starter-websocket),
  [`starter-grpc`](https://github.com/spice-framework/starter-grpc), and
  [`starter-kafka`](https://github.com/spice-framework/starter-kafka) own
  independently gated real-time, RPC, and broker integrations.
- [`development`](https://github.com/spice-framework/development) owns
  cross-repository workspace, compatibility, coordinated verification, and the
  central deterministic starter-release renderer/signer.
- [`.github`](https://github.com/spice-framework/.github) owns organization
  governance and reusable verification and signed-library-release workflows.

Each active starter has its own product gate and real-system acceptance where
applicable. All ten use the same immutable central source-release workflow,
distinct committed Ed25519 trust anchors, separate protected signing and
publication approvals, and restricted immutable release tags; copied local
release builders have been retired. This is a statement about repository and
release-infrastructure readiness. Consult each repository's Releases page for
what is actually published; an in-flight preview run is not advertised as a
completed release.

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

Spice is pre-1.0. Compatibility declarations and reference-application matrices
are pinned consumer contracts, not aliases for the latest repository heads.
Review both the declared compatibility and published release before depending
on a component, and use private vulnerability reporting for security issues.
