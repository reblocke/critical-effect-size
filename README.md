# Wald Critical Effect Size

[![CI](https://github.com/reblocke/critical-effect-size/actions/workflows/ci.yml/badge.svg)](https://github.com/reblocke/critical-effect-size/actions/workflows/ci.yml)

A static, client-side app for exact one-parameter Wald detectability and critical-effect
calculations.

[Open the app](https://reblocke.github.io/critical-effect-size/)

## Version, release, and citation

Current app version: **0.1.5**.

Canonical release record:
[`v0.1.5`](https://github.com/reblocke/critical-effect-size/releases/tag/v0.1.5).
Release maturity: experimental software. GitHub publication state is recorded on the versioned
release page.

For software citation, use [`CITATION.cff`](CITATION.cff) and cite the exact tagged release used.
If you use unreleased code, cite the exact repository commit instead.

## Why this app exists and intended use

Detectability questions are often mixed with interpretation of an observed result or with claims
about scientific importance. This focused app isolates the prospective inverse question: for a
fixed Wald precision and selected-claim rule, how far from the null must an assumed true effect be
to reach a specified repeated-study probability?

It is intended for researchers, methodologists, educators, and reviewers exploring one-parameter
design sensitivity, comparing precision scenarios, or teaching the distinction between
detectability and importance. It is not intended to infer evidence from a completed study, choose
a meaningful clinical threshold, or replace design-specific planning.

## Question answered

Given a working-scale standard error, selected-claim rule, alpha, and target probability, what is
the closest-to-null true effect in each selected direction whose exact repeated-study
selected-claim probability meets the target? Equivalently, what is the smallest absolute
working-scale distance from the null that meets the target in each selected direction?

For standardized true effect

```text
delta = (theta_true - theta_null) / SE
```

the app uses the exact normal/Wald tail probability and inverse implemented by released
[`wald-inference` v0.4.2](https://github.com/reblocke/wald-inference-core/releases/tag/v0.4.2).
For a two-sided rule it reports paired effects around the null. For a one-sided rule it reports
only the selected direction.

This quantity is a forward operating characteristic under an assumed true effect and fixed SE. It
is not a confidence bound, an observed estimate, “observed power,” a posterior probability, a
clinically validated minimum important difference, or a study-specific sample-size result.

## Inputs

Precision can be supplied as either:

- a reported nominal 95% CI, with an optional estimate validated against the CI midpoint; or
- a direct standard error on the Wald working scale.

Ratio measures use the log working scale, so direct SE must be a log-scale SE. Additive measures
use the identity scale. Other controls are the effect measure, null, alpha, two-sided or directional
one-sided rule, target selected-claim probability, optional user-defined meaningful-effect
scenario, optional information multiplier, and optional natural-scale display range.

The information scenario uses Core's
`scenario SE = current SE / sqrt(information multiplier)`. It is relative information, not
automatically a sample-size multiplier.

## Outputs

- exact current and information-scenario critical effects;
- signed standardized critical delta and achieved probability;
- exact selected-claim probability curves;
- effects meeting 50%, 80%, and 90% probability;
- probability at a user-defined meaningful-effect scenario;
- observed estimate, null, meaningful-effect, and reported-CI context markers when supplied;
- an optional legacy closed-form benchmark at the historical fixed defaults;
- an explicit four-column curve CSV, figure PNG, dashboard PNG, and copyable caption.

Ratio critical effects are calculated as equal log distances and displayed on the natural scale.
They are multiplicatively, not arithmetically, symmetric around the null ratio.

## Exact result versus legacy benchmark

The primary result solves the exact selected-claim probability equation through released Core
v0.4.2. When the rule is two-sided with alpha 0.05 and target 0.80, the app also displays the
preserved historical benchmark

```text
(z_(1 - alpha/2) + z_power) * SE
```

as **Legacy closed-form benchmark**. It is intentionally not labeled as the exact solution of the
two-tailed probability equation.

## Architecture and dependency integrity

```text
browser form
  -> dedicated Web Worker
  -> hash-verified generated Python bundle
  -> critical_effect_size.contract.calculate_json
  -> wald-inference 0.4.2 exact APIs
  -> strict focused JSON
  -> textual summaries + Plotly + explicit exports
```

- `src/critical_effect_size/` owns validation, orchestration, display payloads, and exports.
- `wald-inference` owns every Wald probability, inverse, reconstruction, transformation, legacy
  benchmark, and information-scaling primitive.
- `browser-stage.toml`, `pyproject.toml`, and `uv.lock` bind the Core wheel to its v0.4.2 release URL
  and SHA-256
  `225331d7b9d7b70e2508eecb92851a92a8c4e245baf412a1eb0f464d85da1349`.
- `scripts/stage_browser_packages.py` stages the installed app and Core from the locked
  environment. Generated `web/assets/py/` is ignored and verified byte-for-byte before import.

No sibling checkout is used at runtime or during clean staging.

## Privacy and clinical boundary

The app has no backend, database, telemetry, cookies, browser storage, upload path, or
input-bearing URL. Values exist only in page and worker memory; exports are created locally after
an explicit button press. Synthetic fixtures contain no clinical records.

The app is an educational and research-facing design aid, not a validated clinical or regulatory
device. It does not diagnose, recommend treatment, select a clinical MCID, or validate a study
design.

See [scientific scope](docs/SCIENTIFIC_SCOPE.md), [validation](docs/VALIDATION.md),
[privacy](docs/PRIVACY.md), [provenance](docs/PROVENANCE.md), and the
[private security-reporting policy](SECURITY.md).

## Related Wald tools

[Wald inference tools catalog](https://reblocke.github.io/wald-inference-tools/) ·
[Precision guardrail planner](https://reblocke.github.io/precision-guardrail-planner/) ·
[Integrated workbench](https://reblocke.github.io/conf_curve_likelihood/) ·
[Repository](https://github.com/reblocke/critical-effect-size)

Numerical authority:
[wald-inference Core v0.4.2](https://github.com/reblocke/wald-inference-core/releases/tag/v0.4.2).
[Privacy](docs/PRIVACY.md) documents the client-side, no-storage boundary.

## Local development

```bash
uv sync --locked
uv run playwright install chromium webkit
make verify
```

Other useful commands:

```bash
make stage-web
make test
make e2e
make e2e-webkit-smoke
make serve
```

## Repository governance and future releases

Third-party GitHub Actions retain their established major families and are pinned to reviewed full
commit SHAs. Dependabot applies a seven-day eligibility cooldown and groups weekly `uv` and Actions
updates for review; it does not merge them automatically. CI has read-only contents access, Pages
build and deploy privileges are separated, and checkouts do not persist credentials.

For a new version, an annotated tag's exact remote object must resolve to the event commit, be
contained in protected `main` history, and equal `v` plus the project version before repository
code runs. The workflow uses an exact checksummed GitHub CLI, reruns `make verify` without a release
cache, builds and checksums the source and browser-stage artifacts, and transfers the complete
bundle to a narrowly write-enabled job. Using only the job-scoped GitHub token, that job creates a
draft stable release, redownloads and compares the exact body and assets, publishes the verified
draft once, and verifies the resulting immutable release and asset attestations.

The existing `v0.1.3` release predates this workflow; its one-time promotion to stable is complete.
Do not move its tag or replace its assets. New versions publish once into their intended stable,
immutable lifecycle state.
See [CONTRIBUTING.md](CONTRIBUTING.md) and [maintenance](docs/MAINTENANCE.md).

## Method reference and citation roles

Perugini A, Gambarota F, Toffalini E, Lakens D, Pastore M, Finos L, Core Team Psicostat, Altoè G.
The Benefits of Reporting Critical-Effect-Size Values. *Advances in Methods and Practices in
Psychological Science*. 2025;8(2):25152459251335298. doi:
[10.1177/25152459251335298](https://doi.org/10.1177/25152459251335298).

The source was retrieved on 2026-04-23 and is distributed under
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). It motivates
critical-effect-size design reasoning; it does not define or validate this app's exact inverse,
probability target, supported effect registry, or legacy benchmark. The transparent definitions
above and the exact pinned Core release govern the implemented quantity. No publication figure,
table, dataset, code, or substantial text is copied.

When discussing the method context, cite Perugini et al.; independently cite the exact software
release or commit used through [`CITATION.cff`](CITATION.cff).

## License and citation

Code is MIT licensed. Copyright (c) 2026 Brian Locke. Cite the exact repository release or commit
used; machine-readable metadata is in [`CITATION.cff`](CITATION.cff).
