from __future__ import annotations

import re
from pathlib import Path

from wald_inference import EFFECT_SPECS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = PROJECT_ROOT / "web"


def test_worker_is_manifest_driven_and_verifies_before_import() -> None:
    worker = (WEB_ROOT / "pyodide_worker.js").read_text(encoding="utf-8")

    assert "manifest.packages" in worker
    assert "fileRecord.path" in worker
    assert "PACKAGE_FILES" not in worker
    assert "fetchVerifiedBundle()" in worker
    assert worker.index("await fetchVerifiedBundle()") < worker.index("importScripts(")
    assert worker.index("failed integrity verification") < worker.index("loadPyodide(")
    assert "if (bundle.manifest.pyodide_packages.length > 0)" in worker


def test_production_web_code_has_no_persistence_telemetry_or_input_urls() -> None:
    production = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(WEB_ROOT.rglob("*"))
        if path.is_file() and "assets/py" not in path.as_posix()
    )

    forbidden_fragments = [
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "document.cookie",
        "location.search",
        "location.hash",
        "sendBeacon",
        "gtag(",
        "analytics",
        "console.log",
    ]
    assert not [fragment for fragment in forbidden_fragments if fragment in production]
    assert "new URL(path" not in production
    for argument in re.findall(r"fetch\(([^,)]+)", production):
        assert "input" not in argument.lower()


def test_ui_contains_accessibility_scope_and_text_alternatives() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
    css = (WEB_ROOT / "styles.css").read_text(encoding="utf-8")

    assert 'aria-live="polite"' in html
    assert 'role="alert"' in html
    for control_id in [
        "effect-type",
        "precision-mode",
        "ci-lower",
        "ci-upper",
        "standard-error",
        "observed-estimate",
        "null-value",
        "alpha",
        "target-probability",
        "selection-rule",
        "meaningful-effect",
        "information-multiplier",
        "display-min",
        "display-max",
    ]:
        assert re.search(rf'<label for="{control_id}"', html)
    assert "<details>" in html and "<summary>" in html
    assert 'class="skip-link"' in html
    assert 'id="reference-table"' in html
    assert 'id="figure-caption"' in html
    assert ":focus-visible" in css
    assert "not a confidence bound" in html.lower()
    assert "not a validated clinical" in html.lower()
    assert "no backend, telemetry, persistence" in html.lower()


def test_browser_effect_options_match_the_released_core_registry() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
    effect_select = html.split('id="effect-type"', maxsplit=1)[1].split(
        "</select>",
        maxsplit=1,
    )[0]
    configured = re.findall(r'<option value="([a-z_]+)">', effect_select)

    assert configured == list(EFFECT_SPECS)
    for key, spec in EFFECT_SPECS.items():
        assert f'value="{key}">{spec.label}</option>' in effect_select


def test_exports_use_exact_focused_columns_and_separate_png_hooks() -> None:
    exports = (WEB_ROOT / "js" / "exports.js").read_text(encoding="utf-8")

    for key in [
        "true_effect_display",
        "true_effect_working",
        "current_selected_claim_probability",
        "scenario_selected_claim_probability",
    ]:
        assert f'key: "{key}"' in exports
    for excluded in [
        "relative_likelihood",
        "compatibility",
        "type_s",
        "type_m",
        "required_information",
    ]:
        assert f'key: "{excluded}"' not in exports
    assert "exportDashboardPng" in exports
    assert "exportFigurePng" in exports
    assert "copyText" in exports
    assert "filenameSlug" in exports


def test_ui_is_limited_to_the_three_detectability_rules() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
    rule_select = html.split('id="selection-rule"', maxsplit=1)[1].split(
        "</select>",
        maxsplit=1,
    )[0]

    for required in [
        "two_sided_p_lt_alpha",
        "one_sided_positive_p_lt_alpha",
        "one_sided_negative_p_lt_alpha",
    ]:
        assert required in rule_select
    for forbidden in [
        "ci_excludes_null_in_beneficial_direction",
        "estimate_exceeds_mcid_and_p_lt_alpha",
        "ci_excludes_mcid",
        "type_s",
        "type_m",
        "relative_likelihood",
    ]:
        assert forbidden not in html.lower()


def test_external_source_link_is_safe() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'href="https://journals.sagepub.com/doi/10.1177/25152459251335298"' in html
    source = html.split("journals.sagepub.com", maxsplit=1)[1].split(">", maxsplit=1)[0]
    assert 'target="_blank"' in source
    assert 'rel="noopener noreferrer"' in source
