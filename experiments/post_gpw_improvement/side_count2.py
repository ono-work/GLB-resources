"""Antichain counting for canonical regions via (augmented) distributive-lattice structure.

Given a finite poset S (induced from G_3), adjoin a formal bottom and/or top if needed.
If the augmented poset is a distributive lattice J(Q), count |A(J(Q))| with dlat and subtract
the number of adjoined elements (each adjoined element is comparable to all others, so it
contributes exactly one extra antichain, the singleton).
Fallback: include/exclude counter (glbcore.count_antichains_bitset) for small S.
"""
from __future__ import annotations
import time
import glbcore as g
import dlat


def abstract_from(P, S):
    S = list(S)
    n = len(S)
    pos = {x: i for i, x in enumerate(S)}
    m = sum(1 << x for x in S)
    up = [0] * n
    for i, x in enumerate(S):
        u = 0
        for y in g.bits(P.up[x] & m):
            u |= 1 << pos[y]
        up[i] = u
    return up  # up[i] = mask of j with S[i] <= S[j] (includes i)


def augment(up):
    n = len(up)
    full = (1 << n) - 1
    down = [0] * n
    for i in range(n):
        for j in g.bits(up[i]):
            down[j] |= 1 << i
    mins = [i for i in range(n) if down[i] == 1 << i]
    maxs = [i for i in range(n) if up[i] == 1 << i]
    added = 0
    up = list(up)
    if len(mins) != 1:
        # new bottom index n: below everything
        up = [u for u in up] + [full | (1 << n)]
        n += 1; added += 1
        full = (1 << n) - 1
    if len(maxs) != 1:
        t = n
        up = [u | (1 << t) for u in up] + [1 << t]
        n += 1; added += 1
    return up, added


def distributive_Q(up):
    """Return (is_distributive, Q_indices, leq on Q) for abstract poset given by up-masks."""
    n = len(up)
    down = [0] * n
    for i in range(n):
        for j in g.bits(up[i]):
            down[j] |= 1 << i
    lc = []
    for x in range(n):
        d = down[x] & ~(1 << x)
        lc.append([y for y in g.bits(d) if not (up[y] & d & ~(1 << y))])
    order = sorted(range(n), key=lambda x: g.popcount(down[x]))
    r = [0] * n
    for x in order:
        r[x] = 1 + max([r[y] for y in lc[x]], default=0)
    graded = all(r[x] == r[y] + 1 for x in range(n) for y in lc[x])
    mins = [x for x in range(n) if down[x] == 1 << x]
    maxs = [x for x in range(n) if up[x] == 1 << x]
    if not graded or len(mins) != 1 or len(maxs) != 1:
        return False, None, None
    # lattice check: unique minimal upper bound for each pair
    for x in range(n):
        for y in range(x + 1, n):
            ub = up[x] & up[y]
            if sum(1 for z in g.bits(ub) if not (down[z] & ub & ~(1 << z))) != 1:
                return False, None, None
    ji = [x for x in range(n) if len(lc[x]) == 1]
    if max(r) - 1 != len(ji):
        return False, None, None
    return True, ji, (lambda a, b: (up[ji[a]] >> ji[b]) & 1 == 1)


def side_count(P, S, mode="float", max_M=400, max_cells=1.2e9, threads=16, log=None, fallback_limit=130):
    S = list(S)
    t = time.time()
    if not S:
        return {"value": 1, "method": "empty", "sec": 0}
    up, added = augment(abstract_from(P, S))
    ok, ji, leq = distributive_Q(up)
    if ok:
        n = len(ji)
        plans = dlat.best_plans(n, leq, max_M=max_M, max_cells=max_cells, top=1)
        if plans:
            c, mr, nM, Qa, pl = plans[0]
            val = dlat.count_float(pl, threads) if mode == "float" else dlat.count(pl, threads, log)
            return {"value": val - added, "method": f"dlat-{mode}(+{added})", "Qsize": n, "M": nM, "maxrank": mr,
                    "cells": c, "sec": round(time.time() - t, 2)}
    if len(S) <= fallback_limit:
        try:
            v = g.count_antichains_bitset(P, S, memo_cap=3_000_000)
            return {"value": float(v) if mode == "float" else v, "method": "bitset", "sec": round(time.time() - t, 2)}
        except g.MemoCap:
            pass
    return {"value": None, "method": "uncounted", "distributive": ok, "n": len(S), "sec": round(time.time() - t, 2)}
