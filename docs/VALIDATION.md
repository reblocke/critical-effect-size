# Validation

## Numerical authority

The app pins released `wald-inference` v0.4.1 from:

```text
https://github.com/reblocke/wald-inference-core/releases/download/v0.4.1/
wald_inference-0.4.1-py3-none-any.whl
```

The wheel SHA-256 is
`d7272023f65088729d3ff997cab7cac57b84f22ac6108244ec2170434557d99b`; annotated tag
`v0.4.1` peels to `f4613177b6dc81d194aa70762152de2bfa86663b`. Core release run
`30545293704` and main CI run `30545147370` were green, and the released Core retained zero
difference across the frozen 23,095-value pre-split parity contract.

The app keeps orchestration and presentation local but delegates every scientific primitive to
that released Core. The v0.4.1 repair release corrects active-threshold inverse-precision
bracketing, extreme pairwise support comparison, and strict ratio back-transform underflow; this
app adds no local formula.

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
  and non-overlap;
- no persistence, telemetry, cookie, input-bearing URL, or input-bearing network request;
- explicit four-column CSV, figure PNG, dashboard PNG, and caption exports;
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
make verify
uv run pytest -q tests/regression/ tests/scientific_reference/
uv run python scripts/stage_browser_packages.py
git diff --check
git status --short
```

For each release, record the exact commit/tag, Core artifact hash, generated stage manifest hash,
local/CI results, release assets, Pages deployment, hosted smoke, and any skipped check or known
limitation.
