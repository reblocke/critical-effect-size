from __future__ import annotations

import hashlib
import json
import subprocess
import tomllib
from pathlib import Path

import pytest
from scripts.stage_browser_packages import StagingError, stage_browser_packages

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_URL = (
    "https://github.com/reblocke/wald-inference-core/releases/download/"
    "v0.4.1/wald_inference-0.4.1-py3-none-any.whl"
)
CORE_SHA256 = "d7272023f65088729d3ff997cab7cac57b84f22ac6108244ec2170434557d99b"


def _descriptor(files: list[dict[str, object]]) -> str:
    return "".join(
        f"{record['path']}\0{record['sha256']}\0{record['bytes']}\n"
        for record in sorted(files, key=lambda item: str(item["path"]))
    )


def test_stage_manifest_records_versions_provenance_files_and_hashes(
    tmp_path: Path,
) -> None:
    target = tmp_path / "py"
    manifest = stage_browser_packages(target, project_root=PROJECT_ROOT)

    assert json.loads((target / "manifest.json").read_text(encoding="utf-8")) == manifest
    assert manifest["schema_version"] == 1
    assert manifest["pyodide_version"] == "0.29.3"
    assert manifest["pyodide_packages"] == ["numpy", "scipy"]
    assert (
        manifest["source_commit"]
        == subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    app, core = manifest["packages"]
    assert {key: app[key] for key in ("role", "distribution", "import_name", "version")} == {
        "role": "app",
        "distribution": "critical-effect-size",
        "import_name": "critical_effect_size",
        "version": "0.1.1",
    }
    assert app["artifact_url"] is None
    assert app["artifact_sha256"] is None
    assert {key: core[key] for key in ("role", "distribution", "import_name", "version")} == {
        "role": "core",
        "distribution": "wald-inference",
        "import_name": "wald_inference",
        "version": "0.4.1",
    }
    assert core["artifact_url"] == CORE_URL
    assert core["artifact_sha256"] == CORE_SHA256

    all_files = [record for package in (app, core) for record in package["files"]]
    for record in all_files:
        contents = (target / record["path"]).read_bytes()
        assert len(contents) == record["bytes"]
        assert hashlib.sha256(contents).hexdigest() == record["sha256"]
    for package in (app, core):
        descriptor = _descriptor(package["files"])
        assert hashlib.sha256(descriptor.encode()).hexdigest() == package["package_sha256"]
    assert hashlib.sha256(_descriptor(all_files).encode()).hexdigest() == manifest["bundle_sha256"]


def test_lock_uses_the_exact_released_core_wheel_and_checksum() -> None:
    lock = tomllib.loads((PROJECT_ROOT / "uv.lock").read_text(encoding="utf-8"))
    [core] = [package for package in lock["package"] if package["name"] == "wald-inference"]

    assert core["version"] == "0.4.1"
    assert core["source"] == {"url": CORE_URL}
    assert core["wheels"] == [
        {
            "url": CORE_URL,
            "hash": f"sha256:{CORE_SHA256}",
        }
    ]


def test_stage_is_deterministic_and_removes_stale_files(tmp_path: Path) -> None:
    target = tmp_path / "py"
    target.mkdir()
    (target / "stale.py").write_text("stale = True\n", encoding="utf-8")

    first = stage_browser_packages(target, project_root=PROJECT_ROOT)
    first_bytes = (target / "manifest.json").read_bytes()
    second = stage_browser_packages(target, project_root=PROJECT_ROOT)

    assert not (target / "stale.py").exists()
    assert second == first
    assert (target / "manifest.json").read_bytes() == first_bytes


def test_stage_fails_on_configured_version_mismatch(tmp_path: Path) -> None:
    config = tmp_path / "browser-stage.toml"
    source = (PROJECT_ROOT / "browser-stage.toml").read_text(encoding="utf-8")
    config.write_text(
        source.replace('version = "0.4.1"', 'version = "9.9.9"'),
        encoding="utf-8",
    )

    with pytest.raises(StagingError, match="expected '9.9.9'"):
        stage_browser_packages(
            tmp_path / "py",
            project_root=PROJECT_ROOT,
            config_path=config,
        )


def test_stage_fails_when_configured_core_checksum_differs_from_lock(
    tmp_path: Path,
) -> None:
    config = tmp_path / "browser-stage.toml"
    source = (PROJECT_ROOT / "browser-stage.toml").read_text(encoding="utf-8")
    config.write_text(source.replace(CORE_SHA256, "0" * 64), encoding="utf-8")

    with pytest.raises(StagingError, match="configured checksum"):
        stage_browser_packages(
            tmp_path / "py",
            project_root=PROJECT_ROOT,
            config_path=config,
        )
