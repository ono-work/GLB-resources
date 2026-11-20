# Post-GPW exact counting: the exhausted Ψ(S, C) framework (results as of 2026-11-12)

This directory is the frozen evidence for

```text
g(4) >= 29247125847589399267405782004907476922410   (log10 = 40.466083, about 2.9247 * 10^40)
```

the certified lower bound obtained after the GPW 2026 paper. It is the package that was
frozen on 2026-11-12 as `certified/psi_framework_exhausted/` in the private research tree
(121 files, listed with their digests in `SHA256SUMS`), plus five analysis documents and
this README added for the public release. Every file named in `SHA256SUMS` is byte-identical
to the freeze; `python scripts/verify_post_gpw.py` (repository root) checks this first.

## Layout note

In the freeze, the campaign directory `psi_exhaustion/` was a subdirectory of this package.
Here it is the sibling directory [`../psi_exhaustion/`](../psi_exhaustion/), which is the
layout the scripts were written for (`psi_exhaustion/*.py` locate this directory as
`../post_gpw_improvement`). References to `psi_exhaustion/...` inside the frozen documents
therefore resolve to `../psi_exhaustion/...`. The scripts find the `G_3` input through the
repository root (`../../data/gub/game_export/`, `../../src/`,
`../../experiments/lower_bound/...`), so this directory must stay at
`experiments/post_gpw_improvement/`.

## What is here

| file(s) | role |
|---|---|
| `CERTIFIED_PSI_FRAMEWORK_EXHAUSTED.md` | the certified statement: the 36-key table (v5 plus 34 Ψ families, each with its exact original count, mirror, verifier status and producer/verifier commits), the disjointness argument, the aggregation |
| `COUNTED_FAMILIES.json` | machine-readable ledger: baseline v5 and the 34 included Ψ(S, C) families with keys `(world, S, C, E)`, P-cells, certificate paths and digests, mirror flags |
| `certificate_v5.json`, `certificates/verify_v5_record.json`, `certificates/audit_v5_structure_record.json` | the v5 baseline (`G1`, `G2` and mirrors; 1.911e39) with its independent CRT verification and structural audit |
| `harvest/psi_S*_C*.json` (34 files) | producer certificates: exact count of each Ψ(S, C) family, with its `(S, C, T)` definition and per-profile rows |
| `harvest/certificates/verify_psi_*.json` (34 files) | independent verifier records (`AUDIT PASSED`, same exact total, recomputed on a different lattice split with a different modulus set and CRT) |
| `harvest/certificates/audit_psi_structure_record.json` | structural audit of all 34 families (hypotheses checked exactly, random members checked for canonicity and key) |
| `harvest/certificates/global_audit_record.json` | `GLOBAL AUDIT PASSED`: hashes, verifier statuses, keys, P-cells, mirror classes and the integer sum, recomputed from the ledger |
| `harvest/psi_exact.py`, `harvest/psi_regions.py`, `harvest/mitm.py`, `harvest/rank_transfer_mitm.cpp` | the producer: Ψ(S, C) family enumeration and exact counting by rank transfer |
| `barrier/cmp_mitm.cpp`, `barrier/cmp.py` | the compressed mixed-radix meet-in-the-middle producer used for the large regions |
| `barrier/vsweep.cpp`, `barrier/vsweep.py`, `harvest/verify_psi.py` | the independent low-memory verifier (full sweep on the dual split, moduli 2^32 and 31-bit primes, CRT uniqueness) |
| `barrier/memgate.py`, `barrier/plan_runs.py` | memory projection (calibrated state-count model) and run planning |
| `harvest/audit_psi_structure.py`, `harvest/build_ledger.py`, `harvest/global_audit.py` | structural audit, ledger builder, global aggregation audit |
| `verify_v2.py`, `verify_v5.py`, `verify_v5_crt.py`, `audit_v5_structure.py`, `verify_count_numpy.py`, `glbcore.py`, `dlat.py`, `side_count2.py`, `src/hit_antichain_counter.py` | the `G_3` model, the v5 verifiers and the lattice helpers shared by all of the above |
| `REPRODUCE.md` | the producer and verifier commands for all 34 families |
| `HARVEST_CERTIFIED_BASELINE.md`, `COMPRESSED_MITM_BASELINE.md`, `NEXT_EXACT_RUNS.md` | historical milestone notes (1.0388e40 on 2026-11-06; the reference compressed run; pre-run planning), superseded by the final result |
| `V5_METHOD_SUMMARY.md` | the mathematics of the safe-family construction (added for the release) |
| `COMPUTATIONAL_BARRIER.md`, `MEMORY_MODEL.md`, `NEXT_REGION_FEASIBILITY.md`, `POST_COMPRESSION_FRONTIER.md` | the memory story: dense `|M|^w` estimates versus the exact mixed-radix state count `prod |D_a|`, measured peaks, and the projection that made all 22 remaining keys feasible (added for the release) |

