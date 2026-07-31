# Validation

## Numerical authority

The app pins the stable, immutable `wald-inference` v0.4.2 release from:

```text
https://github.com/reblocke/wald-inference-core/releases/download/v0.4.2/
wald_inference-0.4.2-py3-none-any.whl
```

The wheel SHA-256 is
`225331d7b9d7b70e2508eecb92851a92a8c4e245baf412a1eb0f464d85da1349`; annotated tag object
`26ea4a721b2dfa07f75c2f388a42d6272c88477c` peels to
`8afd0a463cc1d2586b8ce5cf92f40900647c3190`. Core release run `30629025349` and main CI run
`30628647428` were green, and the released Core retained zero
difference across the frozen 23,095-value pre-split parity contract.

The app keeps orchestration and presentation local but delegates every scientific primitive to
that released Core. Core v0.4.2 changes repository and release governance only while preserving
every numerical API and frozen value from v0.4.1, including its active-threshold inverse-precision,
extreme pairwise support, and strict ratio-underflow repairs. This app adds no local formula and
retains its existing scientific tolerances without widening.

## Independent scientific targets

`tests/scientific_reference/test_detectability.py` checks:

- exact two-sided and directional one-sided probability at the null equals alpha;
- one-sided inverses agree with independent Python `statistics.NormalDist` quantiles;
- the two-sided inverse agrees with direct normal-tail evaluation;
- positive and negative two-sided working distances are symmetric;
- ratio natural-scale solutions are multiplicatively symmetric;
- fourfold information halves SE and halves the required working distance;
- direct-SE and equivalent reported-CI inputs agree;
- meaningful-effect probability agrees with direct normal tails;
- the exact result differs from the unchanged, distinctly labeled legacy benchmark.

Ordinary probability comparisons use absolute tolerances from `2e-15` to `8e-15`; inverse
working-scale comparisons use up to `2e-13`. These tolerances cover binary64 distribution and
quantile evaluation while remaining much smaller than displayed precision. Core's stricter
conservative predecessor-minimality and extreme-tail contracts are tested in the Core release.

## Frozen regression provenance

`tests/fixtures/integrated_baseline/critical_effect_scenarios.json` freezes two synthetic
standard-error cases from integrated behavior source
`830756ecb11b4e8161f8dfe1fc75afc346ef4467`. The fixture records exact v0.3.0 two-sided inverse
distances and unchanged legacy distances. It contains no patient or study data.

## Contract, browser, privacy, and accessibility

The suite verifies:

- exact eight-part focused response and absence of compatibility, likelihood, Type S/M, and
  inverse-planning sections;
- strict input and output JSON with non-finite and oversized-number rejection;
- invalid alpha, target, SE, multiplier, mode, range, and unsupported-rule failures;
- exact-version, release-URL, checksum, installed RECORD, and deterministic browser staging;
- manifest and byte verification before Python import;
- CI/direct-SE control state, one-/two-sided output routing, stale-result clearing, sanitized
  errors, and recovery;
- textual alternatives, labeled controls, linked error focus, visible focus, keyboard flow, and
  responsive layout, including 390 px rendered Plotly title, legend, and annotation containment
  and non-overlap, an 850 px two-column compact plot, and post-render plot-width category
  crossings;
- no persistence, telemetry, cookie, input-bearing URL, or input-bearing network request;
- explicit four-column CSV, figure PNG, dashboard PNG, and caption exports, including
  mobile-origin PNGs rendered from a temporary noncompact direct-label plot;
- Chromium full E2E and WebKit worker/calculation smoke.

## Browser parity

The browser stages the same installed app and checksum-bound Core used by local Python tests.
Pyodide 0.29.3 supplies NumPy and SciPy. The manifest records app/Core versions and file,
package, and aggregate SHA-256 hashes; the worker verifies them before import. E2E assertions run
the default ratio case and additive/direct-SE, information, one-sided, validation, export,
accessibility, and privacy cases through Pyodide.

## Release gate

```bash
uv sync --locked
uv run playwright install chromium webkit
uvx --from zizmor==1.28.0 zizmor .
make verify
uv run pytest -q tests/regression/ tests/scientific_reference/
uv run python scripts/stage_browser_packages.py
git diff --check
git status --short
```

For each release, record the exact commit/tag, Core artifact hash, generated stage manifest hash,
local/CI results, release assets, Pages deployment, hosted smoke, and any skipped check or known
limitation.

For a new release, also record:

- exact identity of the local and remote annotated tag objects and their event-commit target;
- containment of that target in protected `main` before repository metadata or code execution;
- the checksummed GitHub CLI version and archive digest;
- the nonempty release body extracted only from the matching changelog section;
- the transferred and redownloaded source archive, browser-stage manifest, and `SHA256SUMS`;
- exact equality of the draft body, asset names, bytes, and checksums before publication;
- operator confirmation before tagging that immutable releases are enabled; and
- post-publication stable lifecycle, immutable provenance, and per-asset verification.

Repository-policy tests cover `.yml` and `.yaml` workflow action pins, retained action major
families, explicit permissions, disabled checkout credential persistence, disabled release cache,
annotated-tag identity and protected-main ordering, checksummed GitHub CLI installation, exact
draft transfer, stable one-time publication, Dependabot coverage, private-reporting guidance, and
preservation of the app's exact-versus-legacy and negative-scope boundaries. These tests establish
engineering policy; they do not expand the scientific validation claim.
