# Memory model of the exact counters

Date: 2026-11-07. Machine: Captain (Mac Pro 2019, 16 cores, 48 GB). "GiB" means 2^30 bytes. RSS values are `maximum resident set size` from `/usr/bin/time -l`.

## 0. What is being counted

A region `S` is a distributive lattice `J(Q)`. The count is `|A(S)|`, the number of antichains of `S`, which equals the number of ideals of `J(Q)`.

**The split.** `dlat.plan` splits `Q` into a down-set `Qa` and the rest `Qb`. With this split, ideals of `J(Q)` correspond to maps `f : JA = J(Qa) → M = J(J(Qb))` satisfying:

- `f(a) ⊆ A_a`, where `A_a` is the *allowed* set;
- `f(b) ∩ A_a ⊆ f(a)` for every cover `a < b` in `JA`.

**The transfer.** `JA` is graded by rank. The rank transfer keeps one table per rank `r`, indexed by the values on that rank's `K_r` coordinates. Covers join only consecutive ranks, and the subset/superset-sum transform eliminates a whole rank at once.

**Size measures.**

- *Dense size*: a table on rank `r` has `|M|^{K_r}` entries.
- *Exact state space*: coordinate `a` can only take values in `D_a = {m ∈ M : m ⊆ A_a}`, so the exact state space of rank `r` is `∏_{a∈r} |D_a|`. Every tuple in `∏ D_a` is reachable: set all lower ranks to `A` and all higher ranks to `∅`. Each constraint then holds trivially. So the compressed state space contains no unreachable states, and further sparsification within a rank is impossible.

## 1. Objects and measured peaks of the existing implementations

The typical size is `|M| = 171`. One `171^4` table holds `8.55e8` entries: 6.37 GiB as u64, 3.19 GiB as u32. One `171^5` table holds `1.46e11` entries: 1.064 TiB as u64, 0.53 TiB as u32.

| implementation | objects alive at the peak | entries | type | theory | measured peak RSS |
|---|---|---:|---|---:|---:|
| `bin/rank_transfer_gen` (dlat; N4/N5 producers) | `G_r` and `H_{r+1}` during a transition (both `171^4`); in-place transform | 2 × 8.55e8 | u64 | 12.7 GiB | 12.8 GiB (13.72 GB, N4/N5/Z1/Z2 logs) |
| `bin/rank_transfer_mitm` (old MITM; N3/N6 producers) | forward `Ĝ_{r*−1}` (`171^4`), plus backward `B_r` and `H_{r−1}` during the last backward transition (`171^4` each) | 3 × 8.55e8 | u64 | 19.1 GiB | 19.15 GiB (20.56 GB, N3 and N6) |
| NumPy verifier `verify_count_numpy.residue` (26×26 products) | `G`, the transposed contiguous copy made by `tensordot`, the `tensordot` output, the result of `moveaxis` (a view), `H` during a transition, BLAS buffers | ≈ 5.1 × 8.55e8 | float64 | ≥ 3 tables = 19.1 GiB (minimum of the `tensordot` path) | **32.3 GiB** (34.72 GB, one prime, v5 676 region); 32.9–33.3 GiB in the `verify_psi` runs |
| `verify_psi` on Z2 (MITM regions only) | as `rank_transfer_mitm` with two tables | 2 × 8.55e8 | u64 | 12.7 GiB | 12.8 GiB |

**Why the MITM uses `|M|^w`.** The MITM streams the widest rank `r*` and never stores it. It stores the forward table `Ĝ` on rank `r*−1` and the backward table `B̌` on rank `r*+1`, each with `K = 4` coordinates over all of `M`. So the stored state is `171^4 · 8 B = 6.37 GiB` per table.

**The width-5 case.** If the second-widest rank also has 5 coordinates (as in N7, N8, Z3, Z4 under the dense plan: `K = [1,3,5,5,5,5,4,…]`), a dense table holds `171^5 = 1.46e11` entries. That is 1.06 TiB per u64 table, and a transition holds two of them: **2.13 TiB**. The best dense MITM plans found for N7/N8 need memory `2.92e11` entries (2.1 TiB as u64). These are the "no plan" results of the harvest.

## 2. New implementations

