# The frontier after domain compression

Date: 2026-11-09. Machine: Captain (48 GB, memgate budget 38 GiB).

The data comes from `barrier/plan_runs.py` (`barrier/plan_runs_<key>.json`, `barrier/plan_runs_frontier.out`) and from `barrier/frontier_mass.py` (`barrier/frontier_mass.json`).

## Where we are

- **Certified bound:** `g(4) ≥ 26779208541153893647347341345937714190772`, which is 2.678e40 (log10 40.427798).
  - It is frozen in `certified/post_gpw_compressed_mitm/`. The old `certified/post_gpw_1e40/` is untouched (its SHA256SUMS were re-checked).
  - It is 18780× the GPW bound 1.426e36, and 2.578× the post_gpw_1e40 milestone.

| list | families |
|---|---|
| CERTIFIED | v5 (G1, G2 + mirrors), N2, N3, N4, N5, N6, N7, N8, Z1, Z2, Z3, Z4, Z-G2 |
| PRODUCER_EXACT_NOT_YET_VERIFIED | none |
| NOT_YET_COMPUTED | the 22 keys below |

The compressed campaign certified N7, Z3, N8 and Z4. Each was produced by `cmp_mitm` and reproduced exactly by `vsweep` on a different split. Each passed the structural audit, the disjointness audit (key separation) and the mirror bookkeeping, and was added to the ledger and the global audit.

## The 22 remaining keys

All keys are `(world, S, C, E)`, with `F0 = {3=*, 12=±1, 21=*2}`.

- **Planning.** For every region with `n ≥ 400` that is not yet cached, the planner chose the compressed producer split (minimal memory) and an independent verifier split.
  - `S(B) = ∏|D_a|` is the exact state count on the widest rank. All tuples are reachable.
  - The projected producer and verifier peaks use the calibrated memgate models: N7 776 projected 18.77 GiB, measured 18.17 GiB.
- **Times** are estimates, calibrated on the measured N7 and N8 family runs.
  - Producer: about `2.5e-7 s × Σ_rank S(B)`.
  - Verifier: about `5e-7 s × sweep work`.
- **Masses are HEURISTIC.** They are the SIS leading-term estimate `Σ_D e(D)·|A(X(D))|`.
  - On certified families the ratio estimate/exact was 1.02 (N7), 1.19 (Z3), 2.39 (Z-G2) and 0.38 (N3). So the error is up to a factor of about 3 either way.
  - They are used only for ranking, never in a bound.

| key | S | C | largest region n | regions ≥400 to compute | |M| (widest) | factorization of max S(B) | max S(B) | w_eff | producer peak (proj.) | verifier peak (proj.) | producer time (est.) | verifier time (est.) | mass est. (orig., HEURISTIC) |
|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| R_0_sp_E2 | [] | [3, 12] | 802 | 29 | 172 | 172^4·9 | 7.88e+09 | 4.432 | 13.0 GiB | 26.1 GiB | 5.5 h | 8.0 h | 10^38.54 |
| R_s_p_E2 | [3] | [12] | 744 | 9 | 171 | 171^4·8 | 6.84e+09 | 4.404 | 12.7 GiB | 12.4 GiB | 2.0 h | 1.8 h | 10^38.53 |
| RZ_s_0p_E2 | [3] | [0, 12] | 802 | 24 | 172 | 172^4·9 | 7.88e+09 | 4.432 | 13.0 GiB | 26.1 GiB | 4.9 h | 6.0 h | 10^38.48 |
| R_p_s | [12] | [3] | 752 | 5 | 172 | 172^4 | 8.75e+08 | 4.005 | 13.0 GiB | 13.4 GiB | 0.6 h | 2.0 h | 10^38.14 |
| R_0_p2_Es | [] | [12, 21] | 808 | 32 | 714 | 171^3·352 | 1.76e+09 | 4.140 | 19.6 GiB | 32.6 GiB | 3.8 h | 12.2 h | 10^37.76 |
| R_2_p_Es | [21] | [12] | 768 | 14 | 352 | 171^3·352 | 1.76e+09 | 4.140 | 18.8 GiB | 28.7 GiB | 1.9 h | 5.8 h | 10^37.19 |
| RZ_s_02_Ep | [3] | [0, 21] | 814 | 21 | 171 | 171^4·8 | 6.84e+09 | 4.404 | 18.8 GiB | 28.7 GiB | 5.1 h | 12.1 h | 10^37.18 |
| R_0_s2 | [] | [3, 21] | 814 | 21 | 171 | 171^4·8 | 6.84e+09 | 4.404 | 18.8 GiB | 28.7 GiB | 5.1 h | 12.1 h | 10^37.05 |
| R_s2_0 | [3, 21] | [] | 718 | 5 | 171 | 171^4·8 | 6.84e+09 | 4.404 | 12.7 GiB | 12.4 GiB | 1.6 h | 1.6 h | 10^36.91 |
| R_s_2 | [3] | [21] | 744 | 10 | 171 | 171^4·8 | 6.84e+09 | 4.404 | 12.7 GiB | 12.4 GiB | 3.3 h | 3.3 h | 10^36.80 |
| RZ_s2_0_Ep | [3, 21] | [0] | 768 | 10 | 171 | 171^4·8 | 6.84e+09 | 4.404 | 18.8 GiB | 28.7 GiB | 2.5 h | 6.1 h | 10^36.73 |
| R_p_2 | [12] | [21] | 752 | 10 | 172 | 172^4 | 8.75e+08 | 4.005 | 13.0 GiB | 13.4 GiB | 1.1 h | 3.5 h | 10^36.70 |
| R_p2_0 | [12, 21] | [] | 726 | 5 | 171 | 171^4 | 8.55e+08 | 4.000 | 12.7 GiB | 13.2 GiB | 0.5 h | 1.7 h | 10^36.58 |
| R_2_s | [21] | [3] | 768 | 10 | 171 | 171^4·8 | 6.84e+09 | 4.404 | 18.8 GiB | 28.7 GiB | 2.5 h | 6.1 h | 10^36.52 |
| R_0_2 | [] | [21] | 802 | 14 | 172 | 172^4·9 | 7.88e+09 | 4.432 | 13.0 GiB | 26.1 GiB | 4.2 h | 6.3 h | 10^36.31 |
| R_0_p_Es2 | [] | [12] | 814 | 17 | 334 | 171^3·334 | 1.67e+09 | 4.130 | 18.8 GiB | 28.7 GiB | 1.8 h | 5.8 h | 10^36.29 |
| RZ_s_0_Ep2 | [3] | [0] | 808 | 16 | 171 | 171^4·9 | 7.70e+09 | 4.427 | 19.6 GiB | 32.6 GiB | 3.2 h | 6.7 h | 10^35.91 |
| R_2_0 | [21] | [] | 776 | 7 | 171 | 171^4·9 | 7.70e+09 | 4.427 | 12.7 GiB | 26.1 GiB | 2.1 h | 3.1 h | 10^35.89 |
| R_p_0 | [12] | [] | 772 | 5 | 171 | 171^4 | 8.55e+08 | 4.000 | 12.7 GiB | 13.2 GiB | 0.5 h | 1.7 h | 10^35.53 |
| R_s_0 | [3] | [] | 758 | 7 | 171 | 171^4·9 | 7.70e+09 | 4.427 | 12.7 GiB | 13.0 GiB | 1.8 h | 1.7 h | 10^35.28 |
| R_0_s | [] | [3] | 808 | 16 | 171 | 171^4·9 | 7.70e+09 | 4.427 | 19.6 GiB | 32.6 GiB | 3.2 h | 6.7 h | 10^35.24 |
| R_0_0 | [] | [] | 856 | 6 | 171 | 171^4·9 | 7.70e+09 | 4.427 | 12.7 GiB | 28.6 GiB | 2.1 h | 3.9 h | 10^33.31 |

