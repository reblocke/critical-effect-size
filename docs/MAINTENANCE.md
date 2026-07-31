# Maintenance

## Status and ownership

Status: active experimental scientific app, version 0.1.4.

Maintainer: Brian Locke (`@reblocke`). Use repository issues and pull requests for public
coordination. Scientific behavior changes require review of Core authority, app contract, tests,
public wording, and export interpretation.

## Dependency updates

Review Pyodide, Plotly, Python, uv, Ruff, pytest, Playwright, and GitHub Actions updates
deliberately. Dependabot applies a seven-day eligibility cooldown and groups weekly `uv` and GitHub
Actions proposals for human review; it does not authorize automatic merging. Every third-party
Action remains pinned to a full commit SHA with its reviewed version in a comment. For a
`wald-inference` upgrade:

1. review its release notes, exact API, and scientific changes;
2. bind the exact release wheel URL and SHA-256 in `pyproject.toml`, `uv.lock`, and
   `browser-stage.toml`;
3. regenerate the environment and inspect the lock;
4. rerun strict JSON, scientific references, frozen regressions, staging, Chromium, WebKit, and a
   clean-checkout stage without sibling repositories;
5. update Core versions and validation evidence in docs, UI, and release notes.

## Release

Use a reviewed pull request. Verify the exact expected head, merge, then create an annotated
semantic-version tag at that merge commit. The tag must equal `v` plus the authoritative project
version and have a nonempty matching changelog section.

The release workflow installs a checksummed GitHub CLI, binds the exact remote annotated tag object
to the event commit, and requires that commit to be contained in protected `main` history before
isolated version parsing or repository code execution. It reruns `make verify` under read-only
contents permission with release caching disabled, then builds the deterministic source archive,
browser-stage manifest, SHA-256 checksums, and version-specific release body before a release
exists.

A separate job with only contents-write permission retrieves and rechecks the complete bundle. It
uses the job-scoped GitHub token to create a draft stable release with the exact assets, redownload
and compare its body and every asset, and publish once. It then requires the release to be stable
and immutable and verifies the release and every asset attestation with the same token.

If the workflow fails after draft creation, retain the draft for inspection. Repair through a
reviewed new commit and version/tag after the failure is understood; never move a published tag or
replace a published asset. The draft is the candidate, and new versions publish once into their
intended stable lifecycle state.

The existing `v0.1.3` release predates this process; its one-time promotion to stable is complete.
Do not move its tag or replace its assets. New versions publish once into their intended stable,
immutable lifecycle state.

Repository settings must retain read-only default workflow permissions, protect `main` and `v*`
tags, enable private vulnerability reporting and Dependabot security updates, and enable immutable
releases before a new tag is created. Confirm that setting operationally before tagging; the
workflow carries no external repository-settings credential and verifies immutability after
publication with its job-scoped GitHub token.

## Deprecation

No deprecation is scheduled. If the app is deprecated, publish a tagged notice, add visible README
and hosted-app banners naming any successor, and retain historical release artifacts. Do not
silently redirect or delete the public URL.
