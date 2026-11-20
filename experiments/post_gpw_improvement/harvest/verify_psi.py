#!/usr/bin/env python3
"""Independent verifier for a harvested family certificate (harvest/psi_S*_C*.json).

The producer (psi_exact.py) used: e(D) from the histogram DP (hist_count); region counts from dlat (rank_transfer_gen,
4x61-bit primes) or the meet-in-the-middle transfer (rank_transfer_mitm).  This verifier re-derives everything from
the definitions and recounts with different algorithms / primes:
  * structure (T, C, E, pool, V_max, REQ, req(T), profiles D, regions) re-derived from verify_v2 data;
  * e(D) by inclusion-exclusion n(D) = Σ_{Y ⊆ max D} (-1)^|Y| |A(pool \\ up Y)| (ie_count) + Möbius inversion;
  * regions: |S| < 160 -> archived GPW exact counter;  product J1 x J2 -> numpy/BLAS transfer mod 45-bit primes + CRT
    (verify_v5_crt method, modulus > |M|^|J1|);  otherwise -> meet-in-the-middle transfer mod a disjoint set of 59-bit
    primes + CRT (modulus > |M|^|JA|), cross-checked against the certificate value;
  * exact re-aggregation  total = Σ_D e(D) Σ_U (-1)^|U| |A(X(D) \\ down U)|.
Usage: .venv/bin/python harvest/verify_psi.py harvest/psi_S12_21_C3.json
"""
import sys, json, time, math, itertools, hashlib
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
import verify_v2 as v, verify_v5 as w, verify_count_numpy as vn, hit_antichain_counter as hc
import verify_v5_crt as vc
import glbcore as g, side_count2 as s2, mitm, dlat
sys.path.insert(0, str(HERE.parent / "barrier"))

F0 = [3, 12, 21]
PP = g.poset()
down = [0] * v.N
for i in range(v.N):
    m = v.rows[i]
    while m:
        b = m & -m; down[b.bit_length() - 1] |= 1 << i; m ^= b
ADJ = tuple((v.rows[i] | down[i]) & ~(1 << i) for i in range(v.N))


def req(x):
    L = v.LEFT[x]
    return [o for o in L if not any(v.leq(o, z) and o != z for z in L)]


def downsets(REQ):
    out = []
    for k in range(len(REQ) + 1):
        for S in itertools.combinations(REQ, k):
            if all(all(y in S for y in REQ if v.leq(y, x)) for x in S): out.append(tuple(sorted(S)))
    return out


def e_by_ie(pool, REQ, Ds):
    f = {}
    def fA(Y):
        Y = tuple(sorted(Y))
        if Y not in f:
            f[Y] = g.count_antichains_cpp(PP, [x for x in pool if not any(v.leq(y, x) for y in Y)])[0]
        return f[Y]
    allD = downsets(REQ)
    n = {}
    for D in allD:
        mx = [d for d in D if not any(v.leq(d, e) and d != e for e in D)]
        n[D] = sum((-1) ** k * fA(Y) for k in range(len(mx) + 1) for Y in itertools.combinations(mx, k))
    e = {}
    for D in sorted(allD, key=len, reverse=True):
        e[D] = n[D] - sum(e[E] for E in allD if set(D) < set(E))
    return {D: e[D] for D in Ds}


MITM_PRIMES = None
# verifier-own cache: region (sha256 of the sorted element list) -> count computed by THIS verifier in an earlier run.
# Never filled from producer output.
VCACHE_PATH = HERE / "certificates/verify_region_cache.json"
VCACHE = json.loads(VCACHE_PATH.read_text()) if VCACHE_PATH.exists() else {}


def count_region(S, cert_value, log):
    S = sorted(S)
    if len(S) < 160:
        c, _ = hc.count_independent_sets(sum(1 << x for x in S), ADJ, "max_degree")
        return c, {"method": "archived exact counter"}
    # Every region >= 160 elements: bin/vsweep (barrier/vsweep.cpp), an independent full bottom-up sweep with
    # 32-bit tables, moduli 2^32 + 31-bit primes, split chosen by minimal sweep peak (<= 9e9 entries = 33.5 GiB).
    # (The NumPy J1xJ2 transfer peaked at 35 GB and is no longer used; see MEMORY_MODEL.md.)
    import vsweep
    with open(HERE / "logs/vsweep_regions.log", "a") as lg:
        print(f"region n={len(S)} sha={hashlib.sha256(','.join(map(str, S)).encode()).hexdigest()}", file=lg, flush=True)
        X, inf = vsweep.verify_region(S, peak_cap=9e9, log=lg)
    return X, {"method": "vsweep full sweep (u32, 2^32 + 31-bit primes) + CRT", "dual": inf["dual"], "Qa": inf["Qa"],
               "M": inf["nM"], "K": inf["K"], "peak_entries": int(inf["peak_entries"]), "maxrss": inf["maxrss"],
               "moduli": inf["moduli"], "residues": inf["residues"], "binary_sha256": inf.get("binary_sha256")}


