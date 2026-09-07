from __future__ import annotations

import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_wheel_contains_package() -> None:
    """The 0.1.0 scaffold wheel shipped metadata only — no package code.

    Root cause: ``[tool.hatch.build.targets.wheel] packages = ["scapy_mcp"]``
    while the code lived at ``src/scapy_mcp``, so hatchling collected nothing.
    This test is the regression guard for the flat-layout fix.
    """
    result = subprocess.run(
        [sys.executable, "-m", "hatchling", "build", "-t", "wheel"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    wheels = sorted((REPO_ROOT / "dist").glob("*.whl"))
    assert wheels, "no wheel produced"
    with zipfile.ZipFile(wheels[-1]) as zf:
        names = zf.namelist()
    assert any(n.endswith("scapy_mcp/__init__.py") for n in names), names
    assert not any(n.startswith("src/") for n in names), names


def test_coverage_floor_is_70() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    addopts = pyproject["tool"]["pytest"]["ini_options"]["addopts"]
    assert "--cov-fail-under=85" in addopts
