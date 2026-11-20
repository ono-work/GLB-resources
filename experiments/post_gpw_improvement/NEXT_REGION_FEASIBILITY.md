# Feasibility of the next regions (N7, N8, Z3, Z4)

Date: 2026-11-07. All measurements were taken on Captain. Data sources:

- `barrier/anatomy_*.json` and `barrier/domain_tables.md`: plan search over every split, both orientations.
- `barrier/frontier_*.json`: weighted frontier search.
- `barrier/cmp_N7_776.out`, `barrier/vtest_*.out`: measured runs.
- `harvest/psi_S*_dry.json`: region inventories.

## Region inventory: what is genuinely new

Each family is `Σ_D e(D) Σ_{U⊆C} (−1)^{|U|} |A(X(D) ∖ ↓U)|`. The terms with `U ≠ ∅` remove the elements below the members of `U`. That gives exactly the regions of families already counted and verified (N3, N4, N5, N6, and the 26×26 products). So only the `U = ∅` terms are new.

| family | rows (profiles D) | regions ≥ 400 elements | new regions ≥ 600 (`U = ∅`) |
|---|---:|---:|---|
| N7 = Ψ([*2],[*,±1]) | 34 | 32 | 698, 750, 776 |
| Z3 = Ψ([*,*2],[0,±1]) | 34 | 32 | 698, 750, 776 (isomorphic to N7) |
| N8 = Ψ([],[*,±1,*2]) | 60 | 73 | 641, 667, 778, 830, 856 |
| Z4 = Ψ([*],[0,±1,*2]) | 43 | 73 | 641, 667, 778, 830, 856 (isomorphic to N8) |

## Feasibility table

All four targets use the dense-optimal split (`|M| = 171`). Dense memory means two `171^5` tables.

| target | current plan (dense MITM) | current projected RAM | best new plan | projected RAM | projected time | status |
|---|---|---:|---|---:|---:|---|
| N7 max region (776) | `K=[1,3,5,5,5,5,4,…]`, memory 2.92e11 entries | 2.1 TiB (u64) | compressed MITM, same split: stream 7.7e9, stored ≤ 2.43e9 entries | 18.1 GiB u64 / about 9 GiB u32 | **measured** 2560 s (5 primes × 450–540 s), RSS 18.17 GiB | **CAPTAIN_FEASIBLE_NOW** (counted: 47521522721017059017745700795827) |
| N7 family | no plan | 2.1 TiB | compressed MITM for the 3 new `U=∅` regions; cached N3/N4 counts for `U ≠ ∅`; vsweep (dual split) as verifier | ≤ 18 GiB producer; ≤ 26 GiB verifier | about 2.5 h producer + about 3–4 h verifier (from the 718 and 776 measurements) | **CAPTAIN_FEASIBLE_NOW** |
| Z3 family | no plan | 2.1 TiB | same as N7 (same region shapes) | same | same | **CAPTAIN_FEASIBLE_NOW** |
| N8 family (largest 856) | best dense plan `K=[…,5,5,5,5,…]`, memory 2.92e11 | 2.1 TiB | compressed MITM: stream 7.7e9, memory 1.71e9 (`anatomy_N8.json`) | about 18 GiB | 5 new regions × about 45 min ≈ 4 h producer, plus verifier | **CAPTAIN_FEASIBLE_WITH_LONG_RUN** (hours, not days) |
| Z4 family | same | 2.1 TiB | same as N8 | about 18 GiB | about 4 h + verifier | **CAPTAIN_FEASIBLE_WITH_LONG_RUN** |

The time projections scale the measured N3 718-region (≈ 330 s per 61-bit prime) and N7 776-region (≈ 480 s per prime) runs with the compressed stream size. Nothing in N8/Z4 exceeds the N7 constants by more than the ratio of region sizes, because all four have the same compressed maxima (stream 7.7e9, memory 1.71e9).

## Verification plan (independence)

- **Producer:** `bin/cmp_mitm`, compressed MITM, on the `|M| = 171` split, u64 with 61-bit primes.
- **Verifier:** `bin/vsweep`, written separately: a full bottom-up sweep without MITM, u32, moduli `2^32` and 31-bit primes. It runs on the *dual* split (`|M| = 714`, 1796 or 849), so its tables, `M` and coordinates differ from the producer's.
- **N7 776, measured:** the verifier needs a peak of 7.01e9 entries (26.1 GiB) unsliced. It ran in 4076 s (8 moduli) with 26.14 GiB RSS and **matched** the producer: 47521522721017059017745700795827. With slicing, 9.7 GiB is possible, but at 1796 slices it costs too much time; see `COMPUTATIONAL_BARRIER.md`.
