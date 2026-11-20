#!/usr/bin/env python3
"""Driver for bin/cmp_mitm (compressed MITM producer).

count_region(S, criterion) -> exact |A(S)| : abstract region -> J(Q) -> best split by compressed cost -> CRT.
Plan choice: minimise compressed MITM memory subject to compressed stream <= stream_cap (or the reverse).
Memory is measured with /usr/bin/time -l when run via run_timed().
"""
import sys, math, subprocess, collections, json, time, resource
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "harvest")); sys.path.insert(0, str(HERE))
import glbcore as g, side_count2 as s2, dlat, lattice_antichains as la
import mitm, memgate
from anatomy import plan_stats, mitm_cost
BIN = ROOT / "bin/cmp_mitm"
PP = g.poset()


def _sha(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def plans(S, maxM=4000, capJB=400):
    up, added = s2.augment(s2.abstract_from(PP, S)); ok, ji, lq0 = s2.distributive_Q(up)
    assert ok, "not distributive"
    n = len(ji); out = []
    for dual in (False, True):
        lq = (lambda a, b: lq0(b, a)) if dual else lq0
        for Qa in dlat.downsets_of(n, lq):
            if not Qa or len(Qa) == n: continue
            try: pl = dlat.plan(n, lq, Qa, capJB=capJB, capM=maxM)
            except (AssertionError, dlat.TooMany): continue
            t = plan_stats(pl); sc, mc, rs = mitm_cost(t, "comp")
            out.append(dict(pl=pl, dual=dual, stream=sc, mem=mc, rs=rs, nM=t["nM"], K=t["K"], comp=t["comp"]))
    return added, len(ji), out


def choose(cands, key="mem", stream_cap=3e10, mem_cap=3e9, exclude=None):
    c = [x for x in cands if x["stream"] <= stream_cap and x["mem"] <= mem_cap
         and (exclude is None or (x["dual"], tuple(x["pl"]["Qa"])) != exclude)]
    if not c: return None
    return min(c, key=lambda x: (x[key], x["stream"] + x["mem"]))


def primes_for(bound, bits):
    ps, prod, n = [], 1, (1 << bits) - 1
    while prod <= 2 * bound:
        if mitm.is_prime(n): ps.append(n); prod *= n
        n -= 2
    return ps


def projected_peak_bytes(c, w32=False):
    """forward pass: max |G_r|+|G_{r+1}| below the stream; backward: Ghat_{rs-1} kept + max |B_r|+|B_{r-1}| above.
    Calibrated on N7 776 (2.43e9 entries u64 -> 18.17 GiB measured)."""
    t, rs = [int(x) for x in c["comp"]], c["rs"]
    fwd = max([t[r] + t[r + 1] for r in range(rs - 1)] or [t[0]])
    bwd = (t[rs - 1] if rs >= 1 else 0) + max([t[r] + t[r - 1] for r in range(rs + 2, len(t))] or [t[-1]])
    return (4 if w32 else 8) * max(fwd, bwd) * 1.02 + 0.3 * 2 ** 30


def count_plan(c, threads=16, w32=False, primes=None, log=None):
    pl = c["pl"]
    lines, rs = mitm.lines_for(pl, c["rs"])
    bound = len(pl["M"]) ** len(pl["JA"])
    ps = primes or primes_for(bound, 31 if w32 else 61)
    res, mx = [], 0
    for p in ps:
        lines[0] = str(p)
        t = time.time()
        args = ["/usr/bin/time", "-l", str(BIN), str(threads)] + (["w32"] if w32 else [])
        with memgate.reserve(projected_peak_bytes(c, w32), f"cmp_mitm |M|={len(pl['M'])}", log):
            r = subprocess.run(args, input="\n".join(lines) + "\n", capture_output=True, text=True, check=True)
        rss = int([l for l in r.stderr.splitlines() if "maximum resident set size" in l][0].split()[0])
        res.append(int(r.stdout.split()[0])); mx = max(mx, rss)
        if log: print(f"   p={p} residue={res[-1]} [{time.time()-t:.1f}s, maxRSS {rss/2**30:.2f} GiB]", file=log, flush=True)
    x, Mod = la._crt(res, ps)
    assert Mod > 2 * bound
    return x, dict(primes=ps, residues=res, rs=rs, bound_log2=math.log2(bound), modulus_log2=math.log2(Mod), maxrss=mx)


def count_region(S, key="mem", w32=False, threads=16, log=sys.stdout, exclude=None, **kw):
    added, nji, cands = plans(S)
    c = choose(cands, key=key, exclude=exclude, **kw)
    assert c is not None, "no plan within caps"
    if log: print(f"  |S|={len(S)} JI={nji} plan dual={c['dual']} |Qa|={len(c['pl']['Qa'])} |M|={c['nM']} K={c['K']} "
                  f"comp stream={c['stream']:.3g} mem={c['mem']:.3g} rs={c['rs']}", file=log, flush=True)
    x, info = count_plan(c, threads=threads, w32=w32, log=log)
    info.update(dual=c["dual"], Qa=c["pl"]["Qa"], nM=c["nM"], K=c["K"], stream=c["stream"], mem=c["mem"], JI=nji, added=added,
                ranks_S=[int(z) for z in c["comp"]], w_eff=round(math.log(max(c["comp"]), 171), 3), binary_sha256=_sha(BIN))
    return x - added, info
