# Environment Record

## Public verification

- Python: 3.11 or later
- Third-party packages: none
- Optimizer: not required
- Supported paths: repository-relative; no private absolute path is required

The public quick verifier uses Python arbitrary-precision integers and only the
standard library.

## Original computations

- Kernel optimization: Gurobi Optimizer 10.0.0
- Original GLB source commit: `5af167dd68a193b83de35a5ddaf4ecc3c534b46a`
- Original GUB/input source commit: `85d17f1e840632978b3baed5b69622d51f6419bf`
- Exported-input SHA-256 values are stored in
  `experiments/lower_bound/general_safe_rectangle_ip_followup/certificate.json`.

Individual reports and certificates contain the elapsed-time, memory, and
forward/reverse-enumeration information available for each stage.

## Post-GPW computations (results as of 2026-11-12)

- Machine: Captain, Mac Pro 2019, Xeon W-3223 @ 3.5 GHz (8 cores / 16 threads), 48 GB RAM,
  macOS 26 (Darwin 25.5.0)
- Compiler: Apple clang 21.0.0, `clang++ -O3 -std=c++17 -march=native`
  (`experiments/post_gpw_improvement/barrier/cmp_mitm.cpp`, `barrier/vsweep.cpp`,
  `harvest/rank_transfer_mitm.cpp`; binary digests in `COMPRESSED_MITM_BASELINE.md`)
- Python 3.11 with NumPy for the drivers and `harvest/verify_psi.py`
- Memory and time of every run: `/usr/bin/time -l`, summarised per key in
  `experiments/psi_exhaustion/PSI_EXHAUSTION_LEDGER.json`
- Source: private development branch `post-gpw-improvement`, frozen at commit
  `2c49c11ed6511c211cd29b0671fc7314a02d4ee1`
- The public post-GPW verifier (`scripts/verify_post_gpw.py`) needs only the Python
  standard library (3.11 or later).
