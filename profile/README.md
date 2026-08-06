<p align="center">
  <img src="assets/spice-framework-hero.png" alt="Spice Framework — Go-native application development. Compile-time wiring. Deterministic Go. No runtime magic." width="100%">
</p>

<p><sub><strong>START HERE</strong></sub></p>

<table>
  <tr>
    <td align="center" width="25%">
      <strong><a href="https://github.com/spice-framework/spice">Framework</a></strong><br>
      <sub>Runtime &amp; public SDK</sub>
    </td>
    <td align="center" width="25%">
      <strong><a href="https://github.com/spice-framework/toolchain">Toolchain</a></strong><br>
      <sub>Compiler, CLI &amp; LSP</sub>
    </td>
    <td align="center" width="25%">
      <strong><a href="https://github.com/spice-framework/spice/blob/main/docs/getting-started.md">Quickstart</a></strong><br>
      <sub>Create your first app</sub>
    </td>
    <td align="center" width="25%">
      <strong><a href="https://github.com/spice-framework/spice/blob/main/ROADMAP.md">Roadmap</a></strong><br>
      <sub>See what is next</sub>
    </td>
  </tr>
</table>

## Core repositories

<table>
  <tr>
    <td width="33%" valign="top">
      <h3><a href="https://github.com/spice-framework/spice">spice</a></h3>
      <p>The framework runtime and public SDK contracts for modular production services.</p>
      <p><sub>VALID GO · SMALL RUNTIME</sub></p>
    </td>
    <td width="33%" valign="top">
      <h3><a href="https://github.com/spice-framework/toolchain">toolchain</a></h3>
      <p>The compiler, deterministic generator, CLI, LSP, and independent release verifier.</p>
      <p><sub>COMPILE TIME · DETERMINISTIC</sub></p>
    </td>
    <td width="33%" valign="top">
      <h3><a href="https://github.com/spice-framework/spice-agent">spice-agent</a></h3>
      <p>The experimental Spice-native agent kernel, public SDK, and generated extension graph.</p>
      <p><sub>EXPERIMENTAL · GENERATED GRAPH</sub></p>
    </td>
  </tr>
</table>

## Ecosystem

<table>
  <tr>
    <td width="33%" valign="top">
      <h3>Starters</h3>
      <p>
        <a href="https://github.com/spice-framework/starter-postgres">PostgreSQL</a> ·
        <a href="https://github.com/spice-framework/starter-mysql">MySQL</a> ·
        <a href="https://github.com/spice-framework/starter-redis">Redis</a> ·
        <a href="https://github.com/spice-framework/starter-smtp">SMTP</a>
      </p>
      <p>
        <a href="https://github.com/spice-framework/starter-otel">OpenTelemetry</a> ·
        <a href="https://github.com/spice-framework/starter-oauth2client">OAuth2 client</a> ·
        <a href="https://github.com/spice-framework/starter-oidc">OIDC</a>
      </p>
      <p>
        <a href="https://github.com/spice-framework/starter-websocket">WebSocket</a> ·
        <a href="https://github.com/spice-framework/starter-grpc">gRPC</a> ·
        <a href="https://github.com/spice-framework/starter-kafka">Kafka</a>
      </p>
    </td>
    <td width="33%" valign="top">
      <h3>Developer tools</h3>
      <p><a href="https://github.com/spice-framework/goland">GoLand</a><br><sub>Annotation editing, navigation, run &amp; debug</sub></p>
      <p><a href="https://github.com/spice-framework/zed">Zed</a><br><sub>Shared Spice language-server integration</sub></p>
      <p><a href="https://github.com/spice-framework/development">Development</a><br><sub>Cross-repository compatibility and release tooling</sub></p>
    </td>
    <td width="33%" valign="top">
      <h3>Reference apps</h3>
      <p><a href="https://github.com/spice-framework/petclinic">Petclinic</a><br><sub>Standalone Spring Petclinic proof</sub></p>
      <p><a href="https://github.com/spice-framework/commerce">Commerce</a><br><sub>Production-shaped modular application</sub></p>
      <p><a href="https://github.com/spice-framework/spice-agent-coding">Spice Agent Coding</a><br><sub>SDK-first end-to-end agent proof</sub></p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td align="center" width="25%"><strong>Valid Go source</strong><br><sub>Ordinary tooling keeps working</sub></td>
    <td align="center" width="25%"><strong>Committed generated Go</strong><br><sub>No compiler at runtime</sub></td>
    <td align="center" width="25%"><strong>Explicit dependencies</strong><br><sub>Typed and reflection-free</sub></td>
    <td align="center" width="25%"><strong>Pre-1.0</strong><br><sub>Evidence-backed maturity</sub></td>
  </tr>
</table>

<details>
  <summary><strong>Agent extensions and the complete repository map</strong></summary>
  <br>

  The independently versioned agent extensions are
  <a href="https://github.com/spice-framework/spice-agent-provider-openai">OpenAI Responses</a>,
  <a href="https://github.com/spice-framework/spice-agent-tools-coding">coding tools</a>, and
  <a href="https://github.com/spice-framework/spice-agent-tui">the terminal UI</a>.
  The <a href="https://github.com/spice-framework/.github"><code>.github</code></a>
  repository owns organization governance and reusable verification and signed-release workflows.

  Every active starter has its own product gate and real-system acceptance where applicable.
  Compatibility declarations and reference-application matrices are pinned consumer contracts,
  not aliases for the latest repository heads. Check each repository's Releases page before
  depending on a component.

  The dated <a href="https://github.com/spice-framework/development/blob/main/docs/spice-agent-phase-0.md">Spice Agent Phase 0 compatibility snapshot</a>
  records exact commits for all five agent repositories, their selected module pins,
  dependency-ordered local verification, and the limits of macOS cross-compilation.
  The canonical implementation ledger remains in <a href="https://github.com/spice-framework/spice-agent/tree/main/docs/implementation"><code>spice-agent</code></a>.
</details>

<p align="center">
  <a href="https://github.com/spice-framework/spice/blob/main/docs/getting-started.md"><strong>Get started</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/spice-framework/spice/tree/main/docs"><strong>Read the docs</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/spice-framework/.github/blob/main/CONTRIBUTING.md"><strong>Contribute</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/spice-framework/.github/blob/main/SECURITY.md"><strong>Security</strong></a>
</p>
