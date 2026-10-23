# Computational Artifact for a Lower Bound on Partizan Games Born by Day 4

This repository is the public computational artifact accompanying the paper
*A New Lower Bound on the Number of Partizan Games Born by Day 4* (GPW 2026).

The certified result packaged here is

```text
g(4) >= 1425933741673169505174021654095740659
     > 1.4259 * 10^36.
```

The artifact contains the finite-poset input, selected exact experiment
records, certificates, independent checking code, and provenance needed to
inspect the computational claims used in the paper. It is a curated packaging
of the original research records and adds no new scientific claims.

Start here, then see:

- [`PAPER_RESULTS.md`](PAPER_RESULTS.md): every numerical claim mapped to its evidence.
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md): quick verification and expensive-recomputation scope.
- [`VERIFICATION_REPORT.md`](VERIFICATION_REPORT.md): checks run when this package was assembled.
- [`provenance/`](provenance/): source commits, selection policy, and excluded data.

## Quick verification

Python 3.11 or later is sufficient; Gurobi is not needed.

```console
python scripts/verify_all.py
```

The command checks all packaged SHA-256 digests, the links between the
certified counting stages, the six disjoint-cell truth tables, the final
integer sum, and small regression tests. A successful run ends with

```text
FINAL LOWER BOUND VERIFIED: 1425933741673169505174021654095740659
ALL PUBLIC ARTIFACT CHECKS PASSED
```

The quick check validates the frozen evidence and its arithmetic. It does not
rerun the expensive Gurobi search or enumerate the largest antichain layers.
See `REPRODUCIBILITY.md` for that distinction.

## Evidence classes

The repository deliberately separates four kinds of evidence.

1. **Mathematical arguments.** Safe antichain pairs, admissible kernels, and
   disjoint-cell addition are justified in the paper.
2. **Checkable constructions.** The displayed freedom-98 kernel and all
   adopted cell rectangles can be checked directly against the supplied
   finite poset.
3. **Deterministic exact counts.** Canonical Layers 0--6, residual-profile
   closure, sufficient-statistic Layers 4--5, and the exact old/common union
   are stored with independent forward/reverse checks.
4. **Solver provenance.** Gurobi 10.0.0 reported objective and bound 98 with
   zero gap for the stated 0--1 model. This optimality claim is solver-based;
   the validity of the final lower bound only needs the supplied freedom-98
   kernel to be feasible.

## Repository layout

```text
data/gub/game_export/       G_3 finite-poset input used by the calculations
experiments/g2_calibration/ G_2 -> G_3 exact calibration (1448 of 1474)
experiments/lower_bound/    selected evidence on the path to the final bound
reports/                    original Japanese experiment reports
src/                        original counting and verification sources
scripts/                    public read-only verification entry points
tests/                      small solver-free regression tests
environment/                software and input-version information
provenance/                 source inventory and exclusion policy
generated/                  untracked outputs from optional local reruns
```

## Scope of the final disjoint-cell search

The final certificate has `status = AUDIT PASSED` and
`scope_status = PARTIAL_STOP`. The latter means that canonical thickening was
not completed for three of 56 explored candidates. None of those candidates
is used in the reported best partition. The three adopted cells, their exact
contributions, their pairwise disjointness, and their disjointness from the
previous family are all covered by the packaged verification. No contribution
from an incomplete candidate is included in the stated lower bound.

## Excluded material

The artifact intentionally excludes approximately 2.3 GiB of historical
Layer-6 slice checkpoints, approximately 693 MiB of regenerable MPS models,
Layer-7 workload estimates, superseded experiments, compiled binaries, and
failed or incomplete searches that do not support a paper claim.

## License

This artifact is released under the MIT License; see [`LICENSE`](LICENSE).
