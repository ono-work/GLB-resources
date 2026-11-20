#!/usr/bin/env python3
"""Independent regeneration of the complete Psi(S,C) key universe and check against the ledger.

Framework (as implemented in post_gpw_improvement/harvest/psi_exact.py, verify_psi.py, global_audit.py):
  F0 = {3=*, 12=±1, 21=*2}.
  0-world  (class O0 = {0 ∈ R \\ L}):  key = a map F0 -> {S, C, E};  T = {0} ∪ S,
           pool = {g ≠ 0 : every right option of g is >= some element of T ∪ C} = H_L(T ∪ C) \\ {0}.
  Z-world  (class OZ = {0 ∉ L ∪ R, 0 covered strictly below, * ∈ R \\ L}):  * ∈ S, 0 ∈ C fixed,
           key = a map {±1, *2} -> {S, C, E};  T = S,  pool = H_L(T ∪ C) \\ {0, *}.
  Members: L ∈ A(pool), req(T) ⊆ ↓dom L, R = T ∪ B, B ∈ A(V(dom L)), B ∩ F = ∅,
           m ∈ C: B ∩ ↓m ∖ {m} ≠ ∅ (then B ∩ ↑m = ∅ automatically), m ∈ E: B ∩ ↓m = ∅.
  Mirrors: negation, classes -O0 = {0 ∈ L \\ R}, -OZ = {0 ∉ L ∪ R, * ∈ L \\ R}.
Checks:
  U1  the universe is exactly the 27 + 9 = 36 keys (all maps), each with a canonical ID;
  U2  hypotheses of the safety lemma hold for every key (T antichain, V_max || T, pool hit, 0 [and *] ∉ pool);
  U3  the key is a function of (L, R): random members of every key family are re-keyed from (L, R) alone and land in
      their own key (so the 36 families are pairwise disjoint and every framework member has exactly one key);
  U4  v5 G1 = key (0; F0; -; -) with the same pool; v5 G2 = key (0; *±1; -; *2) entirely (C = ∅ so the pool is
      already H_L([0,*,±1])) plus key (0; *±1; *2; -) restricted to L ⊆ H_L([0,*,±1]); N2 = the complement;
  U5  every key appears exactly once among {v5, ledger families (COUNTED_FAMILIES.json), remaining keys};
  U6  every ledger family's (world, S, C) is in the universe and certified entries have both certificates.
Usage (from experiments/post_gpw_improvement):  python3.11 ../psi_exhaustion/audit_psi_exhaustiveness.py [samples]
Writes ../psi_exhaustion/audit_psi_exhaustiveness_record.json.
"""
import sys, json, itertools, random, time, hashlib
from pathlib import Path
OUTDIR = Path(__file__).resolve().parent
PG = OUTDIR.parent / "post_gpw_improvement"
sys.path.insert(0, str(PG)); sys.path.insert(0, str(PG / "harvest"))
import verify_v2 as v
import audit_v5_structure as a5
import audit_psi_structure as aps

leq, comp = v.leq, v.comp
NAME = {3: "*", 12: "±1", 21: "*2", 0: "0"}
errors = []


def check(c, msg):
    if not c: errors.append(msg); print("FAIL:", msg, flush=True)
    return bool(c)


def universe():
    U = []
    for a in itertools.product("SCE", repeat=3):
        S = [m for m, x in zip([3, 12, 21], a) if x == "S"]; C = [m for m, x in zip([3, 12, 21], a) if x == "C"]
        U.append(("0", tuple(S), tuple(C), tuple(m for m, x in zip([3, 12, 21], a) if x == "E")))
    for a in itertools.product("SCE", repeat=2):
        S = [3] + [m for m, x in zip([12, 21], a) if x == "S"]; C = [0] + [m for m, x in zip([12, 21], a) if x == "C"]
        U.append(("Z", tuple(S), tuple(sorted(C)), tuple(m for m, x in zip([12, 21], a) if x == "E")))
    return U


def kid(k):
    w, S, C, E = k
    f = lambda xs: ",".join(NAME[x] for x in xs) or "-"
    return f"{w}|S={f(S)}|C={f(C)}|E={f(E)}"


def rekey(L, R):
    """Key of an option pair, computed from (L, R) only."""
    R = set(R)
    below = lambda m: any(leq(b, m) and b != m for b in R)
    if 0 in R and 0 not in L:
        F, w = [3, 12, 21], "0"
    elif 0 not in R and 0 not in L and below(0) and 3 in R and 3 not in L:
        F, w = [0, 3, 12, 21], "Z"
    else:
        return None
    S = tuple(m for m in F if m in R); C = tuple(m for m in F if m not in R and below(m))
    E = tuple(m for m in F if m not in R and not below(m))
    return (w, tuple(sorted(S)), tuple(sorted(C)), E)


