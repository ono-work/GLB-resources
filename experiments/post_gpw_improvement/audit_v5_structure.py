#!/usr/bin/env python3
"""Structural audit of the v5 construction (Phase 3: safety, antichains, disjointness, mirrors, GPW overlap).

Independent of the producer modules (uses only the verify_v2 loader of the frozen input).
 A0. the input table is a correct set of distinct canonical games born by day 3:
     leq_rows agrees with Conway's recursive definition on all 1474^2 pairs given the option lists,
     is antisymmetric, every game's option sets are antichains without reversible options,
     birthdays 0..3; negation table = Conway negation (options swapped and negated), order-reversing.
 A.  hypotheses of the safe-pair lemma for every counted family (re-derived from definitions).
 B.  T antichain, V_max subset of {g : g || T}, so T u B is an antichain for every antichain B in V_max.
 C.  G1 / G2 disjointness (21 in R for G1, 21 notin R for G2); within-family injectivity.
 D.  mirror lemma hypotheses: 0 in T, -0 = 0, req(T) contains q > 0  (so 0 notin L, 0 in mirror left sets).
 E.  GPW families: kernels main/K1/K2/K5 satisfy T_L u Q_L^+ subset H_L(T) and Q_R^+ subset V(dom T_L),
     so Can(K) subset G1; the v5 bound adds no GPW term.
 F.  end-to-end random test: sampled members of G1, G2, -G1, -G2 are checked with a generic Conway
     comparison (games of day 4 as option sets): option sets antichains, no reversible option
     (=> canonical), and all sampled games pairwise unequal as games.
Usage: python3.11 audit_v5_structure.py [samples_per_family]
"""
import json, sys, time, random
from pathlib import Path
import verify_v2 as v

HERE = Path(__file__).resolve().parent
check = v.check
N, leq, comp, LEFT, RIGHT, NEG = v.N, v.leq, v.comp, v.LEFT, v.RIGHT, v.NEG
out = {}


def a0_table():
    t = time.time()
    # birthdays
    bd = [None] * N
    changed = True
    while changed:
        changed = False
        for x in range(N):
            if bd[x] is None and all(bd[o] is not None for o in LEFT[x] + RIGHT[x]):
                bd[x] = 1 + max([bd[o] for o in LEFT[x] + RIGHT[x]], default=-1); changed = True
    check(all(b is not None and b <= 3 for b in bd), "birthdays <= 3")
    # Conway: x <= y  iff  no x^L with y <= x^L  and  no y^R with y^R <= x
    bad = 0
    for x in range(N):
        for y in range(N):
            c = not any(leq(y, xl) for xl in LEFT[x]) and not any(leq(yr, x) for yr in RIGHT[y])
            if c != leq(x, y): bad += 1
    check(bad == 0, f"leq table vs Conway recursion: {bad} mismatches")
    check(all(not (leq(x, y) and leq(y, x)) for x in range(N) for y in range(x + 1, N)), "antisymmetry (distinct games)")
    canon = all(v.antichain(LEFT[x]) and v.antichain(RIGHT[x])
                and not any(leq(xlr, x) for xl in LEFT[x] for xlr in RIGHT[xl])
                and not any(leq(x, xrl) for xr in RIGHT[x] for xrl in LEFT[xr]) for x in range(N))
    check(canon, "every table game is in canonical form")
    negok = all(sorted(LEFT[NEG[x]]) == sorted(NEG[y] for y in RIGHT[x]) and
                sorted(RIGHT[NEG[x]]) == sorted(NEG[y] for y in LEFT[x]) for x in range(N))
    check(negok and all(NEG[NEG[x]] == x for x in range(N)), "negation table = Conway negation, involution")
    check(all(leq(i, j) == leq(NEG[j], NEG[i]) for i in range(N) for j in range(N)), "negation order-reversing")
    out["A0"] = {"games": N, "by_birthday": [bd.count(k) for k in range(4)], "conway_mismatches": bad,
                 "canonical": canon, "negation_ok": negok, "sec": round(time.time() - t)}
    print("A0", out["A0"], flush=True)


def req(x):
    L = LEFT[x]
    return [o for o in L if not any(leq(o, z) and o != z for z in L)]


def fam_struct(f):
    TR, x0 = f["T_R"], f["x0"]
    HL = [g for g in range(N) if v.hitL(g, TR)]
    Vmax = [g for g in range(N) if g not in TR and not any(comp(g, t) for t in TR)]
    REQ = sorted(set(q for x in TR + Vmax for q in req(x)))
    reqT = sorted(set(q for t in TR for q in req(t)))
    return TR, x0, HL, Vmax, REQ, reqT


def dom(L, REQ): return frozenset(q for q in REQ if any(leq(q, l) for l in L))
def VD(D, Vmax): return [x for x in Vmax if all(any(leq(o, d) for d in D) for o in req(x))]


