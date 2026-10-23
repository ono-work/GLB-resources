from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class PaperResultTests(unittest.TestCase):
    def test_g2_calibration(self):
        result = load("experiments/g2_calibration/safe_profile_g2_exact.json")
        self.assertEqual(sum(int(row["contribution"]) for row in result["profiles"]), 1448)
        self.assertEqual(result["direct_left_total"], 1448)

    def test_z98_boolean_rectangle(self):
        cert = load("experiments/lower_bound/general_safe_rectangle_ip_followup/certificate.json")
        self.assertEqual(int(cert["best_solution"]["rectangle_size"]), 1 << 98)

    def test_final_sum(self):
        result = load("experiments/lower_bound/z98_disjoint_cell_rectangle_pilot/new_lower_bound.json")
        self.assertEqual(
            int(result["previous"]) + int(result["addition"]),
            int(result["new_lower_bound"]),
        )
        self.assertEqual(
            int(result["new_lower_bound"]),
            1425933741673169505174021654095740659,
        )


if __name__ == "__main__":
    unittest.main()
