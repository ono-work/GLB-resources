#!/usr/bin/env python3
"""Freeze the compressed-MITM milestone into certified/post_gpw_compressed_mitm/ (adapted from freeze_1e40.py;
the old certified/post_gpw_1e40/ snapshot is never touched: its SHA256SUMS is checked before and after).

Runs build_ledger.py and global_audit.py (must print GLOBAL AUDIT PASSED), then copies the ledger, all certificates,
audit records and the producer / verifier source into the milestone directory, writes SHA256SUMS,
CERTIFIED_1E40.md and REPRODUCE.md.  Refuses to freeze if the global audit fails or the bound is <= 10^40.
Usage (from experiments/post_gpw_improvement): python3.11 harvest/freeze_1e40.py
"""
import json, hashlib, math, shutil, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "certified/post_gpw_compressed_mitm"
OLD = ROOT / "certified/post_gpw_1e40"
PREV = 10388063614992087355867888261572976595948   # post_gpw_1e40 milestone
GPW = 1425933741673169505174021654095740659


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout[-2000:], r.stderr[-2000:]); return r


def git(*a): return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def main():
    run(["python3.11", "harvest/build_ledger.py"])
    r = run(["python3.11", "harvest/global_audit.py"])
    g = json.loads((ROOT / "harvest/certificates/global_audit_record.json").read_text())
    if r.returncode != 0 or g["status"] != "GLOBAL AUDIT PASSED" or int(g["total"]) <= PREV:
        sys.exit("refusing to freeze: global audit not passed or bound <= previous milestone")
    old_ok = subprocess.run(["shasum", "-a", "256", "-c", "SHA256SUMS", "--quiet"], cwd=OLD).returncode == 0
    if not old_ok or OUT == OLD: sys.exit("refusing: old milestone modified")
    led = json.loads((ROOT / "COUNTED_FAMILIES.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    files = ["COUNTED_FAMILIES.json", "certificate_v5.json", "certificates/verify_v5_record.json",
             "certificates/audit_v5_structure_record.json", led["audit_record"],
             "harvest/certificates/global_audit_record.json", "HARVEST_CERTIFIED_BASELINE.md"]
    for e in led["families"]:
        if e.get("included"): files += [e["producer_certificate"], e["verifier_certificate"]]
    code = ["verify_v2.py", "verify_v5.py", "verify_v5_crt.py", "verify_count_numpy.py", "audit_v5_structure.py",
            "glbcore.py", "side_count2.py", "dlat.py",
            "harvest/psi_exact.py", "harvest/n2_exact.py", "harvest/mitm.py", "harvest/rank_transfer_mitm.cpp",
            "harvest/verify_psi.py", "harvest/audit_psi_structure.py", "harvest/build_ledger.py",
            "harvest/global_audit.py", "harvest/make_baseline_md.py", "harvest/freeze_1e40.py", "harvest/freeze_compressed.py",
            "harvest/psi_regions.py", "barrier/cmp_mitm.cpp", "barrier/vsweep.cpp", "barrier/cmp.py", "barrier/vsweep.py",
            "barrier/memgate.py", "barrier/plan_runs.py", "COMPRESSED_MITM_BASELINE.md", "NEXT_EXACT_RUNS.md"]
    for f in files + [c for c in code if (ROOT / c).exists()]:
        dst = OUT / f; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT / f, dst)
    src = ROOT.parent.parent / "src/hit_antichain_counter.py"   # archived GPW exact counter (imported via sys.path)
    (OUT / "src").mkdir(exist_ok=True); shutil.copy2(src, OUT / "src/hit_antichain_counter.py")
    T = int(g["total"])
    fams = [e for e in led["families"] if e.get("included")]
    prod_commit = {e["id"]: git("log", "-1", "--format=%H", "--", e["producer_certificate"]) for e in fams}
    ver_commit = {e["id"]: git("log", "-1", "--format=%H", "--", e["verifier_certificate"]) for e in fams}
    head = git("rev-parse", "HEAD")
    bins = {b: hashlib.sha256((ROOT / b).read_bytes()).hexdigest() for b in ["bin/cmp_mitm", "bin/vsweep"]}
    L = [f"# Certified: post-GPW compressed-MITM milestone",
         "",
         f"**g(4) ≥ {T}**",
         "",
         f"**log10 = {math.log10(T):.6f}**   ({T / 10**40:.6f} × 10^40); factor {T/GPW:.1f} over GPW (1.426e36), {T/PREV:.4f} over the post_gpw_1e40 milestone",
         "",
         "Compressed producer `bin/cmp_mitm` sha256 `" + bins["bin/cmp_mitm"] + "`, verifier `bin/vsweep` sha256 `" + bins["bin/vsweep"] + "` (Apple clang 21.0.0, `-O3 -std=c++17 -march=native`; binaries are not copied, they rebuild byte-identically from `barrier/*.cpp`, see COMPRESSED_MITM_BASELINE.md).",
         "",
         f"Frozen {time.strftime('%Y-%m-%d %H:%M')} on Captain. HEAD at freeze: `{head}` (branch `post-gpw-improvement`). The status line `GLOBAL AUDIT PASSED` is in `harvest/certificates/global_audit_record.json`.",
         "",
         "## Included families",
         "",
         "| family | key (world; S; C; E) | exact original | mirror (= original, by negation) | ×2 included | verifier | producer commit | verifier commit |",
         "|---|---|---:|---:|---|---|---|---|",
         f"| v5 (G1, G2 + mirrors) | (0; *±1*2; –; –), (0; *±1; –/*2; ·) with L ⊆ H_L | {led['baseline']['value']} (total incl. mirrors) | incl. | – | verify_v5 AUDIT PASSED | – | – |"]
    for e in fams:
        L.append(f"| {e['id']} | ({e['world']}; {e['S']}; {e['C']}; {e['E']}) | {e['exact']} | {e['exact'] if e['mirror_included'] else 0} | "
                 f"{'yes' if e['mirror_included'] else 'no'} | verify_psi AUDIT PASSED | `{prod_commit[e['id']][:10]}` | `{ver_commit[e['id']][:10]}` |")
    L += ["",
          f"Sum: B_v5 + Σ 2·exact = {T}.",
          "",
          "Families that are produced but not used in this milestone (verification pending or not needed) are listed in `COUNTED_FAMILIES.json` with `included: false`.",
          "",
          "## Proof of disjointness (summary)",
          "",
          "1. **Safe pairs are canonical.** Every counted pair `{L|R}` is a safe pair of antichains of G_3. Safe pairs are canonical forms (v5 theory; machine-checked on samples by `audit_v5_structure.py` and `audit_psi_structure.py`). So distinct option pairs give distinct games of birthday ≤ 4.",
          "2. **Within a family.** A pair is determined by `(L, B)`, where `R = T ∪ B`. The count is `Σ_D e(D)·c(D)` with `D = dom(L)` a function of `L`, so nothing is counted twice. The inclusion–exclusion over `U ⊆ C` counts exactly the `B` that cover every `m ∈ C` strictly below.",
          "3. **Between originals.** The key `(world, S, C, E)` is a function of `R`. Here `S = R ∩ {*,±1,*2}`, `C` is the set covered strictly below by `R`, and `E` is the set not covered. The world is 0 if `0 ∈ R` and Z if `0 ∉ R` with 0 covered strictly below.",
          "   - All included Ψ families have distinct keys, and none of them has v5 G1's key.",
          "   - N2 shares v5 G2's `R`-key but has `L ⊄ H_L([0,*,±1])`, while G2 has `L ⊆ H_L([0,*,±1])`.",
          "   - The P-cells (`P = R ∩ G_2`) spanned by each family are listed in the ledger. N5, Z2 and N6 each span two cells, because `B` may contain one extra day-2 game. The key, and so the disjointness, does not depend on `P`.",
          "4. **Mirrors.** Negation `{L|R} ↦ {−R|−L}` is an involution, so it is injective, and it preserves canonicality. It fixes 0 and *.",
          "   - Originals lie in `O0 = {0 ∈ R ∖ L}` or `OZ = {0 ∉ L ∪ R, * ∈ R ∖ L}`.",
          "   - Mirrors lie in `−O0 = {0 ∈ L ∖ R}` or `−OZ = {0 ∉ L ∪ R, * ∈ L ∖ R}`.",
          "   - These four classes are pairwise disjoint. So mirrors never meet originals, and mirrors of disjoint families are disjoint. Hence each family contributes exactly 2 × its original count.",
          "5. **Machine checks.** `harvest/global_audit.py` re-checks all of the above from `COUNTED_FAMILIES.json` (hashes, verifier status, keys, P-cells, mirror classes) and recomputes the sum.",
          "",
          "## Files",
          "",
          "- `SHA256SUMS` lists the checksums of every file in this directory.",
          "- `REPRODUCE.md` gives the commands to reproduce.",
          ]
    (OUT / "CERTIFIED_COMPRESSED_MITM.md").write_text("\n".join(L) + "\n")
    R = ["# Reproduce", "", "Run everything from `experiments/post_gpw_improvement/` on the `post-gpw-improvement` branch.", "",
         "Producers:", "", "```",
         "python3.11 verify_v5.py            # v5 baseline (and verify_v5_crt.py)"]
    for e in fams:
        R.append(f"python3.11 harvest/psi_exact.py '{json.dumps(e['S']).replace(' ', '')}' '{json.dumps(e['C']).replace(' ', '')}'   # {e['id']} -> {e['producer_certificate']}")
    R += ["```", "", "Independent verifiers (one at a time; peak RSS up to 36 GB):", "", "```"]
    for e in fams: R.append(f".venv/bin/python harvest/verify_psi.py {e['producer_certificate']}")
    R += ["python3.11 harvest/audit_psi_structure.py '<list of [S,C]>' 150",
          "python3.11 harvest/build_ledger.py && python3.11 harvest/global_audit.py    # -> GLOBAL AUDIT PASSED", "```", ""]
    (OUT / "REPRODUCE.md").write_text("\n".join(R) + "\n")
    sums = []
    for p in sorted(OUT.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS":
            sums.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}")
    (OUT / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    if subprocess.run(["shasum", "-a", "256", "-c", "SHA256SUMS", "--quiet"], cwd=OLD).returncode != 0: sys.exit("old milestone changed!")
    print("FROZEN", T, math.log10(T), OUT)


if __name__ == "__main__":
    main()
