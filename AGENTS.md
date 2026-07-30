# Codex AGENTS

## Purpose

- This repository is a static client-side app for exact one-parameter Wald critical-effect and
  selected-claim probability calculations.
- Released `wald-inference` is the sole numerical source of truth.
- Python under `src/critical_effect_size/` owns strict validation, orchestration, and browser
  payloads; generated browser Python is ignored.

## Commands

- Setup: `uv sync --locked`
- Stage: `make stage-web`
- Format: `make fmt`
- Format check: `make fmt-check`
- Lint: `make lint`
- Non-browser tests: `make test`
- Chromium: `make e2e`
- WebKit smoke: `make e2e-webkit-smoke`
- Full verification: `make verify`

## Working rules

- Before non-trivial changes, state assumptions, ambiguities, tradeoffs, success criteria, risks,
  expected files, and verification commands.
- Do not implement or copy a Wald probability, inverse, reconstruction, effect transformation,
  information-scaling formula, or legacy benchmark in this repository. Release missing primitives
  in `wald-inference-core` first.
- Keep the exact critical effect primary. Never relabel the legacy z-sum benchmark as the exact
  two-tailed solution or present observed power as evidence.
- Keep user-defined meaningful effects explicitly unvalidated and information multipliers distinct
  from study-specific sample size.
- Run staging; never hand-edit `web/assets/py/`.
- Keep Core upgrades exact-version, release-URL, and checksum bound in package metadata, lock, and
  stage configuration.
- Preserve client-side privacy: no backend, telemetry, persistence, cookies, PHI logging, upload,
  or input-bearing URLs.
- Keep accessible textual output; plots must not be the sole carrier of a result.
- Use `uv`, Ruff, pytest, and Playwright; avoid parallel dependency or build systems.

## Done criteria

- Scientific-reference, regression, contract, staging, privacy, accessibility, Chromium, and
  WebKit checks pass.
- Stage output reproduces from a clean checkout without sibling repositories.
- Scientific scope, validation, privacy, provenance, citation, maintenance, and release notes are
  synchronized.
- Hosted Pages loads the pinned app/Core versions and passes a calculation/privacy smoke check.