| implementation | design | objects alive at the peak | measured |
|---|---|---|---|
| `bin/cmp_mitm` (producer, `barrier/cmp_mitm.cpp`) | the same MITM recurrence, but every coordinate ranges over its own domain `D_a` (mixed radix); `need`/`m` indices are projected into `D_a`; u64 with 61-bit primes, or u32 with 31-bit primes (`w32`) | `Ĝ_{r*−1}` + `B̌_{r*+1}` | N3 718-region: **13.13 GiB** (previously 19.15), 320 s per prime; N7 776-region: **18.17 GiB**, 450–540 s per prime (5 primes, 2560 s) |
| `bin/vsweep` (independent verifier, `barrier/vsweep.cpp`) | separately written full bottom-up sweep (no MITM); u32 tables; moduli `2^32` (native wrap-around) and 31-bit primes; run on a *different* split from the producer's | `T_r` + `T_{r+1}` | v5 676 region (26×26): **6.41 GiB** (NumPy: 32.3 GiB); N3 718-region on the dual split (`|M| = 334`): **12.48 GiB**; N7 776-region on the dual split (`|M| = 714`, `K=[1,3,3,4,4,4,3,2,1,1]`, peak 7.01e9 entries): **26.14 GiB**, about 460 s per modulus (8 moduli, 4076 s) |

Validation:

- `cmp_mitm` (u64 and w32) and `vsweep` agree with the certified counts of 17 N3 sub-regions of 156–354 elements.
- Both agree with the N3 718-region count `23274146661487257322073705873832`.
- `vsweep` reproduces the v5 676-region count.
- **N7 776-region:** `cmp_mitm` (split `|M| = 171`, 61-bit primes) and `vsweep` (dual split `|M| = 714`, `2^32` + 31-bit primes) both give `47521522721017059017745700795827`. The two runs share no split, modulus or code.

**Correction to the peak model.** The `cmp_mitm` peak is `Ĝ_{r*−1}` *plus* the forward table kept during the backward transitions: for N7, `7.2e8 + 2·8.55e8 = 2.43e9` u64 entries = 18.1 GiB, which matches the measured 18.17 GiB. `anatomy.py`'s `mem` column (1.71e9) omits the kept `Ĝ`.

## 3. Coordinate domains: dense vs compressed

The full tables are in `barrier/domain_tables.md` (generator `barrier/domain_table.py`).

The structure is the same in every target. Each rank has some *full* coordinates (`|D_a| = 171`) and some *small* ones (`|D_a| ∈ {5, 8, 9, 16}`). The small coordinates come from the join-irreducibles added by the elements below `*`, `±1` and `*2`.

N7's 776 region on the dense-optimal split (`|M| = 171`):

| rank | K | domains | dense | compressed |
|---:|---:|---|---:|---:|
| 2 | 5 | 171,16,16,9,9 | 1.46e11 | 3.55e6 |
| 3–4 | 5 | 171,171,171,16,9 | 1.46e11 | 7.2e8 |
| 5 | 5 | 171,171,171,171,9 | 1.46e11 | **7.7e9** (stream) |
| 6–7 | 4 | 171 ×4 | 8.55e8 | 8.55e8 |

So the effective width is `log_171(7.7e9) = 4.43`, not 5, and the stored tables are at most `171^4`.

Projected costs for the four targets (compressed MITM):

| target | compressed stream | compressed memory | memory as u64 | memory as u32 |
|---|---:|---:|---:|---:|
| N3 / N6 | 6.8e9 / 7.7e9 | 1.71e9 | 12.7 GiB | 6.4 GiB |
| N7, Z3 | 7.7e9 | 1.71e9 (+7.2e8 kept) | 18.1 GiB (measured 18.17) | about 9 GiB |
| N8, Z4 | 7.7e9 | 1.71e9 (+kept Ĝ) | about 18 GiB | about 9 GiB |

## 4. Other options measured or estimated

- **Sparsity.** Inside `∏ D_a` there are no unreachable states (proof in §0), so after compression a sparse representation gains nothing. Before compression, the reachable fraction of a dense rank table is `∏|D_a| / |M|^K`: between 1/19 and 1/41,000 per rank (`domain_tables.md`). Compression is exactly the removal of those zeros.
- **Frontier / elimination orders** (`barrier/frontier.py`, beam 1500). A vertex-by-vertex frontier DP is worse than the rank transfer for every plan. For N3, N6, N7 and N8 the best weighted frontier peak is `10^11.2` entries (fused elimination), against `10^9.2` for the compressed rank MITM. In unweighted terms, the best generic elimination width found is 6–7 for `|M| = 171` splits, against a rank width of 5. The reason is that the zeta transform removes a whole rank at once, while a vertex can be forgotten only after all its upper covers are placed. Rank separators are therefore the right decomposition here.
- **Slicing** (fix one stream coordinate). This is not needed once the domains are compressed: memory is already `≤ 2·171^4`. For the dense width-5 case it would give `171` slices × `171^4`, i.e. 1.46e11 states processed in 6.4 GiB slices, at about 171× the time of one slice.
- **32-bit words.** `cmp_mitm w32` halves the table memory to 6.4 GiB at the cost of about 2× the moduli (8 instead of 5 for a 2^250 bound). `vsweep` is always 32-bit.