Totals (sum over keys, shared regions counted once per key): producer ≈ 59 h, verifier ≈ 118 h, mass ≈ 1.26e+39 (originals), ×2 with mirrors ≈ 2.52e+39.

## Findings

1. **No remaining key hits a memory barrier on Captain.**
   - Every planned region has `w_eff ≤ 4.432`, with `max S(B) ≤ 7.9e9`.
   - The projected producer peak is ≤ 19.6 GiB and the verifier peak ≤ 32.6 GiB.
   - The widest ranks still have the form `171^4·d` (or `172^4·9`, `171^3·352`) with a small fifth domain. No region needs five full coordinates on a *stored* rank.
   - The largest region is 856 elements (in R_0_0, the same size as N8/Z4).
   - So the dense `171^5` = 2.1 TiB barrier does not come back anywhere in this key set.
2. **The barrier is now mass per CPU-hour, not RAM.**
   - The 22 keys together are estimated at about 1.3e39 (originals), or about 2.5e39 with mirrors. That is a ≈ +9% gain, giving a final ≈ 2.9e40 (range ≈ 2.8–3.3e40 at the calibration error).
   - It would cost about 60 h of producer time plus about 120 h of verifier time. With the gate, mostly one verifier plus one producer run at once, so this is roughly 5–7 days of wall clock.
   - Three keys carry about 75% of the estimated mass: R_0_sp_E2, R_s_p_E2 and RZ_s_0p_E2, each ≈ 3e38. Together they need about 32 h, for ≈ +1.9e39 with mirrors.
   - The keys with `±1 ∉ C` are each ≤ 10^38.2. The last 10 keys together are < 10^37.
3. **The first genuinely unavoidable barrier is therefore not computational inside this framework.**
   - Once the 22 keys are done, the Ψ(S,C) framework (originals in `O0 = {0 ∈ R∖L}` and `OZ = {0 ∉ L∪R, 0 covered below, * ∈ R∖L}`, plus mirrors) is exhausted at ≈ 3e40.
   - We have not established here whether the key enumeration in `plan_runs.py` exhausts `O0 ∪ OZ`. That needs to be checked before claiming this ceiling.
   - Going towards 1e41 needs *new classes of games* with their own canonicity and disjointness arguments, for example games whose right options contain neither 0 nor *, or are not covered in the same way. That is a theory step, not a RAM step.
   - The computational barrier proper is still the one stated in `COMPUTATIONAL_BARRIER.md`: a region needing five full 171-value coordinates on a stored rank (`171^5`, 0.53 TiB u32 per table, or slicing at ×171 time). No currently enumerated region needs it.
   - P116 (a Dedekind-type cell) was out of scope this round.

## Recommendation

1. If more mass is wanted from the existing framework, run R_0_sp_E2, R_s_p_E2 and RZ_s_0p_E2 first. This is about 1.5 days for ≈ +7%.
2. The rest gives ≈ +2% for about 4 more days.
3. The larger step is mathematical: define and audit new families outside `O0 ∪ OZ`.
