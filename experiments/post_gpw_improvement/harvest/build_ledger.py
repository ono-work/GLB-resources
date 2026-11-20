#!/usr/bin/env python3
"""Build COUNTED_FAMILIES.json (canonical ledger) from the producer / verifier / audit certificate files.

Exact values are read from the certificate files, never typed by hand.  A family is marked included only if
its verifier certificate exists with status AUDIT PASSED and the same total, and the structural audit record
contains it with all hypotheses and pattern checks true.
Usage: python3.11 harvest/build_ledger.py
"""
import json, hashlib, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import verify_v2 as v

FAMILIES = [  # id, S, C, producer certificate (relative to ROOT)
    ("N2", [3, 12], [21], "harvest/psi_S3_12_C21.json"),
    ("N4", [12, 21], [3], "harvest/psi_S12_21_C3.json"),
    ("N5", [12], [3, 21], "harvest/psi_S12_C3_21.json"),
    ("Z1", [3, 12, 21], [0], "harvest/psi_S3_12_21_C0.json"),
    ("Z2", [3, 12], [0, 21], "harvest/psi_S3_12_C0_21.json"),
    ("ZG2", [3, 12], [0], "harvest/psi_S3_12_C0.json"),
    ("N3", [3, 21], [12], "harvest/psi_S3_21_C12.json"),
    ("N6", [3], [12, 21], "harvest/psi_S3_C12_21.json"),
    # compressed-MITM campaign (COMPRESSED_MITM_BASELINE.md)
    ("N7", [21], [3, 12], "harvest/psi_S21_C3_12.json"),
    ("Z3", [3, 21], [0, 12], "harvest/psi_S3_21_C0_12.json"),
    ("N8", [], [3, 12, 21], "harvest/psi_Snone_C3_12_21.json"),
    ("Z4", [3], [0, 12, 21], "harvest/psi_S3_C0_12_21.json"),
    # Psi-framework exhaustion campaign (experiments/psi_exhaustion/REMAINING_KEYS.json)
    ("R_s_p_E2", [3], [12], "harvest/psi_S3_C12.json"),
    ("R_p_s", [12], [3], "harvest/psi_S12_C3.json"),
    ("RZ_s_0p_E2", [3], [0, 12], "harvest/psi_S3_C0_12.json"),
    ("R_0_sp_E2", [], [3, 12], "harvest/psi_Snone_C3_12.json"),
    ("R_0_p2_Es", [], [12, 21], "harvest/psi_Snone_C12_21.json"),
    ("R_s2_0", [3, 21], [], "harvest/psi_S3_21_Cnone.json"),
    ("R_2_p_Es", [21], [12], "harvest/psi_S21_C12.json"),
    ("R_p2_0", [12, 21], [], "harvest/psi_S12_21_Cnone.json"),
    ("R_p_2", [12], [21], "harvest/psi_S12_C21.json"),
    ("R_s_2", [3], [21], "harvest/psi_S3_C21.json"),
    ("RZ_s_02_Ep", [3], [0, 21], "harvest/psi_S3_C0_21.json"),
    ("R_0_s2", [], [3, 21], "harvest/psi_Snone_C3_21.json"),
    ("RZ_s2_0_Ep", [3, 21], [0], "harvest/psi_S3_21_C0.json"),
    ("R_2_s", [21], [3], "harvest/psi_S21_C3.json"),
    ("R_0_p_Es2", [], [12], "harvest/psi_Snone_C12.json"),
    ("R_0_2", [], [21], "harvest/psi_Snone_C21.json"),
    ("R_p_0", [12], [], "harvest/psi_S12_Cnone.json"),
    ("R_2_0", [21], [], "harvest/psi_S21_Cnone.json"),
    ("RZ_s_0_Ep2", [3], [0], "harvest/psi_S3_C0.json"),
    ("R_s_0", [3], [], "harvest/psi_S3_Cnone.json"),
    ("R_0_s", [], [3], "harvest/psi_Snone_C3.json"),
    ("R_0_0", [], [], "harvest/psi_Snone_Cnone.json"),
]
AUDIT = "harvest/certificates/audit_psi_structure_record.json"


