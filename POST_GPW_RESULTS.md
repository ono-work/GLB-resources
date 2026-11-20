# Post-GPW Results and Evidence Map (results as of 2026-11-12)

This file maps the post-GPW claims to the evidence frozen in this artifact, in the same
way that `PAPER_RESULTS.md` does for the GPW 2026 paper. All displayed counts are exact
integers. Heuristic estimates (used only to order the work) are never added to a bound.

| Claim | Exact result | Primary evidence | Quick verification |
|---|---:|---|---|
| v5 baseline: families `G1`, `G2` and mirrors | `1910895019390363935559973877007439048864` | `experiments/post_gpw_improvement/certificate_v5.json`, `certificates/verify_v5_record.json` (CRT), `certificates/audit_v5_structure_record.json` | value, verifier and structural status |
| 12 Ψ families certified before the campaign (N2–N8, Z1–Z4, Z-G2); frozen milestone `B0` | `26779208541153893647347341345937714190772` | `experiments/psi_exhaustion/BASELINE_B0.md`; producer/verifier certificates under `experiments/post_gpw_improvement/harvest/` | v5 + 2 x the 12 exact values reproduces `B0` |
| The framework has exactly 36 keys: 2 owned by v5, 12 in the ledger, 22 remaining | 36 = 2 + 12 + 22 | `experiments/psi_exhaustion/PSI_FRAMEWORK_EXHAUSTIVENESS.md`, `audit_psi_exhaustiveness_record.json` | status `EXHAUSTIVENESS AUDIT PASSED` and counts; re-run on a copy |
| The 22 remaining keys are all certified (none empty, none infeasible) | 22 x `CERTIFIED` | `experiments/psi_exhaustion/PSI_EXHAUSTION_LEDGER.json`, `REMAINING_KEYS.json` | statuses and per-key values against the ledger |
| Every family: producer total = independent verifier total | 34 equalities | `harvest/psi_S*_C*.json` (producers), `harvest/certificates/verify_psi_*.json` (verifiers, `AUDIT PASSED`) | recomputed for all 34 families |
| Final certified lower bound `B_Ψ` | `29247125847589399267405782004907476922410` | `experiments/post_gpw_improvement/CERTIFIED_PSI_FRAMEWORK_EXHAUSTED.md`, `COUNTED_FAMILIES.json`, `harvest/certificates/global_audit_record.json` | v5 + 2 x each of the 34 exact values; `GLOBAL AUDIT PASSED` |
| Fresh global audit A1–A7 | `PSI FRAMEWORK GLOBAL AUDIT PASSED` | `experiments/psi_exhaustion/psi_framework_global_audit_record.json` | record checked, then regenerated on a copy and compared |
| Peak memory of the completed computations | 30.70 GB (verifier), 21.17 GB (producer); machine 48 GB | `PSI_EXHAUSTION_LEDGER.json` (`*_peak_rss`), `WHAT_LIMITS_US_NOW.md` | not part of the quick check |

## Numbers derived from the certified values

```text
B_Psi / GPW  = 20510.9        (+4.312 decimal orders)
B_Psi / B0   = 1.0921580      (+9.22 %, +0.0383 decimal orders)
log10 B_Psi  = 40.466083
```

Share of the mass added by the 22 campaign keys (`2.468 * 10^39`, mirrors included):

| largest k keys | share |
|---:|---:|
| 1 | 27.2 % |
| 3 | 73.4 % |
| 5 | 93.2 % |
| 10 | 97.2 % |
| 22 | 100 % |

The four largest campaign keys (`R_0_sp_E2`, `RZ_s_0p_E2`, `R_p_s`, `R_s_p_E2`) each
contribute between `2.3 * 10^38` and `3.4 * 10^38` originals; the smallest (`R_0_0`)
contributes `7640582146961891627716322233936205`. The full sorted table is in
`experiments/psi_exhaustion/FINAL_PSI_FRAMEWORK_REPORT.md`; the per-key table with
measured memory, wall time and effective width is `PSI_EXHAUSTION_STATUS.md`.

## Interpretation

The Ψ(S, C) framework is exhausted: every one of its 36 cells has been counted exactly and
independently verified, and no cell was limited by the 48 GB of the machine. The remaining
cells added about 9 % to the previous milestone. A substantially larger lower bound needs a
new combinatorial construction (see `README.md`, "Beyond this snapshot"), not more memory.
Nothing here is an upper bound, and nothing here shows that no stronger construction exists.
