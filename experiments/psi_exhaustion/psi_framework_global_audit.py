#!/usr/bin/env python3
"""Fresh global audit of the exhausted Psi(S,C) framework.  Prints PSI FRAMEWORK GLOBAL AUDIT PASSED only if:

  A1 complete universe            audit_psi_exhaustiveness.py re-run (36 keys, U1-U6, random re-keying) passes;
  A2 one status per key           every one of the 22 remaining keys has exactly one final status in
                                  {CERTIFIED, PROVABLY_EMPTY, REDUNDANT, INFEASIBLE}; no key is open;
  A3 pairwise disjointness        key = function of (L, R) (A1/U3); all ledger + v5 keys distinct except the
                                  G2/N2 split; 34-family structural audit record covers every included family;
  A4 mirrors counted once         each included family contributes exactly 2 x original (mirror_included flag),
                                  mirror classes separated (A1/U3);
  A5 no v5 double count           v5 keys not among the ledger / remaining keys except N2 (L-split) (A1/U4);
  A6 valid certificates           harvest/global_audit.py re-run: producer hashes, verifier AUDIT PASSED with the
                                  same exact total (CRT-checked sweeps), structural audit;
  A7 correct aggregation          B0 (frozen) + sum over the 22 keys of 2 x exact == ledger total == global audit
                                  total, recomputed here from the certificates themselves.
Usage (from experiments/post_gpw_improvement): python3.11 ../psi_exhaustion/psi_framework_global_audit.py [samples]
Writes ../psi_exhaustion/psi_framework_global_audit_record.json.
"""
import sys, json, subprocess, hashlib, time, math
from pathlib import Path
OUTDIR = Path(__file__).resolve().parent
PG = OUTDIR.parent / "post_gpw_improvement"
B0 = 26779208541153893647347341345937714190772
FINAL = {"CERTIFIED", "PROVABLY_EMPTY", "REDUNDANT", "INFEASIBLE"}
errors = []


def check(c, msg):
    if not c: errors.append(msg); print("FAIL:", msg, flush=True)
    else: print("ok:", msg, flush=True)
    return bool(c)


def run(cmd):
    r = subprocess.run(cmd, cwd=PG, capture_output=True, text=True)
    print(r.stdout[-1500:], r.stderr[-1500:], flush=True); return r


