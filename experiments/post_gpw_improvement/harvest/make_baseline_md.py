#!/usr/bin/env python3
"""Write HARVEST_CERTIFIED_BASELINE.md from COUNTED_FAMILIES.json (no hand-copied numbers)."""
import json, math, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
led = json.loads((ROOT / "COUNTED_FAMILIES.json").read_text())
B5 = int(led["baseline"]["value"])
tot = B5; cand = B5
rows = []
for e in led["families"]:
    x = int(e["exact"]) if e.get("exact") else 0
    cand += 2 * x
    if e.get("included"): tot += (2 if e["mirror_included"] else 1) * x
    ver = "AUDIT PASSED" if e.get("verifier_ok") else ("pending" if e.get("exact") else "–")
    aud = "PASSED" if e.get("structural_audit_ok") else "–"
    rows.append(f"| {e['id']} = Ψ({e['S']},{e['C']}) | {e.get('exact', '–')} | "
                f"{e.get('exact', '–') if e.get('mirror_included') else '(not yet)'} | {ver} | {aud} | {'yes' if e.get('included') else 'no'} |")
L = [f"# Harvest certified baseline",
     "",
     f"Generated {time.strftime('%Y-%m-%d %H:%M')} by `harvest/make_baseline_md.py` from `COUNTED_FAMILIES.json`.",
     "",
     "```",
     f"certified bound   B = {tot}",
     f"                  log10 B = {math.log10(tot):.6f}   ({tot / 10**40:.4f} × 10^40)",
     f"exceeds 10^40:    {tot > 10**40}" + ("" if tot > 10**40 else f"   (gap {10**40 - tot})"),
     f"candidate (all producer values, if all verified) = {cand}  (log10 {math.log10(cand):.6f})",
     "```",
     "",
     "| family | exact original contribution | mirror contribution | verifier | structural audit | included in total |",
     "|---|---:|---:|---|---|---|",
     f"| v5 (G1, G2 and their mirrors) | {B5} (including mirrors) | (included) | verify_v5 AUDIT PASSED | PASSED | yes |",
     *rows,
     "",
     "## Mirror accounting",
     "",
     "- **Mirror map.** The map is negation `{L|R} ↦ {−R|−L}`. It is an involution on games, so it is injective. It maps canonical forms to canonical forms, and safe pairs to safe pairs, because the conditions are symmetric under negation (machine-checked on samples by the audit).",
     "- **Fixed points.** `−0 = 0` and `−* = *`. The global audit checks both.",
     "- **Four classes.** Every counted original lies in one of two classes, and each mirror lies in the negated class:",
     "  - `O0` = {0 ∈ R, 0 ∉ L}: v5 G1/G2 and the N-families; their mirrors lie in `−O0` = {0 ∈ L, 0 ∉ R}.",
     "  - `OZ` = {0 ∉ L ∪ R, * ∈ R ∖ L}: the Z-families; their mirrors lie in `−OZ` = {0 ∉ L ∪ R, * ∈ L ∖ R}.",
     "- **Consequences.** The four classes are pairwise disjoint. So no mirror equals any original, and no mirror appears as any other counted cell. Mirrors of disjoint originals are disjoint, because negation is injective.",
     "",
     "## Disjointness of originals",
     "",
     "- **The key.** The key `(world, S, C, E)` is a function of `R`. It records which of `{0,*,±1,*2}` lie literally in `R`, which are covered strictly below, and which are uncovered. Distinct keys therefore mean disjoint families.",
     "- **v5 G1.** G1 has key (0; *±1*2; –; –), which no Ψ family uses.",
     "- **v5 G2 and N2.** v5 G2 has `R ∩ F0 = {*, ±1}` and `L ⊆ H_L([0,*,±1])`. N2 has the same `S` but requires `L ⊄ H_L([0,*,±1])`, so the two are disjoint.",
     "- **P-cells.** `P = R ∩ G_2` is not always constant on a family. In N5, Z2 and N6, `B` may contain one further day-2 game (ids 17, 15 and 19 respectively). Those families span the two cells `P = T` and `P = T ∪ {x}`, listed in `COUNTED_FAMILIES.json` (`P_cells`). Disjointness does not rely on `P`: it relies on the key. `S = R ∩ F` is unaffected because `B ∩ F = ∅`. The global audit recomputes the P-cells exactly.",
     "",
     "Distinct option pairs give distinct games, because safe pairs are canonical. The global audit is `harvest/global_audit.py`.",
     ]
(ROOT / "HARVEST_CERTIFIED_BASELINE.md").write_text("\n".join(L) + "\n")
print(tot, math.log10(tot))
