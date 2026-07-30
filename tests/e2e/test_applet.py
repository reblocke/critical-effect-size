from __future__ import annotations

import struct
from pathlib import Path

from playwright.sync_api import Page, expect


def _ready(page: Page, app_url: str) -> None:
    page.goto(app_url)
    expect(page.locator("#runtime-status")).to_have_attribute(
        "data-state",
        "ready",
        timeout=120_000,
    )


def _png_dimensions(path: Path) -> tuple[int, int]:
    contents = path.read_bytes()
    assert contents.startswith(b"\x89PNG\r\n\x1a\n")
    return struct.unpack(">II", contents[16:24])


def test_worker_loads_and_calculates(page: Page, app_url: str) -> None:
    _ready(page, app_url)

    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Calculation complete.")
    expect(page.locator("#result-summary")).to_contain_text("exact 80% critical effect(s)")
    expect(page.locator("#current-critical-summary")).to_contain_text("negative: 0.6408734")
    expect(page.locator("#current-critical-summary")).to_contain_text("positive: 1.560371")
    expect(page.locator("#legacy-summary")).to_contain_text("not the exact solution")
    expect(page.locator("#meaningful-summary")).to_contain_text("72.35%")
    expect(page.locator("#reference-table tbody tr")).to_have_count(12)
    expect(page.locator("#plot .plot-container")).to_be_visible()
    expect(page.locator("#plot .gtitle")).to_contain_text("Exact selected-claim probability")
    for label in [
        "Exact current (negative)",
        "Exact current (positive)",
        "Null",
        "Meaningful scenario",
    ]:
        expect(page.locator("#plot .textpoint").filter(has_text=label)).to_be_visible()
    for label in [
        "Target 80%",
        "Reported 95% CI context",
        "Observed estimate (context only)",
    ]:
        expect(page.locator("#plot .annotation-text").filter(has_text=label)).to_be_visible()
    expect(page.locator("#runtime-versions")).to_contain_text("critical-effect-size 0.1.1")
    expect(page.locator("#runtime-versions")).to_contain_text("wald-inference 0.4.1")
    expect(page.locator("#core-version")).to_have_text("Core: wald-inference 0.4.1")


def test_direct_se_additive_mode_and_information_scenario(
    page: Page,
    app_url: str,
) -> None:
    _ready(page, app_url)
    page.locator("#effect-type").select_option("mean_difference")
    page.locator("#precision-mode").select_option("direct_se")
    expect(page.locator("#ci-fields")).to_be_hidden()
    expect(page.locator("#se-fields")).to_be_visible()
    page.locator("#standard-error").fill("0.2")
    page.locator("#observed-estimate").fill("")
    page.locator("#information-multiplier").fill("4")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Calculation complete.")
    expect(page.locator("#precision-summary")).to_contain_text("Current working-scale SE: 0.2")
    expect(page.locator("#precision-summary")).to_contain_text("Scenario SE: 0.1")
    expect(page.locator("#current-critical-summary")).to_contain_text("positive: 0.5603164")
    expect(page.locator("#scenario-critical-summary")).to_contain_text("positive: 0.2801582")
    expect(page.locator("#warnings-list")).to_contain_text(
        "not automatically a sample-size multiplier"
    )


def test_one_sided_negative_has_only_relevant_direction(
    page: Page,
    app_url: str,
) -> None:
    _ready(page, app_url)
    page.locator("#selection-rule").select_option("one_sided_negative_p_lt_alpha")
    page.locator("#meaningful-effect").fill("0.7")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Calculation complete.")
    expect(page.locator("#current-critical-summary")).to_contain_text("negative:")
    expect(page.locator("#current-critical-summary")).not_to_contain_text("positive:")
    expect(page.locator("#legacy-section")).to_be_hidden()
    expect(page.locator("#reference-table tbody tr")).to_have_count(6)
    expect(page.locator("#rule-summary")).to_contain_text("One-sided negative")


def test_validation_error_is_sanitized_and_worker_recovers(
    page: Page,
    app_url: str,
) -> None:
    _ready(page, app_url)
    page.locator("#alpha").fill("1")
    page.locator("#calculate").click()

    expect(page.locator("#error-summary")).to_contain_text("Alpha must be between 0 and 1")
    expect(page.locator("#runtime-status")).to_have_attribute("data-state", "error")
    expect(page.locator("#error-summary")).not_to_contain_text("Traceback")
    expect(page.locator("#error-summary")).not_to_contain_text("/Users/")

    page.locator("#alpha").fill("0.05")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Calculation complete.")
    expect(page.locator("#result-summary")).to_contain_text("exact 80%")


def test_input_errors_link_to_controls(page: Page, app_url: str) -> None:
    _ready(page, app_url)
    page.locator("#target-probability").fill("")
    page.locator("#calculate").click()

    expect(page.locator("#error-summary")).to_be_visible()
    expect(page.locator("#error-summary a")).to_have_attribute(
        "href",
        "#target-probability",
    )
    page.locator("#error-summary a").click()
    expect(page.locator("#target-probability")).to_be_focused()
    expect(page.locator("#target-probability")).to_have_attribute(
        "aria-invalid",
        "true",
    )


