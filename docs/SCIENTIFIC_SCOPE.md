# Scientific Scope

## Question

Given a one-parameter Wald standard error, selected-claim rule, alpha, and target probability, what
is the closest-to-null true effect in each selected direction whose exact selected-claim
probability is at least the target? Equivalently, what is the smallest absolute working-scale
distance from the null meeting the target in each selected direction?

With

```text
delta = (theta_true - theta_null) / SE
```

and a future `Z ~ Normal(delta, 1)`:

- two-sided selection at alpha uses
  `P(Z < -z_(1-alpha/2)) + P(Z > z_(1-alpha/2))`;
- one-sided positive selection uses `P(Z > z_(1-alpha))`;
- one-sided negative selection uses `P(Z < -z_(1-alpha))`.

The exact critical effect is the closest-to-null representable effect in each relevant direction
meeting the probability target under that model. Equivalently, it has the smallest absolute
working-scale distance from the null in that direction. For the symmetric two-sided rule, the app
reports both directions.

## Intended users and setting

The app is an educational and research-facing design aid for people interpreting a one-parameter
Wald analysis. It separates current precision, prospective statistical detectability,
user-specified scientific importance, an optional observed estimate, and reported-CI context.

It is not intended for bedside care, diagnosis, treatment selection, regulatory decisions, or
automated study approval.

## Inputs

- `effect_type`: one of the nine released Core effect-registry keys.
- `precision_mode`: nominal reported 95% CI or direct working-scale SE.
- `ci_lower`, `ci_upper`: finite natural-scale limits, required together in CI mode.
- `standard_error`: finite positive working-scale SE, required in direct-SE mode. Ratio measures
  require a log-scale SE; additive measures require an identity-scale SE.
- `observed_estimate`: optional finite natural-scale context marker. In CI mode Core validates it
  against the CI-implied midpoint; in direct-SE mode it is display-only.
- `null_value`: finite natural-scale null; ratio inputs must be strictly positive.
- `alpha`: finite value strictly between zero and one.
- `selection_rule`: two-sided, one-sided positive, or one-sided negative p-value selection.
- `target_probability`: finite value strictly between zero and one.
- `meaningful_effect`: optional finite natural-scale scenario. The app does not validate its
  clinical or scientific importance.
- `information_multiplier`: finite positive relative information. It is not automatically sample
  size.
- `display_min`, `display_max`: optional finite natural-scale pair with minimum less than maximum.

Entered clinical values could be sensitive even without identifiers. The app keeps them in
browser memory only; see `PRIVACY.md`.

## Outputs

The primary output is the exact critical-effect value or pair on the natural display scale, with
signed standardized delta, working-scale value, and achieved probability. The app also returns:

- current and information-scenario working-scale SE;
- exact selected-claim probability curves under both precision states;
- exact 50%, 80%, and 90% reference critical effects;
- exact probability at an optional meaningful-effect scenario;
- optional observed-estimate and reported-CI context markers;
- a legacy closed-form benchmark only for the historical two-sided alpha 0.05 / target 0.80 case;
- strict JSON, explicit curve CSV, figure PNG, dashboard PNG, and caption.

The reported CI is a precision-reconstruction input and shaded context, not a true-effect
distribution. The observed estimate is not used to create an “observed power” result.

## Formula authority and assumptions

Released `wald-inference` v0.3.0 is the sole numerical authority. The app calls:

- `reconstruct_wald_from_95_ci`;
- `to_working_scale` and `from_working_scale`;
- `selected_claim_probability` and `power_curve`;
- `critical_effect_for_target_probability`;
- `information_scaled_standard_error`;
- `legacy_critical_effect_distance` and `legacy_critical_effect_markers`.

The app does not implement a Wald probability or inverse formula locally.

Assumptions are a one-parameter normal/Wald sampling approximation, a fixed valid working-scale SE,
the selected p-value rule, and a true effect treated as fixed for each prospective probability.
Ratio effects use log distance from the null; equal log distances are multiplicatively symmetric.

The Perugini et al. AMPS 2025 source carried from the integrated repository supplies
critical-effect-size design rationale. It does not supersede the transparent definitions or
released Core numerical contract.

## Distinctions and limitations

- Exact critical effect is not an MCID. A user-entered meaningful effect is an unvalidated scenario.
- Exact critical effect is not a confidence bound and does not describe effects excluded by an
  observed CI.
- Exact critical effect is not an observed estimate and is not evidence about an observed dataset.
- The historical z-sum marker is a legacy closed-form benchmark, not the exact two-tailed inverse.
- The information multiplier is relative information, not automatically a sample-size multiplier.
- Study-specific sample-size planning may differ because it can require outcome variance,
  allocation, clustering, attrition, survival-event, noncentral-distribution, or other design
  assumptions absent here.

Out of scope are noncentral t/F/chi-square designs, arbitrary non-Wald intervals, study-specific
sample-size formulas, cluster or attrition adjustments, Type S/M, likelihood or compatibility
curves, threshold-conditioned selection rules, and multi-target inverse precision planning.

## Clinical and regulatory boundary

Software verification establishes only the documented mathematical and engineering contract. It
does not establish clinical validity, clinical utility, regulatory clearance, or suitability for
patient-specific decisions. The app provides no diagnosis or treatment recommendation and does
not transmit, store, or link entered values.
