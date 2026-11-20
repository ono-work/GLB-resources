#!/usr/bin/env python3
"""Self-contained core for post-GPW experiments.

Loads the frozen G_3 poset from the public artifact (read-only) and provides
kernel / canonical-region helpers that mirror src/glb_lower_bound.py and
src/local_components_g3.py:q_sets exactly.

Conventions (identical to the certified code):
  leq(i,j)  <=>  game_i <= game_j         (row i of leq_rows.hex, bit j)
  Q_L^+(T_L,T_R) = { g notin T_L, g incomparable to all of T_L,
                     every right option y of g has some t in T_R with t <= y }
  Q_R^+(T_L,T_R) = { g notin T_R, g incomparable to all of T_R,
                     every left option x of g has some t in T_L with x <= t }
For an admissible kernel, every (T_L u A, T_R u B) with A in A(Q_L^+),
B in A(Q_R^+) is a safe antichain pair, and distinct (A,B) give distinct
canonical forms; hence the canonical family has size |A(Q_L^+)|*|A(Q_R^+)|.
"""
from __future__ import annotations

import csv
import hashlib
import json
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXPORT = REPO / "data/gub/game_export"
CACHE = REPO / "experiments/lower_bound/local_components/g3_universe_cache.json"


def sha_file(p) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha_normalized(p) -> str:
    """SHA-256 of the file with CRLF restored (the original GUB export used CRLF;
    the public git checkout normalises to LF)."""
    data = Path(p).read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return hashlib.sha256(data).hexdigest()


class Poset:
    def __init__(self):
        with (EXPORT / "games.csv").open() as f:
            orig = [int(r["orig_gid"]) for r in csv.DictReader(f)]
        rows = [int(x, 16) for x in (EXPORT / "leq_rows.hex").read_text().split() if x]
        c = json.loads(CACHE.read_text())
        assert c["orig_gids"] == orig
        self.n = len(rows)
        self.up = rows  # up[i] = {j : i <= j}
        down = [0] * self.n
        for i, r in enumerate(rows):
            m = r
            while m:
                b = m & -m
                down[b.bit_length() - 1] |= 1 << i
                m ^= b
        self.down = down  # down[j] = {i : i <= j}
        self.comp = [self.up[i] | self.down[i] for i in range(self.n)]
        self.left = [tuple(x) for x in c["left"]]
        self.right = [tuple(x) for x in c["right"]]
        self.negation = list(c["negation"])
        self.birthdays = list(c["birthdays"])
        self.input_hashes = {
            "games.csv": sha_normalized(EXPORT / "games.csv"),
            "leq_rows.hex": sha_normalized(EXPORT / "leq_rows.hex"),
            "metadata.json": sha_normalized(EXPORT / "metadata.json"),
        }

    def leq(self, i, j):
        return (self.up[i] >> j) & 1 == 1

    def comparable(self, i, j):
        return (self.comp[i] >> j) & 1 == 1

    def is_antichain(self, xs):
        xs = list(xs)
        return all(not self.comparable(xs[a], xs[b]) for a in range(len(xs)) for b in range(a + 1, len(xs)))

    # ---- safety -----------------------------------------------------------
    def hit_left(self, g, TRmask):
        """every right option y of g has some t in T_R with t <= y."""
        return all(self.down[y] & TRmask for y in self.right[g])

    def hit_right(self, g, TLmask):
        """every left option x of g has some t in T_L with x <= t."""
        return all(self.up[x] & TLmask for x in self.left[g])

    def admissible(self, TL, TR):
        tl = sum(1 << t for t in TL)
        tr = sum(1 << t for t in TR)
        return (self.is_antichain(TL) and self.is_antichain(TR)
                and all(self.hit_left(t, tr) for t in TL)
                and all(self.hit_right(t, tl) for t in TR))

    def q_sets(self, TL, TR):
        tl = sum(1 << t for t in TL)
        tr = sum(1 << t for t in TR)
        ql = tuple(g for g in range(self.n) if not (tl >> g) & 1 and not self.comp[g] & tl
                   and self.hit_left(g, tr))
        qr = tuple(g for g in range(self.n) if not (tr >> g) & 1 and not self.comp[g] & tr
                   and self.hit_right(g, tl))
        return ql, qr

    def check_safe_pair(self, L, R):
        """Direct check of Definition 2 (no reversible options) + antichains."""
        Lm = sum(1 << x for x in L)
        Rm = sum(1 << x for x in R)
        if not self.is_antichain(L) or not self.is_antichain(R):
            return False
        for a in L:
            for y in self.right[a]:
                if not self.down[y] & Rm:
                    return False
        for b in R:
            for x in self.left[b]:
                if not self.up[x] & Lm:
                    return False
        return True


@lru_cache(maxsize=1)
def poset() -> Poset:
    return Poset()


def bits(m):
    while m:
        b = m & -m
        yield b.bit_length() - 1
        m ^= b


def popcount(m):
    return bin(m).count("1")


class MemoCap(Exception):
    pass


def count_antichains_bitset(P, S, memo_cap=None):
    """|A(S)| by include/exclude recursion on the comparability graph with connected-component
    splitting and memoisation (pivot = lowest index; independent of src/hit_antichain_counter)."""
    import sys
    sys.setrecursionlimit(100000)
    Sm = sum(1 << x for x in S)
    adj = {x: P.comp[x] & Sm & ~(1 << x) for x in S}
    memo = {}

    def comps(mask):
        out = []
        while mask:
            b = mask & -mask
            seen = b; fr = b
            while fr:
                nf = 0
                for v in bits(fr):
                    nf |= adj[v]
                nf &= mask & ~seen
                seen |= nf; fr = nf
            out.append(seen); mask &= ~seen
        return out

    def rec(mask):
        if mask == 0:
            return 1
        r = memo.get(mask)
        if r is not None:
            return r
        cs = comps(mask)
        if len(cs) > 1:
            r = 1
            for c in cs:
                r *= rec(c)
        else:
            v = (mask & -mask).bit_length() - 1
            r = rec(mask & ~(1 << v)) + rec(mask & ~(1 << v) & ~adj[v])
        memo[mask] = r
        if memo_cap is not None and len(memo) > memo_cap:
            raise MemoCap(len(memo))
        return r
    return rec(Sm)


def count_antichains_cpp(P, S, cap=400_000_000, big=False):
    """C++ include/exclude counter (bin/ie_count); exact; returns (count, memo_entries)."""
    import subprocess
    from pathlib import Path
    S = list(S); pos = {x: i for i, x in enumerate(S)}; m = sum(1 << x for x in S)
    lines = [str(len(S))]
    for x in S:
        nb = [pos[y] for y in bits(P.comp[x] & m & ~(1 << x))]
        lines.append(" ".join(map(str, [len(nb)] + nb)))
    exe = "ie_count_big" if (big or len(S) > 512) else "ie_count"
    out = subprocess.run([str(Path(__file__).resolve().parent / "bin" / exe), str(cap)],
                         input="\n".join(lines) + "\n", capture_output=True, text=True, check=True)
    c, k = out.stdout.split()
    return int(c), int(k)