The campaign that resolved the last 22 keys is documented in [`../psi_exhaustion/`](../psi_exhaustion/).

## Verification

From the repository root:

```console
python scripts/verify_post_gpw.py
```

It checks the frozen manifest, recomputes the final integer from the certificates
(v5 + 2 x each of the 34 producer totals, each equal to its independent verifier total),
checks the key universe (36 = 2 + 12 + 22) and all audit records, and then re-runs the
frozen audit chain (`../psi_exhaustion/psi_framework_global_audit.py`) on a copy of the
repository under `generated/`, comparing the regenerated records with the committed ones.
It needs only the Python standard library and about one minute. It ends with

```text
PSI FRAMEWORK GLOBAL AUDIT PASSED
POST-GPW LOWER BOUND VERIFIED: 29247125847589399267405782004907476922410
```

`python scripts/verify_all.py` runs this after the GPW checks.

## Reproducing the counts

`REPRODUCE.md` lists the producer and verifier commands for every family. They are not part
of the quick verification: the producers took 45.6 hours and the independent verifiers
62.7 hours on Captain (Mac Pro 2019, Xeon W-3223, 48 GB), with a maximum resident set of
30.70 GB (verifier) and 21.17 GB (producer). They need `clang++ -O3 -std=c++17 -march=native`
builds of `barrier/cmp_mitm.cpp`, `barrier/vsweep.cpp` and `harvest/rank_transfer_mitm.cpp`
in `bin/` (the binaries rebuild byte-identically; their digests are recorded in
`COMPRESSED_MITM_BASELINE.md`), Python 3.11 and NumPy for `harvest/verify_psi.py`. The
scripts write their outputs in place: work on a copy.

## Not included

As in the GPW artifact, raw working material was left out: the compiled binaries (`bin/`),
the Python virtual environment, the `/usr/bin/time -l` logs of every run (their peak-RSS and
wall-time values are summarised in `../psi_exhaustion/PSI_EXHAUSTION_LEDGER.json`), the
split-search and measurement files under `barrier/` (`anatomy_*.json`, `plan_runs_*.json`,
`domain_tables.md`, `*.out`), the cell-screening tables, the exploratory P116 and phase-6
material, and the superseded v2–v4 certificates. `MEMORY_MODEL.md`,
`NEXT_REGION_FEASIBILITY.md`, `POST_COMPRESSION_FRONTIER.md` and the two baseline notes
cite some of those files; the numbers they quote are in the documents themselves.

## Provenance

The work was done on the private development branch `post-gpw-improvement` of the research
tree. The package was frozen at its commit `2c49c11ed6511c211cd29b0671fc7314a02d4ee1`
(2026-11-12 02:56 JST); the producer and verifier commit hashes in
`CERTIFIED_PSI_FRAMEWORK_EXHAUSTED.md` and `../psi_exhaustion/BASELINE_B0.md` refer to that
branch, which is not published. The GPW 2026 paper artifact itself is unchanged and is
tagged `gpw26-v1.0`.
