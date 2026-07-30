# Maintenance

## Status and ownership

Status: active experimental scientific app, version 0.1.3.

Maintainer: Brian Locke (`@reblocke`). Use repository issues and pull requests for public
coordination. Scientific behavior changes require review of Core authority, app contract, tests,
public wording, and export interpretation.

## Dependency updates

Review Pyodide, Plotly, Python, uv, Ruff, pytest, Playwright, and GitHub Actions updates
deliberately. For a `wald-inference` upgrade:

1. review its release notes, exact API, and scientific changes;
2. bind the exact release wheel URL and SHA-256 in `pyproject.toml`, `uv.lock`, and
   `browser-stage.toml`;
3. regenerate the environment and inspect the lock;
4. rerun strict JSON, scientific references, frozen regressions, staging, Chromium, WebKit, and a
   clean-checkout stage without sibling repositories;
5. update Core versions and validation evidence in docs, UI, and release notes.

## Release

Use a reviewed pull request. Verify the exact expected head, merge, then create an annotated
semantic-version tag at that merge commit. The release workflow reruns `make verify` and publishes
a prerelease with a deterministic source archive, browser-stage manifest, and SHA-256 checksums.
Promote only after Pages and hosted smoke checks pass.

## Deprecation

No deprecation is scheduled. If the app is deprecated, publish a tagged notice, add visible README
and hosted-app banners naming any successor, and retain historical release artifacts. Do not
silently redirect or delete the public URL.
