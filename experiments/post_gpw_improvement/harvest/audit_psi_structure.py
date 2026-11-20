#!/usr/bin/env python3
"""Structural audit of the harvested families Psi(S, C) (independent of the producer; uses verify_v2 loader and the
generic Conway comparator of audit_v5_structure).

Psi(S, C):  T = [0] + S,  F0 = {3,12,21} (*, ±1, *2),  C ⊆ F0 \\ S covered strictly below,  E = F0 \\ S \\ C uncovered.
  L ∈ A(H_L(T ∪ C) \\ {0}),  req(T) ⊆ down(dom L)   [Psi([3,12],[21]) additionally L ⊄ H_L(T)]
  R = T ∪ B,  B ∈ A(V(dom L)),  B ∩ F0 = ∅,  for m ∈ C: B ∩ up(m) = ∅, B ∩ down(m) ≠ ∅;  for m ∈ E: B ∩ down(m) = ∅.
Checks:
 H. hypotheses: T antichain; V_max || T; every y in RIGHT[l] (l in pool) is >= some t in T or >= some m in C;
    0 ∉ pool; req(T) contains q > 0 or 0 is excluded from the pool (0 ∉ L);
 P. pattern separation: R ∩ F0 = S and the coverage pattern (C covered, E uncovered) are functions of R, so families with
    distinct (S, C) are disjoint; v5 G1 has R ∩ F0 = F0; v5 G2 has R ∩ F0 = {3,12} and L ⊆ H_L([0,3,12]).
 F. random end-to-end test: sampled members of every family, of G1, G2 and of all mirrors: option sets antichains,
    no reversible option (canonical), 0 ∈ R \\ L for originals and 0 ∈ L \\ R for mirrors, and pairwise distinct as games.
Usage: python3.11 harvest/audit_psi_structure.py FAMILIES_JSON [samples_per_family]
  FAMILIES_JSON: list of [S, C] pairs, e.g. '[[[3,12],[21]],[[12,21],[3]],[[12],[3,21]]]'
"""
import sys, json, random, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import verify_v2 as v
import audit_v5_structure as a5

N, leq, comp, LEFT, RIGHT, NEG = v.N, v.leq, v.comp, v.LEFT, v.RIGHT, v.NEG
F0 = [3, 12, 21]
check = v.check


def req(x):
    L = LEFT[x]
    return [o for o in L if not any(leq(o, z) and o != z for z in L)]


def fam(S, C):
    Z = 0 in C   # Z-world: 0 covered strictly below, * ∈ R literally, * and 0 removed from the L-pool
    F = [0, 3, 12, 21] if Z else F0
    T = list(S) if Z else [0] + S
    excl = {0, 3} if Z else {0}
    E = [m for m in F if m not in S and m not in C]
    pool = [g for g in range(N) if g not in excl and v.hitL(g, T + C)]
    small = set(g for g in range(N) if g not in excl and v.hitL(g, T)) if sorted(S) == [3, 12] and not Z else None
    Vmax = [g for g in range(N) if g not in T and not any(comp(g, t) for t in T)]
    REQ = sorted(set(q for x in T + Vmax for q in req(x)))
    reqT = sorted(set(q for t in T for q in req(t)))
    return dict(S=S, C=C, E=E, T=T, pool=pool, small=small, Vmax=Vmax, REQ=REQ, reqT=reqT, Z=Z, F=F)


def hyp(f):
    r = {}
    T, C = f["T"], f["C"]
    r["T_antichain"] = check(v.antichain(T), "T antichain")
    r["Vmax_incomparable"] = check(all(not comp(g, t) for g in f["Vmax"] for t in T), "Vmax || T")
    r["pool_hit"] = check(all(all(any(leq(t, y) for t in T) or any(leq(m, y) for m in C) for y in RIGHT[l]) for l in f["pool"]),
                          "pool right options hit by T or above a covered m")
    r["zero_not_in_pool"] = check(0 not in f["pool"], "0 not in pool")
    if f["Z"]:
        r["Z_star_literal_not_in_pool"] = check(3 in f["S"] and 3 not in f["pool"] and 0 not in f["T"], "Z: * ∈ S, * ∉ pool, 0 ∉ T")
    r["C_E_disjoint_from_S"] = check(not (set(f["C"]) & set(f["S"])) and not (set(f["E"]) & set(f["S"])), "C,E ∩ S = ∅")
    return r


def dom(L, REQ): return [q for q in REQ if any(leq(q, l) for l in L)]
def VD(D, Vmax): return [x for x in Vmax if all(any(leq(o, d) for d in D) for o in req(x))]


