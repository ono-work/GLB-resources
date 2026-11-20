# Version history

## 2026-11-12 post-GPW snapshot (tag `v2026.11.12`)

Certified bound:

```text
g(4) >= 29247125847589399267405782004907476922410   (about 2.9247125848 * 10^40)
```

Results as of 2026-11-12; published later. Main changes:

- generalized safe-family counting (right kernel `T`, pairs `{L | T ∪ B}` counted exactly);
- the Ψ(S, C) decomposition of the construction into 36 pairwise disjoint cells (keys), each doubled once by the negation mirror;
- mixed-radix exact counting (state count `prod |D_a|` instead of `|M|^w`), which brought every cell within 48 GB;
- all 36 keys of the current framework resolved, none empty or infeasible;
- independent verification of every family (different split, different moduli, CRT) and a global audit (`PSI FRAMEWORK GLOBAL AUDIT PASSED`);
- new files: `experiments/post_gpw_improvement/` (frozen package, 121 files with `SHA256SUMS`), `experiments/psi_exhaustion/`, `scripts/verify_post_gpw.py`, `tests/test_post_gpw.py`, `POST_GPW_RESULTS.md`, `RELEASE_2026-11-12.md`, this file;
- `scripts/verify_all.py` now verifies both results.

Repository fix included in this version: five input files (`data/gub/game_export/games.csv`,
`leq_rows.hex`, `metadata.json`, `experiments/g2_calibration/safe_profile_g2_exact.json`,
`safe_profile_g2_exact_ja.md`) had been hashed with CRLF line endings but were normalised
to LF by `.gitattributes`, so `scripts/verify_all.py` reported a checksum mismatch on every
clone of the paper artifact. They are now stored byte-for-byte (`-text`), and all hashes,
including the kernel certificate's input hashes, match from a fresh clone.

## GPW 2026 paper artifact (tag `gpw26-v1.0`, 2026-10-24)

Certified bound:

```text
g(4) >= 1425933741673169505174021654095740659   (about 1.4259337417 * 10^36)
```

Freedom-98 admissible kernel, canonical thickening of right Layers 0–6, residual-profile
closure, sufficient-statistic Layers 4–5, three disjoint residual cells. The paper artifact
is described in the second half of `README.md`, `PAPER_RESULTS.md`, `REPRODUCIBILITY.md`
and `VERIFICATION_REPORT.md`.