def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def main():
    v5 = json.loads((ROOT / "certificate_v5.json").read_text())
    v5r = json.loads((ROOT / "certificates/verify_v5_record.json").read_text())
    audit = json.loads((ROOT / AUDIT).read_text()) if (ROOT / AUDIT).exists() else {"families": {}, "status": None}
    led = {"schema": "glb-harvest-ledger-1",
           "note": "Every original family has a mirror (negation {L|R} -> {-R|-L}); 'mirror_included' says whether 2x is counted.",
           "baseline": {"id": "v5", "families": ["G1 = G([0,3,12,21],-)", "G2 = G([0,3,12],x0=21)"], "mirrors_included": True,
                        "value": v5["new_lower_bound"], "producer_certificate": "certificate_v5.json",
                        "producer_sha256": sha("certificate_v5.json"),
                        "verifier_certificate": "certificates/verify_v5_record.json", "verifier_status": v5r["status"],
                        "structural_audit": "certificates/audit_v5_structure_record.json",
                        "keys": [{"world": "0", "S": [3, 12, 21], "C": [], "L": "L ⊆ H_L([0,3,12,21])"},
                                 {"world": "0", "S": [3, 12], "C": "[] or [21]", "L": "L ⊆ H_L([0,3,12])"}]},
           "families": [], "audit_record": AUDIT, "audit_status": audit.get("status")}
    for fid, S, C, prod in FAMILIES:
        e = {"id": fid, "S": S, "C": C, "world": "Z" if 0 in C else "0", "mirror_id": "-" + fid}
        if not (ROOT / prod).exists():
            e.update(status="NOT PRODUCED", included=False, mirror_included=False); led["families"].append(e); continue
        cert = json.loads((ROOT / prod).read_text())
        assert cert["S"] == S and cert["C"] == C, fid
        T = cert["T"]
        ver = f"harvest/certificates/verify_{Path(prod).stem}.json"
        vr = json.loads((ROOT / ver).read_text()) if (ROOT / ver).exists() else None
        af = audit["families"].get(f"Psi({S},{C})")
        aud_ok = bool(af) and all(af["hypotheses"].values()) and af["pattern_ok"] and audit.get("status") == "AUDIT PASSED"
        ver_ok = bool(vr) and vr["status"] == "AUDIT PASSED" and vr["total"] == cert["total"]
        Z = 0 in C; F = [0, 3, 12, 21] if Z else [3, 12, 21]
        E_ = [m for m in F if m not in S and m not in C]
        Vmax = [x for x in range(v.N) if x not in T and not any(v.comp(x, t) for t in T)]
        Y = [x for x in Vmax if x < 22 and x not in F and not any(v.leq(m, x) for m in C) and not any(v.leq(x, m) for m in E_)]
        Pcells = [sorted(T + [y for i, y in enumerate(Y) if mask >> i & 1]) for mask in range(1 << len(Y))
                  if v.antichain([y for i, y in enumerate(Y) if mask >> i & 1])]
        e.update(P_cells=Pcells, E=[m for m in ([0, 3, 12, 21] if 0 in C else [3, 12, 21]) if m not in S and m not in C],
                 L_condition="L ⊄ H_L([0,3,12])" if cert.get("subtract_H_L_T") else None,
                 exact=cert["total"], producer_certificate=prod, producer_sha256=sha(prod),
                 verifier_certificate=ver if vr else None, verifier_sha256=sha(ver) if vr else None, verifier_ok=ver_ok,
                 structural_audit=AUDIT if af else None, structural_audit_ok=aud_ok,
                 disjointness_basis=("key (world,S,C,E) is a function of R; world Z: 0∉L∪R, *∈R∖L" if 0 in C else
                                     "key (world,S,C,E) is a function of R; world 0: 0∈R∖L")
                 + ("; vs v5 G2 (same key): L ⊄ H_L([0,3,12])" if cert.get("subtract_H_L_T") else ""))
        e["included"] = ver_ok and aud_ok
        e["mirror_included"] = e["included"]
        e["status"] = "CERTIFIED" if e["included"] else "PRODUCER ONLY"
        led["families"].append(e)
    (ROOT / "COUNTED_FAMILIES.json").write_text(json.dumps(led, indent=1, ensure_ascii=False) + "\n")
    for e in led["families"]: print(e["id"], e["status"], e.get("exact"))


if __name__ == "__main__":
    main()
