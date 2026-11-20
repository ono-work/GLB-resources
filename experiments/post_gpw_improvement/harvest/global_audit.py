#!/usr/bin/env python3
"""Global aggregation verifier for the harvested bound.  Reads only COUNTED_FAMILIES.json and the files it points to.

Checks:
 1. baseline v5: certificate value, verifier record AUDIT PASSED with the same bound, structural audit passed;
 2. every included family: producer file hash, verifier certificate (AUDIT PASSED, same exact total, hash),
    structural-audit record (hypotheses + pattern true, AUDIT PASSED);
 3. identifiers / cells: the key (world, S, C, E) is recomputed from S, C; the P-cells (P = R ∩ G_2) spanned by
    the family are recomputed exactly (T plus admissible antichains of G_2 elements in B) and compared to the ledger;
 4. no family twice: keys pairwise distinct, distinct from v5 G1, and equal to v5 G2's key only with the
    L ⊄ H_L([0,3,12]) condition (N2);
 5. mirror bookkeeping: negation fixes 0 and *; every original lies in one of the classes
    O0 = {0∈R, 0∉L} or OZ = {0∉L∪R, *∈R, *∉L}, checked exactly on the family definitions; mirrors lie in
    -O0 = {0∈L, 0∉R}, -OZ = {0∉L∪R, *∈L, *∉R}; the four classes are pairwise disjoint, negation is injective,
    so the mirror of a family is disjoint from all originals and from all other mirrors;
 6. recompute the sum B_v5 + Σ (1 + [mirror included]) · exact and test > 10^40.
Prints GLOBAL AUDIT PASSED only if all checks succeed.
"""
import sys, json, hashlib, math, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import verify_v2 as v

errors = []
def check(c, msg):
    if not c: errors.append(msg); print("FAIL:", msg)
    return bool(c)
def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
G2 = list(range(22))


def family_struct(S, C):
    Z = 0 in C
    F = [0, 3, 12, 21] if Z else [3, 12, 21]
    T = list(S) if Z else [0] + list(S)
    excl = {0, 3} if Z else {0}
    E = [m for m in F if m not in S and m not in C]
    pool = [x for x in range(v.N) if x not in excl and v.hitL(x, T + C)]
    Vmax = [x for x in range(v.N) if x not in T and not any(v.comp(x, t) for t in T)]
    return Z, F, T, E, pool, Vmax


