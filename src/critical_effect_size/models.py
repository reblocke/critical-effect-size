"""Typed request and response models for exact Wald detectability."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Literal

type PrecisionMode = Literal["ci_95", "direct_se"]


class ValidationError(ValueError):
    """A user-correctable request error safe to show in the browser."""


def _finite_number(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValidationError(f"{field} must be a number.")
    try:
        number = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValidationError(f"{field} must be finite.") from exc
    if not math.isfinite(number):
        raise ValidationError(f"{field} must be finite.")
    return number


def _optional_finite_number(value: object, *, field: str) -> float | None:
    if value is None:
        return None
    return _finite_number(value, field=field)


def _required_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{field} must be a non-empty string.")
    return value


@dataclass(frozen=True)
class CriticalEffectRequest:
    """Validated controls for one exact selected-claim probability analysis."""

    precision_mode: PrecisionMode
    effect_type: str
    observed_estimate: float | None
    ci_lower: float | None
    ci_upper: float | None
    standard_error: float | None
    null_value: float
    alpha: float
    selection_rule: str
    target_probability: float
    meaningful_effect: float | None
    information_multiplier: float
    display_min: float | None
    display_max: float | None

    @classmethod
    def from_mapping(cls, payload: object) -> CriticalEffectRequest:
        """Build a request from the stable, flat browser payload."""

        if not isinstance(payload, dict):
            raise ValidationError("Request must be a JSON object.")
        expected = {
            "alpha",
            "ci_lower",
            "ci_upper",
            "display_max",
            "display_min",
            "effect_type",
            "information_multiplier",
            "meaningful_effect",
            "null_value",
            "observed_estimate",
            "precision_mode",
            "selection_rule",
            "standard_error",
            "target_probability",
        }
        unexpected = sorted(set(payload) - expected)
        missing = sorted(expected - set(payload))
        if missing:
            raise ValidationError(f"Missing required field: {missing[0]}.")
        if unexpected:
            raise ValidationError(f"Unexpected field: {unexpected[0]}.")

        precision_mode = _required_string(
            payload["precision_mode"],
            field="Precision mode",
        )
        if precision_mode not in {"ci_95", "direct_se"}:
            raise ValidationError("Precision mode must be 'ci_95' or 'direct_se'.")

        return cls(
            precision_mode=precision_mode,
            effect_type=_required_string(payload["effect_type"], field="Effect measure"),
            observed_estimate=_optional_finite_number(
                payload["observed_estimate"],
                field="Observed estimate",
            ),
            ci_lower=_optional_finite_number(
                payload["ci_lower"],
                field="Lower 95% confidence limit",
            ),
            ci_upper=_optional_finite_number(
                payload["ci_upper"],
                field="Upper 95% confidence limit",
            ),
            standard_error=_optional_finite_number(
                payload["standard_error"],
                field="Working-scale standard error",
            ),
            null_value=_finite_number(payload["null_value"], field="Null value"),
            alpha=_finite_number(payload["alpha"], field="Alpha"),
            selection_rule=_required_string(
                payload["selection_rule"],
                field="Selected-claim rule",
            ),
            target_probability=_finite_number(
                payload["target_probability"],
                field="Target selected-claim probability",
            ),
            meaningful_effect=_optional_finite_number(
                payload["meaningful_effect"],
                field="Meaningful effect",
            ),
            information_multiplier=_finite_number(
                payload["information_multiplier"],
                field="Information multiplier",
            ),
            display_min=_optional_finite_number(
                payload["display_min"],
                field="Display minimum",
            ),
            display_max=_optional_finite_number(
                payload["display_max"],
                field="Display maximum",
            ),
        )


@dataclass(frozen=True)
class CriticalEffectResponse:
    """Focused response with no likelihood, compatibility, Type S/M, or planner panels."""

    meta: dict[str, Any]
    precision: dict[str, Any]
    rule: dict[str, Any]
    critical_effect: dict[str, Any]
    legacy_benchmark_optional: dict[str, Any] | None
    probability_curve: dict[str, Any]
    reference_effects: dict[str, Any]
    warnings: list[str]

    def to_payload(self) -> dict[str, Any]:
        """Return the stable eight-part browser contract."""

        return {
            "meta": self.meta,
            "precision": self.precision,
            "rule": self.rule,
            "critical_effect": self.critical_effect,
            "legacy_benchmark_optional": self.legacy_benchmark_optional,
            "probability_curve": self.probability_curve,
            "reference_effects": self.reference_effects,
            "warnings": self.warnings,
        }