def main(n):
    t0 = time.time()
    # A6 (certificates) + rebuilt ledger
    run(["python3.11", "harvest/build_ledger.py"])
    g = run(["python3.11", "harvest/global_audit.py"])
    grec = json.loads((PG / "harvest/certificates/global_audit_record.json").read_text())
    check(g.returncode == 0 and grec["status"] == "GLOBAL AUDIT PASSED", "A6: harvest/global_audit.py GLOBAL AUDIT PASSED")
    # A1, A3 (re-keying), A4 (mirror classes), A5
    x = run(["python3.11", str(OUTDIR / "audit_psi_exhaustiveness.py"), str(n)])
    xrec = json.loads((OUTDIR / "audit_psi_exhaustiveness_record.json").read_text())
    check(x.returncode == 0 and xrec["status"] == "EXHAUSTIVENESS AUDIT PASSED" and xrec["samples_per_key"] == n,
          "A1/A3/A4/A5: exhaustiveness audit re-run passed")
    check(xrec["counts"] == {"universe": 36, "v5_only": 2, "ledger": 12, "remaining": 22}, f"A1: counts {xrec['counts']}")
    # A2 statuses
    run(["python3.11", str(OUTDIR / "build_exh.py")])
    exh = json.loads((OUTDIR / "PSI_EXHAUSTION_LEDGER.json").read_text())
    led = json.loads((PG / "COUNTED_FAMILIES.json").read_text())
    byid = {e["id"]: e for e in led["families"]}
    rem = json.loads((OUTDIR / "REMAINING_KEYS.json").read_text())["keys"]
    check(sorted(r["id"] for r in rem) == sorted(k["id"] for k in exh["keys"]) and len(rem) == 22, "A2: 22 remaining keys in ledger")
    statuses = {}
    for k in exh["keys"]:
        st = "PROVABLY_EMPTY" if k["status"] == "CERTIFIED (PROVABLY EMPTY)" else k["status"]
        statuses[k["id"]] = st
        check(st in FINAL, f"A2: {k['id']} final status {st}")
    # A3 structural audit covers every included family; distinct keys
    srec = json.loads((PG / "harvest/certificates/audit_psi_structure_record.json").read_text())
    inc = [e for e in led["families"] if e.get("included")]
    check(srec.get("status") == "AUDIT PASSED", "A3: structural audit record AUDIT PASSED")
    sfams = set(srec.get("families", {}))
    check(all(f"Psi({sorted(e['S'])},{sorted(e['C'])})" in sfams for e in inc),
          f"A3: structural audit covers all included families ({len(sfams)} in record)")
    miss = [e["id"] for e in inc if f"Psi({sorted(e['S'])},{sorted(e['C'])})" not in sfams]
    print("structural-record families not matched by Psi(S,C) name:", miss)
    check(all(e.get("structural_audit_ok") for e in inc), "A3: structural_audit_ok on every included family")
    keys = [(e["world"], tuple(sorted(e["S"])), tuple(sorted(e["C"]))) for e in inc]
    check(len(keys) == len(set(keys)), "A3: included ledger keys pairwise distinct")
    # A4 / A6 / A7: recompute the sum from the certificates
    base = int(led["baseline"]["value"]); s = base
    for e in inc:
        p = json.loads((PG / e["producer_certificate"]).read_text()); v = json.loads((PG / e["verifier_certificate"]).read_text())
        check(int(p["total"]) == int(v["total"]) == int(e["exact"]) and v["status"] == "AUDIT PASSED", f"A6: {e['id']} producer = verifier = ledger")
        check(e.get("mirror_included") is True, f"A4: {e['id']} mirror counted once (x2)")
        s += 2 * int(p["total"])
    s0 = base + sum(2 * int(e["exact"]) for e in inc if e["id"] not in statuses)
    check(s0 == B0, f"A7: frozen baseline B0 reproduced from v5 + the 12 pre-campaign families ({s0})")
    s22 = B0 + sum(2 * int(json.loads((PG / byid[i]["producer_certificate"]).read_text())["total"])
                   for i, st in statuses.items() if st in ("CERTIFIED", "PROVABLY_EMPTY"))
    check(s == s22 == int(grec["total"]) == int(exh["total"]), f"A7: aggregation {s} = B0 + 22 keys = global audit = exhaustion ledger")
    check(all(byid[i].get("included") for i, st in statuses.items() if st in ("CERTIFIED", "PROVABLY_EMPTY")), "A7: every certified key included")
    status = "PSI FRAMEWORK GLOBAL AUDIT PASSED" if not errors else "PSI FRAMEWORK GLOBAL AUDIT FAILED"
    rec = dict(status=status, B_psi=str(s), log10=math.log10(s), B0=str(B0), gain=s / B0, statuses=statuses,
               errors=errors, samples_per_key=n, runtime_s=round(time.time() - t0),
               ledger_sha256=hashlib.sha256((PG / "COUNTED_FAMILIES.json").read_bytes()).hexdigest(),
               exhaustion_ledger_sha256=hashlib.sha256((OUTDIR / "PSI_EXHAUSTION_LEDGER.json").read_bytes()).hexdigest())
    (OUTDIR / "psi_framework_global_audit_record.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(status, s, f"{s:.6e}", f"{time.time()-t0:.0f}s")
    return status


if __name__ == "__main__":
    sys.exit(0 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 100) == "PSI FRAMEWORK GLOBAL AUDIT PASSED" else 1)
