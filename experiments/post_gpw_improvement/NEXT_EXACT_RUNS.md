# Next exact runs: pre-run analysis (compressed model)

Generated from `barrier/plan_runs_<family>.json` (`barrier/plan_runs.py`, tables via `barrier/summarize_plans.py`).

## Model

For every rank `B` of the chosen split, the compressed state product is `S(B) = ∏_{a∈B} |D_a|`, with `D_a = {m ∈ M : m ⊆ A_a}`. Every tuple of `∏ D_a` is reachable, so this is the exact state space; there is no separate "reachable domain".

- **Producer (`cmp_mitm`, u64).** Peak ≈ 8 B × (stored ranks next to the stream + the kept forward table). This is calibrated on N7 776: 2.43e9 entries ↔ 18.17 GiB measured. The time per 61-bit prime is ≈ 6.5e-8 s × stream (N7 776: 7.7e9 → about 480 s).
- **Verifier (`vsweep`, u32).** Peak = 4 B × max_r (|T_r| + |T_{r+1}|), on a split different from the producer's. Calibrated: N7 776 7.01e9 → 26.14 GiB measured, about 460 s per modulus.
- `w_eff = log_171 max_B S(B)`. "dense max" is `|M|^{max K}` on the same split, i.e. the old dense model.
- Regions under 400 elements: the producer uses the archived dense paths (`ie_count`, or the `rank_transfer_gen` transfer up to `171^4`). The verifier uses the archived exact counter (< 160) or `vsweep`.

Memory policy: keep each process under ≈ 26 GiB and the combined load under ≈ 35 GiB. A verifier run above 20 GiB never overlaps a producer run.

## N7 = Ψ([*2],[*,±1])

