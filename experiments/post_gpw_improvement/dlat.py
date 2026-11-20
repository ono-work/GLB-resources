#!/usr/bin/env python3
"""Exact |A(S)| for a finite distributive lattice S (given abstractly by its poset Q of
join-irreducibles, S ~= J(Q)).

Split Q = Qa (a down-set) + Qb.  Then
    J(Q) ~= {(Ia,Ib) in J(Qa) x J(Qb) : down(Ib) & Qa  subseteq Ia}
with componentwise order, and ideals of J(Q) <-> maps f: J(Qa) -> J(J(Qb)) with
    f(Ia) subseteq allowed(Ia) := {Ib : down(Ib)&Qa subseteq Ia}      (a down-set of J(Qb))
    f(Ia') & allowed(Ia) subseteq f(Ia)    for every cover Ia < Ia' in J(Qa).
(Covers of J(Q) add one element either to Ia or to Ib; the first kind gives the second
constraint, the second kind says f(Ia) is down-closed, i.e. f(Ia) in J(J(Qb)).)
Counted by bin/rank_transfer_gen modulo four 61-bit primes + CRT with an a-priori bound.
"""
from __future__ import annotations

import itertools
import subprocess
from pathlib import Path

import lattice_antichains as la

BIN = Path(__file__).resolve().parent / "bin" / "rank_transfer_gen"
PR4 = la._PR4


class TooMany(Exception):
    pass


def ideals_masks(n, below, cap=None):
    """ideals of poset on range(n) where below[i] = mask of strict lower elements."""
    out = []
    order = sorted(range(n), key=lambda i: bin(below[i]).count("1"))
    def rec(k, mask):
        if k == n:
            out.append(mask)
            if cap is not None and len(out) > cap:
                raise TooMany()
            return
        i = order[k]
        rec(k + 1, mask)
        if below[i] & ~mask == 0:
            rec(k + 1, mask | (1 << i))
    rec(0, 0)
    return sorted(out)


def plan(n, leq, Qa, capJB=None, capM=None):
    """Return the abstract data for a split; Qa must be a down-set (list of indices of Q)."""
    Qa = sorted(Qa); Qb = [q for q in range(n) if q not in Qa]
    sa = set(Qa)
    assert all(not (leq(x, y) and y in sa and x not in sa) for x in range(n) for y in range(n)), "Qa not a down-set"
    ia = {q: i for i, q in enumerate(Qa)}; ib = {q: i for i, q in enumerate(Qb)}
    belowA = [sum(1 << ia[x] for x in Qa if x != q and leq(x, q)) for q in Qa]
    belowB = [sum(1 << ib[x] for x in Qb if x != q and leq(x, q)) for q in Qb]
    JA = ideals_masks(len(Qa), belowA)
    JB = ideals_masks(len(Qb), belowB, capJB)
    # D(Ib) = down(Ib) & Qa as mask over Qa
    downA = {q: sum(1 << ia[x] for x in Qa if leq(x, q)) for q in Qb}
    D = []
    for Ib in JB:
        m = 0
        for q in Qb:
            if Ib >> ib[q] & 1:
                m |= downA[q]
        D.append(m)
    subJB = lambda i, j: JB[i] & ~JB[j] == 0
    M = ideals_masks(len(JB), [sum(1 << j for j in range(len(JB)) if j != i and subJB(j, i)) for i in range(len(JB))], capM)
    allowed = [sum(1 << j for j in range(len(JB)) if D[j] & ~Ia == 0) for Ia in JA]
    Mset = set(M)
    assert all(a in Mset for a in allowed)
    return {"Qa": Qa, "Qb": Qb, "JA": JA, "JB": JB, "M": M, "allowed": allowed}


def cost(pl):
    pc = lambda x: bin(x).count("1")
    from collections import Counter
    mr = max(Counter(pc(x) for x in pl["JA"]).values())
    return len(pl["M"]) ** mr, mr


