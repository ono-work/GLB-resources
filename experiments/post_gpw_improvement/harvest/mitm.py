"""Wrapper: exact |A(S)| for a distributive region via dlat split + meet-in-the-middle rank transfer
(bin/rank_transfer_mitm), CRT over enough 61-bit primes for the a-priori bound |M|^|JA|."""
import sys, subprocess, collections, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import glbcore as g, side_count2 as s2, dlat, lattice_antichains as la
BIN = Path(__file__).resolve().parents[1] / "bin" / "rank_transfer_mitm"
def is_prime(n):
    if n < 2: return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0: return n == q
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True
def primes61(k):
    out, n = [], (1 << 61) - 1
    while len(out) < k:
        if is_prime(n): out.append(n)
        n -= 2
    return out
def lines_for(pl, rstar):
    JA, M, allowed = pl["JA"], pl["M"], pl["allowed"]
    pc = lambda x: bin(x).count("1")
    R = max(pc(x) for x in JA) + 1
    byr = [[i for i, x in enumerate(JA) if pc(x) == r] for r in range(R)]
    pos = {i: j for r in range(R) for j, i in enumerate(byr[r])}
    Midx = {m: i for i, m in enumerate(M)}
    lines = [None, str(len(M)), " ".join(map(str, M)), str(R), " ".join(str(len(b)) for b in byr)]
    sub = lambda a, b: a & ~b == 0
    for r in range(R - 1):
        for i in byr[r]:
            ups = [pos[j] for j in byr[r + 1] if sub(JA[i], JA[j])]
            lines.append(" ".join(map(str, [len(ups)] + ups)))
    for r in range(R):
        lines.append(" ".join(str(Midx[allowed[i]]) for i in byr[r]))
    if rstar is None: rstar = max(range(R), key=lambda r: len(byr[r]))
    lines.append(str(rstar))
    return lines, rstar
def count_plan(pl, rstar=None, threads=16, log=None):
    lines, rstar = lines_for(pl, rstar)
    bound = len(pl["M"]) ** len(pl["JA"])
    k = 1
    while (((1 << 61) - 1) ** k) // 2 ** k < bound * 2: k += 1   # crude: product of k primes > 2*bound
    primes = primes61(k + 1)
    res = []
    for p in primes:
        lines[0] = str(p)
        out = subprocess.run([str(BIN), str(threads)], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True)
        res.append(int(out.stdout.split()[0]))
        if log:
            with open(log, "a") as f: f.write(f"Qa={pl['Qa']} |M|={len(pl['M'])} rstar={rstar} p={p} residue={res[-1]}\n")
    x, Mod = la._crt(res, primes)
    assert bound < Mod
    return x, {"primes": primes, "residues": res, "bound_log2": math.log2(bound), "rstar": rstar}
def best_mitm_plan(n, lq, maxM=2000, mem_cap=1.5e9, stream_cap=3e11):
    best = None
    for dual in (False, True):
        lqd = (lambda a, b: lq(b, a)) if dual else lq
        for Qa in dlat.downsets_of(n, lqd):
            if not Qa or len(Qa) == n: continue
            try: pl = dlat.plan(n, lqd, Qa, capJB=300, capM=maxM)
            except (AssertionError, dlat.TooMany): continue
            K = sorted(collections.Counter(bin(x).count('1') for x in pl['JA']).values(), reverse=True)
            nM = len(pl['M']); stream = nM ** K[0]; mem = nM ** (K[1] if len(K) > 1 else 0)
            if mem <= mem_cap and stream <= stream_cap and (best is None or (stream, mem) < best[:2]):
                best = (stream, mem, pl, dual)
    return best
def exact_A_mitm(PP, S, threads=16, log=None):
    """exact |A(S)| for S a distributive region (formal bottom/top adjoined if needed)."""
    up, added = s2.augment(s2.abstract_from(PP, S))
    ok, ji, lq = s2.distributive_Q(up)
    assert ok, "region is not a distributive lattice"
    b = best_mitm_plan(len(ji), lq)
    assert b is not None, "no feasible meet-in-the-middle plan"
    x, info = count_plan(b[2], threads=threads, log=log)
    info.update(stream=b[0], mem=b[1], dual=b[3], Qsize=len(ji), added=added)
    return x - added, info
