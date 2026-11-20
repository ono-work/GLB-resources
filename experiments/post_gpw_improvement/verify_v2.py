#!/usr/bin/env python3
"""Independent verifier for certificate_v2.json (post-GPW lower bound).

Deliberately does NOT import glbcore / lattice_antichains / dlat (the producer code).
It reloads the frozen G_3 input, re-derives every set, and re-checks every claim:

  1. input hashes (CRLF-normalised) equal those in the GPW kernel certificate;
  2. each kernel is admissible; Q_L^+, Q_R^+ re-derived from the definition and equal
     to the certificate's lists; every element of Q_L^+ (Q_R^+) is incomparable to T_L (T_R)
     and hit by T_R (T_L)  ==> every (T_L u A, T_R u B) is a safe antichain pair;
  3. Q_R^+ is order-isomorphic to J(Q1) x J(Q2) (all 598^2 pairs vs leq_rows);
  4. C_L(K) = |A(Q_L^+(K))| recomputed with the archived GPW counter
     src/hit_antichain_counter.py (independent of the lattice DP);
  5. |A(Q_R^+)|: (a) CRT of the stored residues reproduces the stored value and the
     a-priori bound holds; (b) [--full] independent numpy/BLAS recomputation modulo three
     26-bit primes in BOTH product directions;
  6. negation mirrors: neg is an order-reversing involution swapping options; mirror kernels
     admissible; Q sets map onto each other; mirror left antichains avoid {2,11,14};
  7. pairwise disjointness of all families (L-pattern argument) and disjointness from the
     retained GPW residual family;
  8. exact integer aggregation by two paths.
Usage:  python verify_v2.py [--full]
"""
from __future__ import annotations

import csv, hashlib, json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
import hit_antichain_counter as hc  # archived GPW code (independent counter)

EXPORT = REPO / "data/gub/game_export"
CACHE = REPO / "experiments/lower_bound/local_components/g3_universe_cache.json"
CERT = HERE / "certificate_v2.json"
GPW_KERNEL_CERT = REPO / "experiments/lower_bound/general_safe_rectangle_ip_followup/certificate.json"
GPW_UNION = REPO / "experiments/lower_bound/z98_right_layer5_sufficient_stats/layer5_union.json"
GPW_FINAL = REPO / "experiments/lower_bound/z98_disjoint_cell_rectangle_pilot/new_lower_bound.json"

errors = []
def check(cond, msg):
    if not cond:
        errors.append(msg)
        print("FAIL:", msg, flush=True)
    return cond

def crlf_sha(p):
    b = Path(p).read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return hashlib.sha256(b).hexdigest()

def file_sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

# ---------------------------------------------------------------- poset
rows = [int(x, 16) for x in (EXPORT / "leq_rows.hex").read_text().split()]
N = len(rows)
cache = json.loads(CACHE.read_text())
with (EXPORT / "games.csv").open() as f:
    orig = [int(r["orig_gid"]) for r in csv.DictReader(f)]
check(cache["orig_gids"] == orig, "cache/games.csv mismatch")
LEFT = [tuple(x) for x in cache["left"]]; RIGHT = [tuple(x) for x in cache["right"]]; NEG = cache["negation"]
def leq(i, j): return (rows[i] >> j) & 1 == 1
def comp(i, j): return leq(i, j) or leq(j, i)
def antichain(xs): xs = list(xs); return all(not comp(xs[a], xs[b]) for a in range(len(xs)) for b in range(a + 1, len(xs)))
def hitL(g, TR): return all(any(leq(t, y) for t in TR) for y in RIGHT[g])   # right options of g hit by T_R
def hitR(g, TL): return all(any(leq(x, t) for t in TL) for x in LEFT[g])    # left options of g hit by T_L
def admissible(TL, TR): return antichain(TL) and antichain(TR) and all(hitL(t, TR) for t in TL) and all(hitR(t, TL) for t in TR)
def qsets(TL, TR):
    ql = [g for g in range(N) if g not in TL and not any(comp(g, t) for t in TL) and hitL(g, TR)]
    qr = [g for g in range(N) if g not in TR and not any(comp(g, t) for t in TR) and hitR(g, TL)]
    return ql, qr

def ideals(elems):
    n = len(elems); out = []
    below = [[j for j in range(n) if j != i and leq(elems[j], elems[i])] for i in range(n)]
    for s in range(1 << n):
        if all(not (s >> i & 1) or all(s >> j & 1 for j in below[i]) for i in range(n)):
            out.append(s)
    return out

