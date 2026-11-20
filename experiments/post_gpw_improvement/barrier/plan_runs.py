#!/usr/bin/env python3
"""Pre-run analysis for the compressed campaign (NEXT_EXACT_RUNS.md).

For each family: all regions, which are cached (producer caches results/exact_A_cache.json + harvest/mitm_cache.json,
verifier cache harvest/certificates/verify_region_cache.json), and for every uncached region with n >= NMIN:
  * compressed producer plan (cmp_mitm, min memory): per-rank compressed products S(B), stream, stored, w_eff;
  * verifier plan (vsweep, min sweep peak, other split than the producer's).
Usage: python barrier/plan_runs.py N7 [Z3 ...]  -> barrier/plan_runs_<fam>.json
"""
import sys, json, math, time
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "harvest")); sys.path.insert(0, str(HERE))
import psi_regions as pr, cmp, vsweep

FAM = {"N7": ([21], [3, 12]), "Z3": ([3, 21], [0, 12]), "N8": ([], [3, 12, 21]), "Z4": ([3], [0, 12, 21]),
       "N3": ([3, 21], [12]), "Z1": ([3, 12, 21], [0]), "ZG2": ([3, 12], [0]),
       # remaining keys (frontier analysis): 0-world with ±1 ∈ C and E ≠ ∅
       "R_s_p_E2": ([3], [12]), "R_2_p_Es": ([21], [12]), "R_0_p_Es2": ([], [12]), "R_0_sp_E2": ([], [3, 12]), "R_0_p2_Es": ([], [12, 21]),
       # remaining Z-world keys
       "RZ_s2_0_Ep": ([3, 21], [0]), "RZ_s_0p_E2": ([3], [0, 12]), "RZ_s_02_Ep": ([3], [0, 21]), "RZ_s_0_Ep2": ([3], [0]),
       # 0-world with ±1 ∉ C (psi_estimate.py list)
       "R_p_s": ([12], [3]), "R_p_2": ([12], [21]), "R_p_0": ([12], []), "R_p2_0": ([12, 21], []), "R_s2_0": ([3, 21], []),
       "R_s_2": ([3], [21]), "R_2_s": ([21], [3]), "R_0_s2": ([], [3, 21]), "R_s_0": ([3], []), "R_2_0": ([21], []),
       "R_0_s": ([], [3]), "R_0_2": ([], [21]), "R_0_0": ([], [])}
NMIN = 400


def load(p):
    p = ROOT / p
    return json.loads(p.read_text()) if p.exists() else {}


def main(fid):
    S, C = FAM[fid]
    pc = {**load("results/exact_A_cache.json"), **load("harvest/mitm_cache.json")}
    vc = load("harvest/certificates/verify_region_cache.json")
    regs = pr.regions(S, C)
    uniq = {}
    for r in regs: uniq.setdefault(r["sha"], r)
    out = {"family": fid, "S": S, "C": C, "terms": len(regs), "unique_regions": len(uniq), "regions": []}
    for h, r in sorted(uniq.items(), key=lambda kv: -kv[1]["n"]):
        rec = dict(n=r["n"], sha=h, D=r["D"], U=r["U"], producer_cached=h in pc, verifier_cached=h in vc)
        if r["n"] >= NMIN and not (rec["producer_cached"] and rec["verifier_cached"]):
            t = time.time()
            added, nji, cands = cmp.plans(r["elems"])
            c = cmp.choose(cands, key="mem")
            rec.update(JI=nji, plan_sec=round(time.time() - t))
            if c:
                rec["producer"] = dict(dual=c["dual"], Qa=c["pl"]["Qa"], nM=c["nM"], K=c["K"], ranks_S=[int(x) for x in c["comp"]],
                                       stream=c["stream"], stored=c["mem"], rs=c["rs"],
                                       w_eff=round(math.log(max(c["comp"]), 171), 3),
                                       dense_max=c["nM"] ** max(c["K"]))
                ex = (c["dual"], tuple(c["pl"]["Qa"]))
                vs = [x for x in cands if (x["dual"], tuple(x["pl"]["Qa"])) != ex]
                if vs:
                    b = min(vs, key=lambda x: (vsweep.sweep_peak(x), sum(x["comp"])))
                    rec["verifier"] = dict(dual=b["dual"], nM=b["nM"], K=b["K"], peak=vsweep.sweep_peak(b),
                                           peak_GiB=round(4 * vsweep.sweep_peak(b) / 2 ** 30, 2), work=sum(b["comp"]))
            print(json.dumps({k: rec[k] for k in rec if k not in ("D",)})[:400], flush=True)
        out["regions"].append(rec)
    (HERE / f"plan_runs_{fid}.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    for f in sys.argv[1:]: main(f)
