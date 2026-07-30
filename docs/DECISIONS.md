# Decisions

## 2026-07-29 — Functional Python contract and verified browser worker

Python is the contract source of truth. The static UI sends strict JSON to a restartable Web Worker
running exact-version Pyodide. Installed app and Core files are generated from the locked
environment, ignored in Git, and verified by file, package, and aggregate hashes before import.

The repository owns its copied UI at creation time rather than depending on a live shared
template. There is no backend, telemetry, persistence, cookie, or input-bearing URL.

## 2026-07-30 — Released Core is the sole numerical authority

`wald-inference` v0.3.0 owns effect transformations, CI reconstruction, selected-claim
probabilities, power curves, critical-effect inversion, information scaling, and the legacy
benchmark. The app owns strict validation, orchestration, warnings, display payloads, and exports
but implements no alternative Wald probability or solver.

The dependency is pinned to the release wheel URL and SHA-256 in `pyproject.toml`, `uv.lock`, and
`browser-stage.toml`. A sibling checkout is never a staging source.

## 2026-07-30 — Exact critical effect is primary

The primary quantity is the closest-to-null representable effect in each selected direction whose
exact selected-claim probability meets the requested target under a fixed-SE one-parameter Wald
model, equivalently the smallest absolute working-scale distance from the null in that direction.
Two-sided selection reports paired directions; one-sided selection reports only its selected
direction.

The preserved z-sum calculation appears only at its fixed historical defaults and is labeled
**Legacy closed-form benchmark**, with an explicit statement that it is not the exact two-tailed
solution.

## 2026-07-30 — Separate prospective detectability from observed evidence

The reported CI reconstructs precision and may be shaded only as observed context. An observed
estimate is an optional marker and is not used to report “observed power.” Power is evaluated at a
user-specified meaningful-effect scenario, which is explicitly not clinically or scientifically
validated by the app.

An information multiplier changes only hypothetical SE through released Core. It is labeled
relative information and not automatically translated into sample size.

## 2026-07-30 — Ratio effects use log-distance semantics

Direct SE for ratio measures is on the log scale. Exact critical effects are solved on that scale
and converted through Core to natural ratios. Paired natural values are described as
multiplicatively, not arithmetically, symmetric around the null ratio.

## 2026-07-30 — Focused stable response and exports

The response has exactly `meta`, `precision`, `rule`, `critical_effect`,
`legacy_benchmark_optional`, `probability_curve`, `reference_effects`, and `warnings`. It has no
compatibility, likelihood, S−2, Type S/M, threshold-conditioned, or multi-target precision-planner
sections.

CSV exports exactly the natural/working true effect and current/scenario selected-claim
probabilities. PNGs and the caption disclose conditioning, information scenario, CI context, and
display-range omissions.
