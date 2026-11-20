#!/usr/bin/env python3
"""Region inventory of a family Psi(S, C), re-derived with the same definitions as psi_exact.py / verify_psi.py.

regions(S, C) -> list of dicts {D, U, n, elems, sha}.  Used for run planning only (no counting)."""
import sys, json, itertools, hashlib
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
import verify_v2 as v, verify_v5 as w
import complete_TR as ct


def req(x):
    L = v.LEFT[x]
    return [o for o in L if not any(v.leq(o, z) and o != z for z in L)]


def sha(r): return hashlib.sha256(",".join(map(str, sorted(r))).encode()).hexdigest()


def regions(S, C):
    Z = 0 in C
    F = [0, 3, 12, 21] if Z else [3, 12, 21]
    E = [m for m in F if m not in S and m not in C]
    T = list(S) if Z else [0] + S
    excl = {0, 3} if Z else {0}
    Vmax = [g for g in range(v.N) if g not in T and not any(v.comp(g, t) for t in T)]
    REQ = sorted(set(q for x in T + Vmax for q in req(x)))
    reqT = sorted(set(q for t in T for q in req(t)))
    Hbig = [g for g in range(v.N) if g not in excl and v.hitL(g, T + C)]
    hb = w.histogram(Hbig, REQ)
    hs = {}
    if sorted(S) == [3, 12] and not Z:
        hs = w.histogram([g for g in range(v.N) if g not in excl and v.hitL(g, T)], REQ)
    Ds = [D for D in ct.downsets(REQ) if all(any(v.leq(q, d) for d in D) for q in reqT)]
    out = []
    for D in Ds:
        m = sum(1 << j for j, q in enumerate(REQ) if q in D)
        e = hb.get(m, 0) - hs.get(m, 0)
        if e == 0: continue
        VD = [x for x in Vmax if all(any(v.leq(o, d) for d in D) for o in req(x))]
        X = [b for b in VD if b not in F and not any(v.leq(mm, b) for mm in C) and not any(v.leq(b, mm) for mm in E)]
        for k in range(len(C) + 1):
            for U in itertools.combinations(C, k):
                r = [b for b in X if not any(v.leq(b, u) for u in U)]
                out.append(dict(D=list(D), U=list(U), n=len(r), elems=r, sha=sha(r)))
    return out