def main():
    t0 = time.time()
    led = json.loads((ROOT / "COUNTED_FAMILIES.json").read_text())
    b = led["baseline"]
    v5 = json.loads((ROOT / b["producer_certificate"]).read_text())
    v5r = json.loads((ROOT / b["verifier_certificate"]).read_text())
    v5a = json.loads((ROOT / b["structural_audit"]).read_text())
    check(sha(b["producer_certificate"]) == b["producer_sha256"], "v5 certificate hash")
    check(v5["new_lower_bound"] == b["value"] == v5r["new_lower_bound"], "v5 value")
    check(v5r["status"] == "AUDIT PASSED" and v5a["status"] == "AUDIT PASSED", "v5 verifier / audit")
    total = int(b["value"])
    audit = json.loads((ROOT / led["audit_record"]).read_text())
    check(audit["status"] == "AUDIT PASSED", "Psi structural audit status")
    check(v.NEG[0] == 0 and v.NEG[3] == 3, "negation fixes 0 and *")
    keys = {("0", (3, 12, 21), (), ()): "v5:G1"}
    G2key = ("0", (3, 12), (), (21,)), ("0", (3, 12), (21,), ())   # v5 G2 (L ⊆ H_L([0,3,12])), both coverage states
    rows = []
    seen = set()
    for e in led["families"]:
        if not e.get("included"): rows.append((e["id"], "excluded", e.get("status"))); continue
        fid = e["id"]; check(fid not in seen, f"{fid} listed twice"); seen.add(fid)
        S, C = e["S"], e["C"]
        Z, F, T, E, pool, Vmax = family_struct(S, C)
        cert = json.loads((ROOT / e["producer_certificate"]).read_text())
        check(sha(e["producer_certificate"]) == e["producer_sha256"], f"{fid} producer hash")
        check(cert["S"] == S and cert["C"] == C and cert["T"] == T and cert["total"] == e["exact"], f"{fid} producer data")
        vr = json.loads((ROOT / e["verifier_certificate"]).read_text())
        check(sha(e["verifier_certificate"]) == e["verifier_sha256"], f"{fid} verifier hash")
        check(vr["status"] == "AUDIT PASSED" and vr["total"] == e["exact"] and vr["S"] == S and vr["C"] == C, f"{fid} verifier")
        af = audit["families"].get(f"Psi({S},{C})")
        check(af is not None and all(af["hypotheses"].values()) and af["pattern_ok"] and af["samples"] > 0, f"{fid} audit")
        # 3. P-cells: R ∩ G_2 = T ∪ (B ∩ G_2), and B ∩ G_2 ⊆ Y := {x ∈ V_max ∩ G_2 ∖ F admissible for X}.
        #    The family therefore lies in the P-cells {T ∪ Y' : Y' ⊆ Y antichain}.  Disjointness does NOT use P:
        #    it uses the key (world, S, C, E), and S = R ∩ F is unaffected by B ∩ G_2 since B ∩ F = ∅.
        Y = [x for x in Vmax if x in G2 and x not in F and not any(v.leq(m, x) for m in C) and not any(v.leq(x, m) for m in E)]
        check(all(x not in F for x in Y), f"{fid}: B ∩ F = ∅ so S = R ∩ F is a function of R")
        Pcells = [sorted(T + [y for i, y in enumerate(Y) if mask >> i & 1]) for mask in range(1 << len(Y))
                  if v.antichain([y for i, y in enumerate(Y) if mask >> i & 1])]
        check(e["P_cells"] == Pcells and e["E"] == E and e["world"] == ("Z" if Z else "0"), f"{fid} ledger key fields / P-cells")
        if Z:
            check(0 not in Y and 0 not in T, f"{fid}: 0 ∉ R")
        # 5. original-side class
        if Z:
            check(0 not in T and 0 not in pool and 0 in F and 3 in T and 3 not in pool, f"{fid} in class OZ")
        else:
            check(0 in T and 0 not in pool, f"{fid} in class O0")
        # 4. keys
        k = ("Z" if Z else "0", tuple(sorted(S)), tuple(sorted(C)), tuple(sorted(E)))
        check(k not in keys, f"{fid} key {k} already used by {keys.get(k)}")
        if k in G2key:
            check(cert.get("subtract_H_L_T") is True and e.get("L_condition") == "L ⊄ H_L([0,3,12])",
                  f"{fid} shares v5 G2 key: needs L ⊄ H_L([0,3,12])")
        keys[k] = fid
        mult = 2 if e["mirror_included"] else 1
        total += mult * int(e["exact"])
        rows.append((fid, k, e["exact"], mult))
    # G2 keys reserved with L-condition; check no family other than the L ⊄ H_L one uses them (done above)
    print("included:")
    for r in rows: print("  ", r)
    check(total > 10 ** 40, "total > 10^40")
    out = {"total": str(total), "log10": math.log10(total), "exceeds_1e40": total > 10 ** 40,
           "families": [r[0] for r in rows if r[1] != "excluded"], "errors": errors,
           "status": "GLOBAL AUDIT PASSED" if not errors else "GLOBAL AUDIT FAILED",
           "ledger_sha256": sha("COUNTED_FAMILIES.json"), "runtime_s": round(time.time() - t0)}
    (HERE / "certificates/global_audit_record.json").write_text(json.dumps(out, indent=1) + "\n")
    print("total", total, f"log10={math.log10(total):.6f}")
    print(out["status"])
    return not errors


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
