"""Strict focused contract for exact Wald critical-effect calculations."""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from typing import Any

import wald_inference
from wald_inference import (
    critical_effect_for_target_probability,
    from_working_scale,
    get_effect_spec,
    information_scaled_standard_error,
    legacy_critical_effect_distance,
    legacy_critical_effect_markers,
    power_curve,
    reconstruct_wald_from_95_ci,
    selected_claim_probability,
    standardized_distance,
    to_working_scale,
)

from .models import CriticalEffectRequest, CriticalEffectResponse, ValidationError
from .version import __version__

SUPPORTED_RULES = (
    "two_sided_p_lt_alpha",
    "one_sided_positive_p_lt_alpha",
    "one_sided_negative_p_lt_alpha",
)
REFERENCE_PROBABILITIES = (0.50, 0.80, 0.90)
DEFAULT_GRID_POINTS = 301
DEFAULT_GRID_HALF_WIDTH_SE = 4.0

_RULE_LABELS = {
    "two_sided_p_lt_alpha": "Two-sided p < alpha",
    "one_sided_positive_p_lt_alpha": "One-sided positive p < alpha",
    "one_sided_negative_p_lt_alpha": "One-sided negative p < alpha",
}


def _reject_nonstandard_constant(value: str) -> None:
    raise ValidationError(f"Non-finite JSON constant is not allowed: {value}.")


def _call_core(function, /, *args, **kwargs):
    """Translate the released core's user-facing errors to this app boundary."""

    try:
        return function(*args, **kwargs)
    except wald_inference.ValidationError as exc:
        raise ValidationError(str(exc)) from exc


def _working_value(effect_type: str, value: float) -> float:
    return float(_call_core(to_working_scale, effect_type, value))


def _display_value(effect_type: str, value: float) -> float:
    return float(_call_core(from_working_scale, effect_type, value))


def _rule_direction(selection_rule: str) -> str:
    return "negative" if selection_rule == "one_sided_negative_p_lt_alpha" else "positive"


def _solution_directions(selection_rule: str) -> tuple[str, ...]:
    if selection_rule == "two_sided_p_lt_alpha":
        return ("negative", "positive")
    return (_rule_direction(selection_rule),)


def _validate_request(request: CriticalEffectRequest) -> None:
    if request.selection_rule not in SUPPORTED_RULES:
        valid = ", ".join(SUPPORTED_RULES)
        raise ValidationError(f"Unsupported selected-claim rule. Expected one of: {valid}.")
    if not 0 < request.alpha < 1:
        raise ValidationError("Alpha must be between 0 and 1.")
    if not 0 < request.target_probability < 1:
        raise ValidationError("Target selected-claim probability must be between 0 and 1.")
    if request.information_multiplier <= 0:
        raise ValidationError("Information multiplier must be greater than 0.")

    if request.precision_mode == "ci_95":
        if request.ci_lower is None or request.ci_upper is None:
            raise ValidationError("Both 95% confidence limits are required in CI mode.")
        if request.standard_error is not None:
            raise ValidationError("Working-scale standard error must be blank in CI mode.")
    else:
        if request.standard_error is None:
            raise ValidationError("Working-scale standard error is required in direct-SE mode.")
        if request.standard_error <= 0:
            raise ValidationError("Working-scale standard error must be positive.")
        if request.ci_lower is not None or request.ci_upper is not None:
            raise ValidationError("Confidence limits must be blank in direct-SE mode.")

    if (request.display_min is None) != (request.display_max is None):
        raise ValidationError("Display minimum and maximum must be supplied together.")
    if (
        request.display_min is not None
        and request.display_max is not None
        and request.display_min >= request.display_max
    ):
        raise ValidationError("Display minimum must be less than the display maximum.")


