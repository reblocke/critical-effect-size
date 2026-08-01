# Decisions

## 2026-07-31 — Publish reviewed maintenance updates as v0.1.5

The v0.1.5 patch records reviewed build/test dependency and GitHub Actions updates, keeps the
repository-policy allowlist synchronized to the exact reviewed Action pins, and restores exact
identity among the hosted Pages commit, package metadata, citation, annotated tag, and immutable
release artifacts. These maintenance updates do not change the checksum-pinned Core v0.4.2
authority, any critical-effect result, exact-versus-legacy interpretation, focused response or
export contract, scientific tolerance, browser behavior, or client-side privacy boundary.

## 2026-07-31 — Adopt stable Core v0.4.2 without numerical change

The v0.1.4 app patch adopts the stable, immutable `wald-inference` v0.4.2 release at commit
`8afd0a463cc1d2586b8ce5cf92f40900647c3190`, annotated tag object
`26ea4a721b2dfa07f75c2f388a42d6272c88477c`, and exact wheel SHA-256
`225331d7b9d7b70e2508eecb92851a92a8c4e245baf412a1eb0f464d85da1349`. Core v0.4.2 changes only
repository and release governance; it preserves every formula, public API, tolerance, dependency
resolution, and frozen baseline value, including the exact detectability behavior and unchanged
legacy benchmark retained by v0.4.1.

The app still delegates every scientific primitive to root-public Core APIs and adds or copies no
Wald probability, inverse, reconstruction, transformation, information-scaling, or legacy
benchmark formula. Its focused response, exact-versus-legacy interpretation, exports, privacy
boundary, and scientific tolerances remain unchanged; exact pin, lock, staging,
scientific-reference, strict-JSON, Chromium, WebKit, and no-sibling clean-checkout verification are
release gates.

## 2026-07-29 — Functional Python contract and verified browser worker

Python is the contract source of truth. The static UI sends strict JSON to a restartable Web Worker
running exact-version Pyodide. Installed app and Core files are generated from the locked
environment, ignored in Git, and verified by file, package, and aggregate hashes before import.

The repository owns its copied UI at creation time rather than depending on a live shared
template. There is no backend, telemetry, persistence, cookie, or input-bearing URL.

## 2026-07-30 — Released Core is the sole numerical authority

`wald-inference` v0.4.1 owns effect transformations, CI reconstruction, selected-claim
probabilities, power curves, critical-effect inversion, information scaling, and the legacy
benchmark. The app owns strict validation, orchestration, warnings, display payloads, and exports
but implements no alternative Wald probability or solver.

The dependency is pinned to the release wheel URL and SHA-256 in `pyproject.toml`, `uv.lock`, and
`browser-stage.toml`. A sibling checkout is never a staging source.

The initial v0.1.0 app used Core v0.3.0. Patch release v0.1.1 adopts v0.4.1 because it repairs an
active-threshold inverse-precision bracket, extreme finite pairwise support comparison, and strict
ratio back-transform underflow while retaining the ordinary and frozen parity contracts. The
repairs remain in Core; no corresponding formula is copied into this app.

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

## 2026-07-30 — Compact plots prioritize readable labels

When the rendered plot—not merely the browser window—is at most 480 px wide, the plot wraps its
title and long contextual annotations, hides the mode bar, and moves critical-effect, null, and
meaningful-scenario marker labels into a compact legend. A `ResizeObserver` rebuilds the plot only
when its measured container crosses that category. Wider plots retain direct marker labels.

Figure and dashboard PNGs always render a temporary, fixed-size noncompact plot with direct marker
labels and export-scale typography, even when the visible result is compact. The temporary plot is
removed after image generation and does not change the live plot, response, or exported values.
These are presentation-only choices and do not alter the app contract or released-Core
calculations.

The layout is guarded with real Plotly text bounding boxes at 390 px, a narrow two-column plot at
an 850 px viewport, post-render breakpoint crossings, and mobile-origin export inspection.
Page-level `scrollWidth` alone is insufficient because an SVG title can be clipped without
widening the document.

## 2026-07-31 — Release verification uses repository workflow credentials only

This decision supersedes only the signed-tag-verification and dedicated settings-secret portions
of the 2026-07-30 governance decision below. A release still requires an annotated version tag.
Before repository code runs, the workflow requires the local tag to be an annotated tag at the
event commit, binds that tag to the exact remote tag object and event commit, requires protected
`main` containment, and matches the tag to the authoritative project version. GitHub's
`verification.verified` and `verification.reason` fields are no longer release gates; a tag may be
signed, but a valid GitHub signature is not required.

Repository release immutability remains an operator prerequisite, but the workflow no longer
queries that setting with an external administration-read credential. Remote tag inspection and
release publication use the job-scoped GitHub token. The publishing job still creates a draft,
compares its exact body and every downloaded asset before publication, then requires the published
release to report `isImmutable = true` and verifies the release and each asset attestation with the
same job-scoped token. The legacy `v0.1.3` one-time promotion is complete; that historical stable
release predates immutable publication and must not be moved or replaced. All other
least-privilege, protected-history, deterministic-artifact, and one-time publication controls from
the prior decision remain in force.

## 2026-07-30 — Fail-closed repository and stable-release governance

Third-party GitHub Actions retain their reviewed major families and are content-addressed by full
commit SHA. Dependabot applies a seven-day eligibility cooldown and proposes grouped weekly `uv`
and Actions updates for review without automatic merging. CI and Pages build jobs have explicit
read-only contents permission; Pages deployment and release publication receive only their
required writes, and every checkout disables persisted credentials.

A new release requires a GitHub-verified signed annotated tag bound to the event commit and
contained in protected `main` history. These checks precede isolated project-version parsing or
repository code execution. Release verification disables dependency caching, installs an exact
checksummed GitHub CLI, reruns the complete suite, and constructs a deterministic source archive,
browser-stage manifest, checksum file, and bounded version-specific release body before any
release exists.

A separate publishing job receives the verified bundle and only contents-write permission. A
dedicated repository-administration read secret checks that immutable releases are enabled. The
job creates a draft stable release, compares the GitHub-returned body and every redownloaded asset
with the verified local bundle, and publishes once only after exact agreement. Published tags,
assets, and lifecycle state are never rewritten.

The existing `v0.1.3` prerelease is a legacy exception: one administrative promotion may occur
only before immutability is enabled and only after tag, asset, checksum, Pages, and hosted-smoke
evidence proves that no release bytes or commit identity change. This governance decision changes
no scientific calculation, focused response, browser behavior, version, or exact Core dependency.
