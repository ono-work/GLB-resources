#!/usr/bin/env python3
"""Fast, solver-free verification of the published GLB artifact.

This script checks file integrity, certificate status, the arithmetic linking
the certified stages, and the logical disjointness of the final three cells.
It does not rerun the expensive antichain enumerations or the Gurobi search.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINAL_BOUND = 1425933741673169505174021654095740659
PRE_DISJOINT_BOUND = 1416805572004163810711501940302641257
T0 = (2, 11, 14)


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_checksums() -> None:
    checksum_file = ROOT / "CHECKSUMS.sha256"
    require(checksum_file.is_file(), "CHECKSUMS.sha256 is missing")
    checked = 0
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        require(path.is_file(), f"checksum target is missing: {relative}")
        require(sha256(path) == expected, f"checksum mismatch: {relative}")
        checked += 1
    require(checked > 0, "empty checksum manifest")
    print(f"FILE INTEGRITY VERIFIED ({checked} files)")


def verify_g2_calibration() -> None:
    result = load("experiments/g2_calibration/safe_profile_g2_exact.json")
    contributions = sum(int(row["contribution"]) for row in result["profiles"])
    class_sizes = sum(int(row["class_size"]) for row in result["profiles"])
    require(result["status"] == "EXACT COMPLETE", "G2 calibration is incomplete")
    require(result["antichain_count"] == class_sizes == 98, "G2 antichain total mismatch")
    require(result["profile_count"] == len(result["profiles"]) == 23, "G2 profile total mismatch")
    require(contributions == result["profile_aggregated_total"] == 1448, "G2 aggregated total mismatch")
    require(result["direct_left_total"] == 1448 and result["totals_match"], "G2 direct count mismatch")
    print("G2 CALIBRATION VERIFIED (1448 safe pairs; g(3)=1474)")


def verify_kernel() -> None:
    base = "experiments/lower_bound/general_safe_rectangle_ip_followup"
    cert = load(f"{base}/certificate.json")
    for name, expected in cert["input_hashes"].items():
        path = ROOT / "data/gub/game_export" / name
        require(sha256(path) == expected, f"G3 input hash mismatch: {name}")
    solution = ROOT / base / "solutions/max_seed0_focus1.sol"
    log = ROOT / base / "logs/max_seed0_focus1.log"
    require(sha256(solution) == cert["best_solution"]["solution_sha256"], "z=98 solution hash mismatch")
    require(sha256(log) == cert["log_sha256"], "z=98 solver log hash mismatch")
    z = int(cert["optimal_value"])
    rectangle = int(cert["best_solution"]["rectangle_size"])
    require(cert["status"] == "GLOBAL_OPTIMUM_PROVED", "z=98 certificate status mismatch")
    require(z == cert["best_solution"]["z"] == 98, "kernel freedom mismatch")
    require(rectangle == 1 << z, "Boolean rectangle size is not 2^z")
    require(cert["optimality"]["incumbent"] == cert["optimality"]["best_bound"] == 98,
            "stored optimization bounds do not meet at 98")
    require(cert["optimality"]["mip_gap"] == 0, "stored Gurobi gap is not zero")
    print("Z98 KERNEL EVIDENCE VERIFIED (2^98)")


def verify_canonical_layer6() -> int:
    base = "experiments/lower_bound/z98_inverted_canonical_layer6"
    cert = load(f"{base}/certificate.json")
    for relative in ("main/full.json", "verifier/full.json", "layer6.json", "input_manifest.json"):
        require(sha256(ROOT / base / relative) == cert["hashes"][relative],
                f"canonical Layer 6 hash mismatch: {relative}")
    main = load(f"{base}/main/full.json")
    reverse = load(f"{base}/verifier/full.json")
    histogram = main["histogram"]
    require(histogram == reverse["histogram"], "forward/reverse Layer 6 histograms differ")
    require(sum(histogram) == main["leaves"] == reverse["leaves"] == 415959237179,
            "Layer 6 antichain count mismatch")
    require(main["set_hash_sum"] == reverse["set_hash_sum"], "Layer 6 hash-sum mismatch")
    require(main["set_hash_xor"] == reverse["set_hash_xor"], "Layer 6 hash-xor mismatch")
    r6 = sum(count * (1 << (78 - blocked)) for blocked, count in enumerate(histogram))
    summary = cert["summary"]
    require(r6 == int(summary["R6"]), "Layer 6 right-family total mismatch")
    contribution = 319901739 * r6
    canonical = 561500558847364965813467832318868800 + contribution
    require(canonical == int(summary["B_can_06"]), "canonical Layer 0--6 bound mismatch")
    require(cert["audit_status"] == "AUDIT PASSED", "canonical certificate did not pass")
    print(f"CANONICAL LAYER 0--6 VERIFIED ({canonical})")
    return canonical


def verify_residual_profiles(canonical: int) -> int:
    base = "experiments/lower_bound/z98_residual_profile_closure"
    cert = load(f"{base}/certificate.json")
    for relative, expected in cert["artifact_hashes"].items():
        require(sha256(ROOT / base / relative) == expected,
                f"residual-profile hash mismatch: {relative}")
    require(cert["status"] == "AUDIT PASSED", "residual-profile certificate did not pass")
    require(int(cert["canonical_bound"]) == canonical, "residual-profile canonical input mismatch")
    require(sum(int(v) for v in cert["layer_counts"].values()) == int(cert["all_left_antichains"]),
            "residual-profile layer distribution mismatch")
    residual_bound = canonical + int(cert["all_residual_contribution_0_1"])
    require(residual_bound == int(cert["new_bound"]), "residual-profile bound mismatch")
    print(f"RESIDUAL PROFILE CLOSURE VERIFIED ({residual_bound})")
    return residual_bound


def verify_layer4_and_layer5(canonical: int) -> int:
    base4 = "experiments/lower_bound/z98_right_layer4_sufficient_stats"
    cert4 = load(f"{base4}/certificate.json")
    require(cert4["audit"] == "AUDIT PASSED", "Layer 4 certificate did not pass")
    for key, relative in (
        ("summary_sha256", "summary.json"),
        ("input_manifest_sha256", "input_manifest.json"),
    ):
        require(sha256(ROOT / base4 / relative) == cert4[key], f"Layer 4 hash mismatch: {relative}")
    require(all(cert4["identities"].values()), "Layer 4 identities are incomplete")

    base5 = "experiments/lower_bound/z98_right_layer5_sufficient_stats"
    cert5 = load(f"{base5}/certificate.json")
    for key, relative in (
        ("summary_sha256", "summary.json"),
        ("input_manifest_sha256", "input_manifest.json"),
        ("layer5_verifier_sha256", "certificates/layer5_verifier.json"),
        ("union_verifier_sha256", "certificates/union_verifier.json"),
    ):
        require(sha256(ROOT / base5 / relative) == cert5[key], f"Layer 5 hash mismatch: {relative}")
    require(cert5["status"] == "AUDIT PASSED", "Layer 5 certificate did not pass")
    require(all(cert5["identities"].values()), "Layer 5 identities are incomplete")
    union = load(f"{base5}/layer5_union.json")
    summary = load(f"{base5}/summary.json")
    rows_total = sum(int(row["W"]) * int(row["union_0_5"]) for row in union["rows"])
    require(rows_total == int(union["union_0_5"]), "Layer 5 weighted union mismatch")
    require(int(union["canonical_bound"]) == canonical, "Layer 5 canonical input mismatch")
    bound = canonical + int(union["union_0_5"])
    require(bound == int(union["new_lower_bound"]) == int(summary["new_lower_bound"]),
            "Layer 5 lower bound mismatch")
    require(bound == PRE_DISJOINT_BOUND, "unexpected pre-disjoint lower bound")
    print(f"LAYER 4/5 EXACT UNION VERIFIED ({bound})")
    return bound


def verify_disjoint_partition(previous: int) -> int:
    base = "experiments/lower_bound/z98_disjoint_cell_rectangle_pilot"
    cert = load(f"{base}/certificate.json")
    require(cert["status"] == "AUDIT PASSED", "disjoint-cell certificate did not pass")
    require(cert["scope_status"] == "PARTIAL_STOP", "unexpected disjoint-cell scope status")
    for relative, expected in cert["artifact_hashes"].items():
        require(sha256(ROOT / base / relative) == expected,
                f"disjoint-cell hash mismatch: {relative}")
    definitions = {
        row["tag"]: row
        for row in load(f"{base}/cell_definitions.json")["unique_cells"]
    }
    partitions = load(f"{base}/partition_results.json")
    winner = load(f"{base}/best_partition.json")
    additions = []
    for partition in partitions["partitions"]:
        for bits in range(8):
            left = {T0[index] for index in range(3) if bits >> index & 1}
            hits = sum(
                set(definitions[tag]["required"]) <= left
                and not (set(definitions[tag]["forbidden"]) & left)
                for tag in partition["cells"]
            )
            require(hits == (bits != 7), f"cell partition truth table failed: {partition['cells']}")
        addition = sum(
            int(partitions["cell_representatives"][tag]["D_cell"])
            for tag in partition["cells"]
        )
        require(addition == int(partition["D_partition"]), "cell contribution sum mismatch")
        require(previous + addition == int(partition["new_lower_bound"]), "partition bound mismatch")
        additions.append(addition)
    best_addition = int(winner["D_partition"])
    require(best_addition == max(additions), "stored partition is not best among the six checked partitions")
    new = load(f"{base}/new_lower_bound.json")
    final = previous + best_addition
    require(final == int(winner["new_lower_bound"]) == int(new["new_lower_bound"]),
            "final lower bound mismatch")
    require(final == FINAL_BOUND, "unexpected final lower bound")
    print(f"DISJOINT PARTITION VERIFIED (+{best_addition})")
    print(f"FINAL LOWER BOUND VERIFIED: {final}")
    return final


def main() -> int:
    try:
        verify_checksums()
        verify_g2_calibration()
        verify_kernel()
        canonical = verify_canonical_layer6()
        verify_residual_profiles(canonical)
        previous = verify_layer4_and_layer5(canonical)
        verify_disjoint_partition(previous)
    except (OSError, KeyError, TypeError, ValueError, VerificationError) as error:
        print(f"VERIFICATION FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
