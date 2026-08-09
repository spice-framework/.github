"""Regression checks for the reusable keyless Go-module release boundary."""

from pathlib import Path


WORKFLOW = Path(".github/workflows/go-module-release.yml")
DISABLED_PIN = "0000000000000000000000000000000000000000"
DEVELOPMENT_PIN = "67b9ca3f20793da881beeea05910042a81ad9877"
TOOLCHAIN_PIN = "83c2a7e41945f8e7ce187f5fb333158c4e6ff223"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"go-module-release trust-boundary check failed: {message}")


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

    require(
        "library-release" not in text,
        "generic module workflow must not reuse or modify the starter release path",
    )
    require("go-distribution-v1" not in text, "distribution release authority must remain separate")
    require(
        "RELEASE_PROFILE: go-module-v1" in contract,
        "workflow must be fixed to the generic Go-module profile",
    )
    require(
        "workflow_commit:\n"
        "        description: Immutable commit used in this reusable workflow's uses reference.\n"
        "        required: true" in contract,
        "caller must declare the exact reusable-workflow commit",
    )
    require(
        text.count("runs-on: ubuntu-24.04") == 6,
        "every release job must pin Ubuntu 24.04",
    )
    require("ubuntu-latest" not in text, "release jobs must not use moving runner labels")
    require(text.count("contents: write") == 1, "only publication may write contents")
    require(text.count("id-token: write") == 1, "only attestation may mint OIDC identity")
    require(
        text.count("attestations: write") == 1,
        "only attestation may persist provenance",
    )
    require(
        text.count("artifact-metadata: write") == 1,
        "only attestation may record artifact metadata",
    )
    require("secrets:" not in contract, "keyless release must accept no caller secrets")
    require("secrets: inherit" not in text, "release workflow must inherit no secrets")
    require(
        "SPICE_LIBRARY_RELEASE_SIGNING_KEY" not in text,
        "generic module release must not receive the starter signing key",
    )
    require(text.count("cache: false") == 3, "every Go setup must disable action caching")
    require(
        text.count("merge-base --is-ancestor") == 4,
        "all candidate-bearing phases must require origin/main ancestry",
    )
    require(
        text.count("persist-credentials: false") == 6,
        "every checkout must discard persisted workflow credentials",
    )
    require(
        text.count("go tool ") == 0,
        "release authority must never execute candidate-selected Go tools",
    )

    require("make -C candidate verify-release" in validate, "candidate gate is missing")
    require(
        '[[ "$REPOSITORY_VISIBILITY" == public ]]' in validate,
        "keyless public-good signing must reject non-public callers",
    )
    require(
        "GOPROXY: https://proxy.golang.org" in validate
        and "GOSUMDB: sum.golang.org" in validate,
        "only uncredentialed candidate validation may use authenticated public modules",
    )
    require(
        'GOPRIVATE: ""' in validate and 'GONOSUMDB: ""' in validate,
        "candidate validation must clear private-module exceptions",
    )
    require("id-token: write" not in validate, "candidate code must not receive OIDC")
    require("attestations: write" not in validate, "candidate code must not attest")
    require("contents: write" not in validate, "candidate code must not publish")
    require(
        "artifact-metadata: write" not in validate,
        "candidate code must not record artifact metadata",
    )

    require("needs: validate" in render, "rendering must follow candidate validation")
    require(
        "repository: spice-framework/development" in render,
        "rendering must use immutable organization-owned source",
    )
    require(
        "go-release render" in render and "go-release verify" in render,
        "renderer-owned deterministic module checks are incomplete",
    )
    require("-mod=vendor" in render and "-trimpath" in render, "renderer build is not reproducible")
    require(
        render.index("Validate immutable trusted implementation pins")
        < render.index("Check out inert exact candidate input"),
        "trusted pin validation must precede source checkout",
    )

    require("needs: render" in verify, "independent verification must follow rendering")
    require(
        "repository: spice-framework/toolchain" in verify,
        "independent verifier must come from toolchain",
    )
    require(
        "./cmd/spice-go-release-verify" in verify
        and '"$RUNNER_TEMP/trusted-bin/spice-go-release-verify"' in verify,
        "independent verifier command is not built and executed",
    )
    require("-mod=vendor" in verify and "-trimpath" in verify, "verifier build is not reproducible")
    require("id-token: write" not in verify, "artifact verifier must not mint OIDC identity")
    require("contents: write" not in verify, "artifact verifier must not publish")
    require(
        "artifact-metadata: write" not in verify,
        "artifact verifier must not record artifact metadata",
    )
    request = '-verified-output="$RUNNER_TEMP/go-module-release-verified"'
    require(request in verify, "verifier must own the trusted handoff directory")
    require(
        "path: ${{ runner.temp }}/go-module-release-verified/" in verify,
        "verification must upload only verifier-owned output",
    )
    require(
        "path: ${{ runner.temp }}/go-module-release-rendered/" not in verify,
        "untrusted renderer output must never cross the verification boundary",
    )

    require("needs: verify" in attest, "attestation must consume independent verification")
    require(
        "environment: release-attestation" in attest,
        "keyless signing must use its protected approval environment",
    )
    require(
        "name: go-module-release-verified" in attest,
        "attestation must receive only independently verified artifacts",
    )
    require(
        "actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6" in attest,
        "attestation action must be pinned to the reviewed immutable commit",
    )
    require("contents: write" not in attest, "attestation must not publish releases")
    require(
        "artifact-metadata: write" in attest,
        "actions/attest v4 requires narrowly scoped artifact metadata authority",
    )

    require(
        "needs: attest" in verify_attestation,
        "keyless verification must follow attestation",
    )
    require(
        "gh attestation verify" in verify_attestation,
        "portable Sigstore bundle must be independently authenticated",
    )
    for expected in (
        "--repo \"$GITHUB_REPOSITORY\"",
        "--bundle \"$bundle\"",
        "--cert-oidc-issuer https://token.actions.githubusercontent.com",
        "--signer-repo spice-framework/.github",
        "--signer-workflow spice-framework/.github/.github/workflows/go-module-release.yml",
        "--signer-digest \"$WORKFLOW_COMMIT\"",
        "--source-digest \"$GITHUB_SHA\"",
        "--source-ref \"$GITHUB_REF\"",
        "--deny-self-hosted-runners",
    ):
        require(expected in verify_attestation, f"missing attestation identity check {expected!r}")
    require("id-token: write" not in verify_attestation, "verification must not mint identity")
    require("contents: write" not in verify_attestation, "verification must not publish")
    require(
        "artifact-metadata: write" not in verify_attestation,
        "verification must not record artifact metadata",
    )

    require("needs: verify_attestation" in publish, "publication must follow keyless verification")
    require(
        "environment: release-publish" in publish,
        "publication must use a separate protected environment",
    )
    require(
        "name: go-module-release-authenticated" in publish,
        "publication must receive only authenticated artifacts",
    )
    require("id-token: write" not in publish, "publication must not mint OIDC identity")
    require("attestations: write" not in publish, "publication must not create provenance")
    require(
        "artifact-metadata: write" not in publish,
        "publication must not record artifact metadata",
    )
    require("resolve_remote_tag()" in publish, "publication must resolve annotated and lightweight tags")
    require(
        'test "$target_before" = "$GITHUB_SHA"' in publish
        and 'test "$target_after" = "$GITHUB_SHA"' in publish
        and 'test "$direct_after" = "$direct_before"' in publish,
        "remote tag identity must remain stable through publication",
    )
    require("GH_REPO: ${{ github.repository }}" in publish, "gh must target the caller repository")

    # Both halves of the trust boundary are pinned explicitly. Updating either
    # implementation requires a corresponding reviewed assertion here.
    require(
        f"TRUSTED_DEVELOPMENT_COMMIT: {DEVELOPMENT_PIN}" in contract,
        "renderer must remain pinned to the reviewed development commit",
    )
    require(
        f"TRUSTED_TOOLCHAIN_COMMIT: {TOOLCHAIN_PIN}" in contract,
        "verifier must remain pinned to the reviewed toolchain commit",
    )
    require(
        text.count(DISABLED_PIN) == 2
        and f'[[ "$TRUSTED_DEVELOPMENT_COMMIT" != {DISABLED_PIN} ]]' in render
        and f'[[ "$TRUSTED_TOOLCHAIN_COMMIT" != {DISABLED_PIN} ]]' in render,
        "enabled release workflow must retain only explicit fail-closed zero guards",
    )


if __name__ == "__main__":
    main()
