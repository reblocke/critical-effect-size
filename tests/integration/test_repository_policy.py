from __future__ import annotations

import json
import subprocess
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_makefile_exposes_required_commands() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

    for target in [
        "stage-web:",
        "fmt:",
        "fmt-check:",
        "lint:",
        "test:",
        "e2e:",
        "verify:",
        "serve:",
        "clean:",
    ]:
        assert target in makefile


def test_ci_and_pages_use_repository_targets() -> None:
    ci = (PROJECT_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    pages = (PROJECT_ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")

    assert "make fmt-check" in ci
    assert "make lint" in ci
    assert "make test" in ci
    assert "make e2e" in ci
    assert "make e2e-webkit-smoke" in ci
    assert "make stage-web" in pages
    assert "web" in pages


def test_generated_stage_is_ignored_and_not_tracked() -> None:
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "web/assets/py/" in gitignore
    assert (
        subprocess.run(
            ["git", "check-ignore", "web/assets/py/manifest.json"],
            cwd=PROJECT_ROOT,
            check=False,
        ).returncode
        == 0
    )
    assert (
        subprocess.run(
            ["git", "ls-files", "web/assets/py"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        == ""
    )


def test_initialized_identity_author_license_and_release_metadata_are_exact() -> None:
    identity = json.loads((PROJECT_ROOT / ".template-identity.json").read_text(encoding="utf-8"))
    project = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    license_text = (PROJECT_ROOT / "LICENSE").read_text(encoding="utf-8")
    citation = (PROJECT_ROOT / "CITATION.cff").read_text(encoding="utf-8")

    assert identity == {
        "initialized": True,
        "schema_version": 1,
        "values": {
            "app_title": "Wald Critical Effect Size",
            "description": (
                "Exact one-parameter Wald detectability and critical-effect calculations"
            ),
            "distribution_name": "critical-effect-size",
            "import_name": "critical_effect_size",
            "repository_name": "critical-effect-size",
        },
    }
    assert project["authors"] == [{"name": "Brian Locke"}]
    assert project["maintainers"] == [{"name": "Brian Locke"}]
    assert project["license"] == "MIT"
    assert "Copyright (c) 2026 Brian Locke" in license_text
    assert "title: Wald Critical Effect Size" in citation
    assert "given-names: Brian" in citation
    assert "family-names: Locke" in citation
    assert "date-released: 2026-07-30" in citation


def test_public_docs_have_no_unresolved_template_prompts() -> None:
    paths = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "CHANGELOG.md",
        PROJECT_ROOT / "CITATION.cff",
        PROJECT_ROOT / "llms.txt",
        *(PROJECT_ROOT / "docs").rglob("*.md"),
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)

    assert "AUTHOR ACTION REQUIRED" not in text
    assert "replace-me demonstration" not in text
    assert "docs/TEMPLATE_USAGE.md" not in text
    provenance = (PROJECT_ROOT / "docs" / "PROVENANCE.md").read_text(encoding="utf-8")
    assert "a360bde95c192d8de4f9a3b531e73600ebf3d8b8" in provenance
    assert "6a6c8c33cbef24b5dcbd35706d2292d9d3e5e359" in provenance
