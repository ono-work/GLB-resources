# Preserved Research Sources

This directory contains the original Python sources associated with the
selected certificates and independent checks. They are retained for audit and
for expensive reruns.

The original research layout placed these modules at the repository root and
used a sibling `GUB` checkout. In this public package the frozen input is under
`data/gub/game_export/`. Consequently, the source files should be treated as
provenance-preserving research code unless a command in
`REPRODUCIBILITY.md` explicitly invokes them. The supported read-only public
entry point is `scripts/verify_all.py`.