def abcde(C):
    res = {}
    fams = [fam_struct(f) for f in C["families"]]
    for (TR, x0, HL, Vmax, REQ, reqT), f in zip(fams, C["families"]):
        r = {}
        r["T_antichain"] = check(v.antichain(TR), "T antichain")
        r["H_L_def"] = check(HL == f["H_L"], "H_L")
        r["req_is_all_left_options"] = all(sorted(req(x)) == sorted(LEFT[x]) for x in TR + Vmax)  # canonical => antichain
        r["Vmax_incomparable_to_T"] = check(all(not comp(g, t) and g != t for g in Vmax for t in TR), "Vmax || T")
        r["zero_in_T_selfneg"] = check(0 in TR and NEG[0] == 0, "0 in T, -0 = 0")
        r["reqT_has_q_gt_0"] = check(any(q != 0 and leq(0, q) for q in reqT), "q > 0 in req(T)")
        r["x0"] = x0
        if x0 is not None:
            r["x0_notin_T"] = check(x0 not in TR, "x0 notin T")
        res[str(TR)] = r
    (T1, x1, *_), (T2, x2, *_) = fams
    res["G1_G2"] = check(21 in T1 and 21 not in T2 and x2 == 21 and x1 is None, "21 separation")
    # E: GPW kernels inside G1
    TR, _, HL, Vmax, REQ, _ = fams[0]
    gpw = {"main": [2, 11, 14], "K1": [2, 14, 288], "K2": [2, 11, 318], "K5": [11, 14, 50]}
    e = {}
    for name, TL in gpw.items():
        ql, qr = v.qsets(TL, TR)
        ok = (v.admissible(TL, TR) and set(TL + ql) <= set(HL) and set(qr) <= set(Vmax)
              and set(qr) <= set(VD(dom(TL, REQ), Vmax)))
        e[name] = {"T_L": TL, "Q_L+": len(ql), "Q_R+": len(qr), "Can(K) subset G1": check(ok, f"GPW {name} in G1")}
    res["E_gpw_kernels"] = e
    out["ABCDE"] = res
    print("ABCDE", json.dumps(res), flush=True)
    return fams


# ---------------- generic Conway comparison for games of day <= 4 -----------------
# a game is an int (table index) or a pair (tuple L, tuple R) of table indices
def opts(g, side):
    if isinstance(g, int): return LEFT[g] if side == 0 else RIGHT[g]
    return g[side]


def le(x, y, memo):
    if isinstance(x, int) and isinstance(y, int): return leq(x, y)
    k = (x, y)
    if k in memo: return memo[k]
    r = not any(le(y, xl, memo) for xl in opts(x, 0)) and not any(le(yr, x, memo) for yr in opts(y, 1))
    memo[k] = r
    return r


def random_antichain(pool, rng):
    pool = pool[:]; rng.shuffle(pool); A = []
    for x in pool:
        if rng.random() < 0.5 and all(not comp(x, a) for a in A): A.append(x)
    return A


def f_random(fams, n, seed=1):
    rng = random.Random(seed)
    samples = []
    for fi, (TR, x0, HL, Vmax, REQ, reqT) in enumerate(fams):
        got = 0
        while got < n:
            L = random_antichain(HL, rng)
            D = dom(L, REQ)
            if not all(any(leq(q, d) for d in D) for q in reqT): continue
            B = random_antichain([x for x in VD(D, Vmax) if x != x0], rng)
            samples.append((f"G{fi+1}", (tuple(sorted(L)), tuple(sorted(TR + B)))))
            got += 1
    samples += [("-" + nm, (tuple(sorted(NEG[r] for r in g[1])), tuple(sorted(NEG[l] for l in g[0])))) for nm, g in samples]
    memo, bad = {}, []
    for nm, G in samples:
        Lx, Rx = G
        if not (v.antichain(Lx) and v.antichain(Rx)): bad.append((nm, "not antichain"))
        if any(le(lr, G, memo) for l in Lx for lr in RIGHT[l]): bad.append((nm, "reversible left"))
        if any(le(G, rl, memo) for r in Rx for rl in LEFT[r]): bad.append((nm, "reversible right"))
        mir = nm.startswith("-")
        if (0 in Lx, 0 in Rx) != ((True, False) if mir else (False, True)):
            bad.append((nm, "0-separation"))
    check(not bad, f"random canonicality {bad[:5]}")
    # pairwise distinct as games (equal canonical forms <=> equal games)
    eq = 0
    keys = {}
    for i, (nm, G) in enumerate(samples):
        keys.setdefault(G, []).append(i)
    distinct = list(keys)
    for i in range(len(distinct)):
        for j in range(i + 1, len(distinct)):
            if le(distinct[i], distinct[j], memo) and le(distinct[j], distinct[i], memo): eq += 1
    check(eq == 0, "distinct option sets give distinct games")
    out["F_random"] = {"samples": len(samples), "distinct_option_pairs": len(distinct), "equal_game_pairs": eq,
                       "violations": bad[:10]}
    print("F", out["F_random"], flush=True)


def main():
    t0 = time.time()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    C = json.loads((HERE / "certificate_v5.json").read_text())
    a0_table()
    fams = abcde(C)
    f_random(fams, n)
    status = "AUDIT PASSED" if not v.errors else "AUDIT FAILED"
    out.update(status=status, errors=v.errors, runtime_s=round(time.time() - t0), command="python3.11 audit_v5_structure.py " + str(n))
    (HERE / "certificates/audit_v5_structure_record.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(status, f"{time.time()-t0:.0f}s")
    return status


if __name__ == "__main__":
    sys.exit(0 if main() == "AUDIT PASSED" else 1)
