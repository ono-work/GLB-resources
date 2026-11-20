# Harvest certified baseline

Generated 2026-11-06 21:15 by `harvest/make_baseline_md.py` from `COUNTED_FAMILIES.json`.

```
certified bound   B = 10388063614992087355867888261572976595948
                  log10 B = 40.016535   (1.0388 × 10^40)
exceeds 10^40:    True
candidate (all producer values, if all verified) = 13944846602194712391703620560836501567040  (log10 40.144414)
```

| family | exact original contribution | mirror contribution | verifier | structural audit | included in total |
|---|---:|---:|---|---|---|
| v5 (G1, G2 and their mirrors) | 1910895019390363935559973877007439048864 (including mirrors) | (included) | verify_v5 AUDIT PASSED | PASSED | yes |
| N2 = Ψ([3, 12],[21]) | 493487524783195558377314979133320190779 | 493487524783195558377314979133320190779 | AUDIT PASSED | PASSED | yes |
| N4 = Ψ([12, 21],[3]) | 789191188948717705917614333988532013894 | 789191188948717705917614333988532013894 | AUDIT PASSED | PASSED | yes |
| N5 = Ψ([12],[3, 21]) | 1031357479510084678164489779817476179310 | 1031357479510084678164489779817476179310 | AUDIT PASSED | PASSED | yes |
| Z1 = Ψ([3, 12, 21],[0]) | 789191188948717705917614333988532013894 | (not yet) | pending | PASSED | no |
| Z2 = Ψ([3, 12],[0, 21]) | 1031357479510084678164489779817476179310 | 1031357479510084678164489779817476179310 | AUDIT PASSED | PASSED | yes |
| ZG2 = Ψ([3, 12],[0]) | 234090676789438332929918204237281734338 | (not yet) | pending | PASSED | no |
| N3 = Ψ([3, 21],[12]) | 755109627863156479070333611405948737314 | (not yet) | pending | PASSED | no |
| N6 = Ψ([3],[12, 21]) | 893190625048779089530048319525964210249 | 893190625048779089530048319525964210249 | AUDIT PASSED | PASSED | yes |

## Mirror accounting

- **Mirror map.** The map is negation `{L|R} ↦ {−R|−L}`. It is an involution on games, so it is injective. It maps canonical forms to canonical forms, and safe pairs to safe pairs, because the conditions are symmetric under negation (machine-checked on samples by the audit).
- **Fixed points.** `−0 = 0` and `−* = *`. The global audit checks both.
- **Four classes.** Every counted original lies in one of two classes, and each mirror lies in the negated class:
  - `O0` = {0 ∈ R, 0 ∉ L}: v5 G1/G2 and the N-families; their mirrors lie in `−O0` = {0 ∈ L, 0 ∉ R}.
  - `OZ` = {0 ∉ L ∪ R, * ∈ R ∖ L}: the Z-families; their mirrors lie in `−OZ` = {0 ∉ L ∪ R, * ∈ L ∖ R}.
- **Consequences.** The four classes are pairwise disjoint. So no mirror equals any original, and no mirror appears as any other counted cell. Mirrors of disjoint originals are disjoint, because negation is injective.

## Disjointness of originals

- **The key.** The key `(world, S, C, E)` is a function of `R`. It records which of `{0,*,±1,*2}` lie literally in `R`, which are covered strictly below, and which are uncovered. Distinct keys therefore mean disjoint families.
- **v5 G1.** G1 has key (0; *±1*2; –; –), which no Ψ family uses.
- **v5 G2 and N2.** v5 G2 has `R ∩ F0 = {*, ±1}` and `L ⊆ H_L([0,*,±1])`. N2 has the same `S` but requires `L ⊄ H_L([0,*,±1])`, so the two are disjoint.
- **P-cells.** `P = R ∩ G_2` is not always constant on a family. In N5, Z2 and N6, `B` may contain one further day-2 game (ids 17, 15 and 19 respectively). Those families span the two cells `P = T` and `P = T ∪ {x}`, listed in `COUNTED_FAMILIES.json` (`P_cells`). Disjointness does not rely on `P`: it relies on the key. `S = R ∩ F` is unaffected because `B ∩ F = ∅`. The global audit recomputes the P-cells exactly.

Distinct option pairs give distinct games, because safe pairs are canonical. The global audit is `harvest/global_audit.py`.
