# Runtime Dependencies and Provenance

## Browser runtime

- Pyodide 0.29.3, MPL-2.0, loaded from its versioned jsDelivr path.
- Plotly.js 3.1.0, MIT, loaded from Plotly's versioned CDN path.
- NumPy 2.2.6 and SciPy 1.14.1, BSD-3-Clause, supplied by the pinned Pyodide runtime.
- Generated local Python files listed and hashed in `web/assets/py/manifest.json`.

Static CDN requests do not include user values. App availability depends on reaching those CDNs;
the app does not silently fall back to a different runtime version.

## Scientific Core

`wald-inference` 0.3.0 is required for all numerical behavior.

- source:
  `https://github.com/reblocke/wald-inference-core/releases/download/v0.3.0/wald_inference-0.3.0-py3-none-any.whl`
- SHA-256:
  `630fdece13c2940f751d1f5d3a4d6477182dbb099131a9907ceef7067348f939`
- license: MIT
- release/tag: `v0.3.0`, peeled commit
  `9618abf3a632838794e9e40752af7823e77115cb`

The direct URL and checksum are bound in package metadata, `uv.lock`, and
`browser-stage.toml`. Staging verifies installed distribution provenance and every staged Core
file against its wheel RECORD.

## Development dependencies

`uv.lock` controls local and CI resolution. Ruff formats and lints; pytest supplies the test
runner; Playwright and pytest-playwright drive Chromium/WebKit; Hypothesis remains available for
bounded property tests. These are development-only and are not staged into the app.

## Licensing boundary

Repository-authored code, documentation, tests, and synthetic fixtures are MIT licensed.
Dependencies and publications retain their own licenses. No external code, publisher figure,
table, dataset, or substantial publication text is copied into the repository.
