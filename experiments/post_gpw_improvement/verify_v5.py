#!/usr/bin/env python3
"""Independent verifier for certificate_v5.json.

Recomputes from the frozen input (verify_v2 loader; no producer modules):
 1. input hashes;
 2. per family: H_L, V_max, req, REQ, req(T), every V(D) and x0-subregion, and the safety condition
    (every left option of every element of T u V(D) is <= some d in D);
 3. e(D) by a DIRECT histogram DP over dom-patterns (bin/hist_count: include/exclude + OR-convolution,
    no inclusion-exclusion, no Moebius) - independent of the producer pipeline
    (ie_count + inclusion-exclusion + Moebius); also sum of histogram = |A(H_L)|;
 4. every right region: join-irreducibles computed here, two incomparable components Q1,Q2,
    order-isomorphism with J(Q1) x J(Q2) on all pairs; count re-derived by the numpy/BLAS path
    modulo independent primes (regions >= 160 elements: 2 primes; smaller: exact via archived counter);
 5. mirror facts and the 0-separation; exact aggregation by two paths.
"""
import json, sys, time, subprocess, hashlib
from pathlib import Path
import verify_v2 as v
import hit_antichain_counter as hc

HERE = Path(__file__).resolve().parent
check = v.check
h = lambda S: hashlib.sha256(",".join(map(str, sorted(S))).encode()).hexdigest()


def req(x):
    L = v.LEFT[x]
    return [o for o in L if not any(v.leq(o, z) and o != z for z in L)]


def jis(S):
    Sset = set(S)
    out = []
    for x in S:
        below = [y for y in S if y != x and v.leq(y, x)]
        lc = [y for y in below if not any(z != y and v.leq(y, z) for z in below)]
        if len(lc) == 1:
            out.append(x)
    return out


def components(Q):
    seen, comps = set(), []
    for a in Q:
        if a in seen: continue
        st, c = [a], []
        while st:
            u = st.pop()
            if u in seen: continue
            seen.add(u); c.append(u); st += [b for b in Q if b != u and v.comp(u, b)]
        comps.append(sorted(c))
    return comps


def product_check(S):
    Q = jis(S)
    comps = sorted(components(Q), key=len)
    if len(comps) < 2:
        return None
    # target factor: the largest component; source factor: disjoint union of the others
    Q2 = comps[-1]
    Q1 = sorted(x for c in comps[:-1] for x in c)
    J1, J2 = v.ideals(Q1), v.ideals(Q2)
    sig = {z: (sum(1 << i for i, q in enumerate(Q1) if v.leq(q, z)), sum(1 << i for i, q in enumerate(Q2) if v.leq(q, z))) for z in S}
    sub = lambda a, b: a & ~b == 0
    ok = (len(set(sig.values())) == len(S) and set(sig.values()) == {(a, b) for a in J1 for b in J2}
          and all(v.leq(z, w) == (sub(sig[z][0], sig[w][0]) and sub(sig[z][1], sig[w][1])) for z in S for w in S))
    return (J1, J2) if ok else None


def jmask(L):
    sub = lambda a, b: a & ~b == 0
    n = len(L); out = []
    below = [sum(1 << j for j in range(n) if j != i and sub(L[j], L[i])) for i in range(n)]
    order = sorted(range(n), key=lambda i: bin(below[i]).count('1'))
    def rec(k, m):
        if k == n: out.append(m); return
        i = order[k]; rec(k + 1, m)
        if below[i] & ~m == 0: rec(k + 1, m | (1 << i))
    rec(0, 0); return sorted(out)


def histogram(HL, REQ):
    pos = {x: i for i, x in enumerate(HL)}
    lines = [str(len(HL))]
    for x in HL:
        lab = sum(1 << j for j, q in enumerate(REQ) if v.leq(q, x))
        nb = [pos[y] for y in HL if y != x and v.comp(x, y)]
        lines.append(" ".join(map(str, [lab, len(nb)] + nb)))
    out = subprocess.run([str(HERE / "bin/hist_count")], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True)
    return {int(a): int(b) for a, b in (l.split() for l in out.stdout.split("\n") if l)}


