from __future__ import annotations

import math
from statistics import NormalDist

import pytest

from critical_effect_size import CriticalEffectRequest, calculate

NORMAL = NormalDist()
Z975 = 1.959963984540054


def _request(**overrides: object) -> CriticalEffectRequest:
    payload: dict[str, object] = {
        "precision_mode": "direct_se",
        "effect_type": "mean_difference",
        "observed_estimate": None,
        "ci_lower": None,
        "ci_upper": None,
        "standard_error": 0.2,
        "null_value": 0.0,
        "alpha": 0.05,
        "selection_rule": "two_sided_p_lt_alpha",
        "target_probability": 0.8,
        "meaningful_effect": 0.5,
        "information_multiplier": 1.0,
        "display_min": None,
        "display_max": None,
    }
    payload.update(overrides)
    return CriticalEffectRequest.from_mapping(payload)


def _solution(response, *, precision: str, direction: str) -> dict[str, float]:
    return next(
        row
        for row in response.critical_effect[precision]["solutions"]
        if row["direction"] == direction
    )


@pytest.mark.parametrize(
    "selection_rule",
    [
        "two_sided_p_lt_alpha",
        "one_sided_positive_p_lt_alpha",
        "one_sided_negative_p_lt_alpha",
    ],
)
def test_exact_probability_at_null_is_alpha(selection_rule: str) -> None:
    response = calculate(_request(selection_rule=selection_rule))
    index = response.probability_curve["true_effect_working"].index(0.0)

    assert response.probability_curve["current_selected_claim_probability"][index] == 0.05


@pytest.mark.parametrize(
    ("selection_rule", "direction", "sign"),
    [
        ("one_sided_positive_p_lt_alpha", "positive", 1.0),
        ("one_sided_negative_p_lt_alpha", "negative", -1.0),
    ],
)
def test_one_sided_inverse_matches_independent_normal_quantiles(
    selection_rule: str,
    direction: str,
    sign: float,
) -> None:
    response = calculate(_request(selection_rule=selection_rule))
    solution = _solution(response, precision="current", direction=direction)
    expected_delta = sign * (NORMAL.inv_cdf(1.0 - 0.05) + NORMAL.inv_cdf(0.8))

    assert solution["critical_delta"] == pytest.approx(expected_delta, abs=2e-14)
    assert solution["critical_effect_working"] == pytest.approx(
        expected_delta * 0.2,
        abs=5e-15,
    )
    assert solution["achieved_probability"] >= 0.8


def test_two_sided_inverse_is_verified_by_direct_tail_evaluation() -> None:
    response = calculate(_request())
    solution = _solution(response, precision="current", direction="positive")
    delta = solution["critical_delta"]
    critical_z = NORMAL.inv_cdf(1.0 - 0.05 / 2.0)
    direct = NORMAL.cdf(-critical_z - delta) + (1.0 - NORMAL.cdf(critical_z - delta))

    assert solution["critical_delta"] == pytest.approx(
        2.8015817870136996,
        abs=2e-13,
    )
    assert direct == pytest.approx(0.8, abs=8e-15)


def test_two_sided_working_distances_are_symmetric() -> None:
    response = calculate(_request())
    negative = _solution(response, precision="current", direction="negative")
    positive = _solution(response, precision="current", direction="positive")

    assert negative["critical_delta"] == -positive["critical_delta"]
    assert negative["working_distance_from_null"] == positive["working_distance_from_null"]


def test_ratio_natural_values_are_multiplicatively_symmetric() -> None:
    response = calculate(
        _request(
            effect_type="odds_ratio",
            null_value=1.0,
            meaningful_effect=1.5,
        )
    )
    negative = _solution(response, precision="current", direction="negative")
    positive = _solution(response, precision="current", direction="positive")

    assert negative["critical_effect_display"] * positive[
        "critical_effect_display"
    ] == pytest.approx(1.0, rel=2e-15)
    assert any("multiplicatively" in warning for warning in response.warnings)


def test_fourfold_information_halves_se_and_reduces_effect_distance() -> None:
    response = calculate(_request(information_multiplier=4.0))
    current = _solution(response, precision="current", direction="positive")
    scenario = _solution(response, precision="scenario", direction="positive")

    assert response.precision["current_se_working"] == 0.2
    assert response.precision["scenario_se_working"] == 0.1
    assert scenario["working_distance_from_null"] == pytest.approx(
        current["working_distance_from_null"] / 2.0,
        rel=2e-15,
    )


def test_direct_se_and_ci_modes_agree_for_equivalent_precision() -> None:
    direct = calculate(_request())
    ci_half_width = Z975 * 0.2
    ci = calculate(
        _request(
            precision_mode="ci_95",
            standard_error=None,
            ci_lower=-ci_half_width,
            ci_upper=ci_half_width,
        )
    )

    assert ci.precision["current_se_working"] == pytest.approx(0.2, abs=2e-17)
    for direction in ("negative", "positive"):
        assert _solution(
            direct,
            precision="current",
            direction=direction,
        )["critical_effect_working"] == pytest.approx(
            _solution(
                ci,
                precision="current",
                direction=direction,
            )["critical_effect_working"],
            abs=2e-16,
        )


def test_meaningful_effect_probability_matches_direct_normal_tails() -> None:
    response = calculate(_request())
    meaningful = response.reference_effects["meaningful_effect_optional"]
    delta = 0.5 / 0.2
    critical_z = NORMAL.inv_cdf(1.0 - 0.05 / 2.0)
    direct = NORMAL.cdf(-critical_z - delta) + (1.0 - NORMAL.cdf(critical_z - delta))

    assert meaningful["standardized_distance_current"] == 2.5
    assert meaningful["current_selected_claim_probability"] == pytest.approx(
        direct,
        abs=5e-15,
    )
    assert "does not validate this value" in meaningful["note"]


def test_legacy_benchmark_is_unchanged_and_distinctly_labeled() -> None:
    response = calculate(_request())
    legacy = response.legacy_benchmark_optional
    exact = _solution(response, precision="current", direction="positive")

    assert legacy["label"] == "Legacy closed-form benchmark"
    assert "not the exact solution" in legacy["not_exact_note"]
    assert legacy["current"]["working_distance_from_null"] == pytest.approx(
        2.8015852181129683 * 0.2,
        rel=2e-15,
    )
    assert legacy["current"]["working_distance_from_null"] > exact["working_distance_from_null"]
    assert math.isfinite(legacy["current"]["standardized_distance"])
