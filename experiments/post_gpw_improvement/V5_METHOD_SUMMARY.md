# V5 method summary — why `g(4) ≥ 1.911·10^39`

**Result.**

```
g(4) ≥ 1910895019390363935559973877007439048864   ≈ 1.911·10^39   (log10 39.281)
GPW (public, certified): 1425933741673169505174021654095740659 ≈ 1.426·10^36  → factor 1340.10
```

## 1. The basic lemma (GPW)

`G_3` (1474 games) is the set of canonical games born by day 3, ordered by `≤`. Each game born
by day 4 has a unique canonical form `{L | R}` with `L, R` antichains of `G_3`.

A pair `(L, R)` of antichains is **safe** when both of these hold:

- every right option `y` of every `l ∈ L` has some `r ∈ R` with `r ≤ y`;
- dually, every left option `x` of every `r ∈ R` has some `l ∈ L` with `x ≤ l`.

**Lemma.** If `(L, R)` is safe, `{L | R}` is in canonical form. Distinct safe pairs therefore give
distinct games of `G_4`.

*Proof.* No option is dominated, because `L` and `R` are antichains. Suppose a left option `l`
were reversible through `l^R ≤ G`. Pick `r ∈ R` with `r ≤ l^R`. Then `r ≤ G`, which contradicts
`G ⧏ G^R`. The right side is dual. Canonical forms are unique, so distinct pairs give distinct
games. ∎

## 2. The v5 families as exact "cells" of safe pairs

Fix a right kernel `T` (an antichain). The definitions:

- `H_L(T)` = {g : every right option of g is hit by T}.
- `V_max` = {g ∉ T : g ∥ T}.
- `req(g)` = left options of g.
- `dom(L)` = {q ∈ REQ : q ≤ some l ∈ L}.
- `V(D)` = {g ∈ V_max : req(g) ⊆ ↓D}.

```
G(T, x0) = { {L | T ∪ B} : L ∈ A(H_L(T)), req(T) ⊆ ↓dom L, B ∈ A(V(dom L)), x0 ∉ B }
```

**Characterisation.**

```
G(T, x0) = { safe (L, R) : T ⊆ R,  x0 ∉ R,  L ⊆ H_L(T) }
```

- (⊆) This is the safety argument: each `l` is hit by `T ⊆ R`, and each left option of
  `r ∈ T ∪ B` lies below some `q ∈ dom L` and hence below some `l`.
- (⊇) If `(L, R)` is safe with `T ⊆ R`, then:
  - `B = R \ T ⊆ V_max`, because `R` is an antichain;
  - safety for `t ∈ T` gives `req(T) ⊆ ↓dom L`;
  - safety for `b ∈ B` gives `b ∈ V(dom L)`. ∎

So v5 counts the following cells exactly:

```
G1 = G([0,3,12,21], –)  = { safe : {0,3,12,21} ⊆ R,  L ⊆ H_L({0,3,12,21}) }
G2 = G([0,3,12],   21)  = { safe : {0,3,12} ⊆ R, 21 ∉ R,  L ⊆ H_L({0,3,12}) }
```

`G1` and `G2` are the two halves "21 ∈ R" and "21 ∉ R" of the region
`{safe : {0,3,12} ⊆ R, L ⊆ H_L(R ∩ {0,3,12,21})}`.

Each `(L, B)` is counted once. `dom L` is a function of `L`, and `T ∪ B` determines `B` because
`B ∩ T = ∅`.

## 3. Disjointness and the mirror factor 2

**G1 ∩ G2 = ∅.** Every pair in G1 has `21 ∈ R`, and no pair in G2 does. Canonical forms are
unique, so equal games would have equal `R`.

**Mirror lemma.** Negation maps `{L | R}` to `{−R | −L}`. It is an order-reversing involution of
`G_3` that swaps options. It therefore maps safe pairs bijectively to safe pairs, and canonical
forms to canonical forms. In v5 the hypotheses are:

- `0 ∈ T` and `−0 = 0`;
- `req(T)` contains `2`, with `0 < 2`.

Hence `0 ∈ R` for every counted pair, and `0 ∉ L`, since `L` contains some `l ≥ 2 > 0` and is an
antichain. A mirror pair has left set `−R ∋ 0`. So `(G1 ∪ G2) ∩ −(G1 ∪ G2) = ∅`, and
`|−G1 ∪ −G2| = |G1| + |G2|` because negation is a bijection.

**Bound.**

```
bound = 2·(|G1| + |G2|)
```

All hypotheses are checked by machine in `audit_v5_structure.py`. That script also checks that:

- the input table is consistent with Conway's recursive definition of `≤` on all `1474²` pairs;
- every table game is canonical;
- the negation table is Conway negation.

It also runs an end-to-end random test. It samples members of `G1`, `G2`, `−G1` and `−G2`,
checks each for canonicality with a generic Conway comparator for day-4 games, and checks that
no two sampled games are equal.

