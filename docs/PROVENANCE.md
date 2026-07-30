# Provenance

## Template initialization

The repository was created from released `reblocke/scientific-applet-template` v0.1.0.

- annotated template tag peeled commit:
  `a360bde95c192d8de4f9a3b531e73600ebf3d8b8`
- template tree:
  `6a6c8c33cbef24b5dcbd35706d2292d9d3e5e359`
- new repository initial commit:
  `5ff3a10bfc610fbfe915f438aa8f11cdee6c3361`
- new repository initial tree:
  `6a6c8c33cbef24b5dcbd35706d2292d9d3e5e359`

The identical trees prove the initializer started from the released template. The guarded
initializer then ran once with:

```bash
uv run python scripts/initialize_template.py \
  --repository-name critical-effect-size \
  --distribution-name critical-effect-size \
  --import-name critical_effect_size \
  --app-title "Wald Critical Effect Size" \
  --description "Exact one-parameter Wald detectability and critical-effect calculations"
```

Its ignored `.applet-template-initialized.json` report recorded no unresolved identity values.
`.template-identity.json` remains the tracked initialized identity.

## Scientific Core

The app consumes released `wald-inference` v0.3.0, tagged at peeled commit
`9618abf3a632838794e9e40752af7823e77115cb`. The official wheel SHA-256 is
`630fdece13c2940f751d1f5d3a4d6477182dbb099131a9907ceef7067348f939`.

The Core release added exact selected-claim probability, vectorized power-curve, and
critical-effect inverse APIs while retaining the unchanged pre-split legacy z-sum benchmark.

## Integrated behavior fixture

The synthetic fixture under `tests/fixtures/integrated_baseline/` preserves exact and legacy
distances from integrated behavior source
`830756ecb11b4e8161f8dfe1fc75afc346ef4467`, as carried into Core v0.3.0 scientific-reference
tests. It contains no external or clinical data.

## Methodology reference

Perugini et al., *Advances in Methods and Practices in Psychological Science* (2025), is carried
forward for critical-effect-size design rationale; source retrieval date 2026-04-23:

<https://journals.sagepub.com/doi/10.1177/25152459251335298>

The reference is contextual. Transparent normal/Wald definitions and released Core behavior govern
the implemented quantity. No external figure, table, dataset, source code, or substantial text was
copied.

## Authorship and license

The repository owner selected `Brian Locke` as the canonical author and maintainer. Code and
repository-authored artifacts use MIT with `Copyright (c) 2026 Brian Locke`. No affiliation, email,
ORCID, DOI, or additional author is inferred.
