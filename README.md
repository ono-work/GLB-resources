# Computational Artifact for Lower Bounds on Partizan Games Born by Day 4

This repository is the public computational artifact for lower bounds on
`g(4) = |G_4|`, the number of short partizan game values of birthday at
most 4. It holds two certified results: the result of the GPW 2026 paper, and
a stronger result obtained after the paper was finalized.

## Version 2026-11-12 — post-GPW computational snapshot

The GPW 2026 paper *A New Lower Bound on the Number of Partizan Games Born by
Day 4* reported

```text
g(4) >= 1425933741673169505174021654095740659
     > 1.4259 * 10^36.
```

Subsequent computations, completed after the paper was finalized, improve the
certified lower bound to

```text
g(4) >= 29247125847589399267405782004907476922410
     > 2.9247 * 10^40.
```

This larger value does not appear in the GPW paper. Results are as of
2026-11-12, the day the last cell of the current construction was certified.
The original paper artifact is preserved unchanged in the tag `gpw26-v1.0`;
the present snapshot (tag `v2026.11.12`) adds the post-GPW computation, its
certificates and its verification. See [`CHANGELOG.md`](CHANGELOG.md) and
[`RELEASE_2026-11-12.md`](RELEASE_2026-11-12.md).

### Quick verification of both results

Python 3.11 or later, standard library only, no optimizer, about one minute:

```console
python scripts/verify_all.py
```

A successful run contains

```text
FINAL LOWER BOUND VERIFIED: 1425933741673169505174021654095740659
...
PSI FRAMEWORK GLOBAL AUDIT PASSED
POST-GPW LOWER BOUND VERIFIED: 29247125847589399267405782004907476922410
ALL PUBLIC ARTIFACT CHECKS PASSED
```

The first line is the paper result; the last three are the post-GPW result.
The post-GPW part (`scripts/verify_post_gpw.py`) checks that the frozen
package is byte-identical to the 2026-11-12 freeze, recomputes the final
integer from the family certificates (each producer total equal to its
independent verifier total), checks that all 36 keys of the construction are
accounted for exactly once, and re-runs the frozen global audit on a copy of
the repository under `generated/`.

### Where to read

- [`POST_GPW_RESULTS.md`](POST_GPW_RESULTS.md): every post-GPW claim mapped to its evidence.
- [`experiments/post_gpw_improvement/README.md`](experiments/post_gpw_improvement/README.md): contents of the frozen package and how to reproduce the counts.
- [`experiments/post_gpw_improvement/CERTIFIED_PSI_FRAMEWORK_EXHAUSTED.md`](experiments/post_gpw_improvement/CERTIFIED_PSI_FRAMEWORK_EXHAUSTED.md): the certified statement, the 36-key table and the disjointness proof.
- [`experiments/psi_exhaustion/FINAL_PSI_FRAMEWORK_REPORT.md`](experiments/psi_exhaustion/FINAL_PSI_FRAMEWORK_REPORT.md) and [`WHAT_LIMITS_US_NOW.md`](experiments/psi_exhaustion/WHAT_LIMITS_US_NOW.md): the final report and the saturation analysis.
- [`experiments/post_gpw_improvement/COMPUTATIONAL_BARRIER.md`](experiments/post_gpw_improvement/COMPUTATIONAL_BARRIER.md): the memory story (dense estimates versus mixed-radix compression).
- [`experiments/post_gpw_improvement/V5_METHOD_SUMMARY.md`](experiments/post_gpw_improvement/V5_METHOD_SUMMARY.md): the mathematics of the safe-family construction.

### What changed scientifically

1. **GPW 2026 paper.** A freedom-98 admissible kernel, canonical thickening of
   right Layers 0–6, residual-profile closure, sufficient-statistic Layers 4–5
   and three disjoint residual cells gave about `1.426 * 10^36`.
2. **Generalized safe-family counting.** A pair `(L, R)` of antichains of `G_3`
   is *safe* when every right option of every `l` is bounded below by some
   `r`, and dually. Safe pairs are canonical forms, so distinct safe pairs are
   distinct games. Fixing a right kernel `T` and counting the pairs
   `{L | T ∪ B}` exactly through the lattice structure of the option regions
   gave `1.911 * 10^39` (the v5 families `G1`, `G2` and their mirrors).
3. **The Ψ(S, C) decomposition.** With `F0 = {*, ±1, *2}`, a right side `R`
   determines a key `(world, S, C, E)`: `S = R ∩ F0`, `C` the members of `F0`
   covered strictly below by `R`, `E` the rest; the world is `0` when `0 ∈ R`
   and `Z` when `0 ∉ R` is covered below. The key is a function of the pair,
   so the `3^3 + 3^2 = 36` keys are pairwise disjoint cells, each doubled
   once by the negation mirror. v5 owns two keys; 34 are Ψ families.
