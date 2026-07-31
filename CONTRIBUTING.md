# Contributing

## Repository scope

This repository owns strict validation, orchestration, browser payloads, presentation, and exports
for one-parameter Wald critical-effect calculations. Released `wald-inference` owns every
probability, inverse, CI reconstruction, effect transformation, information-scaling primitive, and
legacy benchmark. Add a missing numerical primitive and release it in
`wald-inference-core`—never copy a formula here.

The exact selected-claim result is primary. The historical z-sum quantity remains a distinctly
labeled **Legacy closed-form benchmark**, not the exact two-tailed solution. A user-defined
meaningful effect remains explicitly unvalidated, and relative information remains distinct from
study-specific sample size.

Use public issue forms only for nonsensitive engineering and accessibility reports. Report
vulnerabilities through the private process in [SECURITY.md](SECURITY.md). Never place credentials,
protected health information, patient-level data, unpublished restricted data, or other sensitive
values in an issue, pull request, fixture, screenshot, URL, or workflow log.

## Change process

1. Start from the current protected `main` branch and make one reviewable change.
2. State assumptions, success criteria, silent-failure risks, and verification before editing.
3. Preserve the focused response, exact-versus-legacy distinction, scientific limitations, and
   negative scope unless the reviewed task explicitly changes them.
4. Keep Python under `src/critical_effect_size/` as source of truth and regenerate browser Python
   with `make stage-web`.
5. Keep Core exact-version, release-URL, and checksum bound.
6. Keep third-party GitHub Actions pinned to full commit SHAs with version comments.
7. Open a pull request and let all required checks complete before merging.

Do not add a backend, telemetry, persistence, cookies, hidden state, uploads, input-bearing URLs, or
locally owned Wald formulas as conveniences.

## Verification

Restore the locked environment and run the complete documented suite:

```bash
uv sync --locked
uv run playwright install chromium webkit
make verify
git diff --check
git status --short
```

Scientific or Core-adoption changes also require independent scientific-reference and frozen
regression review. Browser, staging, privacy, and accessibility changes require the corresponding
Chromium and WebKit checks. Document any skipped check or warning.

## Release changes

A new release requires a reviewed pull request and a signed, annotated version tag pointing to the
exact reviewed merge commit. The tag must equal `v` plus the authoritative project version, and
that version needs a nonempty changelog section. The tag workflow:

1. installs an exact checksummed GitHub CLI;
2. cryptographically verifies the GitHub tag object and binds it to the event commit;
3. requires the verified tag target to be contained in protected `main` history before reading
   project metadata or executing repository code;
4. verifies the complete suite with read-only contents permission and release caching disabled;
5. builds and checksums every asset before release creation;
6. transfers the complete bundle to a narrowly write-enabled publishing job;
7. requires repository release immutability through an administration-read token;
8. creates a draft stable release using only the current version's changelog section;
9. downloads and compares the exact release body and every asset; and
10. publishes the verified draft once as stable and confirms immutable provenance.

Before creating a new tag, enable immutable releases and configure a fine-grained
repository-administration read token as the `RELEASE_SETTINGS_READ_TOKEN` Actions secret. The
publishing job uses that secret only for the fail-closed settings query; release creation uses the
job-scoped GitHub token.

The existing `v0.1.3` prerelease predates this workflow. Its one-time administrative promotion may
occur only after tag, asset, checksum, Pages, and hosted-smoke evidence is archived and before
immutable releases are enabled. Promotion must not rebuild assets or move the tag. New releases use
the draft as the candidate and publish once into their intended stable lifecycle state.

If a new release job fails after draft creation, leave the release as a draft for inspection. Do
not replace assets or move a tag after publication.