def count(pl, threads=16, log=None, primes=PR4):
    JA, M, allowed = pl["JA"], pl["M"], pl["allowed"]
    pc = lambda x: bin(x).count("1")
    R = max(pc(x) for x in JA) + 1
    byr = [[i for i, x in enumerate(JA) if pc(x) == r] for r in range(R)]
    pos = {}
    for r in range(R):
        for j, i in enumerate(byr[r]):
            pos[i] = j
    Midx = {m: i for i, m in enumerate(M)}
    assert len(M) < 1 << 16 and all(x < 1 << 64 for x in M), "M must be <=64 bits per value"
    lines = [None, str(len(M)), " ".join(map(str, M)), str(R), " ".join(str(len(b)) for b in byr)]
    sub = lambda a, b: a & ~b == 0
    for r in range(R - 1):
        for i in byr[r]:
            ups = [pos[j] for j in byr[r + 1] if sub(JA[i], JA[j])]
            lines.append(" ".join(map(str, [len(ups)] + ups)))
    for r in range(R):
        lines.append(" ".join(str(Midx[allowed[i]]) for i in byr[r]))
    res = []
    for p in primes:
        lines[0] = str(p)
        out = subprocess.run([str(BIN), str(threads)], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True)
        res.append(int(out.stdout.split()[0]))
        if log:
            with open(log, "a") as f:
                f.write(f"Qa={pl['Qa']} |M|={len(M)} p={p} residue={res[-1]}\n")
    x, Mod = la._crt(res, primes)
    assert len(M) ** len(JA) < Mod, "a-priori bound exceeds CRT modulus"
    return x


def downsets_of(n, leq, max_count=20000):
    below = [sum(1 << x for x in range(n) if x != q and leq(x, q)) for q in range(n)]
    out = ideals_masks(n, below)
    return [[q for q in range(n) if m >> q & 1] for m in out]


def best_plans(n, leq, max_M=400, max_cells=2.5e9, top=3):
    """Enumerate down-set splits; keep feasible ones sorted by table size."""
    cands = []
    for Qa in downsets_of(n, leq):
        if not Qa or len(Qa) == n:
            continue
        Qb = [q for q in range(n) if q not in Qa]
        # quick filter on |J(J(Qb))| via size of Qb (exact computed below)
        if len(Qb) > 14:
            continue
        try:
            pl = plan(n, leq, Qa, capJB=60, capM=max_M)
        except (AssertionError, TooMany):
            continue
        if len(pl["M"]) > max_M:
            continue
        c, mr = cost(pl)
        if c <= max_cells:
            cands.append((c, mr, len(pl["M"]), Qa, pl))
    cands.sort(key=lambda t: t[0])
    return cands[:top]


FBIN = Path(__file__).resolve().parent / "bin" / "rank_transfer_float"


def count_float(pl, threads=16):
    """Approximate |A| (double precision) for screening only - NOT for certification."""
    JA, M, allowed = pl["JA"], pl["M"], pl["allowed"]
    pc = lambda x: bin(x).count("1")
    R = max(pc(x) for x in JA) + 1
    byr = [[i for i, x in enumerate(JA) if pc(x) == r] for r in range(R)]
    pos = {i: j for r in range(R) for j, i in enumerate(byr[r])}
    Midx = {m: i for i, m in enumerate(M)}
    lines = ["0", str(len(M)), " ".join(map(str, M)), str(R), " ".join(str(len(b)) for b in byr)]
    sub = lambda a, b: a & ~b == 0
    for r in range(R - 1):
        for i in byr[r]:
            ups = [pos[j] for j in byr[r + 1] if sub(JA[i], JA[j])]
            lines.append(" ".join(map(str, [len(ups)] + ups)))
    for r in range(R):
        lines.append(" ".join(str(Midx[allowed[i]]) for i in byr[r]))
    out = subprocess.run([str(FBIN), str(threads)], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True)
    return float(out.stdout.split()[0])
