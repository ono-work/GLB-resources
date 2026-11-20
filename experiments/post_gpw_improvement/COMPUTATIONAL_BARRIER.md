# The computational barrier for exact counting on Captain (48 GB)

Date: 2026-11-07. Details are in `MEMORY_MODEL.md` and `NEXT_REGION_FEASIBILITY.md`; scripts are in `barrier/`.

## Summary for a talk

> The exact algorithm is a transfer DP over a distributive lattice. The region is `J(Q)`. A split `Q = Qa + Qb` turns the count into maps from the graded lattice `J(Qa)` into `M = J(J(Qb))`. The DP sweeps `J(Qa)` rank by rank. The state on a rank is the tuple of values of its coordinates.
>
> **Dense view.** The largest certified cases have 4 coordinates per stored rank, each ranging over `|M| = 171` values: `171^4 = 8.6e8` states, 6.4 GiB. The next regions (N7, N8, Z3, Z4) have *five* coordinates on two consecutive ranks under every split we found. In the dense view that is `171^5 = 1.5e11` states per table, 1.06 TiB, which is why they looked impossible.
>
> **Compressed view.** Each coordinate only ranges over its own domain `D_a = {m ⊆ A_a}`. The "fifth" coordinate always has a domain of size 5–16, not 171. The exact state space of the widest rank is `171^4 · 9 = 7.7e9`: effective width `4.43`, not 5. Every state in it is reachable, so this is the true size.
>
> **Result.** With domain compression the next regions fit in about 18 GiB and run in about 40 minutes per region. The remaining barrier is a genuine fourth full coordinate: a `171^4` table on the ranks next to the streamed one.

## Three generations of the barrier (updated 2026-11-09)

| generation | model of the state space | widest case (N7/N8 776–856 regions) | verdict on Captain |
|---|---|---|---|
| 1. dense | `|M|^w` with `w = 5`: `171^5 = 1.46e11` entries per table | 2 stored tables of u64 = **2.1 TiB** | impossible |
| 2. mixed-radix compressed | `S(B) = ∏|D_a|`: `171^4·9 = 7.7e9` streamed, `w_eff = 4.43` | stored ≈ `2·171^4 + 7.2e8` ≈ 2.4e9 u64 = **18 GiB** (measured 18.17 GiB) | done: N7, Z3, N8 and Z4 certified |
| 3. after compression | all 22 remaining keys: `max S(B) ≤ 7.9e9`, `w_eff ≤ 4.432`, regions up to 856 | producer ≤ 19.6 GiB, verifier ≤ 32.6 GiB (projected) | **no RAM barrier**. The limit is mass per CPU-hour (≈ +2.5e39 for ≈ 180 h), then the framework itself (≈ 3e40). See `POST_COMPRESSION_FRONTIER.md`. |

2.1 TiB was the dense artefact, not the final limitation. The true RAM barrier (five full 171-value coordinates on a stored rank, `171^5`) does not occur in any enumerated region.

### Measured campaign (presentation table)

| family | vertices (largest region) | dense estimate | compressed peak states (max S(B)) | producer peak RAM | verifier peak RAM | runtime (producer / verifier) | exact contribution (original; ×2 with mirror) |
|---|---:|---:|---:|---:|---:|---:|---|
| N7 | 776 | 2·171^5 u64 = 2.1 TiB | 7.70e9 (w_eff 4.43) | 19.51e9 B (18.17 GiB) | 27.6e9 B | 9888 s / 18324 s | 1219198574355894293908221739832178001593 |
| Z3 | 776 | 2.1 TiB | 7.70e9 (4.43) | 18.17 GiB | 28.07e9 B | 13421 s / 23961 s | 1219198574355894293908207162508344440731 |
| N8 | 856 | 2.1 TiB | 7.70e9 (4.43) | 19.51e9 B | 30.70e9 B | 17020 s / 25196 s | 1989391910383901020003500436216175933379 |
| Z4 | 856 | 2.1 TiB | 7.70e9 (4.43) | 19.51e9 B | 30.70e9 B | 23353 s / 20551 s | 1989391910383901020001931053993907936163 |

In short: dense TiB → compressed 18 GiB. All RAM figures are maximum RSS from `/usr/bin/time -l` over every subprocess. The certified total is 2.678e40 (`certified/post_gpw_compressed_mitm/`).

## Why the current cases can be counted

1. **Every region is a distributive lattice `J(Q)`** (checked exactly). Its antichains correspond to ideals of `J(Q)`.
2. **The split.** For a down-set `Qa ⊆ Q`, ideals correspond to maps `f : J(Qa) → M` with `f(a) ⊆ A_a` and `f(b) ∩ A_a ⊆ f(a)` for covers `a < b`.
3. **Rank transfer.** A superset-sum (zeta) transform eliminates a whole rank at once. So the state is one rank of `J(Qa)`, not a vertex frontier.
4. **Meet in the middle.** The widest rank is streamed, never stored. Memory is the second-widest rank; time is the widest.
5. **The 26×26 product.** It has `K ≤ 4` and `|M| = 171`: `171^4` states.

## Why the next cases looked difficult

| target | dense widths (best split) | dense table | dense memory |
|---|---|---:|---:|
| N3/N6 (counted) | `[…,4,4,5,4,4,…]` | `171^4` stored, `171^5` streamed | 19.1 GiB (measured) |
| N7, Z3 | `[1,3,5,5,5,5,4,4,…]` | `171^5` stored | 2.1 TiB |
| N8, Z4 | `[…,5,5,5,5,…]` | `171^5` stored | 2.1 TiB |

