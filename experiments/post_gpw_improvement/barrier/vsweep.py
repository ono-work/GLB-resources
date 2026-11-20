#!/usr/bin/env python3
"""Driver for bin/vsweep (independent low-memory verifier).  Chooses a split minimising the full-sweep peak
max_r(|T_r|+|T_{r+1}|), excluding the producer's split; moduli 2^32 and 31-bit primes; CRT."""
import sys, math, subprocess, time
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "harvest")); sys.path.insert(0, str(HERE))
import mitm, cmp, memgate
BIN = ROOT / "bin/vsweep"


def sweep_peak(c):
    t = c["comp"]; return max(t[r] + t[r + 1] for r in range(len(t) - 1)) if len(t) > 1 else t[0]


def sliced_peak(c, cap):
    """peak entries of bin/vsweep with slicing of every rank whose table exceeds cap"""
    from anatomy import plan_stats
    t = plan_stats(c["pl"]); comp = t["comp"]; R = len(comp)
    sl = [1 <= r < R - 1 and comp[r] > cap for r in range(R)]
    if any(sl[r] and sl[r + 1] for r in range(R - 1)): return float("inf")
    pk = 0
    for r in range(R - 1):
        cur = comp[r] // max(t["dom"][i] for i in t["ranks"][r]) + comp[r - 1] if sl[r] else comp[r]
        pk = max(pk, cur if sl[r + 1] else cur + comp[r + 1])
    return pk


def lines(pl):
    JA, M, allowed = pl["JA"], pl["M"], pl["allowed"]
    pc = lambda x: bin(x).count("1"); sub = lambda a, b: a & ~b == 0
    R = max(pc(x) for x in JA) + 1
    byr = [[i for i, x in enumerate(JA) if pc(x) == r] for r in range(R)]
    pos = {i: j for r in range(R) for j, i in enumerate(byr[r])}
    out = [None, str(len(M)), " ".join(map(str, M)), str(R), " ".join(str(len(b)) for b in byr)]
    for r in range(R - 1):
        for i in byr[r]:
            u = [pos[j] for j in byr[r + 1] if sub(JA[i], JA[j])]
            out.append(" ".join(map(str, [len(u)] + u)))
    for r in range(R):
        out.append(" ".join(str(allowed[i]) for i in byr[r]))
    return out


def moduli(bound):
    ms, prod, n = [0], 1 << 32, (1 << 31) - 1
    while prod <= 2 * bound:
        if mitm.is_prime(n): ms.append(n); prod *= n
        n -= 2
    return ms


def crt(res, ms):
    X, Mod = 0, 1
    for r, m in zip(res, ms):
        m = m or (1 << 32)
        t = ((r - X) * pow(Mod, -1, m)) % m
        X += Mod * t; Mod *= m
    return X, Mod


def verify_region(S, exclude=None, threads=16, peak_cap=4e9, slice_cap=None, log=sys.stdout, only_dual=None):
    """slice_cap: tables above this many entries are sliced (None: no slicing)."""
    added, nji, cands = cmp.plans(S)
    pk = (lambda x: sliced_peak(x, slice_cap)) if slice_cap else sweep_peak
    c = [x for x in cands if (exclude is None or (x["dual"], tuple(x["pl"]["Qa"])) != exclude)
         and (only_dual is None or x["dual"] == only_dual) and pk(x) <= peak_cap]
    assert c, "no sweep plan within cap"
    c = min(c, key=lambda x: (pk(x), sum(x["comp"])))
    pl = c["pl"]; L = lines(pl); bound = len(pl["M"]) ** len(pl["JA"]); ms = moduli(bound)
    if log: print(f"  vsweep plan dual={c['dual']} |Qa|={len(pl['Qa'])} |M|={c['nM']} K={c['K']} peak={pk(c):.3g} "
                  f"({4*pk(c)/2**30:.2f} GiB) slice_cap={slice_cap} moduli={len(ms)}", file=log, flush=True)
    res, rss = [], 0
    for q in ms:
        L[0] = str(q); t = time.time()
        with memgate.reserve(4 * pk(c) * 1.02 + 0.3 * 2 ** 30, f"vsweep |M|={c['nM']}", log):
            r = subprocess.run(["/usr/bin/time", "-l", str(BIN), str(threads)] + ([str(int(slice_cap))] if slice_cap else []), input="\n".join(L) + "\n",
                               capture_output=True, text=True, check=True)
        rr = int([l for l in r.stderr.splitlines() if "maximum resident set size" in l][0].split()[0]); rss = max(rss, rr)
        res.append(int(r.stdout.split()[0]))
        if log: print(f"   q={q or '2^32'} residue={res[-1]} [{time.time()-t:.1f}s, maxRSS {rr/2**30:.2f} GiB]", file=log, flush=True)
    X, Mod = crt(res, ms); assert Mod > 2 * bound
    return X - added, dict(dual=c["dual"], Qa=pl["Qa"], nM=c["nM"], K=c["K"], peak_entries=pk(c), slice_cap=slice_cap, moduli=ms,
                           residues=res, maxrss=rss, modulus_log2=math.log2(Mod), bound_log2=math.log2(bound),
                           binary_sha256=__import__('hashlib').sha256(BIN.read_bytes()).hexdigest())
