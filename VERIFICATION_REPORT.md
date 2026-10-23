# Verification Report

Artifact assembly date: 2026-10-24 (Asia/Tokyo)

This report records checks performed on the curated public package. It is not
a claim that the expensive searches were rerun during packaging.

## Intended checks

- file integrity against `CHECKSUMS.sha256`;
- `G_3` input hashes against the certified source hashes;
- `G_2 -> G_3` calibration total 1448;
- freedom-98 rectangle size `2^98`;
- canonical Layer-6 forward/reverse agreement;
- residual-profile arithmetic;
- Layer-4/5 exact-union arithmetic;
- all six disjoint-cell truth tables;
- final lower-bound sum;
- standard-library regression tests.

## Recorded run

Command:

```console
python scripts/verify_all.py
```

Result:

```text
FILE INTEGRITY VERIFIED (208 files)
G2 CALIBRATION VERIFIED (1448 safe pairs; g(3)=1474)
Z98 KERNEL EVIDENCE VERIFIED (2^98)
CANONICAL LAYER 0--6 VERIFIED (1416779128733115417932228068149714027)
RESIDUAL PROFILE CLOSURE VERIFIED (1416780686143449296616167856189137167)
LAYER 4/5 EXACT UNION VERIFIED (1416805572004163810711501940302641257)
DISJOINT PARTITION VERIFIED (+9128169669005694462519713793099402)
FINAL LOWER BOUND VERIFIED: 1425933741673169505174021654095740659
Ran 3 tests
OK
ALL PUBLIC ARTIFACT CHECKS PASSED
```

Status: **PASSED**.

After this report was written, `CHECKSUMS.sha256` was regenerated and the same
command was run again so that this report itself is covered by the published
checksum manifest.
