from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PG = ROOT / "experiments/post_gpw_improvement"
PX = ROOT / "experiments/psi_exhaustion"
B_PSI = 29247125847589399267405782004907476922410
GPW = 1425933741673169505174021654095740659


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class PostGpwResultTests(unittest.TestCase):
    def test_sum_of_certificates(self):
        ledger = load(PG / "COUNTED_FAMILIES.json")
        total = int(ledger["baseline"]["value"])
        included = [e for e in ledger["families"] if e.get("included")]
        self.assertEqual(len(included), 34)
        for entry in included:
            producer = load(PG / entry["producer_certificate"])
            verifier = load(PG / entry["verifier_certificate"])
            self.assertEqual(int(producer["total"]), int(verifier["total"]))
            self.assertEqual(verifier["status"], "AUDIT PASSED")
            total += 2 * int(producer["total"])
        self.assertEqual(total, B_PSI)
        self.assertGreater(B_PSI, GPW)

    def test_campaign_keys_all_certified(self):
        exhaustion = load(PX / "PSI_EXHAUSTION_LEDGER.json")
        self.assertEqual(len(exhaustion["keys"]), 22)
        self.assertTrue(all(k["status"] == "CERTIFIED" for k in exhaustion["keys"]))
        self.assertEqual(int(exhaustion["total"]), B_PSI)

    def test_key_universe_and_global_audit_records(self):
        exhaustiveness = load(PX / "audit_psi_exhaustiveness_record.json")
        self.assertEqual(exhaustiveness["status"], "EXHAUSTIVENESS AUDIT PASSED")
        self.assertEqual(exhaustiveness["counts"], {"universe": 36, "v5_only": 2, "ledger": 12, "remaining": 22})
        record = load(PX / "psi_framework_global_audit_record.json")
        self.assertEqual(record["status"], "PSI FRAMEWORK GLOBAL AUDIT PASSED")
        self.assertEqual(int(record["B_psi"]), B_PSI)


if __name__ == "__main__":
    unittest.main()
