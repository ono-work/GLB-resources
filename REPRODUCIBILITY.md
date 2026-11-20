# Reproducibility

## Level 1: frozen-evidence verification

Requirements:

- Python 3.11 or later;
- no third-party Python packages;
- no optimizer.

From the repository root, run

```console
python scripts/verify_all.py
```

This is the recommended first check. It performs the following read-only
operations:

1. verifies `CHECKSUMS.sha256`;
2. checks the three exported `G_3` input hashes against the kernel certificate;
3. recomputes the `G_2 -> G_3` profile sums;
4. recomputes the canonical Layer-6 weighted histogram and bound;
5. verifies residual-profile and Layer-4/5 union identities;
6. verifies every truth table in the six stored three-cell partitions;
7. recomputes the final arbitrary-precision integer sum;
8. runs the small standard-library regression tests (paper and post-GPW);
9. checks the frozen post-GPW package against its 2026-11-12 manifest
   (`experiments/post_gpw_improvement/SHA256SUMS`, 121 files);
10. recomputes the post-GPW bound from the family certificates (v5 plus
    2 x each of the 34 Ψ(S, C) producer totals, each equal to its independent
    verifier total) and checks the 36-key universe and all audit records;
11. re-runs the frozen post-GPW audit chain on a copy of the repository under
    `generated/verify_post_gpw/` and compares the regenerated records with the
    committed ones (about one minute).

No packaged evidence file is modified. Steps 9–11 can be run alone with
`python scripts/verify_post_gpw.py` (`--quick` skips step 11).

## Level 2: independent structural checks

The original verifier sources are retained in `src/`. They use the exported
finite poset in `data/gub/game_export/` and the cached option relation in
`experiments/lower_bound/local_components/g3_universe_cache.json` to check
kernel feasibility, antichain conditions, coverage conditions, and selected
counts independently of Gurobi.

These sources preserve the research implementation and are included for code
inspection and expensive reruns. Several original drivers were designed for
the larger private research tree and may generate files in place. Work on a
copy and read the corresponding report before invoking them. The public
`scripts/verify_all.py` entry point is intentionally read-only.

## Level 3: expensive counting reruns

The exact canonical Layer-6 and sufficient-statistic Layer-4/5 calculations
used parallel C++ counters and require substantially more time and memory than
the quick verification. The artifact retains the aggregated forward and
reverse results, their hashes, the relevant Python orchestration and verifier
sources, and the mathematical input. It does not include compiled executables,
worker checkpoints, or Layer-7 workload files.

Rebuilding these stages therefore requires compiling the corresponding C++
sources from the original research repository or reimplementing the documented
enumeration. It is not part of the solver-free quick check.

## Level 3b: rerunning the post-GPW counts

`experiments/post_gpw_improvement/REPRODUCE.md` lists the producer and
independent-verifier commands for all 34 Ψ(S, C) families. They need
`clang++ -O3 -std=c++17 -march=native` builds of `barrier/cmp_mitm.cpp`,
`barrier/vsweep.cpp` and `harvest/rank_transfer_mitm.cpp`, Python 3.11 and
NumPy. On the original machine (Mac Pro 2019, 48 GB) the producers took
45.6 hours and the verifiers 62.7 hours in total, with a peak resident set of
30.70 GB. The scripts write their outputs in place; work on a copy. See
`experiments/post_gpw_improvement/README.md`.

## Level 4: rerunning the kernel optimization

The recorded optimization used Gurobi Optimizer 10.0.0. The artifact includes
the selected `.sol` witness, solver log, certificate, and model-generation
source. Regenerable MPS files are excluded because five threshold models alone
occupy approximately 693 MiB.

Rerunning the optimization requires a separately installed and licensed copy
of Gurobi. Verifying the final lower bound does not require rerunning it: the
lower bound uses the supplied freedom-98 kernel as a feasible construction.

## Regenerating the package checksum manifest

After an intentional artifact change, run

```console
python scripts/build_checksums.py
python scripts/verify_all.py
```

The checksum builder excludes `.git`, Python caches, test caches, and
`generated/`.
