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
DEVELOPMENT_PIN = "a90925bdbd671ed7941af1d3b8c33abeca20dfcb"
TOOLCHAIN_PIN = "a0ddf9a940cbe72ddc13c7a104418fe50a6f58aa"
STALE_DEVELOPMENT_PIN = "d0f88db000acb566b72499c736c9134909ee7912"
STALE_TOOLCHAIN_PIN = "4a97e78c3495c5f61bd4e25111722855184a786c"


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
            for label, mutated in mutations(original):
                require_rejected(
                    module,
                    temporary_root / f"{validator_path.stem}-{label.replace(' ', '-')}.yml",
                    label,
                    mutated,
                )


if __name__ == "__main__":
    main()
