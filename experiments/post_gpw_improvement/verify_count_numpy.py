#!/usr/bin/env python3
"""Independent re-computation of #antitone maps S -> M (S graded distributive lattice,
M union-closed family) modulo small primes p < 2^26, using numpy float64 tensordot
(exact: all intermediate values < 171*p < 2^53).  Different code path, language and
primes from rank_transfer.cpp.  Used only to cross-check residues of the CRT value."""
from __future__ import annotations
import sys, time
import numpy as np

SMALL_PRIMES = (67108859, 67108837, 67108819)  # < 2^26


def residue(S, M, p, chunk=4):
    pc = lambda x: bin(x).count("1")
    R = max(pc(x) for x in S) + 1
    byr = [[x for x in S if pc(x) == r] for r in range(R)]
    nM = len(M)
    idx = {m: i for i, m in enumerate(M)}
    JT = np.array([[idx[a | b] for b in M] for a in M], dtype=np.int64)
    Z = np.array([[1.0 if (M[v] & ~M[w]) == 0 else 0.0 for w in range(nM)] for v in range(nM)])  # Z[v,w]=[w ⊇ v]
    sub = lambda a, b: a & ~b == 0
    G = np.ones((nM,) * len(byr[0]), dtype=np.float64)
    for r in range(R - 1):
        k = len(byr[r])
        for c in range(k):
            G = np.moveaxis(np.tensordot(Z, G, axes=([1], [c])), 0, c)
            np.fmod(G, p, out=G)
        k2 = len(byr[r + 1])
        ups = [[j for j, b in enumerate(byr[r + 1]) if sub(a, b)] for a in byr[r]]
        flatG = G.reshape(-1)  # C order: flat = sum_a J_a * nM^(k-1-a)
        strides = [nM ** (k - 1 - a) for a in range(k)]
        H = np.empty((nM,) * k2, dtype=np.float64)
        rest = (nM,) * (k2 - 1)
        base = np.indices(rest, dtype=np.int64) if k2 > 1 else None
        for first in range(nM):
            us = [np.full(rest, first, dtype=np.int64)] + ([base[i] for i in range(k2 - 1)] if k2 > 1 else [])
            flat = np.zeros(rest, dtype=np.int64)
            for a in range(k):
                j = us[ups[a][0]]
                for b in ups[a][1:]:
                    j = JT[j, us[b]]
                flat += j * strides[a]
            H[first] = flatG[flat]
        G = H
    return int(sum(int(x) for x in np.fmod(G, p).reshape(-1)) % p)


def check(S, M, value):
    out = []
    for p in SMALL_PRIMES:
        t = time.time()
        r = residue(S, M, p)
        out.append({"p": p, "residue": r, "expected": value % p, "ok": r == value % p, "sec": round(time.time() - t, 1)})
        print(out[-1], flush=True)
    return out


if __name__ == "__main__":
    import random
    import lattice_antichains as la  # producer-side slow DP, used only as the self-test oracle
    def rand_poset(n, p, rng):
        rel = [[i == j for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < p: rel[i][j] = True
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if rel[i][k] and rel[k][j]: rel[i][j] = True
        return rel
    rng = random.Random(5)
    for t in range(30):
        n1, n2 = rng.randint(1, 5), rng.randint(1, 4)
        r1, r2 = rand_poset(n1, 0.5, rng), rand_poset(n2, 0.5, rng)
        L1 = la.ideals_of(n1, lambda i, j: r1[i][j]); L2 = la.ideals_of(n2, lambda i, j: r2[i][j])
        sub = lambda a, b: a & ~b == 0
        JL2 = la.ideals_of(len(L2), lambda i, j: sub(L2[i], L2[j]))
        exact = la.count_antitone_maps(len(L1), lambda i, j: sub(L1[i], L1[j]), JL2)[0]
        assert residue(L1, JL2, SMALL_PRIMES[0]) == exact % SMALL_PRIMES[0], t
    print("numpy verifier self-test passed (30 random instances)")