def _precision(
    request: CriticalEffectRequest,
    *,
    effect_spec,
    null_working: float,
) -> tuple[dict[str, Any], float, float, list[str]]:
    warnings: list[str] = []
    if request.precision_mode == "ci_95":
        assert request.ci_lower is not None and request.ci_upper is not None
        reconstruction = _call_core(
            reconstruct_wald_from_95_ci,
            effect_type=request.effect_type,
            estimate=request.observed_estimate,
            lower=request.ci_lower,
            upper=request.ci_upper,
            null_value=request.null_value,
        )
        current_se = float(reconstruction.standard_error)
        warnings.extend(reconstruction.warnings)
        ci_context = {
            "ci_lower_display": reconstruction.lower_display,
            "ci_upper_display": reconstruction.upper_display,
            "ci_lower_working": reconstruction.lower_working,
            "ci_upper_working": reconstruction.upper_working,
            "ci_implied_midpoint_display": reconstruction.estimate_display,
            "ci_implied_midpoint_working": reconstruction.estimate_working,
            "ci_reconstruction_method": reconstruction.se_method,
            "estimate_source": reconstruction.estimate_source,
        }
        source_note = (
            "The reported 95% CI reconstructs working-scale SE under a Wald approximation. "
            "Its span is shown only as observed precision context, not as a true-effect "
            "distribution."
        )
    else:
        assert request.standard_error is not None
        current_se = request.standard_error
        ci_context = {
            "ci_lower_display": None,
            "ci_upper_display": None,
            "ci_lower_working": None,
            "ci_upper_working": None,
            "ci_implied_midpoint_display": None,
            "ci_implied_midpoint_working": None,
            "ci_reconstruction_method": None,
            "estimate_source": (
                "provided_for_display" if request.observed_estimate is not None else None
            ),
        }
        source_note = (
            "The entered SE is interpreted on the log working scale."
            if effect_spec.family == "ratio"
            else "The entered SE is interpreted on the identity working scale."
        )

    scenario_se = float(
        _call_core(
            information_scaled_standard_error,
            current_se,
            request.information_multiplier,
        )
    )
    return (
        {
            "mode": request.precision_mode,
            "effect_type": effect_spec.key,
            "effect_label": effect_spec.label,
            "effect_family": effect_spec.family,
            "working_scale": effect_spec.working_scale,
            "null_display": request.null_value,
            "null_working": null_working,
            "current_se_working": current_se,
            "scenario_se_working": scenario_se,
            "information_multiplier": request.information_multiplier,
            "observed_estimate_display": request.observed_estimate,
            "observed_estimate_working": (
                None
                if request.observed_estimate is None
                else _working_value(request.effect_type, request.observed_estimate)
            ),
            "source_note": source_note,
            "information_note": (
                "Scenario SE = current SE / sqrt(information multiplier). The multiplier "
                "represents relative information, not automatically a sample-size multiplier."
            ),
            **ci_context,
        },
        current_se,
        scenario_se,
        warnings,
    )