def test_changed_inputs_clear_stale_result(page: Page, app_url: str) -> None:
    _ready(page, app_url)
    page.locator("#calculate").click()
    expect(page.locator("#runtime-status")).to_have_text("Calculation complete.")
    expect(page.locator("#result")).to_be_visible()

    page.locator("#target-probability").fill("0.9")

    expect(page.locator("#result")).to_be_hidden()
    expect(page.locator(".empty-state")).to_be_visible()
    expect(page.locator("#runtime-status")).to_have_text(
        "Inputs changed. Calculate to update the result."
    )


def test_user_display_range_discloses_omitted_markers(
    page: Page,
    app_url: str,
) -> None:
    _ready(page, app_url)
    page.get_by_text("Optional display range").click()
    page.locator("#display-min").fill("0.9")
    page.locator("#display-max").fill("1.1")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Calculation complete.")
    expect(page.locator("#warnings-list")).to_contain_text("requested display range omits")
    expect(page.locator("#warnings-list")).to_contain_text("Current exact critical effect")
    expect(page.locator("#figure-caption")).to_contain_text(
        "outside the user-requested display range"
    )


def test_csv_png_and_caption_exports(page: Page, app_url: str, tmp_path: Path) -> None:
    page.context.grant_permissions(
        ["clipboard-read", "clipboard-write"],
        origin=app_url.rstrip("/"),
    )
    _ready(page, app_url)
    page.locator("#calculate").click()
    expect(page.locator("#runtime-status")).to_have_text("Calculation complete.")

    with page.expect_download() as csv_info:
        page.locator("#export-csv").click()
    csv_download = csv_info.value
    csv_path = tmp_path / csv_download.suggested_filename
    csv_download.save_as(csv_path)
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == (
        "true_effect_display,true_effect_working,"
        "current_selected_claim_probability,scenario_selected_claim_probability"
    )
    assert len(lines) > 300
    assert csv_download.suggested_filename == ("wald-critical-effect-size-probability-curve.csv")

    for selector, suffix, dimensions in [
        ("#export-figure", "-figure.png", (1600, 1200)),
        ("#export-dashboard", "-dashboard.png", (1400, 1200)),
    ]:
        with page.expect_download(timeout=60_000) as png_info:
            page.locator(selector).click()
        download = png_info.value
        png_path = tmp_path / download.suggested_filename
        download.save_as(png_path)
        assert download.suggested_filename.endswith(suffix)
        assert _png_dimensions(png_path) == dimensions

    page.locator("#copy-caption").click()
    expect(page.locator("#runtime-status")).to_have_text("Caption copied.")
    clipboard = page.evaluate("navigator.clipboard.readText()")
    assert "Exact selected-claim probability" in clipboard
    assert "reported 95% CI shading" in clipboard
    assert "not evidence conditional on an observed dataset" in clipboard


def test_mobile_keyboard_and_privacy_smoke(page: Page, app_url: str) -> None:
    requests: list[tuple[str, str | None]] = []
    page.context.on(
        "request",
        lambda request: requests.append((request.url, request.post_data)),
    )
    page.set_viewport_size({"width": 390, "height": 844})
    _ready(page, app_url)
    initial_url = page.url
    page.locator("#meaningful-effect").fill("1.234567891")
    page.locator("#effect-type").focus()
    for selector in [
        "#precision-mode",
        "#ci-lower",
        "#ci-upper",
        "#observed-estimate",
        "#null-value",
        "#alpha",
        "#target-probability",
        "#selection-rule",
        "#meaningful-effect",
        "#information-multiplier",
    ]:
        page.keyboard.press("Tab")
        expect(page.locator(selector)).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("#runtime-status")).to_have_text("Calculation complete.")
    expect(page.locator("#result-summary")).to_contain_text("exact 80%")

    page.locator("#target-probability").fill("0.90")
    page.keyboard.press("Enter")
    expect(page.locator("#runtime-status")).to_have_text("Calculation complete.")
    expect(page.locator("#result-summary")).to_contain_text("exact 90%")

    assert page.url == initial_url
    assert page.evaluate("localStorage.length") == 0
    assert page.evaluate("sessionStorage.length") == 0
    assert page.evaluate("document.cookie") == ""
    assert (
        page.evaluate("indexedDB.databases ? indexedDB.databases().then((rows) => rows.length) : 0")
        == 0
    )
    serialized_requests = "\n".join(f"{url}\n{body or ''}" for url, body in requests)
    assert "1.234567891" not in serialized_requests
    expect(page.locator(".controls")).to_be_visible()
    expect(page.locator(".results")).to_be_visible()
    assert page.evaluate(
        "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )
