# Ψ exhaustion campaign (2026-11-09 to 2026-11-12)

The campaign that resolved the last 22 keys of the Ψ(S, C) framework, taking the certified
bound from the frozen milestone `B0 = 26779208541153893647347341345937714190772` (2.678e40)
to `B_Ψ = 29247125847589399267405782004907476922410` (2.9247e40). The package it audits is
[`../post_gpw_improvement/`](../post_gpw_improvement/), which the scripts locate as
`../post_gpw_improvement` (see the layout note in its README).

| file | role |
|---|---|
| `PSI_FRAMEWORK_EXHAUSTIVENESS.md` | formal definition of the framework, the 36-key parameter domain, the partition argument, the intentionally excluded cases |
| `audit_psi_exhaustiveness.py`, `audit_psi_exhaustiveness_record.json` | machine check of the above (`EXHAUSTIVENESS AUDIT PASSED`; counts 36 = 2 + 12 + 22; random members re-keyed to their own key) |
| `make_remaining_keys.py`, `REMAINING_KEYS.json`, `REMAINING_KEYS.md` | the 22 remaining keys, regenerated from the partition definitions, with projected state counts, memory and time |
| `BASELINE_B0.md` | the frozen starting point and its 12 pre-campaign families |
| `build_exh.py`, `PSI_EXHAUSTION_LEDGER.json`, `PSI_EXHAUSTION_STATUS.md` | per-key ledger (exact value, mirror, certificates, measured peak RSS and wall time, effective width, status) and the saturation table |
| `psi_framework_global_audit.py`, `psi_framework_global_audit_record.json` | the fresh global audit A1–A7 (`PSI FRAMEWORK GLOBAL AUDIT PASSED`) |
| `FINAL_PSI_FRAMEWORK_REPORT.md`, `WHAT_LIMITS_US_NOW.md` | the final report and the analysis of what limits the bound now (construction, not RAM) |

All of these except the two reports and this README are byte-identical to the 2026-11-12
freeze (`../post_gpw_improvement/SHA256SUMS`, entries `psi_exhaustion/...`). The two reports
were generated on 2026-11-12 by `make_final_reports.py` in the research tree from the ledger,
the audit record and the measurement files; the generator is not included because it reads
measurement files that were left out (see the package README). Their numbers are those of the
frozen ledger and records.

`build_exh.py` and `psi_framework_global_audit.py` rewrite `PSI_EXHAUSTION_LEDGER.json`,
`PSI_EXHAUSTION_STATUS.md` and the audit records when they run (timestamps and run times).
This is why `scripts/verify_post_gpw.py` re-runs them on a copy under `generated/` and
compares the regenerated records with the committed ones instead of running them here.
