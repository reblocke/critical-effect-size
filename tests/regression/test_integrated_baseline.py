from __future__ import annotations

import json
from pathlib import Path

import pytest

from critical_effect_size import CriticalEffectRequest, calculate

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integrated_baseline"
    / "critical_effect_scenarios.json"
)


def test_frozen_integrated_exact_and_legacy_distances() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    for case in fixture["cases"]:
        response = calculate(
            CriticalEffectRequest(
                precision_mode="direct_se",
                effect_type="mean_difference",
                observed_estimate=None,
                ci_lower=None,
                ci_upper=None,
                standard_error=case["standard_error"],
                null_value=0.0,
                alpha=0.05,
                selection_rule="two_sided_p_lt_alpha",
                target_probability=0.8,
                meaningful_effect=None,
                information_multiplier=1.0,
                display_min=None,
                display_max=None,
            )
        )
        positive = next(
            row
            for row in response.critical_effect["current"]["solutions"]
            if row["direction"] == "positive"
        )

        assert positive["critical_effect_working"] == pytest.approx(
            case["exact_positive_working"],
            abs=5e-14,
        )
        assert (
            response.legacy_benchmark_optional["current"]["working_distance_from_null"]
            == case["legacy_distance_working"]
        )
