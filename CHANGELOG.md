# Changelog

All notable changes use a release-oriented record here. This repository follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.2] - 2026-07-30

- Keep the exact selected-claim-probability title and contextual annotations readable at a 390 px
  viewport by wrapping compact copy and moving plot-marker labels into a compact legend.
- Add a real-Plotly browser regression that checks rendered title, legend, and annotation bounding
  boxes for viewport containment and overlap. Numerical values, the focused response, exports, and
  the checksum-bound `wald-inference` v0.4.1 authority are unchanged.

## [0.1.1] - 2026-07-30

- Publish the related-tool-navigation Pages source as a checksum-addressed patch release so the
  deployed app, annotated tag, and release artifacts resolve to the same commit.
- Constrain the two-column layout and resize Plotly after the results panel is visible so the
  calculated app remains contained at a 390 px viewport; cover this with a browser regression.
- Adopt the checksum-bound `wald-inference` v0.4.1 wheel with its precision-bracketing,
  extreme-support, and strict ratio-underflow repairs. The focused contract, exports, and
  exact-versus-legacy distinction remain unchanged; no formula is implemented locally.

## [0.1.0] - 2026-07-30

### Added

- Added exact current and information-scenario critical effects for two-sided, one-sided positive,
  and one-sided negative p-value rules.
- Added reported-95%-CI and direct-working-scale-SE precision modes, identity/log effect support,
  optional meaningful-effect and information scenarios, and optional display range.
- Added exact selected-claim probability curves, 50%/80%/90% reference effects, reported-CI and
  observed-estimate context, explicit CSV, figure/dashboard PNG, and caption exports.
- Added a distinctly labeled fixed-default legacy closed-form benchmark without relabeling it as
  the exact two-tailed inverse.

### Dependency provenance

- Pinned `wald-inference` v0.3.0 to the official release wheel and SHA-256
  `630fdece13c2940f751d1f5d3a4d6477182dbb099131a9907ceef7067348f939`.
- Generated browser staging records and verifies app/Core file, package, and bundle hashes.

### Validation

- Added strict JSON, unit, property, integrated-regression, independent scientific-reference,
  staging, repository-policy, privacy, accessibility, Chromium, and WebKit tests.
- Verified one-/two-sided normal references, exact-vs-legacy distinction, direct-SE/CI
  equivalence, ratio mapping, and fourfold-information behavior.

### Scope

- This is a repeated-study fixed-SE Wald design aid, not observed evidence, an MCID validator,
  clinical decision support, or a study-specific sample-size calculator.

[Unreleased]: https://github.com/reblocke/critical-effect-size/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/reblocke/critical-effect-size/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/reblocke/critical-effect-size/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/reblocke/critical-effect-size/releases/tag/v0.1.0