def sample(f, rng, n, tries=200000):
    out = []
    for _ in range(tries):
        if len(out) >= n: break
        L = a5.random_antichain(f["pool"], rng)
        if not L or (f["small"] is not None and set(L) <= f["small"]): continue
        D = dom(L, f["REQ"])
        if not all(any(leq(q, d) for d in D) for q in f["reqT"]): continue
        X = [b for b in VD(D, f["Vmax"]) if b not in f["F"] and not any(leq(m, b) for m in f["C"])
             and not any(leq(b, m) for m in f["E"])]
        B = []
        ok = True
        for m in f["C"]:            # force coverage: pick a random element below m compatible with B
            cand = [b for b in X if leq(b, m) and b != m and all(not comp(b, c) for c in B)]
            if not cand: ok = False; break
            B.append(rng.choice(cand))
        if not ok: continue
        rest = [b for b in X if b not in B and all(not comp(b, c) for c in B)]
        B += a5.random_antichain(rest, rng)
        out.append((tuple(sorted(L)), tuple(sorted(f["T"] + B))))
    return out


def main():
    t0 = time.time()
    fams = json.loads(sys.argv[1]); n = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    rng = random.Random(11)
    rec = {"families": {}}
    samples = []
    for S, C in fams:
        f = fam(S, C)
        h = hyp(f)
        sm = sample(f, rng, n)
        # pattern of each sample is (S, C, E)
        pat_ok = all(set(R) & set(f["F"]) == set(S)
                     and all(any(leq(b, m) and b != m for b in R) for m in f["C"])
                     and all(not any(leq(b, m) for b in R) for m in f["E"]) for L, R in sm)
        check(pat_ok, f"pattern of samples Psi({S},{C})")
        rec["families"][f"Psi({S},{C})"] = {"hypotheses": h, "pool": len(f["pool"]), "Vmax": len(f["Vmax"]),
                                           "REQ": f["REQ"], "reqT": f["reqT"], "samples": len(sm), "pattern_ok": pat_ok}
        samples += [(("Z:" if f["Z"] else "") + f"Psi({S},{C})", g) for g in sm]
        print(f"Psi({S},{C}): {rec['families'][f'Psi({S},{C})']}", flush=True)
    # v5 families for cross-distinctness
    C5 = json.loads((HERE.parent / "certificate_v5.json").read_text())
    v5f = a5.fam_struct
    for fi, ff in enumerate(C5["families"]):
        TR, x0, HL, Vmax, REQ, reqT = v5f(ff)
        got = 0
        while got < n:
            L = a5.random_antichain(HL, rng); D = dom(L, REQ)
            if not all(any(leq(q, d) for d in D) for q in reqT): continue
            B = a5.random_antichain([x for x in VD(D, Vmax) if x != x0], rng)
            samples.append((f"G{fi+1}", (tuple(sorted(L)), tuple(sorted(TR + B))))); got += 1
    samples += [("-" + nm, (tuple(sorted(NEG[r] for r in g[1])), tuple(sorted(NEG[l] for l in g[0])))) for nm, g in samples]
    memo, bad = {}, []
    for nm, G in samples:
        Lx, Rx = G
        if not (v.antichain(Lx) and v.antichain(Rx)): bad.append((nm, "not antichain"))
        if any(a5.le(lr, G, memo) for l in Lx for lr in RIGHT[l]): bad.append((nm, "reversible left"))
        if any(a5.le(G, rl, memo) for r in Rx for rl in LEFT[r]): bad.append((nm, "reversible right"))
        mir = nm.startswith("-"); z = "Z:" in nm
        if not z and (0 in Lx, 0 in Rx) != ((True, False) if mir else (False, True)): bad.append((nm, "0-separation"))
        if z and ((0 in Lx) or (0 in Rx) or (3 in Lx, 3 in Rx) != ((True, False) if mir else (False, True))): bad.append((nm, "Z *-separation"))
    check(not bad, f"random canonicality {bad[:5]}")
    keys = {}
    for i, (nm, G) in enumerate(samples): keys.setdefault(G, []).append(nm)
    dup_across = [k for k, nms in keys.items() if len(set(nms)) > 1]
    check(not dup_across, f"identical option pairs in two families: {dup_across[:3]}")
    distinct = list(keys); eq = 0
    for i in range(len(distinct)):
        for j in range(i + 1, len(distinct)):
            if a5.le(distinct[i], distinct[j], memo) and a5.le(distinct[j], distinct[i], memo): eq += 1
    check(eq == 0, "distinct option pairs give distinct games")
    rec["F_random"] = {"samples": len(samples), "distinct_option_pairs": len(distinct), "equal_game_pairs": eq,
                       "violations": bad[:10], "cross_family_duplicates": len(dup_across)}
    status = "AUDIT PASSED" if not v.errors else "AUDIT FAILED"
    rec.update(status=status, errors=v.errors, runtime_s=round(time.time() - t0), command=" ".join(sys.argv))
    (HERE / "certificates").mkdir(exist_ok=True)
    (HERE / "certificates/audit_psi_structure_record.json").write_text(json.dumps(rec, indent=1, default=str) + "\n")
    print("F", rec["F_random"]); print(status, f"{time.time()-t0:.0f}s")
    return status


if __name__ == "__main__":
    sys.exit(0 if main() == "AUDIT PASSED" else 1)
