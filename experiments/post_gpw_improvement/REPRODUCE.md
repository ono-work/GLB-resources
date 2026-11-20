# Reproduce

Run everything from `experiments/post_gpw_improvement/` on the `post-gpw-improvement` branch.

Producers:

```
python3.11 verify_v5.py            # v5 baseline (and verify_v5_crt.py)
python3.11 harvest/psi_exact.py '[3,12]' '[21]'   # N2 -> harvest/psi_S3_12_C21.json
python3.11 harvest/psi_exact.py '[12,21]' '[3]'   # N4 -> harvest/psi_S12_21_C3.json
python3.11 harvest/psi_exact.py '[12]' '[3,21]'   # N5 -> harvest/psi_S12_C3_21.json
python3.11 harvest/psi_exact.py '[3,12,21]' '[0]'   # Z1 -> harvest/psi_S3_12_21_C0.json
python3.11 harvest/psi_exact.py '[3,12]' '[0,21]'   # Z2 -> harvest/psi_S3_12_C0_21.json
python3.11 harvest/psi_exact.py '[3,12]' '[0]'   # ZG2 -> harvest/psi_S3_12_C0.json
python3.11 harvest/psi_exact.py '[3,21]' '[12]'   # N3 -> harvest/psi_S3_21_C12.json
python3.11 harvest/psi_exact.py '[3]' '[12,21]'   # N6 -> harvest/psi_S3_C12_21.json
python3.11 harvest/psi_exact.py '[21]' '[3,12]'   # N7 -> harvest/psi_S21_C3_12.json
python3.11 harvest/psi_exact.py '[3,21]' '[0,12]'   # Z3 -> harvest/psi_S3_21_C0_12.json
python3.11 harvest/psi_exact.py '[]' '[3,12,21]'   # N8 -> harvest/psi_Snone_C3_12_21.json
python3.11 harvest/psi_exact.py '[3]' '[0,12,21]'   # Z4 -> harvest/psi_S3_C0_12_21.json
python3.11 harvest/psi_exact.py '[3]' '[12]'   # R_s_p_E2 -> harvest/psi_S3_C12.json
python3.11 harvest/psi_exact.py '[12]' '[3]'   # R_p_s -> harvest/psi_S12_C3.json
python3.11 harvest/psi_exact.py '[3]' '[0,12]'   # RZ_s_0p_E2 -> harvest/psi_S3_C0_12.json
python3.11 harvest/psi_exact.py '[]' '[3,12]'   # R_0_sp_E2 -> harvest/psi_Snone_C3_12.json
python3.11 harvest/psi_exact.py '[]' '[12,21]'   # R_0_p2_Es -> harvest/psi_Snone_C12_21.json
python3.11 harvest/psi_exact.py '[3,21]' '[]'   # R_s2_0 -> harvest/psi_S3_21_Cnone.json
python3.11 harvest/psi_exact.py '[21]' '[12]'   # R_2_p_Es -> harvest/psi_S21_C12.json
python3.11 harvest/psi_exact.py '[12,21]' '[]'   # R_p2_0 -> harvest/psi_S12_21_Cnone.json
python3.11 harvest/psi_exact.py '[12]' '[21]'   # R_p_2 -> harvest/psi_S12_C21.json
python3.11 harvest/psi_exact.py '[3]' '[21]'   # R_s_2 -> harvest/psi_S3_C21.json
python3.11 harvest/psi_exact.py '[3]' '[0,21]'   # RZ_s_02_Ep -> harvest/psi_S3_C0_21.json
python3.11 harvest/psi_exact.py '[]' '[3,21]'   # R_0_s2 -> harvest/psi_Snone_C3_21.json
python3.11 harvest/psi_exact.py '[3,21]' '[0]'   # RZ_s2_0_Ep -> harvest/psi_S3_21_C0.json
python3.11 harvest/psi_exact.py '[21]' '[3]'   # R_2_s -> harvest/psi_S21_C3.json
python3.11 harvest/psi_exact.py '[]' '[12]'   # R_0_p_Es2 -> harvest/psi_Snone_C12.json
python3.11 harvest/psi_exact.py '[]' '[21]'   # R_0_2 -> harvest/psi_Snone_C21.json
python3.11 harvest/psi_exact.py '[12]' '[]'   # R_p_0 -> harvest/psi_S12_Cnone.json
python3.11 harvest/psi_exact.py '[21]' '[]'   # R_2_0 -> harvest/psi_S21_Cnone.json
python3.11 harvest/psi_exact.py '[3]' '[0]'   # RZ_s_0_Ep2 -> harvest/psi_S3_C0.json
python3.11 harvest/psi_exact.py '[3]' '[]'   # R_s_0 -> harvest/psi_S3_Cnone.json
python3.11 harvest/psi_exact.py '[]' '[3]'   # R_0_s -> harvest/psi_Snone_C3.json
python3.11 harvest/psi_exact.py '[]' '[]'   # R_0_0 -> harvest/psi_Snone_Cnone.json
```

Independent verifiers (one at a time; peak RSS up to 36 GB):

```
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_12_C21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S12_21_C3.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S12_C3_21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_12_21_C0.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_12_C0_21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_12_C0.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_21_C12.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_C12_21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S21_C3_12.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_21_C0_12.json
.venv/bin/python harvest/verify_psi.py harvest/psi_Snone_C3_12_21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_C0_12_21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_C12.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S12_C3.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_C0_12.json
.venv/bin/python harvest/verify_psi.py harvest/psi_Snone_C3_12.json
.venv/bin/python harvest/verify_psi.py harvest/psi_Snone_C12_21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_21_Cnone.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S21_C12.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S12_21_Cnone.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S12_C21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_C21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_C0_21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_Snone_C3_21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_21_C0.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S21_C3.json
.venv/bin/python harvest/verify_psi.py harvest/psi_Snone_C12.json
.venv/bin/python harvest/verify_psi.py harvest/psi_Snone_C21.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S12_Cnone.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S21_Cnone.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_C0.json
.venv/bin/python harvest/verify_psi.py harvest/psi_S3_Cnone.json
.venv/bin/python harvest/verify_psi.py harvest/psi_Snone_C3.json
.venv/bin/python harvest/verify_psi.py harvest/psi_Snone_Cnone.json
python3.11 harvest/audit_psi_structure.py '<list of [S,C]>' 150
python3.11 harvest/build_ledger.py && python3.11 harvest/global_audit.py    # -> GLOBAL AUDIT PASSED
```

