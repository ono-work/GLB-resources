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
