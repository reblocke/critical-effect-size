## Scope

Describe the engineering, scientific, documentation, governance, or maintenance problem addressed.
Name `wald-inference-core` when released Core owns the affected numerical behavior.

## Risk and release impact

Describe silent-failure risks, exact-versus-legacy implications, privacy/accessibility effects,
generated-stage changes, and whether the change requires a new release.

## Verification

List the exact commands run and their outcomes. Include skipped checks and warnings.

## Checklist

- [ ] No Wald probability, inverse, reconstruction, transformation, information-scaling formula,
      or legacy benchmark was copied into this repository.
- [ ] The exact selected-claim result remains primary, and the historical z-sum quantity remains a
      distinctly labeled legacy closed-form benchmark.
- [ ] A meaningful effect remains explicitly user-defined and unvalidated; relative information
      remains distinct from study-specific sample size.
- [ ] Public copy stays within validated functionality and does not imply clinical or regulatory
      readiness.
- [ ] Examples and fixtures are synthetic and contain no credentials, sensitive data, or protected
      health information.
- [ ] No backend, telemetry, persistence, cookies, hidden state, upload, or input-bearing URL was
      added.
- [ ] Generated Python under `web/assets/py/` was produced by `make stage-web`, not edited by hand.
- [ ] Every third-party GitHub Action remains pinned to a reviewed full commit SHA with a version
      comment.
- [ ] `uv sync --locked` and `make verify` pass.
- [ ] README, scientific scope, validation, privacy, provenance, runtime dependencies, decisions,
      maintenance, citation, and changelog were reviewed for synchronization.
