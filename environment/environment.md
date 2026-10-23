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
