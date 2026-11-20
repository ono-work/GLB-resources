#!/usr/bin/env python3
"""Verify the post-GPW certified lower bound (results as of 2026-11-12) from frozen evidence.

The frozen Psi(S, C)-framework package lives in ``experiments/post_gpw_improvement/``
together with its campaign directory ``experiments/psi_exhaustion/``.  This script

1. checks every file of the package against the frozen manifest
   ``experiments/post_gpw_improvement/SHA256SUMS`` (byte-identical to the 2026-11-12 freeze);
2. recomputes the final integer directly from the certificates: the v5 baseline
   certificate plus 2 x (producer total) for each of the 34 included Psi(S, C) families,
   checking that every producer total equals the independent verifier total, that the
   22 campaign keys are all CERTIFIED, that the 12 pre-campaign families reproduce the
   frozen intermediate bound B0, and that the key-universe record counts
   36 = 2 (v5) + 12 (ledger) + 22 (campaign) keys;
3. re-runs the frozen audit chain (``psi_exhaustion/psi_framework_global_audit.py``, which
   itself re-runs ``harvest/build_ledger.py``, ``harvest/global_audit.py``,
   ``psi_exhaustion/audit_psi_exhaustiveness.py`` and ``psi_exhaustion/build_exh.py``) on a
   copy of the repository under ``generated/verify_post_gpw/``, so that no tracked file is
   modified, and compares the regenerated records with the committed ones.

Only the Python standard library is needed.  Step 3 takes about one minute on a laptop.
``--quick`` skips step 3; ``--samples N`` changes the number of random members re-keyed
per key in step 3 (default 100, as in the committed record).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PG = ROOT / "experiments/post_gpw_improvement"
PX = ROOT / "experiments/psi_exhaustion"
WORK = ROOT / "generated/verify_post_gpw"

FINAL_BOUND = 29247125847589399267405782004907476922410   # B_Psi, results as of 2026-11-12
B0 = 26779208541153893647347341345937714190772            # frozen intermediate milestone
GPW_BOUND = 1425933741673169505174021654095740659         # GPW 2026 paper
FROZEN_FILES = 121
UNIVERSE = {"universe": 36, "v5_only": 2, "ledger": 12, "remaining": 22}
PASSED_PSI = "PSI FRAMEWORK GLOBAL AUDIT PASSED"


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def frozen_path(relative: str) -> Path:
    """Map a path of the frozen manifest to the public layout.

    In the freeze, ``psi_exhaustion/`` was a subdirectory of the package; here it is the
    sibling directory ``experiments/psi_exhaustion/`` (the layout the scripts were run in).
    """
    if relative.startswith("psi_exhaustion/"):
        return ROOT / "experiments" / relative
    return PG / relative


def verify_frozen_manifest() -> None:
    manifest = PG / "SHA256SUMS"
    require(manifest.is_file(), "frozen manifest SHA256SUMS is missing")
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = frozen_path(relative)
        require(path.is_file(), f"frozen file is missing: {relative}")
        require(sha256(path) == expected, f"frozen file differs from the 2026-11-12 freeze: {relative}")
        checked += 1
    require(checked == FROZEN_FILES, f"frozen manifest lists {checked} files, expected {FROZEN_FILES}")
    print(f"POST-GPW FROZEN PACKAGE VERIFIED ({checked} files byte-identical to the 2026-11-12 freeze)")


def verify_from_certificates() -> int:
    ledger = load(PG / "COUNTED_FAMILIES.json")
    base = ledger["baseline"]
    v5 = load(PG / base["producer_certificate"])
    v5_verifier = load(PG / base["verifier_certificate"])
    v5_structure = load(PG / base["structural_audit"])
    require(sha256(PG / base["producer_certificate"]) == base["producer_sha256"], "v5 certificate hash mismatch")
    require(int(v5["new_lower_bound"]) == int(base["value"]) == int(v5_verifier["new_lower_bound"]),
            "v5 baseline value mismatch")
    require(v5_verifier["status"] == "AUDIT PASSED" and v5_structure["status"] == "AUDIT PASSED",
            "v5 verifier or structural audit did not pass")
    require(int(base["value"]) > GPW_BOUND, "v5 baseline does not exceed the GPW bound")
    total = int(base["value"])

    included = [entry for entry in ledger["families"] if entry.get("included")]
    require(len(included) == 34, f"expected 34 included Psi families, found {len(included)}")
    seen_ids: set[str] = set()
    seen_keys: set[tuple] = set()
    for entry in included:
        fid = entry["id"]
        require(fid not in seen_ids, f"family {fid} listed twice")
        seen_ids.add(fid)
        producer = load(PG / entry["producer_certificate"])
        verifier = load(PG / entry["verifier_certificate"])
        require(sha256(PG / entry["producer_certificate"]) == entry["producer_sha256"],
                f"{fid}: producer certificate hash mismatch")
        require(sha256(PG / entry["verifier_certificate"]) == entry["verifier_sha256"],
                f"{fid}: verifier certificate hash mismatch")
        require(producer["S"] == entry["S"] == verifier["S"] and producer["C"] == entry["C"] == verifier["C"],
                f"{fid}: (S, C) differs between ledger, producer and verifier")
        require(int(producer["total"]) == int(verifier["total"]) == int(entry["exact"]),
                f"{fid}: producer, verifier and ledger totals differ")
        require(verifier["status"] == "AUDIT PASSED", f"{fid}: independent verifier did not pass")
        require(entry.get("structural_audit_ok") is True, f"{fid}: structural audit not recorded as passed")
        require(entry.get("mirror_included") is True, f"{fid}: mirror bookkeeping flag missing")
        key = (entry["world"], tuple(entry["S"]), tuple(entry["C"]), tuple(entry["E"]))
        require(key not in seen_keys, f"{fid}: key {key} used twice")
        seen_keys.add(key)
        total += 2 * int(entry["exact"])
    require(total == FINAL_BOUND, f"recomputed bound {total} differs from the certified value")

    remaining = load(PX / "REMAINING_KEYS.json")["keys"]
    exhaustion = load(PX / "PSI_EXHAUSTION_LEDGER.json")
    require(len(remaining) == 22 and len(exhaustion["keys"]) == 22, "expected 22 campaign keys")
    require(sorted(k["id"] for k in remaining) == sorted(k["id"] for k in exhaustion["keys"]),
            "campaign key lists differ")
    require(all(k["status"] == "CERTIFIED" for k in exhaustion["keys"]), "a campaign key is not CERTIFIED")
    require(int(exhaustion["total"]) == FINAL_BOUND and int(exhaustion["B0"]) == B0,
            "exhaustion ledger totals mismatch")
    campaign_ids = {k["id"] for k in exhaustion["keys"]}
    for k in exhaustion["keys"]:
        ledger_entry = next(e for e in included if e["id"] == k["id"])
        require(int(k["exact"]) == int(ledger_entry["exact"]), f"{k['id']}: exhaustion ledger value differs")
    pre_campaign = [e for e in included if e["id"] not in campaign_ids]
    require(len(pre_campaign) == 12, f"expected 12 pre-campaign families, found {len(pre_campaign)}")
    require(int(base["value"]) + sum(2 * int(e["exact"]) for e in pre_campaign) == B0,
            "the 12 pre-campaign families do not reproduce the frozen B0")

    exhaustiveness = load(PX / "audit_psi_exhaustiveness_record.json")
    require(exhaustiveness["status"] == "EXHAUSTIVENESS AUDIT PASSED", "exhaustiveness audit record did not pass")
    require(exhaustiveness["counts"] == UNIVERSE, f"key universe counts {exhaustiveness['counts']}")
    global_record = load(PG / "harvest/certificates/global_audit_record.json")
    require(global_record["status"] == "GLOBAL AUDIT PASSED" and int(global_record["total"]) == FINAL_BOUND,
            "harvest global audit record mismatch")
    psi_record = load(PX / "psi_framework_global_audit_record.json")
    require(psi_record["status"] == PASSED_PSI and int(psi_record["B_psi"]) == FINAL_BOUND
            and int(psi_record["B0"]) == B0, "Psi framework global audit record mismatch")
    require(set(psi_record["statuses"]) == campaign_ids
            and all(s == "CERTIFIED" for s in psi_record["statuses"].values()),
            "Psi framework global audit statuses mismatch")
    ledger_hash = sha256(PG / "COUNTED_FAMILIES.json")
    require(global_record["ledger_sha256"] == psi_record["ledger_sha256"] == ledger_hash,
            "audit records refer to a different ledger")
    print("POST-GPW CERTIFICATES VERIFIED (v5 + 34 Psi families, 36 keys, 22 campaign keys CERTIFIED)")
    print(f"POST-GPW LOWER BOUND RECOMPUTED: {total}")
    return total


def rerun_audit_chain(samples: int) -> None:
    if WORK.exists():
        shutil.rmtree(WORK)

    def ignore(directory: str, names: list[str]) -> set[str]:
        skip = {".git", "__pycache__", ".pytest_cache", ".venv", "bin"}
        if Path(directory) == ROOT:
            skip.add("generated")
        return {name for name in names if name in skip}

    shutil.copytree(ROOT, WORK, ignore=ignore)
    # The frozen driver calls ``python3.11`` by name; point that name at this interpreter.
    shim_dir = WORK / "_python_shim"
    shim_dir.mkdir()
    shim = shim_dir / "python3.11"
    try:
        shim.symlink_to(sys.executable)
    except OSError:
        shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n', encoding="utf-8")
        shim.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = f"{shim_dir}{os.pathsep}{env.get('PATH', '')}"
    driver = WORK / "experiments/psi_exhaustion/psi_framework_global_audit.py"
    result = subprocess.run([sys.executable, str(driver), str(samples)],
                            cwd=WORK / "experiments/post_gpw_improvement",
                            env=env, capture_output=True, text=True)
    log = WORK / "psi_framework_global_audit.log"
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    require(result.returncode == 0, f"frozen audit chain failed; see {log}")

    regenerated = load(WORK / "experiments/psi_exhaustion/psi_framework_global_audit_record.json")
    committed = load(PX / "psi_framework_global_audit_record.json")
    for field in ("status", "B_psi", "B0", "statuses", "ledger_sha256"):
        require(regenerated[field] == committed[field], f"regenerated audit record differs in '{field}'")
    require(regenerated["status"] == PASSED_PSI and int(regenerated["B_psi"]) == FINAL_BOUND,
            "regenerated Psi framework audit did not pass")
    require(regenerated["samples_per_key"] == samples and not regenerated["errors"],
            "regenerated Psi framework audit has errors")
    global_record = load(WORK / "experiments/post_gpw_improvement/harvest/certificates/global_audit_record.json")
    require(global_record["status"] == "GLOBAL AUDIT PASSED" and int(global_record["total"]) == FINAL_BOUND,
            "regenerated harvest global audit mismatch")
    exhaustiveness = load(WORK / "experiments/psi_exhaustion/audit_psi_exhaustiveness_record.json")
    require(exhaustiveness["status"] == "EXHAUSTIVENESS AUDIT PASSED" and exhaustiveness["counts"] == UNIVERSE
            and exhaustiveness["samples_per_key"] == samples, "regenerated exhaustiveness audit mismatch")
    new_ledger = load(WORK / "experiments/psi_exhaustion/PSI_EXHAUSTION_LEDGER.json")
    old_ledger = load(PX / "PSI_EXHAUSTION_LEDGER.json")
    summarize = lambda led: sorted((k["id"], k["exact"], k["status"]) for k in led["keys"])
    require(summarize(new_ledger) == summarize(old_ledger) and int(new_ledger["total"]) == FINAL_BOUND,
            "regenerated exhaustion ledger differs from the committed one")
    print(f"POST-GPW AUDIT CHAIN RE-RUN ON A COPY: {PASSED_PSI} ({samples} random members per key)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="skip re-running the frozen audit chain")
    parser.add_argument("--samples", type=int, default=100, help="random members re-keyed per key (default 100)")
    args = parser.parse_args()
    try:
        verify_frozen_manifest()
        total = verify_from_certificates()
        if not args.quick:
            rerun_audit_chain(args.samples)
    except (OSError, KeyError, TypeError, ValueError, StopIteration, VerificationError) as error:
        print(f"POST-GPW VERIFICATION FAILED: {error}", file=sys.stderr)
        return 1
    print(PASSED_PSI)
    print(f"POST-GPW LOWER BOUND VERIFIED: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
