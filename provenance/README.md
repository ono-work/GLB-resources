# Provenance and Selection Policy

This package was assembled from the private research trees

```text
GLB source commit: 5af167dd68a193b83de35a5ddaf4ecc3c534b46a
GUB source commit: 85d17f1e840632978b3baed5b69622d51f6419bf
```

Only the chain supporting the GPW 2026 lower bound was selected:

1. `G_2 -> G_3` calibration;
2. freedom-98 admissible kernel;
3. canonical Layers 0--6;
4. residual-profile closure;
5. coverage and sufficient-statistic Layers 4--5 with exact union;
6. the adopted disjoint-cell partition.

The copied experiment JSON and solver witnesses are preserved byte-for-byte.
Public documentation and the scripts in `scripts/` were added during artifact
assembly. `CHECKSUMS.sha256` freezes the distributable package.

## Deliberately excluded

- 251,033 historical Layer-6 slice checkpoints (approximately 2.3 GiB);
- regenerable MPS models (approximately 693 MiB in the final kernel directory);
- Layer-7 workload estimates and benchmarks not used in the lower bound;
- compiled executables;
- superseded kernels and intermediate lower bounds;
- incomplete future experiments such as recursive greedy cell splitting.

No excluded experimental or estimated value is added to the reported lower
bound.

## Post-GPW addition (version 2026-11-12)

`experiments/post_gpw_improvement/` and `experiments/psi_exhaustion/` were copied
byte-for-byte from the package frozen on 2026-11-12 as
`certified/psi_framework_exhausted/` in the private research tree (branch
`post-gpw-improvement`, HEAD `2c49c11ed6511c211cd29b0671fc7314a02d4ee1`); the frozen
manifest `experiments/post_gpw_improvement/SHA256SUMS` lists its 121 files. Added for the
release: the two directory READMEs, five analysis documents
(`V5_METHOD_SUMMARY.md`, `COMPUTATIONAL_BARRIER.md`, `MEMORY_MODEL.md`,
`NEXT_REGION_FEASIBILITY.md`, `POST_COMPRESSION_FRONTIER.md`) and the two generated reports
(`FINAL_PSI_FRAMEWORK_REPORT.md`, `WHAT_LIMITS_US_NOW.md`, with a one-line public-copy
note each and one wording change about the companion upper-bound repository).

Deliberately excluded from the post-GPW material:

- compiled binaries (`bin/`) and the Python virtual environment;
- the `/usr/bin/time -l` logs of every producer and verifier run (summarised in the ledger);
- split-search and measurement files (`barrier/anatomy_*.json`, `plan_runs_*.json`,
  `domain_tables.md`, `*.out`) and the report generator that reads them;
- cell-screening tables, the exploratory P116 and phase-6 material, superseded v2–v4
  certificates and working logs.

No excluded value is added to the reported lower bound.
