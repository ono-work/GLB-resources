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

## Recorded run, version 2026-11-12 (post-GPW snapshot)

Run date: 2026-11-20 (Asia/Tokyo), in a fresh `git clone` of the snapshot commit on the
assembling machine (Python 3.11.x, standard library only).

Command:

```console
python scripts/verify_all.py
```

Result:

```text
FILE INTEGRITY VERIFIED (344 files)
G2 CALIBRATION VERIFIED (1448 safe pairs; g(3)=1474)
Z98 KERNEL EVIDENCE VERIFIED (2^98)
CANONICAL LAYER 0--6 VERIFIED (1416779128733115417932228068149714027)
RESIDUAL PROFILE CLOSURE VERIFIED (1416780686143449296616167856189137167)
LAYER 4/5 EXACT UNION VERIFIED (1416805572004163810711501940302641257)
DISJOINT PARTITION VERIFIED (+9128169669005694462519713793099402)
FINAL LOWER BOUND VERIFIED: 1425933741673169505174021654095740659
----------------------------------------------------------------------
Ran 6 tests in 0.024s

OK
POST-GPW FROZEN PACKAGE VERIFIED (121 files byte-identical to the 2026-11-12 freeze)
POST-GPW CERTIFICATES VERIFIED (v5 + 34 Psi families, 36 keys, 22 campaign keys CERTIFIED)
POST-GPW LOWER BOUND RECOMPUTED: 29247125847589399267405782004907476922410
POST-GPW AUDIT CHAIN RE-RUN ON A COPY: PSI FRAMEWORK GLOBAL AUDIT PASSED (100 random members per key)
PSI FRAMEWORK GLOBAL AUDIT PASSED
POST-GPW LOWER BOUND VERIFIED: 29247125847589399267405782004907476922410
ALL PUBLIC ARTIFACT CHECKS PASSED
```

Status: **PASSED** (paper result and post-GPW result).

The post-GPW part re-runs the frozen audit chain on a copy of the repository under
`generated/verify_post_gpw/` (about one minute) and compares the regenerated records
with the committed ones; no tracked file is modified (`git status` was clean after the
run). The same command also passed in the assembling working tree; see
`RELEASE_2026-11-12.md`.

Note on the paper artifact: in tag `gpw26-v1.0`, five input files were stored with LF
line endings while their recorded digests were computed on CRLF content, so the
recorded run above could not be reproduced from a clone of that tag (first failure:
`checksum mismatch: data/gub/game_export/games.csv`). This version stores the five
files byte-for-byte (`.gitattributes`, `-text`); their content is unchanged apart from
line endings and their digests now match.