**GPW overlap.** The v5 bound adds no GPW term. The GPW kernels main, K1, K2 and K5 all have
`T_R = [0,3,12,21]`, `T_L ∪ Q_L^+ ⊆ H_L` and `Q_R^+ ⊆ V(dom T_L)`, so each `Can(K) ⊆ G1`
(machine-checked). This covers:

- the GPW Layer 0–6 family, which lies in `Can(main)`;
- the GPW cell families, which lie in `Can(K1)`, `Can(K2)` and `Can(K5)`.

The GPW residual family (2.6·10^31, a 2·10^−5 fraction of GPW) is neither added nor needed. v5
**replaces** GPW; it does not add to it.

## 4. Where the factor 1340 comes from

The steps below are measured on exact numbers.

| step | family | size | factor |
|---|---|---:|---:|
| GPW main kernel, right Layer 0–6 | `C_L(main) · (R_0+…+R_6)` = 319901739 · 4.429·10^27 | 1.4168·10^36 | — |
| (+ GPW cells + residual) | GPW total | 1.4259·10^36 | (1.006) |
| **1. remove the Layer cutoff** | `Can(main) = C_L(main) · |A(V)|`, `|A(V)| = 5.200·10^29` | 1.664·10^38 | **×117.4** |
| **2. enlarge the left family** | all `L ∈ A(H_L)` dominating `{2,11,14}`, `N_L = 1160639255`, × `|A(V)|` | 6.036·10^38 | **×3.63** |
| **3. dominance-dependent right region** | `G1 = Σ_D e(D)·|A(V(D))|` (regions 114…676) | 6.292·10^38 | ×1.043 |
| **4. second family** | `+G2` (21 ∉ R, main region `W`, 648 = J(10)×J(8)) | 9.555·10^38 | ×1.518 |
| **5. negation mirror** | `×2` | 1.911·10^39 | ×2 |

1. **Layer cutoff (×117).** GPW counted right antichains in the 598-element region `V` only up to
   "Layer 6" around a maximum antichain, because Layer 7 was estimated at 116 h. In fact `V` is a
   distributive lattice `J(Q1) × J(Q2)` with `|Q1| = 7` and `|Q2| = 9`, giving 23 × 26 ideals.
   Its antichains correspond to antitone maps `J(Q1) → J(J(Q2))`, where `|J(J(Q2))| = 171`. A
   rank-by-rank transfer over the ≤ 4 elements per rank of `J(Q1)` computes the count exactly in
   about 11 min.
2. **Left family (×3.6).** GPW fixed `T_L = {2,11,14}` and the left region `Q_L^+`. Every antichain
   `L ⊆ H_L(T)` (320 elements) that dominates the requirements is admissible, because safety only
   needs `L` to dominate the left options of `R`. Kernels K1, K2 and K5 are special cases. The
   count `N_L` is an antichain count with domination constraints, done by include/exclude plus
   inclusion–exclusion. The verifier recomputes it by a direct histogram DP.
3. **Dominance-dependent right region (×1.04).** If `L` dominates more requirements, more
   right elements become admissible: `V(D)` grows from 598 to 650 to 676. This gives a modest gain
   at present. It is exact, though, and it is what turns the construction into the complete cell
   of §2.
4. **Second family (×1.52).** This is the complementary cell, with `21 ∉ R` and kernel
   `[0,3,12]`. Its main right region is `W` (648 elements), with `|A(W)| = 1.920·10^30`.
5. **Mirror (×2).** Negation gives disjoint copies; see §3. The GPW "PARTIAL_STOP" candidate was
   exactly the mirror of the GPW main kernel.

The dominant effect is structural: canonical regions of `G_3` are distributive lattices, and
those relevant here are products of tiny factors. Exact antichain counting there is cheap. This
allows the whole cell `{safe : T ⊆ R, L ⊆ H_L(T)}` to be counted instead of a rectangle inside it.

## 5. Exactness of the numbers

| quantity | producer | independent verifier |
|---|---|---|
| `e(D)` (left counts per dominance set) | `ie_count` + inclusion–exclusion + Möbius (C++, u128) | `hist_count` direct histogram DP; Σ = `|A(H_L)|` |
| region counts < 160 | `ie_count` | archived GPW counter (exact) |
| region counts ≥ 160 | rank transfer mod 4 × 61-bit primes, CRT, bound `|M|^|S|` | product structure re-derived; numpy/BLAS transfer mod 4–5 × 45-bit primes, CRT with modulus > `|M|^|J1|` → exact equality (`verify_v5_crt.py`) |
| families / bound | exact Python integers | re-aggregated from histogram × reconstructed counts |

## 6. Outlook (toward 10^40)

The characterisation in §2 shows what v5 still misses. These are safe pairs whose left elements
are hit by `R` but not by the kernel `T` alone, and pairs with `{0,3,12} ⊄ R`. The cleanest
large untouched cells are `R = {−2}` and `R = {−3}`, each of which accepts all of `A(G_3)` on the
left. `G_3` is a 1474-element distributive lattice of width 86, so counting its antichains needs
a new method; the join-irreducible poset has 44 elements and is connected. Any new cell must be
separated from `G1`, `G2` and their mirrors by an explicit invariant of `(L, R)`, as in §3.