Going from `w = 4` to `w = 5` multiplies the dense state count by `|M| = 171`.

## Which part was implementation overhead

| implementation | measured peak | minimal model | overhead |
|---|---:|---:|---|
| NumPy verifier (26×26) | 32.3 GiB | 1 table of float64 = 6.4 GiB | `tensordot` transposed copy, output buffer, `H`, BLAS buffers: about 5 live tables |
| New C++ verifier `vsweep` (same region) | **6.41 GiB** | 2 tables of u32 = 6.4 GiB | none |
| Old MITM producer (N3) | 19.15 GiB | 3 tables of u64 | the forward table is kept during the backward transition |
| New compressed MITM (N3) | 13.13 GiB | 2 tables of u64 | – |

The verifier's 35 GB was implementation overhead: a factor of 5 against what the recurrence needs.

## Which part was avoidable dense representation

This is the main finding. For each coordinate, `|D_a|` is either 171 (full) or 5, 8, 9 or 16 (the join-irreducibles contributed by the elements below `*`, `±1`, `*2`). Dense versus exact states for the N7 776 region:

| rank | domains | dense | exact |
|---|---|---:|---:|
| 2 | 171,16,16,9,9 | 1.46e11 | 3.6e6 |
| 3, 4 | 171,171,171,16,9 | 1.46e11 | 7.2e8 |
| 5 (streamed) | 171,171,171,171,9 | 1.46e11 | 7.7e9 |
| 6, 7 | 171 ×4 | 8.6e8 | 8.6e8 |

- **Reachability is exact.** Every tuple of `∏ D_a` is reachable: put `A` on the lower ranks and `∅` on the upper ones. So sparse hash/sorted representations cannot improve on the compressed dense layout. The zeros of the old dense tables are exactly the out-of-domain tuples.
- **Measured.** The N7 776 region was counted in 2560 s with 18.17 GiB RSS (formerly 2.1 TiB of planned memory). The result, 47521522721017059017745700795827, was reproduced independently by `vsweep` on the dual split (`|M| = 714`, 8 moduli of 32 bits, 4076 s, 26.14 GiB).

## Decompositions other than rank width (measured)

- **Vertex-frontier DP.** We beam-searched over linear extensions of `J(Qa)`, with weights `log|D_a|`. The best peak found is `10^11.2` entries for N3, N6, N7 and N8, against `10^9.2` for the compressed rank MITM. Unweighted elimination width is 6–7, against rank width 5. A frontier must keep a vertex until all its upper covers are placed. The rank transform keeps one rank. Rank separators win, so no frontier DP was implemented as a producer.
- **Weighted split choice.** Choosing the split by compressed size instead of dense size changes the optimum. Dual splits with `|M| = 714`–1796 and 4-wide ranks have compressed stream 4–6e9. They serve as independent verifier splits.
- **Slicing.** This is implemented in `vsweep`: a rank above a cap is processed one value of its largest coordinate at a time, verified on 12 forced-slice cases. Memory falls by the domain size `d` and time rises by about `d`. With `d = 1796` (N7, dual split) this is too slow. Slicing is useful only on a coordinate with a moderate domain (`d ≈ 171`), which is not needed for the current targets.
- **32-bit words.** `cmp_mitm w32` and `vsweep` halve the table memory, at about 1.6–2× more moduli.

## What remains after optimization

- **Effective separator.** The stored ranks next to the stream are four full 171-value coordinates: `2·171^4 = 1.7e9` states (12.7 GiB u64, 6.4 GiB u32), plus the kept forward table, `7.2e8`.
- **Streamed rank.** `171^4 · 9 = 7.7e9` states, time only.
- **What would be out of reach.** A region whose *stored* ranks need five full 171-value coordinates would need `171^5 = 1.46e11` states: 0.53 TiB u32 per table. Slicing could split this into 171 slices of 3.2 GiB, at about 171× the time of one `171^4` pass: about 171 × 8 min ≈ 1 day per prime. That is a CAPTAIN_FEASIBLE_WITH_LONG_RUN regime, not impossible.
- **P116.** It is a different kind of barrier: one connected 42-element JI poset with no small split (Dedekind-type). It stays a supercomputer problem.

## What would be needed to go further

- **Further regions of the N/Z type.** Compression + MITM already suffices; the cost is CPU-hours (about 40 min per new 750–860 region per producer).
- **Regions with five full coordinates on stored ranks.** These need slicing (CPU × 171) or about 1 TiB of RAM.
- **Dedekind-type cells (P116).** These need a different algorithm or a supercomputer.

<!-- BEGIN psi_exhaustion (generated by psi_exhaustion/make_final_reports.py) -->
## Ψ exhaustion (2026-11-12)

- All 22 remaining keys CERTIFIED; B_Ψ = 29247125847589399267405782004907476922410 (2.9247e+40), ×1.0922 over B0, 0.0383 decimal orders. `PSI FRAMEWORK GLOBAL AUDIT PASSED`.
- No key needed more than 30.70 GB (verifier) / 21.17 GB (producer); 18 of 22 keys would exceed 48 GB in the old dense form.
- The barrier is now the construction, not RAM: see `../psi_exhaustion/WHAT_LIMITS_US_NOW.md` and `../psi_exhaustion/FINAL_PSI_FRAMEWORK_REPORT.md`.
<!-- END psi_exhaustion -->
