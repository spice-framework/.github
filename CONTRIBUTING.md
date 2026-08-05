# Contributing to Spice

Thank you for helping improve Spice. Start with the issue tracker of the
repository that owns the behavior. For cross-repository changes, open the
coordination issue in `spice-framework/development`.

## Before implementation

Describe the developer outcome, affected public contract, compatibility and
security implications, and the verification evidence the change will add.
Public contracts or architecture changes normally require an ADR or RFC.

## Change requirements

- Keep source valid, idiomatic Go and generated output deterministic.
- Add meaningful success, failure, boundary, cancellation, and ordering tests
  where applicable.
- Update documentation, examples, compatibility metadata, and benchmarks when
  behavior changes.
- Never hand-edit generated or vendored content.
- Run the repository-owned fast gate while iterating and its complete local
  verification command on the exact commit proposed for merge.
- Report commands actually run; do not describe an unexecuted check as green.

External contributions use conventional issues and pull requests. Maintainers
may use a documented direct-main workflow while the project is in single-writer
mode, but the same local gate and reviewable-commit standard applies.

## Commit and pull request scope

Keep commits bounded and independently understandable. A pull request should
state what changed, why, public compatibility effects, tests and executable
evidence, and known follow-up work. Repository extraction must preserve useful
history and must not delete the prior durable source before the new repository
and a clean-room consumer are green.