def main(n):
    t0 = time.time(); rng = random.Random(20261109)
    U = universe()
    check(len(U) == 36 and len(set(U)) == 36, "U1: 36 distinct keys")
    led = json.loads((PG / "COUNTED_FAMILIES.json").read_text())
    rem = json.loads((OUTDIR / "REMAINING_KEYS.json").read_text())["keys"] if (OUTDIR / "REMAINING_KEYS.json").exists() else []
    owner = {k: [] for k in U}
    # v5
    C5 = json.loads((PG / "certificate_v5.json").read_text())
    g1, g2 = C5["families"]
    k_g1 = ("0", (3, 12, 21), (), ()); k_g2E = ("0", (3, 12), (), (21,)); k_g2C = ("0", (3, 12), (21,), ())
    f = aps.fam([3, 12, 21], [])
    check(g1["T_R"] == [0, 3, 12, 21] and g1["x0"] is None and set(g1["H_L"]) - {0} == set(f["pool"]), "U4: v5 G1 = key (0;*±1*2;-;-), same pool")
    fE = aps.fam([3, 12], []); fC = aps.fam([3, 12], [21])
    check(g2["T_R"] == [0, 3, 12] and g2["x0"] == 21 and set(g2["H_L"]) - {0} == set(fE["pool"]) == set(fC["small"]),
          "U4: v5 G2 = T [0,*,±1], x0 = *2, pool H_L([0,*,±1]) = pool of key E and small pool of key C")
    check(set(fC["small"]) < set(fC["pool"]), "U4: N2 part (L ⊄ H_L([0,*,±1])) non-trivial")
    owner[k_g1].append("v5:G1"); owner[k_g2E].append("v5:G2"); owner[k_g2C].append("v5:G2 (L ⊆ H_L([0,*,±1]))")
    remk = {r["id"]: (r["world"], tuple(r["S"]), tuple(r["C"]), tuple(r["E"])) for r in rem}
    for e in led["families"]:
        k = (e["world"], tuple(sorted(e["S"])), tuple(sorted(e["C"])), tuple(sorted(e["E"])))
        check(k in owner, f"U6: ledger {e['id']} key {k} in universe")
        if e["id"] in remk:
            # campaign key: its ledger entry IS the remaining key's resolution (one owner), keys must agree
            check(remk[e["id"]] == k, f"U5: campaign key {e['id']} ledger key = REMAINING_KEYS key")
            if e.get("included"):
                check(e["status"] == "CERTIFIED" and e["verifier_ok"] and e["structural_audit_ok"], f"U6: {e['id']} certified fields")
            continue
        if k in owner: owner[k].append(e["id"] + ("" if k != k_g2C else " (L ⊄ H_L([0,*,±1]))"))
        if e.get("included"):
            check(e["status"] == "CERTIFIED" and e["verifier_ok"] and e["structural_audit_ok"], f"U6: {e['id']} certified fields")
    for r in rem:
        k = (r["world"], tuple(r["S"]), tuple(r["C"]), tuple(r["E"]))
        check(k in owner, f"U5: remaining {r['id']} key in universe")
        if k in owner: owner[k].append("remaining:" + r["id"])
    rows = []
    for k in U:
        ow = owner[k]
        if k == k_g2C:
            ok = sorted(ow) == sorted(["v5:G2 (L ⊆ H_L([0,*,±1]))", "N2 (L ⊄ H_L([0,*,±1]))"])
        else:
            ok = len(ow) == 1
        check(ok, f"U5: key {kid(k)} owners {ow}")
        # U2 hypotheses + U3 rekeying
        S, C = list(k[1]), list(k[2])
        fk = aps.fam(S, C)
        h = aps.hyp(fk)
        check(all(h.values()), f"U2: hypotheses {kid(k)}")
        check(tuple(sorted(fk["E"])) == tuple(sorted(k[3])), f"E of {kid(k)}")
        sm = aps.sample(fk, rng, n)
        bad = [g for g in sm if rekey(*g) != k]
        check(not bad, f"U3: rekey {kid(k)} {bad[:2]}")
        # mirrors: negated pair must rekey to None (not an original of any key) and be in the right mirror class
        mb = [g for g in sm if rekey(tuple(v.NEG[r] for r in g[1]), tuple(v.NEG[l] for l in g[0])) is not None]
        check(not mb, f"U3: mirror of {kid(k)} is an original of some key")
        rows.append(dict(key=kid(k), world=k[0], S=list(k[1]), C=list(k[2]), E=list(k[3]), owners=ow,
                         pool=len(fk["pool"]), samples=len(sm), hypotheses_ok=all(h.values())))
        print(f"{kid(k):32s} pool={len(fk['pool']):3d} samples={len(sm):4d} owners={ow}", flush=True)
    counts = dict(universe=len(U), v5_only=sum(1 for r in rows if all(o.startswith("v5") for o in r["owners"])),
                  ledger=sum(1 for r in rows if any(not o.startswith(("v5", "remaining")) for o in r["owners"])),
                  remaining=sum(1 for r in rows if any(o.startswith("remaining") for o in r["owners"])))
    status = "EXHAUSTIVENESS AUDIT PASSED" if not errors else "EXHAUSTIVENESS AUDIT FAILED"
    rec = dict(status=status, counts=counts, keys=rows, errors=errors, samples_per_key=n,
               ledger_sha256=hashlib.sha256((PG / "COUNTED_FAMILIES.json").read_bytes()).hexdigest(),
               runtime_s=round(time.time() - t0))
    (OUTDIR / "audit_psi_exhaustiveness_record.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(counts); print(status, f"{time.time()-t0:.0f}s")
    return status


if __name__ == "__main__":
    sys.exit(0 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 100) == "EXHAUSTIVENESS AUDIT PASSED" else 1)
