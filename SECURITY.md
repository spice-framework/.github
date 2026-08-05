# Security Policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's private
vulnerability reporting on the affected Spice repository. If repository
routing is unclear, report it privately through
`spice-framework/spice` after that repository becomes canonical; during the
migration, use `StevenBuglione/spice`.

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