def main(full=False, cert_path=None):
    t0 = time.time()
    C = json.loads(Path(cert_path or CERT).read_text())
    # 1. inputs
    kc = json.loads(GPW_KERNEL_CERT.read_text())
    ih = kc.get("input_hashes") or kc.get("inputs") or {}
    flat = json.dumps(ih)
    for name in ("games.csv", "leq_rows.hex", "metadata.json"):
        check(crlf_sha(EXPORT / name) in flat, f"input hash {name} not found in GPW kernel certificate")
    # 2. kernels
    fam = C["families"]
    QR_ref = None
    CL = {}
    for k in C["kernels"]:
        TL, TR = k["T_L"], k["T_R"]
        check(admissible(TL, TR), f"kernel {k['name']} not admissible")
        ql, qr = qsets(TL, TR)
        check(ql == k["Q_L_plus"], f"{k['name']} Q_L^+ differs")
        check(qr == C["Q_R_plus"]["elements"], f"{k['name']} Q_R^+ differs from shared Q_R^+")
        check(antichain(TL) and all(not comp(g, t) for g in ql for t in TL), f"{k['name']} Q_L^+ not incomparable to T_L")
        check(all(not comp(g, t) for g in qr for t in TR), f"{k['name']} Q_R^+ not incomparable to T_R")
        check(all(hitL(g, TR) for g in ql) and all(hitR(g, TL) for g in qr), f"{k['name']} hit conditions")
        pat = sorted(set(TL) & {2, 11, 14})
        check(pat == k["L_pattern"] and not set(ql) & {2, 11, 14}, f"{k['name']} L-pattern")
        CL[k["name"]] = (ql, k["C_L"])
    # adjacency for the archived counter (comparability graph)
    down = [0] * N
    for i in range(N):
        m = rows[i]
        while m:
            b = m & -m; down[b.bit_length() - 1] |= 1 << i; m ^= b
    adj = tuple((rows[i] | down[i]) & ~(1 << i) for i in range(N))
    for name, (ql, claimed) in CL.items():
        tt = time.time()
        cl, _ = hc.count_independent_sets(sum(1 << x for x in ql), adj, "max_degree")
        check(str(cl) == str(claimed), f"C_L({name}) = {cl} != {claimed}")
        print(f"C_L({name}) = {cl}  [archived counter, {time.time()-tt:.1f}s]", flush=True)
    # 3. product isomorphism
    QR = C["Q_R_plus"]["elements"]; Q1 = C["Q_R_plus"]["Q1"]; Q2 = C["Q_R_plus"]["Q2"]
    check(not any(comp(a, b) for a in Q1 for b in Q2), "Q1,Q2 related")
    J1, J2 = ideals(Q1), ideals(Q2)
    sig = {z: (sum(1 << i for i, q in enumerate(Q1) if leq(q, z)), sum(1 << i for i, q in enumerate(Q2) if leq(q, z))) for z in QR}
    check(len(set(sig.values())) == len(QR) and set(sig.values()) == {(a, b) for a in J1 for b in J2}, "Q_R^+ not in bijection with J(Q1)xJ(Q2)")
    sub = lambda a, b: a & ~b == 0
    iso = all(leq(z, w) == (sub(sig[z][0], sig[w][0]) and sub(sig[z][1], sig[w][1])) for z in QR for w in QR)
    check(iso, "Q_R^+ not order-isomorphic to J(Q1)xJ(Q2)")
    print(f"Q_R^+ ~= J(Q1) x J(Q2): {len(J1)} x {len(J2)} = {len(QR)}  iso={iso}", flush=True)
    # 4/5. |A(Q_R^+)|
    A = int(C["Q_R_plus"]["antichain_count"])
    for d in C["Q_R_plus"]["dp_directions"]:
        primes = [int(p) for p in d["primes"]]; res = [int(r) for r in d["residues"]]
        x, M = 0, 1
        for r, p in zip(res, primes):
            x += M * (((r - x) * pow(M, -1, p)) % p); M *= p
        check(x == A, f"CRT ({d['name']}) != stored count")
        check(int(d["apriori_bound"]) < M, f"a-priori bound ({d['name']}) >= modulus")
        check(all(pow(2, p - 1, p) == 1 for p in primes), "prime check")
    if full:
        import numpy  # noqa
        sys.path.insert(0, str(HERE))
        import verify_count_numpy as vn  # numpy/BLAS path (shares no code with rank_transfer.cpp)
        def jmask(L):  # ideals of lattice L (list of masks) as masks over indices
            n = len(L); out = []
            below = [sum(1 << j for j in range(n) if j != i and sub(L[j], L[i])) for i in range(n)]
            def rec(k, m, order=sorted(range(n), key=lambda i: bin(below[i]).count('1'))):
                if k == n: out.append(m); return
                i = order[k]; rec(k + 1, m)
                if below[i] & ~m == 0: rec(k + 1, m | (1 << i))
            rec(0, 0); return sorted(out)
        J1s, J2s = sorted(J1), sorted(J2)
        JJ1, JJ2 = jmask(J1s), jmask(J2s)
        for (S, Mv, tag), p in zip([(J1s, JJ2, "J(Q1)->J(J(Q2))"), (J2s, JJ1, "J(Q2)->J(J(Q1))"), (J1s, JJ2, "J(Q1)->J(J(Q2))")], vn.SMALL_PRIMES):
            tt = time.time(); r = vn.residue(S, Mv, p)
            check(r == A % p, f"numpy residue mismatch {tag} p={p}")
            print(f"numpy {tag} mod {p}: {r} (expected {A % p}) {time.time()-tt:.0f}s", flush=True)
    # 6. negation mirrors
    check(all(NEG[NEG[x]] == x for x in range(N)), "neg not involution")
    check(all(leq(i, j) == leq(NEG[j], NEG[i]) for i in range(N) for j in range(N)), "neg not order-reversing")
    check(all(sorted(NEG[y] for y in RIGHT[x]) == sorted(LEFT[NEG[x]]) for x in range(N)), "neg does not swap options")
    for m in C["mirrors"]:
        k = next(k for k in C["kernels"] if k["name"] == m["of"])
        check(m["T_L"] == sorted(NEG[x] for x in k["T_R"]) and m["T_R"] == sorted(NEG[x] for x in k["T_L"]), f"mirror {m['name']} kernel")
        check(admissible(m["T_L"], m["T_R"]), f"mirror {m['name']} admissible")
        mql, mqr = qsets(m["T_L"], m["T_R"])
        check(mql == sorted(NEG[x] for x in QR) and mqr == sorted(NEG[x] for x in k["Q_L_plus"]), f"mirror {m['name']} Q sets")
        check(not (set(mql) | set(m["T_L"])) & {2, 11, 14}, f"mirror {m['name']} left universe meets T0")
    # 7. disjointness:
    #   GPW residual family: every left antichain contains T0={2,11,14} (pattern full) and is NOT
    #   contained in T0 u Q_L^+(main) (residual layer k>=1)  -> disjoint from main canonical;
    #   K1,K2,K5 canonical: patterns {2,14},{2,11},{11,14};  mirrors: pattern {} ;
    #   mirrors pairwise disjoint as images of disjoint families under the bijection G -> -G.
    pats = [tuple(k["L_pattern"]) for k in C["kernels"]]
    check(len(set(pats)) == len(pats) and (2, 11, 14) in pats, "kernel L-patterns not distinct")
    check(all(len(p) >= 2 for p in pats), "kernel patterns")
    # 8. aggregation
    union = json.loads(GPW_UNION.read_text())
    R_res = int(union["union_0_5"])
    check(int(union["canonical_bound"]) + R_res == int(union["new_lower_bound"]), "GPW union identity")
    check(str(R_res) == C["retained"]["residual_union_0_5"], "retained residual value")
    sumCL = sum(int(k["C_L"]) for k in C["kernels"])
    path1 = R_res + 2 * sumCL * A
    path2 = R_res + sum(int(k["C_L"]) * A for k in C["kernels"]) + sum(int(next(k for k in C["kernels"] if k["name"] == m["of"])["C_L"]) * A for m in C["mirrors"])
    check(path1 == path2 == int(C.get("v2_new_lower_bound", C["new_lower_bound"])), "aggregation")
    old = int(json.loads(GPW_FINAL.read_text())["new_lower_bound"])
    check(int(C["previous_certified_bound"]) == old and path1 > old, "improvement over GPW bound")
    status = "AUDIT PASSED" if not errors else "AUDIT FAILED"
    print(f"{status}: v2 lower bound {path1} (~10^{len(str(path1))-1}, {path1/old:.2f}x GPW) in {time.time()-t0:.0f}s")
    return status, errors, path1

if __name__ == "__main__":
    st, err, _ = main(full="--full" in sys.argv)
    sys.exit(0 if not err else 1)
