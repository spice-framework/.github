"""Regression checks for the reusable library-release trust boundary."""

from pathlib import Path


WORKFLOW = Path(".github/workflows/library-release.yml")
DEVELOPMENT_COMMIT = "4c308d1b9fda11cb2b045f2e0d9e1616d32d007d"
TOOLCHAIN_COMMIT = "71211498297c9ab77cc05c4844db5e64e0170896"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"library-release trust-boundary check failed: {message}")


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
    validate = job(text, "validate", "plan")
    plan = job(text, "plan", "sign")
    sign = job(text, "sign", "verify")
    verify = job(text, "verify", "publish")
    publish = job(text, "publish", None)

    require(DEVELOPMENT_COMMIT in text, "trusted development commit is not pinned")
    require(TOOLCHAIN_COMMIT in text, "trusted toolchain commit is not pinned")
    require("go tool " not in text, "candidate-selected go tool execution is forbidden")
    require(
        "ubuntu-latest" not in text,
        "release jobs must use the pinned runner image",
    )
    require(
        text.count("runs-on: ubuntu-24.04") == 5,
        "every release job must pin Ubuntu 24.04",
    )
    require(text.count("cache: false") == 4, "every Go job must disable action caching")
    require(text.count("contents: write") == 1, "only publication may write contents")
    require(
        text.count("SPICE_LIBRARY_RELEASE_SIGNING_KEY") == 1,
        "private-key secret must have one consumer",
    )
    require(
        text.count('[[ "$mode" == 100644 && "$object_type" == blob ]]') == 4,
        "trusted anchor must be a committed regular blob",
    )
    require(
        text.count('cmp -s "$public_key" <(git -C candidate show') == 4,
        "trusted anchor checkout bytes must match Git",
    )
    require(
        text.count('test ! -L "$current"') == 8,
        "every anchor component must be checked for symlinks",
    )
    require(
        text.count("merge-base --is-ancestor") == 5,
        "every candidate phase must require origin/main ancestry",
    )
    require(
        text.count("ref: ${{ env.TRUSTED_DEVELOPMENT_COMMIT }}") == 2,
        "renderer and signer must consume the immutable development pin",
    )
    require(
        text.count("ref: ${{ env.TRUSTED_TOOLCHAIN_COMMIT }}") == 1,
        "verifier must consume the immutable toolchain pin",
    )

    require(
        "make -C candidate verify-release" in validate,
        "candidate checks must run in uncredentialed validation",
    )
    require(
        "SPICE_LIBRARY_RELEASE_SIGNING_KEY" not in validate,
        "validation must not receive the private key",
    )
    require(
        "name: library-release-plan" not in validate,
        "candidate validation must not produce the trusted plan",
    )
    require(
        "make -C candidate" not in plan + sign + verify + publish,
        "candidate commands must not run after validation",
    )

    require("needs: validate" in plan, "trusted planning must follow candidate validation")
    require(
        "repository: spice-framework/development" in plan,
        "planning must use central renderer checkout",
    )
    require(
        '"$RUNNER_TEMP/trusted-bin/spice-dev"' in plan,
        "planning must run the trusted renderer binary",
    )
    require(
        "go build" in plan and "-C trusted/development" in plan,
        "planning renderer must build from trusted source",
    )
    require(
        "-mod=vendor" in plan and "-trimpath" in plan,
        "planning renderer build must be offline and reproducible",
    )

    require("needs: plan" in sign, "signing must consume the trusted plan")
    require("environment: release-signing" in sign, "signing must use its protected environment")
    require(
        "repository: spice-framework/development" in sign,
        "signing must use central signer checkout",
    )
    require(
        "go build" in sign and "-C trusted/development" in sign,
        "signer must build from trusted source",
    )
    require(
        "GOCACHE:" in sign and "GOMODCACHE:" in sign,
        "signer build caches must be isolated",
    )
    require(
        sign.index("Build trusted signer before exposing the private key")
        < sign.index("Materialize user-owned signing key")
        < sign.index("Sign exact-commit artifacts from inert candidate input"),
        "trusted signer must be built before private-key materialization",
    )

    require("needs: sign" in verify, "verification must follow signing")
    require(
        "repository: spice-framework/toolchain" in verify,
        "verification must use independent verifier checkout",
    )
    require("-C trusted/toolchain" in verify, "verifier must build from trusted source")
    require(
        "GOCACHE:" in verify and "GOMODCACHE:" in verify,
        "verifier build caches must be isolated",
    )
    require(
        '"$RUNNER_TEMP/trusted-bin/spice-library-release-verify"' in verify,
        "trusted verifier binary is not used",
    )
    require(
        "SPICE_LIBRARY_RELEASE_SIGNING_KEY" not in verify,
        "verification must not receive the private key",
    )

    require("needs: verify" in publish, "publication must follow independent verification")
    require(
        "environment: release-publish" in publish,
        "publication must use its protected environment",
    )
    require(
        "name: library-release-verified" in publish,
        "publication must receive verified artifacts",
    )
    require(
        "name: library-release-signed" not in publish,
        "publication must not receive unverified artifacts",
    )
    require(
        "SPICE_LIBRARY_RELEASE_SIGNING_KEY" not in publish,
        "publication must not receive the private key",
    )
    require(
        "resolve_remote_tag()" in publish,
        "publication must resolve lightweight and annotated remote tags",
    )
    require(
        "GH_REPO: ${{ github.repository }}" in publish,
        "gh must target the caller repository outside its checkout",
    )
    require(
        'test "$target_before" = "$GITHUB_SHA"' in publish
        and 'test "$target_after" = "$GITHUB_SHA"' in publish,
        "peeled remote tag target must be checked before and after publication",
    )
    require(
        'test "$direct_after" = "$direct_before"' in publish,
        "direct remote tag object must remain stable through publication",
    )


if __name__ == "__main__":
    main()
