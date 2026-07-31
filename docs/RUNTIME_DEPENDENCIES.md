# Runtime Dependencies and Provenance

## Browser runtime

- Pyodide 0.29.3, MPL-2.0, loaded from its versioned jsDelivr path.
- Plotly.js 3.1.0, MIT, loaded from Plotly's versioned CDN path.
- NumPy 2.2.6 and SciPy 1.14.1, BSD-3-Clause, supplied by the pinned Pyodide runtime.
- Generated local Python files listed and hashed in `web/assets/py/manifest.json`.

Static CDN requests do not include user values. App availability depends on reaching those CDNs;
the app does not silently fall back to a different runtime version.

## Scientific Core

`wald-inference` 0.4.2 is required for all numerical behavior.

- source:
  `https://github.com/reblocke/wald-inference-core/releases/download/v0.4.2/wald_inference-0.4.2-py3-none-any.whl`
- SHA-256:
  `225331d7b9d7b70e2508eecb92851a92a8c4e245baf412a1eb0f464d85da1349`
- size: 38132 bytes
- license: MIT
- release/tag: stable, immutable `v0.4.2`, annotated tag object
  `26ea4a721b2dfa07f75c2f388a42d6272c88477c`, peeled commit
  `8afd0a463cc1d2586b8ce5cf92f40900647c3190`

The direct URL and checksum are bound in package metadata, `uv.lock`, and
`browser-stage.toml`. Staging verifies installed distribution provenance and every staged Core
file against its wheel RECORD.

Core v0.4.2 changes repository and release governance only. It preserves every numerical formula,
public API, tolerance, dependency resolution, and frozen baseline value, including the v0.4.1
detectability and strict ratio-underflow repairs.

## Development dependencies

`uv.lock` controls local and CI resolution. Ruff formats and lints; pytest supplies the test
runner; Playwright and pytest-playwright drive Chromium/WebKit; Hypothesis remains available for
bounded property tests. These are development-only and are not staged into the app.

## Repository automation

Every third-party GitHub Action is pinned in `.github/workflows/` to a reviewed full commit SHA
with its exact version in a comment. The established action major families are retained:
checkout 6, setup-python 6, setup-uv 7, upload-artifact 7, configure-pages 5,
upload-pages-artifact 4, and deploy-pages 4. The split release handoff adds
download-artifact 8. Their upstream repositories report MIT licensing; source repository and
content-addressed revision are machine-readable in the workflow files.

Credentialed release steps install GitHub CLI 2.93.0 from:

```text
https://github.com/cli/cli/releases/download/v2.93.0/gh_2.93.0_linux_amd64.tar.gz
```

The required SHA-256 is
`02d1290eba130e0b896f3709ffff22e1c75a51475ddb70476a85abc6b5807af0`.
GitHub CLI is MIT licensed. The version, upstream checksum manifest, action tags/commits, and
upstream repository licenses were reviewed on 2026-07-30.

Dependabot applies a seven-day eligibility cooldown and proposes grouped weekly `uv` and Actions
updates for review without automatic merging. Workflow static analysis for this governance change
used MIT-licensed zizmor 1.28.0. Neither tool is part of the client-side runtime or scientific
calculation path.

## Licensing boundary

Repository-authored code, documentation, tests, and synthetic fixtures are MIT licensed.
Dependencies and publications retain their own licenses. No external code, publisher figure,
table, dataset, or substantial publication text is copied into the repository.