4. **Mixed-radix state-space compression.** The exact counts are transfer
   computations over distributive lattices. Treating every boundary coordinate
   as ranging over the full state domain (`|M|^w`, with `|M| = 171` and
   `w = 5`) suggested terabyte-scale tables. Each coordinate has its own
   admissible domain `D_a`, and the true state count is `prod |D_a|`: at most
   `7.9 * 10^9` states (effective width `4.43`) for every remaining key.
5. **Everything became computable on one machine.** All 36 keys were counted
   exactly on Captain, a 2019 Mac Pro with 48 GB of RAM. The largest job used
   30.70 GB (independent verifier) and 21.17 GB (producer).
6. **Independent verification.** Every family was counted by a producer
   (compressed meet-in-the-middle, 61-bit primes) and recomputed by an
   independent verifier on a different lattice split with a different modulus
   set and CRT reconstruction, with exact equality; every family passed a
   structural audit; a global audit re-derives the keys, mirror classes and
   the integer sum from the certificates.
7. **Final certified result of the framework.** All 36 keys resolved:
   `g(4) >= 29247125847589399267405782004907476922410`, about `2.9247 * 10^40`,
   a factor of about 20511 over the paper.
8. **Saturation.** The 22 keys certified after the previous milestone
   (`2.678 * 10^40`) added only a factor of 1.0922, about 9.2 %; the five
   largest of them carry 93 % of that addition.

The stopping point is therefore the **saturation of the current
Ψ-construction**, not a 48-GB memory limit: after compression every cell of
the construction was computable, all were computed, and more RAM would not
change the result. This is a statement about this construction only. It is
not an upper bound and not a proof that no stronger construction exists.

### Beyond this snapshot

These are directions, not results. No contribution from them is included.

- **P116.** The cell `P = R ∩ G_2 = [1, 6, 16]` lies outside the Ψ framework
  (it is not anchored at `0` or `*`). Its exact count is a weighted
  Dedekind-type problem on a connected poset with 42 join-irreducibles, a
  reasonable target for a much larger machine. Only heuristic estimates of
  its size exist.
- **New P-worlds.** Safe families outside the exhausted framework: cells
  anchored at other day-2 games, and Z-world pairs with `* ∉ R`, which need a
  new mirror-separation argument.
- **Coupled constructions.** The present framework keeps the admissible left
  options independent of `B`, which is what makes profile-based exact counting
  work. Constructions allowing stronger coupling between `L` and `R` may yield
  substantially larger families.

## GPW 2026 paper artifact (unchanged)

The remainder of this file describes the paper artifact, which is preserved
unchanged (tag `gpw26-v1.0`). The result certified by it is

```text
g(4) >= 1425933741673169505174021654095740659
     > 1.4259 * 10^36.
```

The artifact contains the finite-poset input, selected exact experiment
records, certificates, independent checking code, and provenance needed to
inspect the computational claims used in the paper. It is a curated packaging
of the original research records and adds no new scientific claims.

For the paper artifact, see:

- [`PAPER_RESULTS.md`](PAPER_RESULTS.md): every numerical claim mapped to its evidence.
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md): quick verification and expensive-recomputation scope.
- [`VERIFICATION_REPORT.md`](VERIFICATION_REPORT.md): checks run when this package was assembled.
- [`provenance/`](provenance/): source commits, selection policy, and excluded data.

## Quick verification of the paper result

Python 3.11 or later is sufficient; Gurobi is not needed.

```console
python scripts/verify_all.py
```

The command checks all packaged SHA-256 digests, the links between the
certified counting stages, the six disjoint-cell truth tables, the final
integer sum, and small regression tests, and prints

```text
FINAL LOWER BOUND VERIFIED: 1425933741673169505174021654095740659
```

for the paper result before going on to the post-GPW checks described above
(`python scripts/verify_quick.py` runs the paper checks alone). The quick
check validates the frozen evidence and its arithmetic. It does not rerun the
expensive Gurobi search or enumerate the largest antichain layers. See
`REPRODUCIBILITY.md` for that distinction.

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
data/gub/game_export/            G_3 finite-poset input used by all calculations
experiments/g2_calibration/      G_2 -> G_3 exact calibration (1448 of 1474)        [GPW]
experiments/lower_bound/         selected evidence on the path to the paper bound   [GPW]
experiments/post_gpw_improvement/ frozen post-GPW package: certificates, audits, code [2026-11-12]
experiments/psi_exhaustion/      the campaign that resolved the last 22 keys         [2026-11-12]
reports/                         original Japanese experiment reports               [GPW]
src/                             original counting and verification sources         [GPW]
scripts/                         public read-only verification entry points
tests/                           small solver-free regression tests
environment/                     software and input-version information
provenance/                      source inventory and exclusion policy
generated/                       untracked outputs of local reruns (verify_post_gpw.py works here)
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
