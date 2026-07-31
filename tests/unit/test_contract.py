from __future__ import annotations

import json
from dataclasses import replace

import pytest

from critical_effect_size import (
    CriticalEffectRequest,
    ValidationError,
    calculate,
    calculate_json,
)


def _payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "precision_mode": "direct_se",
        "effect_type": "mean_difference",
        "observed_estimate": 0.4,
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
    return payload


def test_response_has_exact_focused_contract_and_primary_exact_result() -> None:
    response = calculate(CriticalEffectRequest.from_mapping(_payload())).to_payload()

    assert list(response) == [
        "meta",
        "precision",
        "rule",
        "critical_effect",
        "legacy_benchmark_optional",
        "probability_curve",
        "reference_effects",
        "warnings",
    ]
    assert response["meta"]["primary_quantity"] == "exact critical effect"
    assert response["critical_effect"]["target_probability"] == 0.8
    assert response["legacy_benchmark_optional"]["label"] == ("Legacy closed-form benchmark")
    serialized = json.dumps(response, sort_keys=True).lower()
    for excluded in [
        "compatibility_curve",
        "relative_likelihood",
        "type_s",
        "type_m",
        "inverse_precision",
    ]:
        assert excluded not in serialized


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_contract_rejects_nonstandard_json_numbers(constant: str) -> None:
    payload = _payload()
    request = json.dumps(payload).replace("0.2", constant, 1)

    with pytest.raises(ValidationError, match="Non-finite JSON constant"):
        calculate_json(request)


def test_contract_returns_strict_json() -> None:
    response_json = calculate_json(json.dumps(_payload()))

    assert "NaN" not in response_json
    assert "Infinity" not in response_json
    response = json.loads(response_json)
    assert list(response) == [
        "meta",
        "precision",
        "rule",
        "critical_effect",
        "legacy_benchmark_optional",
        "probability_curve",
        "reference_effects",
        "warnings",
    ]
    assert response["meta"]["core_version"] == "0.4.2"


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "Missing required field"),
        (_payload(extra=1), "Unexpected field"),
        (_payload(alpha=True), "Alpha must be a number"),
        (_payload(standard_error="0.2"), "standard error must be a number"),
        (
            _payload(standard_error=10**10000),
            "standard error must be finite",
        ),
        (_payload(precision_mode="other"), "Precision mode must"),
    ],
)
def test_request_validation_is_explicit(
    payload: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValidationError, match=message):
        CriticalEffectRequest.from_mapping(payload)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"alpha": 0.0}, "Alpha must be between"),
        ({"alpha": 1.0}, "Alpha must be between"),
        ({"target_probability": 0.0}, "Target selected-claim probability"),
        ({"target_probability": 1.0}, "Target selected-claim probability"),
        ({"standard_error": 0.0}, "standard error must be positive"),
        ({"information_multiplier": 0.0}, "Information multiplier"),
        (
            {
                "precision_mode": "ci_95",
                "standard_error": None,
                "ci_lower": None,
                "ci_upper": 0.5,
            },
            "Both 95% confidence limits",
        ),
        (
            {"display_min": -1.0, "display_max": None},
            "Display minimum and maximum",
        ),
        (
            {"display_min": 2.0, "display_max": 1.0},
            "Display minimum must be less",
        ),
        ({"selection_rule": "ci_excludes_mcid"}, "Unsupported selected-claim rule"),
    ],
)
def test_semantic_validation_fails_safely(
    overrides: dict[str, object],
    message: str,
) -> None:
    request = CriticalEffectRequest.from_mapping(_payload(**overrides))

    with pytest.raises(ValidationError, match=message):
        calculate(request)


def test_calculate_revalidates_precision_mode_for_direct_python_callers() -> None:
    request = CriticalEffectRequest.from_mapping(_payload())
    invalid_request = replace(request, precision_mode="bogus")  # type: ignore[arg-type]

    with pytest.raises(ValidationError, match="Precision mode must"):
        calculate(invalid_request)


@pytest.mark.parametrize(
    ("selection_rule", "expected_direction"),
    [
        ("one_sided_positive_p_lt_alpha", "positive"),
        ("one_sided_negative_p_lt_alpha", "negative"),
    ],
)
def test_one_sided_rules_return_only_the_selected_direction(
    selection_rule: str,
    expected_direction: str,
) -> None:
    response = calculate(
        CriticalEffectRequest.from_mapping(
            _payload(selection_rule=selection_rule),
        )
    )

    [solution] = response.critical_effect["current"]["solutions"]
    assert solution["direction"] == expected_direction
    assert response.legacy_benchmark_optional is None


def test_target_at_alpha_returns_null_with_explicit_warning() -> None:
    response = calculate(
        CriticalEffectRequest.from_mapping(
            _payload(target_probability=0.05),
        )
    )

    assert {
        solution["critical_effect_working"]
        for solution in response.critical_effect["current"]["solutions"]
    } == {0.0}
    assert any("null already meets" in warning for warning in response.warnings)