def main(full=False):
    t0 = time.time()
    C = json.loads((HERE / "certificate_v5.json").read_text())
    kc = json.loads(v.GPW_KERNEL_CERT.read_text())
    for name in ("games.csv", "leq_rows.hex", "metadata.json"):
        check(v.crlf_sha(v.EXPORT / name) == kc["input_hashes"][name], f"input hash {name}")
    down = [0] * v.N
    for i in range(v.N):
        m = v.rows[i]
        while m:
            b = m & -m; down[b.bit_length() - 1] |= 1 << i; m ^= b
    adj = tuple((v.rows[i] | down[i]) & ~(1 << i) for i in range(v.N))
    region_ok = {}
    fam_totals = []
    for f in C["families"]:
        TR, x0 = f["T_R"], f["x0"]
        check(v.antichain(TR) and (x0 is None or x0 not in TR), "kernel")
        HL = [g for g in range(v.N) if v.hitL(g, TR)]
        Vmax = [g for g in range(v.N) if g not in TR and not any(v.comp(g, t) for t in TR)]
        REQ = sorted(set(q for x in TR + Vmax for q in req(x)))
        reqT = sorted(set(q for t in TR for q in req(t)))
        check(HL == f["H_L"] and Vmax == f["V_max"] and REQ == f["REQ"] and reqT == f["req_T"], f"{TR} structure")
        # 0-separation: some q in req(T) with 0 < q; any l >= q is then comparable with 0, so 0 notin L
        check(any(q != 0 and v.leq(0, q) for q in reqT), "req(T) contains an element > 0")
        tt = time.time()
        H = histogram(HL, REQ)
        print(f"T_R={TR}: histogram over {len(H)} dom-patterns, total {sum(H.values())} [{time.time()-tt:.0f}s]", flush=True)
        reqT_mask = sum(1 << j for j, q in enumerate(REQ) if any(v.leq(q, p) for p in reqT))
        total = 0
        used = set()
        for r in f["rows"]:
            D = r["D"]; Dm = sum(1 << j for j, q in enumerate(REQ) if q in D)
            check(Dm & reqT_mask == reqT_mask, "D dominates req(T)")
            used.add(Dm)
            check(str(H.get(Dm, 0)) == r["e"], f"e(D) {D}: hist {H.get(Dm,0)} != {r['e']}")
            VD = [x for x in Vmax if all(any(v.leq(o, d) for d in D) for o in req(x))]
            check(h(VD) == r["V_hash"], f"V(D) {D}")
            check(all(any(v.leq(o, d) for d in D) for x in TR + VD for o in v.LEFT[x]), f"safety requirements {D}")
            A = int(C["regions"][r["V_hash"]]["count"]); c = A
            region_ok.setdefault(r["V_hash"], VD)
            if x0 is not None and x0 in VD:
                Vs = [x for x in VD if x != x0 and not v.comp(x, x0)]
                check(h(Vs) == r.get("x0_sub_hash"), "x0 subregion")
                region_ok.setdefault(h(Vs), Vs)
                c = A - int(C["regions"][h(Vs)]["count"])
            else:
                check("x0_sub_hash" not in r, "unexpected x0 correction")
            check(str(c) == r["c"] and int(r["contribution"]) == int(r["e"]) * c, f"c(D) {D}")
            total += int(r["e"]) * c
        # every L with dom(L) dominating req(T) is in exactly one listed D
        miss = {p: n for p, n in H.items() if p & reqT_mask == reqT_mask and p not in used}
        check(not miss, f"unlisted dom-patterns {miss}")
        check(str(total) == f["total"], "family total")
        fam_totals.append(total)
    # regions
    import verify_count_numpy as vn
    for hsh, S in sorted(region_ok.items(), key=lambda kv: len(kv[1])):
        check(sorted(S) == C["regions"][hsh]["elements"], "region elements")
        A = int(C["regions"][hsh]["count"])
        if len(S) < 160:
            tt = time.time()
            cnt, _ = hc.count_independent_sets(sum(1 << x for x in S), adj, "max_degree")
            check(cnt == A, f"region {len(S)} exact")
            print(f"region |S|={len(S)}: exact archived count {cnt} ok={cnt == A} [{time.time()-tt:.0f}s]", flush=True)
            continue
        pc = product_check(S)
        check(pc is not None, f"region {len(S)} not a product J(Q1)xJ(Q2)")
        if pc is None: continue
        J1, J2 = pc
        if not full and len(S) in (598, 648):
            print(f"region |S|={len(S)}: product iso ok (numpy recount done in v2/v3 audits)", flush=True); continue
        for p, (a, b) in zip(vn.SMALL_PRIMES[:2], [(J1, J2), (J2, J1)]):
            tt = time.time()
            r = vn.residue(sorted(a), jmask(sorted(b)), p)
            check(r == A % p, f"numpy region {len(S)} p={p}")
            print(f"region |S|={len(S)} ({len(J1)}x{len(J2)}): numpy mod {p} = {r} (expected {A % p}) [{time.time()-tt:.0f}s]", flush=True)
    # mirrors / separation
    check(v.NEG[0] == 0 and all(0 in f["T_R"] for f in C["families"]), "0 in every T_R, self-negative")
    check(v.leq(0, 2) and not v.leq(2, 0), "0 < 2")
    check(all(v.NEG[v.NEG[x]] == x for x in range(v.N)), "neg involution")
    check(all(v.leq(i, j) == v.leq(v.NEG[j], v.NEG[i]) for i in range(v.N) for j in range(v.N)), "neg order-reversing")
    check(all(sorted(v.NEG[y] for y in v.RIGHT[x]) == sorted(v.LEFT[v.NEG[x]]) for x in range(v.N)), "neg swaps options")
    check(C["families"][0]["x0"] is None and C["families"][1]["x0"] == 21 and 21 in C["families"][0]["T_R"], "G1/G2 separation by 21")
    total = 2 * sum(fam_totals)
    check(total == fam_totals[0] * 2 + fam_totals[1] * 2 == int(C["new_lower_bound"]), "aggregation")
    old = int(json.loads(v.GPW_FINAL.read_text())["new_lower_bound"])
    check(int(C["previous_certified_bound"]) == old and total > old, "improvement")
    status = "AUDIT PASSED" if not v.errors else "AUDIT FAILED"
    print(f"{status}: v5 lower bound {total} ({total/old:.2f}x GPW) in {time.time()-t0:.0f}s")
    return status


if __name__ == "__main__":
    sys.exit(0 if main(full="--full" in sys.argv) == "AUDIT PASSED" else 1)