| n | U | prod cached | ver cached | JI | prod split (dual,|M|) | K | max S(B) | w_eff | stored | dense max | ver split (dual,|M|) | ver peak GiB |
| 776 | [] | False | False | 20 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 2, 1, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,714 | 26.1 |
| 750 | [] | False | False | 19 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 2, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,713 | 25.66 |
| 726 | [12] | True | True | – | | | | | | | | |
| 718 | [3] | True | True | – | | | | | | | | |
| 700 | [12] | True | True | – | | | | | | | | |
| 698 | [] | False | False | 18 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,704 | 22.26 |
| 692 | [3] | True | True | – | | | | | | | | |
| 676 | [3, 12] | True | True | – | | | | | | | | |
| 650 | [3, 12] | True | True | – | | | | | | | | |
| 648 | [12] | True | True | – | | | | | | | | |
| 640 | [3] | True | True | – | | | | | | | | |
| 598 | [3, 12] | True | True | – | | | | | | | | |
| 587 | [] | False | False | 18 | True,439 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.59e+08 | 3.831 | 2.76e+08 | 3.71e+10 | False,171 | 5.87 |
| 561 | [] | False | False | 17 | True,438 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.49e+08 | 3.826 | 2.66e+08 | 3.68e+10 | False,171 | 5.87 |
| 544 | [12] | False | False | 17 | True,539 | [1, 1, 3, 3, 4, 3, 3, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.44e+10 | True,163 | 1.03 |
| 529 | [3] | True | True | – | | | | | | | | |
| 518 | [12] | False | False | 16 | True,539 | [1, 3, 3, 4, 3, 3, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.44e+10 | True,162 | 0.99 |
| 516 | [] | False | False | 17 | True,1796 | [1, 2, 3, 3, 3, 3, 1] | 3.41e+08 | 3.821 | 6.49e+07 | 5.79e+09 | True,471 | 0.93 |
| 506 | [] | False | False | 17 | True,1796 | [1, 2, 3, 3, 3, 3, 1] | 3.41e+08 | 3.821 | 4.27e+07 | 5.79e+09 | True,380 | 0.62 |
| 503 | [3] | True | True | – | | | | | | | | |
| 494 | [3, 12] | True | True | – | | | | | | | | |
| 468 | [3, 12] | True | True | – | | | | | | | | |
| 466 | [12] | True | True | – | | | | | | | | |
| 458 | [3] | True | True | – | | | | | | | | |
| 458 | [3] | True | True | – | | | | | | | | |
| 456 | [12] | True | True | – | | | | | | | | |
| 431 | [] | False | False | 16 | True,338 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 4.35e+07 | 3.421 | 2.45e+07 | 1.31e+10 | False,41 | 0.6 |
| 424 | [] | False | False | 16 | True,276 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.41e+07 | 3.374 | 2.07e+07 | 5.8e+09 | False,41 | 0.52 |
| 421 | [] | False | False | 16 | True,276 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.68e+07 | 3.326 | 1.92e+07 | 5.8e+09 | False,41 | 0.51 |
| 416 | [3, 12] | True | True | – | | | | | | | | |
| 416 | [3, 12] | True | True | – | | | | | | | | |
| 402 | [] | False | False | 16 | True,309 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.09e+07 | 3.278 | 1.31e+07 | 9.12e+09 | False,35 | 0.31 |

Note: the 776 region was counted in the baseline run (`COMPRESSED_MITM_BASELINE.md`). Producer and verifier caches were seeded from those runs, so it is not recomputed. The other `U ≠ ∅` regions are cached from N3/N4 (same element sets).

**N7 projection.** New producer regions ≥ 400: 750, 698, 587, 561, 544, 518, 516, 506, 431, 424, 421, 402. Producer peak about 18 GiB (750, 698). Time ≈ 2 × 40 min + about 30 min for the rest, i.e. about 1.5–2 h. Verifier peak 25.7 GiB (750) and 22.3 GiB (698); time ≈ 2 × 60 min + the rest, i.e. about 2.5 h.
Status: **CAPTAIN_FEASIBLE_NOW**, launched.

## Z3 = Ψ_Z([*,*2],[0,±1])

Z3 was analysed on its own element sets (its regions are not the N7 sets). The uncached regions are shown; cached rows are omitted.

| n | U | prod cached | ver cached | JI | prod split (dual,|M|) | K | max S(B) | w_eff | stored | dense max | ver split (dual,|M|) | ver peak GiB |
| 776 | [] | False | False | 20 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 2, 1, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,714 | 26.1 |
| 750 | [] | False | False | 19 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 2, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,713 | 25.66 |
| 698 | [] | False | False | 18 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,704 | 22.26 |
| 587 | [] | False | False | 18 | True,439 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.59e+08 | 3.831 | 2.76e+08 | 3.71e+10 | False,171 | 5.87 |
| 561 | [] | False | False | 17 | True,438 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.49e+08 | 3.826 | 2.66e+08 | 3.68e+10 | False,171 | 5.87 |
| 544 | [12] | False | False | 17 | True,539 | [1, 1, 3, 3, 4, 3, 3, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.44e+10 | True,163 | 1.03 |
| 518 | [12] | False | False | 16 | True,539 | [1, 3, 3, 4, 3, 3, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.44e+10 | True,162 | 0.99 |
| 516 | [] | False | False | 17 | True,1796 | [1, 2, 3, 3, 3, 3, 1] | 3.41e+08 | 3.821 | 6.49e+07 | 5.79e+09 | True,471 | 0.93 |
| 506 | [] | False | False | 17 | True,1796 | [1, 2, 3, 3, 3, 3, 1] | 3.41e+08 | 3.821 | 4.27e+07 | 5.79e+09 | True,380 | 0.62 |
| 431 | [] | False | False | 16 | True,338 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 4.35e+07 | 3.421 | 2.45e+07 | 1.31e+10 | False,41 | 0.6 |
| 424 | [] | False | False | 16 | True,276 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.41e+07 | 3.374 | 2.07e+07 | 5.8e+09 | False,41 | 0.52 |
| 421 | [] | False | False | 16 | True,276 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.68e+07 | 3.326 | 1.92e+07 | 5.8e+09 | False,41 | 0.51 |
| 402 | [] | False | False | 16 | True,309 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.09e+07 | 3.278 | 1.31e+07 | 9.12e+09 | False,35 | 0.31 |

The domain sizes, splits and `S(B)` profiles coincide with N7 region by region (as the isomorphism predicts), but every count is recomputed on Z3's own element sets. The 776 region is not cached for Z3.

**Z3 projection.** Producer: 776, 750 and 698 at about 18 GiB and about 40 min each, plus about 30 min for the rest, i.e. about 2.5 h. Verifier: 26.1 / 25.7 / 22.3 GiB, about 3.5 h.
Status: **CAPTAIN_FEASIBLE_NOW**. Launch after the N7 verifier finishes (the memory policy forbids overlap with a > 20 GiB verifier).

## N8 = Ψ([],[*,±1,*2])

This analysis was run before N7/Z3 were produced. The 'cached' flags are as of that time; the U=[21] regions are N7 (resp. Z3) U=[] regions. Rows cached in both producer and verifier caches are omitted.

| n | U | prod cached | ver cached | JI | prod split (dual,|M|) | K | max S(B) | w_eff | stored | dense max | ver split (dual,|M|) | ver peak GiB |
| 856 | [] | False | False | 24 | False,171 | [1, 1, 2, 3, 3, 4, 5, 5, 5, 5, 4, 4, 3, 2, 1, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,849 | 28.55 |
| 830 | [] | False | False | 23 | False,171 | [1, 1, 2, 3, 3, 4, 5, 5, 5, 5, 4, 4, 3, 2, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,848 | 28.07 |
| 778 | [] | False | False | 22 | False,171 | [1, 1, 2, 3, 3, 4, 5, 5, 5, 5, 4, 4, 3, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,839 | 24.43 |
| 750 | [21] | False | False | 19 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 2, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,713 | 25.66 |
| 698 | [21] | False | False | 18 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,704 | 22.26 |
| 667 | [] | False | False | 22 | True,565 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 4.27e+08 | 3.865 | 3.11e+08 | 1.02e+11 | False,171 | 5.87 |
| 641 | [] | False | False | 21 | True,564 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 4.15e+08 | 3.859 | 2.99e+08 | 1.01e+11 | False,171 | 5.87 |
| 596 | [] | False | False | 21 | True,606 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.12e+08 | 3.728 | 1.23e+08 | 1.35e+11 | False,171 | 5.36 |
| 590 | [12] | False | False | 19 | True,1721 | [1, 1, 3, 3, 4, 3, 3, 1, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.77e+12 | True,172 | 1.16 |
| 587 | [21] | False | False | 18 | True,439 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.59e+08 | 3.831 | 2.76e+08 | 3.71e+10 | False,171 | 5.87 |
| 586 | [] | False | False | 21 | False,171 | [1, 1, 2, 3, 3, 4, 5, 5, 4, 4, 3, 2, 1] | 7.2e+08 | 3.967 | 9e+07 | 1.46e+11 | True,505 | 0.76 |
| 564 | [12] | False | False | 18 | True,1721 | [1, 3, 3, 4, 3, 3, 1, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.77e+12 | True,171 | 1.11 |
| 561 | [21] | True | False | 17 | True,438 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.49e+08 | 3.826 | 2.66e+08 | 3.68e+10 | False,171 | 5.87 |
| 544 | [12, 21] | False | False | 17 | True,539 | [1, 1, 3, 3, 4, 3, 3, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.44e+10 | True,163 | 1.03 |
| 518 | [12, 21] | True | False | 16 | True,539 | [1, 3, 3, 4, 3, 3, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.44e+10 | True,162 | 0.99 |
| 516 | [21] | True | False | 17 | True,1796 | [1, 2, 3, 3, 3, 3, 1] | 3.41e+08 | 3.821 | 6.49e+07 | 5.79e+09 | True,471 | 0.93 |
| 511 | [] | False | False | 20 | True,464 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 5.74e+07 | 3.475 | 3e+07 | 4.64e+10 | False,42 | 2.05 |
| 506 | [21] | True | False | 17 | True,1796 | [1, 2, 3, 3, 3, 3, 1] | 3.41e+08 | 3.821 | 4.27e+07 | 5.79e+09 | True,380 | 0.62 |
| 504 | [] | False | False | 20 | True,393 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 4.55e+07 | 3.43 | 2.55e+07 | 2.39e+10 | False,42 | 1.79 |
| 501 | [] | False | False | 20 | True,393 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.61e+07 | 3.384 | 2.38e+07 | 2.39e+10 | False,42 | 1.73 |
| 482 | [] | False | False | 20 | True,434 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.88e+07 | 3.341 | 1.71e+07 | 3.55e+10 | False,36 | 1.09 |
| 434 | [12] | False | False | 17 | True,111 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.17e+07 | 3.286 | 1.64e+07 | 1.52e+08 | True,1721 | 0.24 |
| 434 | [12] | False | False | 17 | True,111 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.17e+07 | 3.286 | 1.64e+07 | 1.52e+08 | True,1721 | 0.24 |
| 431 | [21] | True | False | 16 | True,338 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 4.35e+07 | 3.421 | 2.45e+07 | 1.31e+10 | False,41 | 0.6 |
| 426 | [] | False | False | 19 | True,353 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 1.43e+07 | 3.204 | 6.75e+06 | 1.55e+10 | False,28 | 0.4 |
| 424 | [12] | False | False | 17 | False,171 | [1, 1, 2, 3, 4, 3, 3, 2, 1] | 8e+07 | 3.539 | 1e+07 | 8.55e+08 | True,88 | 0.08 |
| 424 | [21] | True | False | 16 | True,276 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.41e+07 | 3.374 | 2.07e+07 | 5.8e+09 | False,41 | 0.52 |
| 423 | [] | False | False | 19 | True,353 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 1.15e+07 | 3.161 | 6.75e+06 | 1.55e+10 | False,28 | 0.38 |
| 421 | [21] | True | False | 16 | True,276 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.68e+07 | 3.326 | 1.92e+07 | 5.8e+09 | False,41 | 0.51 |
| 416 | [] | False | False | 19 | True,305 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 9.2e+06 | 3.119 | 5.25e+06 | 8.65e+09 | False,28 | 0.34 |
| 402 | [21] | True | False | 16 | True,309 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.09e+07 | 3.278 | 1.31e+07 | 9.12e+09 | False,35 | 0.31 |

## Z4 = Ψ_Z([*],[0,±1,*2])

This analysis was run before N7/Z3 were produced. The 'cached' flags are as of that time; the U=[21] regions are N7 (resp. Z3) U=[] regions. Rows cached in both producer and verifier caches are omitted.

| n | U | prod cached | ver cached | JI | prod split (dual,|M|) | K | max S(B) | w_eff | stored | dense max | ver split (dual,|M|) | ver peak GiB |
| 856 | [] | False | False | 24 | False,171 | [1, 1, 2, 3, 3, 4, 5, 5, 5, 5, 4, 4, 3, 2, 1, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,849 | 28.55 |
| 830 | [] | False | False | 23 | False,171 | [1, 1, 2, 3, 3, 4, 5, 5, 5, 5, 4, 4, 3, 2, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,848 | 28.07 |
| 778 | [] | False | False | 22 | False,171 | [1, 1, 2, 3, 3, 4, 5, 5, 5, 5, 4, 4, 3, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,839 | 24.43 |
| 776 | [21] | False | False | 20 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 2, 1, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,714 | 26.1 |
| 750 | [21] | False | False | 19 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 2, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,713 | 25.66 |
| 698 | [21] | False | False | 18 | False,171 | [1, 3, 5, 5, 5, 5, 4, 4, 3, 1] | 7.7e+09 | 4.427 | 1.71e+09 | 1.46e+11 | True,704 | 22.26 |
| 667 | [] | False | False | 22 | True,565 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 4.27e+08 | 3.865 | 3.11e+08 | 1.02e+11 | False,171 | 5.87 |
| 641 | [] | False | False | 21 | True,564 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 4.15e+08 | 3.859 | 2.99e+08 | 1.01e+11 | False,171 | 5.87 |
| 596 | [] | False | False | 21 | True,606 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.12e+08 | 3.728 | 1.23e+08 | 1.35e+11 | False,171 | 5.36 |
| 590 | [12] | False | False | 19 | True,1721 | [1, 1, 3, 3, 4, 3, 3, 1, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.77e+12 | True,172 | 1.16 |
| 587 | [21] | False | False | 18 | True,439 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.59e+08 | 3.831 | 2.76e+08 | 3.71e+10 | False,171 | 5.87 |
| 586 | [] | False | False | 21 | False,171 | [1, 1, 2, 3, 3, 4, 5, 5, 4, 4, 3, 2, 1] | 7.2e+08 | 3.967 | 9e+07 | 1.46e+11 | True,505 | 0.76 |
| 564 | [12] | False | False | 18 | True,1721 | [1, 3, 3, 4, 3, 3, 1, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.77e+12 | True,171 | 1.11 |
| 561 | [21] | False | False | 17 | True,438 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.49e+08 | 3.826 | 2.66e+08 | 3.68e+10 | False,171 | 5.87 |
| 544 | [12, 21] | False | False | 17 | True,539 | [1, 1, 3, 3, 4, 3, 3, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.44e+10 | True,163 | 1.03 |
| 518 | [12, 21] | False | False | 16 | True,539 | [1, 3, 3, 4, 3, 3, 1] | 2.7e+09 | 4.223 | 6.54e+07 | 8.44e+10 | True,162 | 0.99 |
| 516 | [21] | False | False | 17 | True,1796 | [1, 2, 3, 3, 3, 3, 1] | 3.41e+08 | 3.821 | 6.49e+07 | 5.79e+09 | True,471 | 0.93 |
| 511 | [] | False | False | 20 | True,464 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 5.74e+07 | 3.475 | 3e+07 | 4.64e+10 | False,42 | 2.05 |
| 506 | [21] | False | False | 17 | True,1796 | [1, 2, 3, 3, 3, 3, 1] | 3.41e+08 | 3.821 | 4.27e+07 | 5.79e+09 | True,380 | 0.62 |
| 504 | [] | False | False | 20 | True,393 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 4.55e+07 | 3.43 | 2.55e+07 | 2.39e+10 | False,42 | 1.79 |
| 501 | [] | False | False | 20 | True,393 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.61e+07 | 3.384 | 2.38e+07 | 2.39e+10 | False,42 | 1.73 |
| 482 | [] | False | False | 20 | True,434 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.88e+07 | 3.341 | 1.71e+07 | 3.55e+10 | False,36 | 1.09 |
| 434 | [12] | False | False | 17 | True,111 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.17e+07 | 3.286 | 1.64e+07 | 1.52e+08 | True,1721 | 0.24 |
| 434 | [12] | False | False | 17 | True,111 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.17e+07 | 3.286 | 1.64e+07 | 1.52e+08 | True,1721 | 0.24 |
| 431 | [21] | False | False | 16 | True,338 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 4.35e+07 | 3.421 | 2.45e+07 | 1.31e+10 | False,41 | 0.6 |
| 426 | [] | False | False | 19 | True,353 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 1.43e+07 | 3.204 | 6.75e+06 | 1.55e+10 | False,28 | 0.4 |
| 424 | [12] | False | False | 17 | False,171 | [1, 1, 2, 3, 4, 3, 3, 2, 1] | 8e+07 | 3.539 | 1e+07 | 8.55e+08 | True,88 | 0.08 |
| 424 | [21] | False | False | 16 | True,276 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 3.41e+07 | 3.374 | 2.07e+07 | 5.8e+09 | False,41 | 0.52 |
| 423 | [] | False | False | 19 | True,353 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 1.15e+07 | 3.161 | 6.75e+06 | 1.55e+10 | False,28 | 0.38 |
| 421 | [21] | False | False | 16 | True,276 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.68e+07 | 3.326 | 1.92e+07 | 5.8e+09 | False,41 | 0.51 |
| 416 | [] | False | False | 19 | True,305 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 9.2e+06 | 3.119 | 5.25e+06 | 8.65e+09 | False,28 | 0.34 |
| 402 | [21] | False | False | 16 | True,309 | [1, 3, 3, 4, 4, 4, 3, 2, 1, 1] | 2.09e+07 | 3.278 | 1.31e+07 | 9.12e+09 | False,35 | 0.31 |

**N8 and Z4 projections.** The new largest regions are 856, 830 and 778 (U=[]). Each has `max S(B) = 7.7e9`, `w_eff = 4.43`, the same rank profile as N7 with a longer tail, and `JI` = 22–24. Bound `171^24` (178 bits), so 3–4 primes of 61 bits.
- Producer: about 18.8 GiB projected, about 40–60 min per large region. With the 600-range regions, about 3–4 h per family.
- Verifier: 28.55 GiB (856), 28.07 GiB (830), 24.4 GiB (778), all within the 38 GiB budget. About 4–5 h per family.

Status: **CAPTAIN_FEASIBLE_NOW** for both. Before this campaign they were rated CAPTAIN_FEASIBLE_WITH_LONG_RUN; it is now hours, not days.

## Scheduling (memory gate)

From 2026-11-08 03:17 every binary invocation reserves its projected peak in `barrier/memgate.py` (budget 38 GiB). Producer and verifier queues can then run concurrently without exceeding the budget. Large producer (18.8 GiB) and large verifier (22–29 GiB) moduli alternate. Wall-clock times under concurrency are therefore longer than the single-job projections above.

## Z3 vs N7 (explained difference)

Z3 = 1219198574355894293908207162508344440731 and N7 = 1219198574355894293908221739832178001593. They differ only in 9 profile weights `e(D)`; all 34 coverage counts agree. The L-pools differ by exactly the element `*` (N7: 319, Z3: 318), because the Z-world requires `* ∉ L`. Recomputing N7's histogram with `*` removed from the pool reproduces Z3's `e(D)` on every row. So Z3 is exactly the L ∌ * part of N7's image, which is not a discrepancy.
