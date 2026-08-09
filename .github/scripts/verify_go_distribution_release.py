"""Regression checks for the reusable keyless Go-distribution boundary."""

from pathlib import Path


WORKFLOW = Path(".github/workflows/go-distribution-release.yml")
DISABLED_PIN = "0000000000000000000000000000000000000000"
DEVELOPMENT_PIN = "67b9ca3f20793da881beeea05910042a81ad9877"
TOOLCHAIN_PIN = "83c2a7e41945f8e7ce187f5fb333158c4e6ff223"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            f"go-distribution-release trust-boundary check failed: {message}"
        )


def job(text: str, name: str, next_name: str | None) -> str:
    start_marker = f"\n  {name}:\n"
    start = text.find(start_marker)
    require(start >= 0, f"missing {name!r} job")
    if next_name is None:
        return text[start:]
    end = text.find(f"\n  {next_name}:\n", start + len(start_marker))
    require(end >= 0, f"missing {next_name!r} job after {name!r}")
    return text[start:end]


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    contract = text[: text.index("\njobs:")]
    validate = job(text, "validate", "render")
    render = job(text, "render", "verify")
    verify = job(text, "verify", "attest")
    attest = job(text, "attest", "verify_attestation")
    verify_attestation = job(text, "verify_attestation", "publish")
    publish = job(text, "publish", None)
    privileged = render + verify + attest + verify_attestation + publish

    require("library-release" not in text, "starter release path must remain separate")
    require("go-module-release.yml" not in text, "module release identity must remain separate")
    require(
        "RELEASE_PROFILE: go-distribution-v1" in contract,
        "workflow must be fixed to the distribution profile",
    )
    require(
        "workflow_commit:\n"
        "        description: Immutable commit used in this reusable workflow's uses reference.\n"
        "        required: true" in contract,
        "caller must repeat the immutable workflow commit",
    )
    require("secrets:" not in contract, "distribution workflow must accept no secrets")
    require("secrets: inherit" not in text, "distribution workflow must inherit no secrets")
    require(text.count("runs-on: ubuntu-24.04") == 6, "all jobs must pin Ubuntu 24.04")
    require("ubuntu-latest" not in text, "moving runner labels are forbidden")
    require(text.count("persist-credentials: false") == 6, "all checkouts must discard credentials")
    require(text.count("cache: false") == 3, "all Go setup actions must disable caches")
    require(text.count("contents: write") == 1, "only publication may write contents")
    require(text.count("id-token: write") == 1, "only attestation may mint OIDC")
    require(text.count("attestations: write") == 1, "only attestation may persist provenance")
    require(text.count("artifact-metadata: write") == 1, "only attestation may record metadata")
    require(text.count("merge-base --is-ancestor") == 4, "all candidate phases must require main ancestry")
    require("go tool " not in text and "go run " not in text, "candidate-selected execution is forbidden")
    require(text.count("make -C candidate verify-release") == 1, "candidate gate must run exactly once")
    require("make -C candidate" not in privileged, "candidate Make targets must remain unprivileged")

    require(
        '[[ "$REPOSITORY_VISIBILITY" == public ]]' in validate,
        "keyless public-good signing must reject non-public callers",
    )
    require(
        "GOPROXY: https://proxy.golang.org" in validate
        and "GOSUMDB: sum.golang.org" in validate,
        "only unprivileged validation may authenticate public modules",
    )
    require(
        'GOPRIVATE: ""' in validate and 'GONOSUMDB: ""' in validate,
        "candidate validation must clear private-module exceptions",
    )
    for authority in ("contents: write", "id-token: write", "attestations: write", "artifact-metadata: write"):
        require(authority not in validate, f"candidate validation received {authority}")

    require("needs: validate" in render, "render must follow validation")
    require("repository: spice-framework/development" in render, "renderer source is not central")
    require(
        "distribution-release render" in render
        and "distribution-release verify" in render,
        "renderer-owned distribution checks are incomplete",
    )
    require("-mod=vendor" in render and "-trimpath" in render, "renderer build is not reproducible")
    require(
        render.index("Validate immutable trusted implementation pins")
        < render.index("Check out inert exact candidate input"),
        "trusted pins must be validated before candidate checkout",
    )

    require("needs: render" in verify, "independent verification must follow rendering")
    require("repository: spice-framework/toolchain" in verify, "verifier source is not independent")
    require(
        "./cmd/spice-go-distribution-release-verify" in verify
        and '"$RUNNER_TEMP/trusted-bin/spice-go-distribution-release-verify"' in verify,
        "independent distribution verifier is not built and run",
    )
    require("-mod=vendor" in verify and "-trimpath" in verify, "verifier build is not reproducible")
    require(
        '-verified-output="$RUNNER_TEMP/go-distribution-release-verified"' in verify,
        "verifier must own the trusted handoff directory",
    )
    require(
        "path: ${{ runner.temp }}/go-distribution-release-verified/" in verify
        and "path: ${{ runner.temp }}/go-distribution-release-rendered/" not in verify,
        "only verifier-owned bytes may cross the verification boundary",
    )
    for authority in ("contents: write", "id-token: write", "artifact-metadata: write"):
        require(authority not in verify, f"artifact verification received {authority}")

    require("needs: verify" in attest, "attestation must follow independent verification")
    require("environment: release-attestation" in attest, "attestation environment is missing")
    require("name: go-distribution-release-verified" in attest, "attestation input is not verified")
    require('test "$(find "$artifacts" -maxdepth 1 -type f | wc -l)" -eq 9' in attest, "closed artifact count is not enforced")
    require("-size +536870912c" in attest, "per-artifact size bound is missing")
    require(
        "actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6" in attest,
        "attestation action is not pinned",
    )
    require("contents: write" not in attest, "attestation must not publish")

    require("needs: attest" in verify_attestation, "provenance authentication must follow attestation")
    for expected in (
        "gh attestation verify",
        '--repo "$GITHUB_REPOSITORY"',
        '--bundle "$bundle"',
        "--cert-oidc-issuer https://token.actions.githubusercontent.com",
        "--signer-repo spice-framework/.github",
        "--signer-workflow spice-framework/.github/.github/workflows/go-distribution-release.yml",
        '--signer-digest "$WORKFLOW_COMMIT"',
        '--source-digest "$GITHUB_SHA"',
        '--source-ref "$GITHUB_REF"',
        "--deny-self-hosted-runners",
    ):
        require(expected in verify_attestation, f"missing provenance identity check {expected!r}")
    for authority in ("contents: write", "id-token: write", "artifact-metadata: write"):
        require(authority not in verify_attestation, f"provenance verification received {authority}")

    require("needs: verify_attestation" in publish, "publication must follow provenance authentication")
    require("environment: release-publish" in publish, "publication environment is missing")
    require("name: go-distribution-release-authenticated" in publish, "publication input is not authenticated")
    require("GH_REPO: ${{ github.repository }}" in publish, "gh is not bound to the caller repository")
    require("resolve_remote_tag()" in publish, "publication must resolve remote tag identity")
    require(
        'test "$target_before" = "$GITHUB_SHA"' in publish
        and 'test "$target_after" = "$GITHUB_SHA"' in publish
        and 'test "$direct_after" = "$direct_before"' in publish,
        "remote tag identity must remain stable through publication",
    )
    for authority in ("id-token: write", "attestations: write", "artifact-metadata: write"):
        require(authority not in publish, f"publication received {authority}")

    require(
        f"TRUSTED_DEVELOPMENT_COMMIT: {DEVELOPMENT_PIN}" in contract,
        "renderer pin is not the reviewed development commit",
    )
    require(
        f"TRUSTED_TOOLCHAIN_COMMIT: {TOOLCHAIN_PIN}" in contract,
        "verifier pin is not the reviewed toolchain commit",
    )
    require(
        text.count(DISABLED_PIN) == 2
        and f'[[ "$TRUSTED_DEVELOPMENT_COMMIT" != {DISABLED_PIN} ]]' in render
        and f'[[ "$TRUSTED_TOOLCHAIN_COMMIT" != {DISABLED_PIN} ]]' in render,
        "trusted implementations must retain explicit zero-pin guards",
    )


if __name__ == "__main__":
    main()
