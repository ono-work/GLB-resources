#!/usr/bin/env python3
"""Exact (CRT) re-derivation of every region count used by certificate_v5.json.

For each region S listed in the certificate:
  * |S| < 160: exact count with the archived GPW counter (src/hit_antichain_counter.py).
  * otherwise: verify_v5.product_check proves S ~= J1 x J2 (order-isomorphism on all pairs, J1, J2
    computed here from the join-irreducibles of S).  Then
        |A(S)| = #down-sets of J1 x J2 = #antitone maps f: J1 -> M,  M = down-sets of J2,
    so 0 <= |A(S)| <= U := |M|^|J1|  (a-priori bound, recorded).
    The count is recomputed modulo k distinct primes p_i < 2^45 with the independent numpy/BLAS
    transfer (verify_count_numpy.residue; float64 exact because every intermediate sum is
    <= |M|*(p-1) < 2^53, asserted below), k minimal with prod p_i > U.  CRT gives the unique
    integer in [0, prod p_i), which must equal the certificate's exact value.
  Residues are cached in results/crt_v5_residues.json (resumable; the cache is only a record:
  on the final run every residue is recomputed unless --use-cache is given).
Finally the bound is re-aggregated exactly from the histogram e(D) (bin/hist_count, as in
verify_v5) and the CRT-reconstructed counts.  Writes certificates/verify_v5_crt_record.json.
Usage: .venv/bin/python verify_v5_crt.py [--use-cache]
"""
import json, sys, time, math, hashlib, resource
from pathlib import Path
import verify_v2 as v
import verify_v5 as w
import verify_count_numpy as vn
import hit_antichain_counter as hc

HERE = Path(__file__).resolve().parent
CACHE = HERE / "results/crt_v5_residues.json"
PBITS = 45


def is_prime(n):  # deterministic Miller-Rabin for n < 3.3e24
    if n < 2: return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
    for q in small:
        if n % q == 0: return n == q
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True


def primes_below(B, k):
    out, n = [], B - 1
    while len(out) < k:
        if is_prime(n): out.append(n)
        n -= 1
    return out


PRIMES = primes_below(1 << PBITS, 8)


def crt(res, ps):
    x, m = 0, 1
    for r, p in zip(res, ps):
        t = ((r - x) * pow(m, -1, p)) % p
        x += m * t; m *= p
    return x, m


def main(use_cache=False):
    t0 = time.time()
    C = json.loads((HERE / "certificate_v5.json").read_text())
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    down = [0] * v.N
    for i in range(v.N):
        m = v.rows[i]
        while m:
            b = m & -m; down[b.bit_length() - 1] |= 1 << i; m ^= b
    adj = tuple((v.rows[i] | down[i]) & ~(1 << i) for i in range(v.N))
    recs = {}
    for hsh, reg in sorted(C["regions"].items(), key=lambda kv: len(kv[1]["elements"])):
        S = reg["elements"]; A = int(reg["count"])
        v.check(w.h(S) == hsh, "region hash")
        if len(S) < 160:
            cnt, _ = hc.count_independent_sets(sum(1 << x for x in S), adj, "max_degree")
            v.check(cnt == A, f"region {len(S)} exact")
            recs[hsh] = {"size": len(S), "method": "archived exact counter", "value": str(cnt), "ok": cnt == A}
            print(f"|S|={len(S)}: archived exact {cnt} ok={cnt == A}", flush=True)
            continue
        pc = w.product_check(S)
        v.check(pc is not None, f"region {len(S)} product structure")
        J1, J2 = sorted(pc[0]), sorted(pc[1])
        M = w.jmask(J2)
        assert len(M) * (PRIMES[0] - 1) < 2 ** 53, "float64 exactness"
        U = len(M) ** len(J1)
        ps, prod = [], 1
        for p in PRIMES:
            if prod > U: break
            ps.append(p); prod *= p
        v.check(prod > U, "enough primes")
        res = []
        for p in ps:
            key = f"{hsh}:{p}"
            if use_cache and key in cache:
                r = cache[key]["residue"]; sec = cache[key]["sec"]
            else:
                tt = time.time(); r = vn.residue(J1, M, p); sec = round(time.time() - tt, 1)
                cache[key] = {"size": len(S), "residue": r, "sec": sec}
                CACHE.write_text(json.dumps(cache, indent=1) + "\n")
            res.append(r)
            print(f"|S|={len(S)} ({len(J1)}x{len(J2)}, |M|={len(M)}): mod {p} = {r} [{sec}s]", flush=True)
        X, _ = crt(res, ps)
        v.check(X == A, f"CRT region {len(S)}: {X} != {A}")
        recs[hsh] = {"size": len(S), "method": "J1xJ2 + numpy transfer mod primes + CRT", "J1": len(J1), "J2": len(J2),
                     "M": len(M), "upper_bound": f"|M|^|J1| = {len(M)}^{len(J1)} = {U}", "upper_bound_log2": math.log2(U),
                     "primes": ps, "residues": res, "modulus_product": str(prod), "modulus_log2": math.log2(prod),
                     "reconstructed": str(X), "certificate_value": str(A), "ok": X == A}
        print(f"  CRT -> {X}  (U < 2^{math.log2(U):.1f} < prod p = 2^{math.log2(prod):.1f})  ok={X == A}", flush=True)
    # exact re-aggregation from histogram e(D) and reconstructed counts
    fams = []
    for f in C["families"]:
        TR, x0 = f["T_R"], f["x0"]
        H = w.histogram(f["H_L"], f["REQ"])
        tot = 0
        for r in f["rows"]:
            Dm = sum(1 << j for j, q in enumerate(f["REQ"]) if q in r["D"])
            c = int(recs[r["V_hash"]]["value" if "value" in recs[r["V_hash"]] else "reconstructed"])
            if "x0_sub_hash" in r:
                s = recs[r["x0_sub_hash"]]; c -= int(s["value" if "value" in s else "reconstructed"])
            tot += H[Dm] * c
        v.check(str(tot) == f["total"], f"family {TR} total")
        fams.append(tot)
    bound = 2 * sum(fams)
    v.check(str(bound) == C["new_lower_bound"], "bound")
    status = "AUDIT PASSED" if not v.errors else "AUDIT FAILED"
    sha = lambda p: hashlib.sha256((HERE / p).read_bytes()).hexdigest()
    out = {"status": status, "statement": "every region count of certificate_v5.json is exact (CRT with modulus "
           "product > a-priori bound, or direct exact count); bound re-aggregated exactly",
           "new_lower_bound": str(bound), "family_totals": {"G1": str(fams[0]), "G2": str(fams[1])}, "mirror_factor": 2,
           "regions": recs, "errors": v.errors, "runtime_s": round(time.time() - t0),
           "peak_rss_GB": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**30, 1),
           "sha256": {p: sha(p) for p in ("certificate_v5.json", "verify_v5_crt.py", "verify_v5.py", "verify_v2.py",
                                          "verify_count_numpy.py", "hist_count.cpp")},
           "command": ".venv/bin/python verify_v5_crt.py", "date": time.strftime("%Y-%m-%d %H:%M:%S")}
    (HERE / "certificates/verify_v5_crt_record.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{status}: v5 bound {bound} — all {len(recs)} region counts exact; {time.time()-t0:.0f}s")
    return status


if __name__ == "__main__":
    sys.exit(0 if main("--use-cache" in sys.argv) == "AUDIT PASSED" else 1)
