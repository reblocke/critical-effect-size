from __future__ import annotations

import pytest

from critical_effect_size import CriticalEffectRequest, calculate


def _request(
    *,
    selection_rule: str,
    standard_error: float,
    alpha: float,
    target_probability: float,
) -> CriticalEffectRequest:
    return CriticalEffectRequest(
        precision_mode="direct_se",
        effect_type="mean_difference",
        observed_estimate=None,
        ci_lower=None,
        ci_upper=None,
        standard_error=standard_error,
        null_value=0.0,
        alpha=alpha,
        selection_rule=selection_rule,
        target_probability=target_probability,
        meaningful_effect=None,
        information_multiplier=1.0,
        display_min=-2.0,
        display_max=2.0,
    )


@pytest.mark.parametrize(
    ("standard_error", "alpha", "target_probability"),
    [
        (0.05, 0.01, 0.50),
        (0.20, 0.05, 0.80),
        (1.00, 0.20, 0.95),
    ],
)
def test_one_sided_curve_is_monotone_in_selected_direction(
    standard_error: float,
    alpha: float,
    target_probability: float,
) -> None:
    positive = calculate(
        _request(
            selection_rule="one_sided_positive_p_lt_alpha",
            standard_error=standard_error,
            alpha=alpha,
            target_probability=target_probability,
        )
    ).probability_curve["current_selected_claim_probability"]
    negative = calculate(
        _request(
            selection_rule="one_sided_negative_p_lt_alpha",
            standard_error=standard_error,
            alpha=alpha,
            target_probability=target_probability,
        )
    ).probability_curve["current_selected_claim_probability"]

    assert all(left <= right for left, right in zip(positive, positive[1:], strict=False))
    assert all(left >= right for left, right in zip(negative, negative[1:], strict=False))
