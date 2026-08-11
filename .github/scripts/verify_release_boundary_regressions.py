"""Mutation regressions for the keyless Go release workflow validators."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
BOOTSTRAP_STEP = "      - name: Bootstrap candidate-owned pinned tools without release authority\n"
OFFLINE_STEP = "      - name: Exercise candidate-owned release checks offline\n"
EXECUTE_JOB = "\n  execute:\n"
ATTEST_JOB = "\n  attest:\n"
VERIFY_ATTESTATION_JOB = "\n  verify_attestation:\n"
DEVELOPMENT_PIN = "678a8d7ce5b20d9f2509f089b918154894064fc1"
TOOLCHAIN_PIN = "93547dc3053b3da2dd4a2791bbc881217a9a50d7"
STALE_DEVELOPMENT_PIN = "6210baa460975be0bfcb12c919cab307da8c3f46"
STALE_TOOLCHAIN_PIN = "0bb834c688ae42865a65deb9b8c00d033d359c9d"


def fail(message: str) -> None:
    raise SystemExit(f"keyless release validator regression failed: {message}")


def load_validator(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        fail(f"cannot load validator {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def section(text: str, start_marker: str, end_marker: str) -> tuple[int, int, str]:
    start = text.find(start_marker)
    if start < 0:
        fail(f"missing mutation start marker {start_marker!r}")
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        fail(f"missing mutation end marker {end_marker!r}")
    return start, end, text[start:end]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        fail(f"{label} mutation expected one match, found {text.count(old)}")
    return text.replace(old, new, 1)


def mutations(text: str) -> tuple[tuple[str, str], ...]:
    bootstrap_start, offline_start, bootstrap = section(text, BOOTSTRAP_STEP, OFFLINE_STEP)
    render_marker = "\n  render:\n"
    _, render_start, offline = section(text, OFFLINE_STEP, render_marker)

    missing_bootstrap = text[:bootstrap_start] + text[offline_start:]
    network_enabled_offline = text[:offline_start] + offline.replace(
        'GOPROXY: "off"',
        "GOPROXY: https://proxy.golang.org",
        1,
    ) + text[render_start:]
    reordered_candidate_steps = (
        text[:bootstrap_start] + offline + bootstrap + text[render_start:]
    )
    reordered_authority = replace_once(
        text,
        "    needs: verify_attestation\n",
        "    needs: attest\n",
        "publication authority order",
    )

    validate_start, validate_end, validate = section(
        text,
        "\n  validate:\n",
        render_marker,
    )
    weakened_validate = replace_once(
        validate,
        "    permissions:\n      contents: read\n",
        "    permissions:\n      contents: write\n",
        "candidate permissions",
    )
    weakened_permissions = text[:validate_start] + weakened_validate + text[validate_end:]

    stale_development_pin = replace_once(
        text,
        f"TRUSTED_DEVELOPMENT_COMMIT: {DEVELOPMENT_PIN}",
        f"TRUSTED_DEVELOPMENT_COMMIT: {STALE_DEVELOPMENT_PIN}",
        "trusted development pin",
    )
    stale_toolchain_pin = replace_once(
        text,
        f"TRUSTED_TOOLCHAIN_COMMIT: {TOOLCHAIN_PIN}",
        f"TRUSTED_TOOLCHAIN_COMMIT: {STALE_TOOLCHAIN_PIN}",
        "trusted toolchain pin",
    )

    return (
        ("missing bootstrap", missing_bootstrap),
        ("network-enabled offline verification", network_enabled_offline),
        ("reordered candidate steps", reordered_candidate_steps),
        ("reordered publication authority", reordered_authority),
        ("weakened candidate permissions", weakened_permissions),
        ("stale trusted development pin", stale_development_pin),
        ("stale trusted toolchain pin", stale_toolchain_pin),
    )


def distribution_mutations(text: str) -> tuple[tuple[str, str], ...]:
    execute_start, attest_start, execute = section(text, EXECUTE_JOB, ATTEST_JOB)
    _, verify_attestation_start, attest = section(text, ATTEST_JOB, VERIFY_ATTESTATION_JOB)

    missing_execute = text[:execute_start] + text[attest_start:]
    reordered_execute = (
        text[:execute_start]
        + attest
        + execute
        + text[verify_attestation_start:]
    )
    bypassed_execution = replace_once(
        text,
        "    needs: [verify, execute]\n",
        "    needs: verify\n",
        "attestation execution dependency",
    )
    moving_windows_runner = replace_once(
        text,
        "          - runner: windows-2025\n",
        "          - runner: windows-latest\n",
        "execution Windows runner",
    )
    weakened_execute = replace_once(
        execute,
        "    permissions:\n      contents: read\n",
        "    permissions:\n      contents: write\n",
        "execution permissions",
    )
    weakened_execute_permissions = (
        text[:execute_start] + weakened_execute + text[attest_start:]
    )
    wrong_artifact = replace_once(
        execute,
        "          name: go-distribution-release-verified\n",
        "          name: go-distribution-release-rendered\n",
        "execution artifact identity",
    )
    wrong_execution_artifact = text[:execute_start] + wrong_artifact + text[attest_start:]
    wrong_subject_count = replace_once(
        execute,
        '          test "$(find "$artifacts" -maxdepth 1 -type f | wc -l)" -eq 9\n',
        '          test "$(find "$artifacts" -maxdepth 1 -type f | wc -l)" -eq 8\n',
        "execution artifact count",
    )
    weakened_subject_count = text[:execute_start] + wrong_subject_count + text[attest_start:]
    wrong_target = replace_once(
        execute,
        "run: make -C candidate verify-release-artifacts\n",
        "run: make -C candidate verify-release\n",
        "execution target",
    )
    wrong_execution_target = text[:execute_start] + wrong_target + text[attest_start:]
    legacy_environment_names = replace_once(
        execute,
        "          SPICE_DISTRIBUTION_EPHEMERAL_RUNNER: ${{ matrix.ephemeral_runner }}\n"
        "          SPICE_DISTRIBUTION_VERIFIED_ARTIFACT_DIR: ${{ runner.temp }}/go-distribution-release-verified\n",
        "          SPICE_AGENT_EPHEMERAL_RUNNER: ${{ matrix.ephemeral_runner }}\n"
        "          SPICE_AGENT_VERIFIED_ARTIFACT_DIR: ${{ runner.temp }}/go-distribution-release-verified\n",
        "legacy installed-execution environment names",
    )
    old_environment_contract = (
        text[:execute_start] + legacy_environment_names + text[attest_start:]
    )
    missing_ephemeral_name = replace_once(
        execute,
        "          SPICE_DISTRIBUTION_EPHEMERAL_RUNNER: ${{ matrix.ephemeral_runner }}\n",
        "",
        "generic ephemeral-runner environment name",
    )
    missing_generic_ephemeral_name = (
        text[:execute_start] + missing_ephemeral_name + text[attest_start:]
    )
    missing_artifact_name = replace_once(
        execute,
        "          SPICE_DISTRIBUTION_VERIFIED_ARTIFACT_DIR: ${{ runner.temp }}/go-distribution-release-verified\n",
        "",
        "generic verified-artifact environment name",
    )
    missing_generic_artifact_name = (
        text[:execute_start] + missing_artifact_name + text[attest_start:]
    )
    missing_windows_acknowledgement = replace_once(
        execute,
        '            ephemeral_runner: "1"\n',
        '            ephemeral_runner: ""\n',
        "ephemeral Windows acknowledgement",
    )
    missing_windows_ack = (
        text[:execute_start] + missing_windows_acknowledgement + text[attest_start:]
    )
    networked_execute = replace_once(
        execute,
        '          GOPRIVATE: ""\n',
        '          GOPRIVATE: ""\n          GOPROXY: https://proxy.golang.org\n',
        "execution network policy",
    )
    network_enabled_execute = text[:execute_start] + networked_execute + text[attest_start:]
    secret_execute = replace_once(
        execute,
        '          GONOSUMDB: ""\n',
        '          GONOSUMDB: ""\n          GH_TOKEN: ${{ secrets.RELEASE_TOKEN }}\n',
        "execution secret",
    )
    secret_enabled_execute = text[:execute_start] + secret_execute + text[attest_start:]
    clean_step = (
        "      - name: Require the candidate checkout to remain clean\n"
        "        if: ${{ always() }}\n"
        "        shell: bash\n"
        "        run: test \"$(git -C candidate status --porcelain=v1 --untracked-files=all)\" = \"\"\n"
    )
    missing_cleanliness = replace_once(
        text,
        clean_step,
        "",
        "execution cleanliness",
    )

    return (
        ("missing execution job", missing_execute),
        ("reordered execution job", reordered_execute),
        ("attestation bypasses execution", bypassed_execution),
        ("moving Windows execution runner", moving_windows_runner),
        ("weakened execution permissions", weakened_execute_permissions),
        ("wrong execution artifact", wrong_execution_artifact),
        ("weakened execution subject count", weakened_subject_count),
        ("wrong candidate execution target", wrong_execution_target),
        ("legacy installed-execution environment names", old_environment_contract),
        ("missing generic ephemeral-runner environment name", missing_generic_ephemeral_name),
        ("missing generic verified-artifact environment name", missing_generic_artifact_name),
        ("missing Windows ephemeral acknowledgement", missing_windows_ack),
        ("network-enabled execution", network_enabled_execute),
        ("secret-enabled execution", secret_enabled_execute),
        ("missing execution cleanliness", missing_cleanliness),
    )


def require_rejected(module: ModuleType, path: Path, label: str, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    module.WORKFLOW = path
    try:
        module.main()
    except SystemExit:
        return
    fail(f"{path.name}: validator accepted {label}")


def main() -> None:
    validators = (
        ROOT / ".github" / "scripts" / "verify_go_module_release.py",
        ROOT / ".github" / "scripts" / "verify_go_distribution_release.py",
    )
    with tempfile.TemporaryDirectory(prefix="spice-release-validator-") as temporary:
        temporary_root = Path(temporary)
        for validator_path in validators:
            module = load_validator(validator_path)
            workflow = module.WORKFLOW
            if not workflow.is_absolute():
                workflow = ROOT / workflow
            original = workflow.read_text(encoding="utf-8")
            cases = mutations(original)
            if validator_path.name == "verify_go_distribution_release.py":
                cases += distribution_mutations(original)
            for label, mutated in cases:
                require_rejected(
                    module,
                    temporary_root / f"{validator_path.stem}-{label.replace(' ', '-')}.yml",
                    label,
                    mutated,
                )


if __name__ == "__main__":
    main()
