"""EXACT family Psi(S, C): S = R ∩ F0 literal (F0 = {3,12,21}), C ⊆ F0\\S covered strictly below, E = rest NOT covered
(B ∩ down(m) = ∅ for m ∈ E); L-pool H_L(T ∪ C).  Exact coverage patterns make Psi(S,C) pairwise disjoint.
  Psi(S) = { {L | T ∪ B} : T = [0] + S,  L ∈ A(H_L(T ∪ C)) [minus A(H_L(T)) if S = {3,12}],  req(T) ⊆ down(dom L),
             B ∈ A(V(dom L)),  B ∩ F0 = ∅,  B ∩ up(m) = ∅ and B ∩ down(m) ≠ ∅ for every m ∈ C }
  V_max(T) = {g ∉ T : g || T},  REQ = ∪ req over T ∪ V_max(T),  V(D) = {x ∈ V_max : req(x) ⊆ down D}   (v5 conventions)
Safety: a right option y of l is hit by T or y >= m (m ∈ C), and b < m <= y for the covering b ∈ B.
Disjointness: R ∩ F0 = S distinguishes Psi(S) from each other and from G1 (S=F0); Psi({3,12}) excludes L ⊆ H_L(T) (= G2).
0 ∈ R, 0 ∉ L (some l >= q > 0, q ∈ req(T), or 0 excluded) -> mirrors disjoint.
Count = Σ_D e(D) Σ_{U ⊆ C} (-1)^|U| |A(X(D) \\ down(U))|,  X(D) = {b ∈ V(D) \\ F0 : b !>= m, m ∈ C}."""
import sys, json, time, itertools
sys.path.insert(0, '.')
import verify_v2 as v, verify_v5 as w
import complete_TR as ct
sys.path.insert(0, 'harvest')
import mitm, hashlib, glbcore as gcore
sys.path.insert(0, 'barrier')
import cmp
from pathlib import Path
MCACHE = Path('harvest/mitm_cache.json')
def exact_any(r, tag, cache):
    try:
        return ct.exact_A(r, tag, cache)
    except AssertionError:
        pass
    key = hashlib.sha256(",".join(map(str, sorted(r))).encode()).hexdigest()
    disk = json.loads(MCACHE.read_text()) if MCACHE.exists() else {}
    if key in disk:
        return int(disk[key]["count"]), "mitm(cached)"
    t = time.time()
    # compressed mixed-radix MITM (barrier/cmp_mitm, reference implementation COMPRESSED_MITM_BASELINE.md);
    # replaces the dense rank_transfer_mitm for every region the dense rank transfer cannot handle.
    with open(f"harvest/logs/cmp_{tag}.log", "a") as lg:
        x, info = cmp.count_region(r, key="mem", log=lg)
    info = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in info.items()}
    disk = json.loads(MCACHE.read_text()) if MCACHE.exists() else {}
    disk[key] = {"size": len(r), "count": str(x), "method": "cmp_mitm", "tag": tag, **info}
    MCACHE.write_text(json.dumps(disk, indent=1))
    print(f"  |A({tag})| size {len(r)} = {x}  [cmp_mitm, {time.time()-t:.0f}s, maxRSS {info['maxrss']/2**30:.2f} GiB]", flush=True)
    return x, "cmp_mitm"
F0 = [3, 12, 21]
S = json.loads(sys.argv[1]); C = json.loads(sys.argv[2]); DRY = len(sys.argv) > 3 and sys.argv[3] == 'dry'
ZERO_COVERED = 0 in C
if ZERO_COVERED:
    # Z-world: 0 ∉ R, 0 covered strictly below; separation from mirrors by * ∈ R \ L (S ∋ *, * removed from the L-pool)
    F0 = [0, 3, 12, 21]
    assert 3 in S and 0 not in S
E = [m for m in F0 if m not in S and m not in C]   # excluded and NOT covered: B ∩ down(m) = ∅
assert set(C) <= set(F0) - set(S)
if not ZERO_COVERED:  # G1 = (S=F0) and G2 = (S={*,±1}, C=∅) are v5 families
    assert [3, 12, 21] != sorted(S) and not (sorted(S) == [3, 12] and not C)
T = list(S) if ZERO_COVERED else [0] + S
POOL_EXCL = {0, 3} if ZERO_COVERED else {0}
req = lambda x: [o for o in v.LEFT[x] if not any(v.leq(o, z) and o != z for z in v.LEFT[x])]
Vmax = [g for g in range(v.N) if g not in T and not any(v.comp(g, t) for t in T)]
REQ = sorted(set(q for x in T + Vmax for q in req(x)))
reqT = sorted(set(q for t in T for q in req(t)))
Hbig = [g for g in range(v.N) if g not in POOL_EXCL and v.hitL(g, T + C)]
Hsmall = [g for g in range(v.N) if g not in POOL_EXCL and v.hitL(g, T)]
t0 = time.time()
hb = w.histogram(Hbig, REQ)
hs = w.histogram(Hsmall, REQ) if sorted(S) == [3, 12] and not ZERO_COVERED else {}
print(f"S={S} C={C} E={E} |H|={len(Hbig)} |Vmax|={len(Vmax)} REQ={REQ} reqT={reqT} hist {len(hb)} [{time.time()-t0:.0f}s]", flush=True)
Ds = [D for D in ct.downsets(REQ) if all(any(v.leq(q, d) for d in D) for q in reqT)]
def emask(D): return sum(1 << j for j, q in enumerate(REQ) if q in D)
cache = {}; total = 0; rows = []
for D in Ds:
    e = hb.get(emask(D), 0) - hs.get(emask(D), 0)
    if e == 0: continue
    VD = [x for x in Vmax if all(any(v.leq(o, d) for d in D) for o in req(x))]
    X = [b for b in VD if b not in F0 and not any(v.leq(m, b) for m in C) and not any(v.leq(b, m) for m in E)]
    terms = []; cov = 0
    for k in range(len(C) + 1):
        for U in itertools.combinations(C, k):
            r = [b for b in X if not any(v.leq(b, u) for u in U)]
            pc = w.product_check(r)
            t = {"U": list(U), "n": len(r), "product": f"{len(pc[0])}x{len(pc[1])}" if pc else None}
            if not DRY:
                A, meth = exact_any(r, f"Psi{'_'.join(map(str,S))}_D{'_'.join(map(str,D))}_U{'_'.join(map(str,U))}", cache)
                t.update(A=str(A), method=meth); cov += (-1) ** k * A
            terms.append(t)
    row = {"D": list(D), "e": str(e), "V": len(VD), "X": len(X), "terms": terms}
    if not DRY:
        assert cov >= 0
        row.update(cov=str(cov), contribution=str(e * cov)); total += e * cov
    rows.append(row); print(json.dumps(row), f"[{time.time()-t0:.0f}s]", flush=True)
print(f"Psi{S} TOTAL", total, "%.6e" % total if total else "", f"{time.time()-t0:.0f}s")
json.dump({"family": f"Psi{S}", "S": S, "C": C, "T": T, "REQ": REQ, "req_T": reqT, "H_size": len(Hbig),
           "E_uncovered": E, "zero_covered": ZERO_COVERED, "pool_excluded": sorted(POOL_EXCL), "subtract_H_L_T": sorted(S) == [3, 12] and not ZERO_COVERED, "rows": rows, "total": str(total)},
          open(f"harvest/psi_S{'_'.join(map(str,S)) or 'none'}_C{'_'.join(map(str,C)) or 'none'}{'_dry' if DRY else ''}.json", 'w'), indent=1)