def _critical_solutions(
    request: CriticalEffectRequest,
    *,
    null_working: float,
    standard_error: float,
    target_probability: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for direction in _solution_directions(request.selection_rule):
        result = _call_core(
            critical_effect_for_target_probability,
            null_working=null_working,
            standard_error=standard_error,
            alpha=request.alpha,
            target_probability=target_probability,
            selection_rule=request.selection_rule,
            claim_direction=direction,
        )
        rows.append(
            {
                "direction": direction,
                "critical_delta": result.critical_delta,
                "critical_effect_working": result.critical_effect_working,
                "critical_effect_display": _display_value(
                    request.effect_type,
                    result.critical_effect_working,
                ),
                "working_distance_from_null": abs(result.critical_effect_working - null_working),
                "achieved_probability": result.achieved_probability,
            }
        )
    return rows


def _legacy_solution(
    request: CriticalEffectRequest,
    *,
    null_working: float,
    standard_error: float,
) -> dict[str, Any]:
    lower, upper = _call_core(
        legacy_critical_effect_markers,
        null_working,
        standard_error,
    )
    distance = float(_call_core(legacy_critical_effect_distance, standard_error))
    return {
        "standard_error_working": standard_error,
        "standardized_distance": distance / standard_error,
        "working_distance_from_null": distance,
        "solutions": [
            {
                "direction": "negative",
                "critical_effect_working": lower,
                "critical_effect_display": _display_value(request.effect_type, lower),
            },
            {
                "direction": "positive",
                "critical_effect_working": upper,
                "critical_effect_display": _display_value(request.effect_type, upper),
            },
        ],
    }


def _linear_grid(lower: float, upper: float, anchors: Sequence[float]) -> list[float]:
    span = upper - lower
    if not math.isfinite(span) or span <= 0:
        raise ValidationError("Display range must be finite and positive on the working scale.")
    values = [
        lower + span * index / (DEFAULT_GRID_POINTS - 1) for index in range(DEFAULT_GRID_POINTS)
    ]
    values[0] = lower
    values[-1] = upper
    values.extend(anchor for anchor in anchors if lower <= anchor <= upper)
    result = sorted(set(values))
    if not all(math.isfinite(value) for value in result):
        raise ValidationError("Probability-curve grid exceeds the finite numeric range.")
    return result


def _plot_range(
    request: CriticalEffectRequest,
    *,
    null_working: float,
    current_se: float,
    scenario_se: float,
    anchor_working: Sequence[tuple[str, float]],
) -> tuple[float, float, list[str]]:
    if request.display_min is not None:
        assert request.display_max is not None
        lower = _working_value(request.effect_type, request.display_min)
        upper = _working_value(request.effect_type, request.display_max)
        if lower >= upper:
            raise ValidationError(
                "Display minimum must be less than the maximum on the working scale."
            )
    else:
        half_width = DEFAULT_GRID_HALF_WIDTH_SE * max(current_se, scenario_se)
        values = [
            null_working - half_width,
            null_working + half_width,
            *(value for _, value in anchor_working),
        ]
        lower = min(values)
        upper = max(values)
        padding = max((upper - lower) * 0.04, min(current_se, scenario_se) * 0.2)
        lower -= padding
        upper += padding

    outside = [label for label, value in anchor_working if value < lower or value > upper]
    return lower, upper, outside


def _ensure_finite_payload(value: object, *, path: str = "response") -> None:
    if value is None or isinstance(value, str | bool):
        return
    if isinstance(value, int | float):
        try:
            finite = math.isfinite(float(value))
        except (OverflowError, TypeError, ValueError) as exc:
            raise RuntimeError(f"{path} contains a non-finite number.") from exc
        if not finite:
            raise RuntimeError(f"{path} contains a non-finite number.")
        return
    if isinstance(value, list | tuple):
        for index, item in enumerate(value):
            _ensure_finite_payload(item, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _ensure_finite_payload(item, path=f"{path}.{key}")
        return
    raise RuntimeError(f"{path} contains a non-JSON value.")


def calculate(request: CriticalEffectRequest) -> CriticalEffectResponse:
    """Calculate exact repeated-study detectability through released core APIs."""

    _validate_request(request)
    effect_spec = _call_core(get_effect_spec, request.effect_type)
    null_working = _working_value(request.effect_type, request.null_value)
    precision, current_se, scenario_se, warnings = _precision(
        request,
        effect_spec=effect_spec,
        null_working=null_working,
    )
    observed_working = precision["observed_estimate_working"]
    meaningful_working = (
        None
        if request.meaningful_effect is None
        else _working_value(request.effect_type, request.meaningful_effect)
    )

    current_solutions = _critical_solutions(
        request,
        null_working=null_working,
        standard_error=current_se,
        target_probability=request.target_probability,
    )
    scenario_solutions = _critical_solutions(
        request,
        null_working=null_working,
        standard_error=scenario_se,
        target_probability=request.target_probability,
    )
    critical_effect = {
        "definition": (
            "Smallest representable effect in each reported direction whose exact "
            "selected-claim probability is at least the requested target under the fixed-SE "
            "one-parameter Wald model."
        ),
        "target_probability": request.target_probability,
        "current": {
            "label": "Current precision",
            "standard_error_working": current_se,
            "solutions": current_solutions,
        },
        "scenario": {
            "label": f"{request.information_multiplier:g}x information scenario",
            "standard_error_working": scenario_se,
            "solutions": scenario_solutions,
        },
    }

    legacy: dict[str, Any] | None = None
    if (
        request.selection_rule == "two_sided_p_lt_alpha"
        and request.alpha == 0.05
        and request.target_probability == 0.80
    ):
        legacy = {
            "label": "Legacy closed-form benchmark",
            "applicability": "Fixed alpha = 0.05 and nominal probability = 0.80 only.",
            "not_exact_note": (
                "This preserved z-sum benchmark is not the exact solution of the two-tailed "
                "selected-claim probability equation."
            ),
            "current": _legacy_solution(
                request,
                null_working=null_working,
                standard_error=current_se,
            ),
            "scenario": _legacy_solution(
                request,
                null_working=null_working,
                standard_error=scenario_se,
            ),
        }

    reference_rows: list[dict[str, Any]] = []
    reference_solution_map: dict[str, list[dict[str, Any]]] = {}
    for target in REFERENCE_PROBABILITIES:
        for precision_label, se in (("current", current_se), ("scenario", scenario_se)):
            solutions = _critical_solutions(
                request,
                null_working=null_working,
                standard_error=se,
                target_probability=target,
            )
            reference_solution_map[f"{precision_label}-{target:g}"] = solutions
            for solution in solutions:
                reference_rows.append(
                    {
                        "precision": precision_label,
                        "information_multiplier": (
                            1.0 if precision_label == "current" else request.information_multiplier
                        ),
                        "target_probability": target,
                        **solution,
                        "note": (
                            "Target is at or below alpha, so the null already meets it."
                            if target <= request.alpha
                            else None
                        ),
                    }
                )

    meaningful: dict[str, Any] | None = None
    if meaningful_working is not None:
        current_probability = float(
            _call_core(
                selected_claim_probability,
                meaningful_working,
                null_working=null_working,
                standard_error=current_se,
                alpha=request.alpha,
                selection_rule=request.selection_rule,
                claim_direction=_rule_direction(request.selection_rule),
            )
        )
        scenario_probability = float(
            _call_core(
                selected_claim_probability,
                meaningful_working,
                null_working=null_working,
                standard_error=scenario_se,
                alpha=request.alpha,
                selection_rule=request.selection_rule,
                claim_direction=_rule_direction(request.selection_rule),
            )
        )
        meaningful = {
            "effect_display": request.meaningful_effect,
            "effect_working": meaningful_working,
            "standardized_distance_current": float(
                _call_core(
                    standardized_distance,
                    meaningful_working,
                    null_working,
                    current_se,
                )
            ),
            "standardized_distance_scenario": float(
                _call_core(
                    standardized_distance,
                    meaningful_working,
                    null_working,
                    scenario_se,
                )
            ),
            "current_selected_claim_probability": current_probability,
            "scenario_selected_claim_probability": scenario_probability,
            "note": (
                "A user-specified scientific scenario. The app does not validate this value "
                "as a clinical or scientific minimum important difference."
            ),
        }

    anchors: list[tuple[str, float]] = [("Null", null_working)]
    if observed_working is not None:
        anchors.append(("Observed estimate", observed_working))
    if meaningful_working is not None:
        anchors.append(("Meaningful-effect scenario", meaningful_working))
    if precision["ci_lower_working"] is not None:
        anchors.extend(
            [
                ("Reported CI lower limit", precision["ci_lower_working"]),
                ("Reported CI upper limit", precision["ci_upper_working"]),
            ]
        )
    for label, solutions in (
        ("Current exact critical effect", current_solutions),
        ("Scenario exact critical effect", scenario_solutions),
        ("Current 90% reference effect", reference_solution_map["current-0.9"]),
        ("Scenario 90% reference effect", reference_solution_map["scenario-0.9"]),
    ):
        anchors.extend((label, solution["critical_effect_working"]) for solution in solutions)

    lower_working, upper_working, outside = _plot_range(
        request,
        null_working=null_working,
        current_se=current_se,
        scenario_se=scenario_se,
        anchor_working=anchors,
    )
    grid_working = _linear_grid(
        lower_working,
        upper_working,
        [value for _, value in anchors],
    )
    current_probabilities = [
        float(value)
        for value in _call_core(
            power_curve,
            grid_working,
            null_working=null_working,
            standard_error=current_se,
            alpha=request.alpha,
            selection_rule=request.selection_rule,
            claim_direction=_rule_direction(request.selection_rule),
        )
    ]
    scenario_probabilities = [
        float(value)
        for value in _call_core(
            power_curve,
            grid_working,
            null_working=null_working,
            standard_error=scenario_se,
            alpha=request.alpha,
            selection_rule=request.selection_rule,
            claim_direction=_rule_direction(request.selection_rule),
        )
    ]
    grid_display = [_display_value(request.effect_type, value) for value in grid_working]

    if request.target_probability <= request.alpha:
        warnings.append(
            "The target does not exceed alpha, so the null already meets the selected-claim "
            "probability target and the exact critical effect is the null."
        )
    if request.precision_mode == "ci_95":
        warnings.append(
            "The reported CI is displayed only as observed precision context; it is not a "
            "probability distribution for the true effect."
        )
    if effect_spec.family == "ratio":
        warnings.append(
            "Ratio effects use log-scale distances. Paired natural-scale critical values are "
            "multiplicatively, not arithmetically, symmetric around the null ratio."
        )
    if request.meaningful_effect is not None:
        warnings.append(
            "The meaningful effect is user-defined and is not clinically or scientifically "
            "validated by this app."
        )
    if request.observed_estimate is not None:
        warnings.append(
            "The observed estimate is a display marker only. The app does not report observed "
            "power or use the estimate as evidence about a future true effect."
        )
    if request.information_multiplier != 1:
        warnings.append(
            "The information multiplier defines a hypothetical precision scenario; it is not "
            "automatically a sample-size multiplier."
        )
    if outside:
        unique_outside = sorted(set(outside))
        warnings.append(
            "The requested display range omits these context markers: "
            + ", ".join(unique_outside)
            + "."
        )

    rule = {
        "key": request.selection_rule,
        "label": _RULE_LABELS[request.selection_rule],
        "alpha": request.alpha,
        "claim_direction": (
            None
            if request.selection_rule == "two_sided_p_lt_alpha"
            else _rule_direction(request.selection_rule)
        ),
        "target_probability": request.target_probability,
        "explanation": (
            "Selection occurs in either tail beyond the two-sided alpha boundary."
            if request.selection_rule == "two_sided_p_lt_alpha"
            else (
                "Selection occurs only beyond the positive one-sided alpha boundary."
                if request.selection_rule == "one_sided_positive_p_lt_alpha"
                else "Selection occurs only beyond the negative one-sided alpha boundary."
            )
        ),
    }
    conditioning_statement = (
        "Each curve conditions on its x-axis value being the true effect in a future repeated "
        "study with fixed working-scale SE."
    )
    caption = (
        f"Exact selected-claim probability for {effect_spec.label.lower()} under "
        f"{_RULE_LABELS[request.selection_rule].lower()} at alpha {request.alpha:g}. "
        f"{conditioning_statement} "
    )
    if request.information_multiplier == 1:
        caption += "The 1x information scenario coincides with current precision. "
    else:
        caption += (
            "The solid line shows current precision; the dashed comparison line uses "
            f"{request.information_multiplier:g}x information. "
        )
    caption += "Vertical markers identify the null and exact critical effect(s)"
    if request.meaningful_effect is not None:
        caption += ", plus the user-defined meaningful-effect scenario"
    if request.observed_estimate is not None:
        caption += " and observed estimate"
    if request.precision_mode == "ci_95":
        caption += (
            ". The reported 95% CI shading is observed precision context, not a true-effect "
            "distribution"
        )
    caption += (
        ". The target and 50%, 80%, and 90% reference probabilities are horizontal guides. "
        "Results are repeated-study operating characteristics, not evidence conditional on an "
        "observed dataset."
    )
    if outside:
        caption += " Some context markers lie outside the user-requested display range."

    response = CriticalEffectResponse(
        meta={
            "schema_version": 1,
            "app_version": __version__,
            "core_version": wald_inference.__version__,
            "title": "Wald Critical Effect Size",
            "effect_type": effect_spec.key,
            "effect_label": effect_spec.label,
            "effect_family": effect_spec.family,
            "working_scale": effect_spec.working_scale,
            "conditioning_statement": conditioning_statement,
            "primary_quantity": "exact critical effect",
            "non_evidential_note": (
                "Detectability is a forward repeated-study operating characteristic, not "
                "observed evidence, a posterior probability, or a confidence bound."
            ),
            "caption": caption,
            "export_columns": [
                "true_effect_display",
                "true_effect_working",
                "current_selected_claim_probability",
                "scenario_selected_claim_probability",
            ],
        },
        precision=precision,
        rule=rule,
        critical_effect=critical_effect,
        legacy_benchmark_optional=legacy,
        probability_curve={
            "true_effect_display": grid_display,
            "true_effect_working": grid_working,
            "current_selected_claim_probability": current_probabilities,
            "scenario_selected_claim_probability": scenario_probabilities,
            "display_min": grid_display[0],
            "display_max": grid_display[-1],
            "axis_spacing": "log" if effect_spec.family == "ratio" else "linear",
            "reported_ci_context_optional": (
                None
                if request.precision_mode != "ci_95"
                else {
                    "lower_display": precision["ci_lower_display"],
                    "upper_display": precision["ci_upper_display"],
                    "interpretation": ("Observed 95% CI span shown only as precision context."),
                }
            ),
            "markers": {
                "null_display": request.null_value,
                "observed_estimate_display_optional": request.observed_estimate,
                "meaningful_effect_display_optional": request.meaningful_effect,
                "current_critical": current_solutions,
                "scenario_critical": scenario_solutions,
                "outside_display_range": sorted(set(outside)),
            },
        },
        reference_effects={
            "probabilities": list(REFERENCE_PROBABILITIES),
            "critical_rows": reference_rows,
            "meaningful_effect_optional": meaningful,
        },
        warnings=warnings,
    )
    _ensure_finite_payload(response.to_payload())
    return response


def calculate_json(request_json: str) -> str:
    """Validate a strict JSON request and return strict focused JSON."""

    try:
        payload = json.loads(request_json, parse_constant=_reject_nonstandard_constant)
    except json.JSONDecodeError as exc:
        raise ValidationError("Request must be valid JSON.") from exc
    response = calculate(CriticalEffectRequest.from_mapping(payload))
    return json.dumps(
        response.to_payload(),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