def main(path):
    t0 = time.time()
    cert = json.loads(Path(path).read_text())
    S, C = cert["S"], cert["C"]
    Z = 0 in C
    F = [0, 3, 12, 21] if Z else F0
    if Z: v.check(3 in S and 0 not in S, "Z-world: * literal in R")
    E = [m for m in F if m not in S and m not in C]
    T = list(S) if Z else [0] + S
    excl = {0, 3} if Z else {0}
    v.check(cert["T"] == T, "T")
    pool = [x for x in range(v.N) if x not in excl and v.hitL(x, T + C)]
    small = [x for x in range(v.N) if x not in excl and v.hitL(x, T)] if sorted(S) == [3, 12] and not Z else None
    Vmax = [x for x in range(v.N) if x not in T and not any(v.comp(x, t) for t in T)]
    REQ = sorted(set(q for x in T + Vmax for q in req(x)))
    reqT = sorted(set(q for t in T for q in req(t)))
    v.check(REQ == cert["REQ"] and reqT == cert["req_T"] and len(pool) == cert["H_size"], "structure")
    Ds = [D for D in downsets(REQ) if all(any(v.leq(q, d) for d in D) for q in reqT)]
    e = e_by_ie(pool, REQ, Ds)
    if small is not None:
        es = e_by_ie(small, REQ, Ds); e = {D: e[D] - es[D] for D in Ds}
    nonzero = {D: x for D, x in e.items() if x}
    v.check(sorted(map(list, nonzero)) == sorted(r["D"] for r in cert["rows"]), "set of profiles with e != 0")
    total = 0; recs = []
    for r in cert["rows"]:
        D = tuple(r["D"]); v.check(str(nonzero[D]) == r["e"], f"e({D})")
        VD = [x for x in Vmax if all(any(v.leq(o, d) for d in D) for o in req(x))]
        X = [b for b in VD if b not in F and not any(v.leq(m, b) for m in C) and not any(v.leq(b, m) for m in E)]
        cov = 0; terms = []
        for t in r["terms"]:
            U = t["U"]; reg = [b for b in X if not any(v.leq(b, u) for u in U)]
            v.check(len(reg) == t["n"], "region size")
            tt = time.time(); rsha = hashlib.sha256(",".join(map(str, sorted(reg))).encode()).hexdigest()
            if rsha in VCACHE and len(reg) >= 160:
                A, info = int(VCACHE[rsha]["value"]), {"method": "verifier cache (" + VCACHE[rsha]["method"] + ")"}
            else:
                A, info = count_region(reg, int(t["A"]), None)
                if len(reg) >= 160:
                    cur = json.loads(VCACHE_PATH.read_text()) if VCACHE_PATH.exists() else {}
                    cur[rsha] = {"value": str(A), "method": info["method"], "n": len(reg)}; VCACHE.update(cur)
                    VCACHE_PATH.write_text(json.dumps(cur, indent=0) + "\n")
            v.check(A == int(t["A"]), f"region count D={D} U={U}: {A} != {t['A']}")
            info.update(U=U, n=len(reg), value=str(A), sha=hashlib.sha256(",".join(map(str, sorted(reg))).encode()).hexdigest(),
                        sec=round(time.time() - tt, 1))
            terms.append(info); cov += (-1) ** len(U) * A
            print(f"  D={list(D)} U={U} n={len(reg)} {info['method']} ok [{info['sec']}s]", flush=True)
        v.check(cov >= 0 and str(cov) == r["cov"], "coverage count")
        total += nonzero[D] * cov
        recs.append({"D": list(D), "e": str(nonzero[D]), "cov": str(cov), "terms": terms})
    v.check(str(total) == cert["total"], f"family total {total} != {cert['total']}")
    status = "AUDIT PASSED" if not v.errors else "AUDIT FAILED"
    out = {"family": cert["family"], "S": S, "C": C, "E": E, "total": str(total), "status": status, "errors": v.errors,
           "rows": recs, "runtime_s": round(time.time() - t0), "command": " ".join(sys.argv)}
    (HERE / "certificates").mkdir(exist_ok=True)
    (HERE / f"certificates/verify_{Path(path).stem}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(status, cert["family"], total, f"{time.time()-t0:.0f}s")
    return status


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1]) == "AUDIT PASSED" else 1)
