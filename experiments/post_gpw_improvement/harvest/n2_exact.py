"""EXACT family N2 (h-cell up{0,*,±1,*2}, *2 covered strictly below):
  N2 = { {L | T ∪ B} : T = [0,3,12],  L ∈ A(H_L(T ∪ {21})) \\ A(H_L(T)),  req(T) ⊆ down(dom L),
                       B ∈ A(V(dom L)),  21 ∉ B,  B ∩ down(21) ≠ ∅ }
  with V_max, REQ, V(D) exactly those of the v5 family G2 (T=[0,3,12], x0=21).
Safe: right options of l are hit by T or by 21, and every y >= 21 is hit by b <= 21 in B.
Disjoint from G1 (21 ∉ R), from G2 (L ⊄ H_L(T)), from all mirrors (0 ∈ R, 0 ∉ L since some l >= 1 > 0).
|N2| = Σ_D [e'(D) - e(D)] · [c(D) - |A(V(D) \\ ({21} ∪ down 21))|]   (c(D) = v5 count of B ∈ A(V(D)), 21 ∉ B)."""
import sys, json, time
sys.path.insert(0, '.')
import verify_v2 as v, verify_v5 as w
import complete_TR as ct
C = json.loads(open('certificate_v5.json').read())
fam = C['families'][1]
T, x0 = fam['T_R'], fam['x0']; assert T == [0, 3, 12] and x0 == 21
REQ = fam['REQ']; reqT = fam['req_T']
Vmax = json.loads(fam['V_max']) if isinstance(fam['V_max'], str) else fam['V_max']
rows = json.loads(fam['rows'].replace("'", '"')) if isinstance(fam['rows'], str) else fam['rows']
H248 = [g for g in range(v.N) if v.hitL(g, T)]
H319 = [g for g in range(v.N) if v.hitL(g, T + [21])]
assert set(H248) <= set(H319) and len(H248) == 249 and len(H319) == 320
DRY = len(sys.argv) > 1 and sys.argv[1] == 'dry'
t0 = time.time()
h248 = w.histogram(H248, REQ); h319 = w.histogram(H319, REQ)
print("histograms", len(h248), len(h319), f"{time.time()-t0:.0f}s", flush=True)
def emask(D): return sum(1 << j for j, q in enumerate(REQ) if q in D)
down21 = set(x for x in Vmax if x != 21 and v.leq(x, 21))
cache = {}; total = 0; out = []
for r in rows:
    D = r['D']; m = emask(D)
    e_old, e_new = h248.get(m, 0), h319.get(m, 0)
    assert e_old == int(r['e']), ("e mismatch vs v5 certificate", D, e_old, r['e'])
    de = e_new - e_old
    VD = [x for x in Vmax if all(any(v.leq(o, d) for d in D) for o in v.LEFT[x])]
    Rn = [x for x in VD if x != 21 and x not in down21]
    pc = w.product_check(Rn)
    line = {"D": D, "e_G2": e_old, "e_new": e_new, "delta_e": str(de), "V": len(VD), "Rnew": len(Rn),
            "Rnew_product": f"{len(pc[0])}x{len(pc[1])}" if pc else None, "c": r['c']}
    if not DRY and de:
        A, meth = ct.exact_A(Rn, "N2_D" + "_".join(map(str, D)), cache)
        cov = int(r['c']) - A
        line.update(A_Rnew=str(A), method=meth, cov=str(cov), contribution=str(de * cov))
        total += de * cov
    out.append(line); print(line, flush=True)
print("N2 TOTAL", total, "%.6e" % total if total else "", f"{time.time()-t0:.0f}s")
json.dump({"family": "N2", "T": T, "x0": x0, "rows": out, "total": str(total)}, open('harvest/n2_exact.json' if not DRY else 'harvest/n2_dry.json', 'w'), indent=1)
