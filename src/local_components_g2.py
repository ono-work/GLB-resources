#!/usr/bin/env python3
"""G_le_2 における singleton (K)-安全部品の完全pilot。"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import time
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import glb_lower_bound as lb

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "experiments/lower_bound/local_components"
OUT_JSON = OUT_DIR / "g2_pilot.json"
CERT_DIR = OUT_DIR / "certificates"
SPEC = ROOT / "memo/idea_20260727_experiment_spec.md"


def popcount(x: int) -> int:
    return bin(x).count("1")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git_commit(path: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "UNAVAILABLE"


@dataclass(frozen=True)
class Part:
    id: str
    A: tuple[int, ...]
    B: tuple[int, ...]
    marker: tuple[str, int]
    kind: str


def part_safe(P: lb.Universe, ids: Sequence[int], TL: tuple[int, ...], TR: tuple[int, ...], A: tuple[int, ...], B: tuple[int, ...]) -> bool:
    left, right = set(TL) | set(A), set(TR) | set(B)
    return (
        P.is_antichain(left)
        and P.is_antichain(right)
        and all(any(P.leq(r, y) for r in right) for a in A for y in P.right[a])
        and all(any(P.leq(x, l) for l in left) for b in B for x in P.left[b])
    )


def enumerate_parts(P: lb.Universe, ids: tuple[int, ...], TL: tuple[int, ...], TR: tuple[int, ...]):
    left, right, pairs = [], [], []
    for a in ids:
        if a not in TL and part_safe(P, ids, TL, TR, (a,), ()):
            left.append(Part(f"L:{a}", (a,), (), ("L", a), "left_singleton"))
    for b in ids:
        if b not in TR and part_safe(P, ids, TL, TR, (), (b,)):
            right.append(Part(f"R:{b}", (), (b,), ("R", b), "right_singleton"))
    for a in ids:
        if a in TL:
            continue
        for b in ids:
            if b not in TR and part_safe(P, ids, TL, TR, (a,), (b,)):
                pairs.append(Part(f"P:{a}:{b}", (a,), (b,), ("L", a), "paired_singleton"))
    return left, right, pairs


def pair_compatible(P: lb.Universe, p: Part, q: Part) -> bool:
    # 集合和で重複を消してから定義どおり検査する。
    return P.is_antichain(set(p.A) | set(q.A)) and P.is_antichain(set(p.B) | set(q.B))


def private_markers(parts: Sequence[Part], TL: tuple[int, ...], TR: tuple[int, ...]) -> bool:
    kernel = {("L", x) for x in TL} | {("R", x) for x in TR}
    supports = [{("L", x) for x in p.A} | {("R", x) for x in p.B} for p in parts]
    for i, p in enumerate(parts):
        others = kernel | set().union(*(supports[j] for j in range(len(parts)) if j != i))
        if not (supports[i] - others):
            return False
    return True


def select_pair_matching(pairs: Sequence[Part], used_l: set[int], used_r: set[int], mode: str) -> list[Part]:
    edges = [p for p in pairs if p.A[0] not in used_l and p.B[0] not in used_r]
    if mode == "lex":
        order = sorted(edges, key=lambda p: (p.A[0], p.B[0]))
        out, L, R = [], set(), set()
        for p in order:
            if p.A[0] not in L and p.B[0] not in R:
                out.append(p); L.add(p.A[0]); R.add(p.B[0])
        return out
    if mode == "reverse":
        order = sorted(edges, key=lambda p: (p.A[0], p.B[0]), reverse=True)
        out, L, R = [], set(), set()
        for p in order:
            if p.A[0] not in L and p.B[0] not in R:
                out.append(p); L.add(p.A[0]); R.add(p.B[0])
        return out
    if mode != "maximum":
        raise ValueError(mode)
    by_l: dict[int, list[Part]] = {}
    for p in edges:
        by_l.setdefault(p.A[0], []).append(p)
    for ps in by_l.values():
        ps.sort(key=lambda p: (p.B[0], p.id))
    match_r: dict[int, Part] = {}
    def augment(a: int, seen: set[int]) -> bool:
        for p in by_l.get(a, []):
            b = p.B[0]
            if b in seen:
                continue
            seen.add(b)
            if b not in match_r or augment(match_r[b].A[0], seen):
                match_r[b] = p; return True
        return False
    for a in sorted(by_l):
        augment(a, set())
    return sorted(match_r.values(), key=lambda p: p.id)


def conflict_graph(P: lb.Universe, parts: Sequence[Part]):
    n = len(parts); adj = [0] * n; edges = []
    for i in range(n):
        for j in range(i + 1, n):
            compatible = pair_compatible(P, parts[i], parts[j])
            # singleton簡略式との全件一致（同一元は衝突にしない）。
            simple_conflict = (
                bool(parts[i].A and parts[j].A and parts[i].A[0] != parts[j].A[0] and P.comparable(parts[i].A[0], parts[j].A[0]))
                or bool(parts[i].B and parts[j].B and parts[i].B[0] != parts[j].B[0] and P.comparable(parts[i].B[0], parts[j].B[0]))
            )
            if compatible == simple_conflict:
                raise AssertionError("simplified conflict test disagrees with set-union definition")
            if not compatible:
                adj[i] |= 1 << j; adj[j] |= 1 << i; edges.append((i, j))
    raw = json.dumps({"vertices": [p.id for p in parts], "edges": edges}, separators=(",", ":")).encode()
    return adj, edges, hashlib.sha256(raw).hexdigest()


def connected_components(adj: Sequence[int]) -> list[int]:
    unseen = (1 << len(adj)) - 1; out = []
    while unseen:
        start = (unseen & -unseen).bit_length() - 1; comp = 0; stack = 1 << start
        while stack:
            bit = stack & -stack; stack ^= bit; v = bit.bit_length() - 1
            if comp & bit:
                continue
            comp |= bit; stack |= adj[v] & ~comp
        out.append(comp); unseen &= ~comp
    return out


def component_shape(mask: int, adj: Sequence[int]) -> str:
    vs = [v for v in range(len(adj)) if (mask >> v) & 1]; n = len(vs)
    deg = [popcount(adj[v] & mask) for v in vs]; e = sum(deg) // 2
    if n == 1: return "K1"
    if n == 2 and e == 1: return "K2"
    if n == 3 and e == 3: return "K3"
    if e == n * (n - 1) // 2: return "clique"
    if e == n - 1 and max(deg) <= 2: return "path"
    if e == n and all(d == 2 for d in deg): return "cycle"
    return "other"


def graph_dp(adj: Sequence[int]):
    total_count = 1; total_alpha = 0; total_states = 0
    comps = connected_components(adj)
    for comp in comps:
        memo: dict[int, tuple[int, int]] = {0: (1, 0)}
        def rec(mask: int) -> tuple[int, int]:
            if mask in memo: return memo[mask]
            candidates = [v for v in range(len(adj)) if (mask >> v) & 1]
            v = max(candidates, key=lambda x: (popcount(adj[x] & mask), -x))
            c0, a0 = rec(mask & ~(1 << v))
            c1, a1 = rec(mask & ~(1 << v) & ~adj[v])
            memo[mask] = (c0 + c1, max(a0, 1 + a1)); return memo[mask]
        c, a = rec(comp); total_count *= c; total_alpha += a; total_states += len(memo)
    return total_count, total_alpha, total_states, comps


def enumerate_generated_pairs(parts: Sequence[Part], adj: Sequence[int], TL: tuple[int, ...], TR: tuple[int, ...]) -> set[tuple[tuple[int, ...], tuple[int, ...]]]:
    out = set()
    def rec(mask: int, L: set[int], R: set[int]):
        if not mask:
            out.add((tuple(sorted(set(TL) | L)), tuple(sorted(set(TR) | R)))); return
        bit = mask & -mask; v = bit.bit_length() - 1
        rec(mask ^ bit, L, R)
        rec((mask ^ bit) & ~adj[v], L | set(parts[v].A), R | set(parts[v].B))
    rec((1 << len(parts)) - 1, set(), set())
    return out


def graph_record(P: lb.Universe, parts: list[Part], TL: tuple[int, ...], TR: tuple[int, ...], rule: str):
    assert private_markers(parts, TL, TR)
    adj, edges, digest = conflict_graph(P, parts)
    count, alpha, states, comps = graph_dp(adj)
    pairs = enumerate_generated_pairs(parts, adj, TL, TR)
    if len(pairs) != count:
        raise AssertionError("identifiability/direct pair count mismatch")
    sizes = sorted((popcount(m) for m in comps), reverse=True)
    shapes = Counter(component_shape(m, adj) for m in comps)
    return {
        "rule": rule,
        "parts": [{"id": p.id, "A": list(p.A), "B": list(p.B), "private_marker": list(p.marker), "kind": p.kind} for p in parts],
        "vertex_count": len(parts), "edge_count": len(edges), "edges": [list(e) for e in edges],
        "component_count": len(comps), "component_sizes": sizes,
        "isolated_vertices": shapes["K1"], "maximum_degree": max((popcount(x) for x in adj), default=0),
        "component_shapes": dict(sorted(shapes.items())), "graph_hash": digest,
        "independent_set_count": str(count), "maximum_independent_set_size": alpha,
        "baseline_subsets_of_maximum": str(2**alpha),
        "improvement_numerator": str(count), "improvement_denominator": str(2**alpha),
        "log2_independent_set_count": math.log2(count), "log2_gain_over_alpha": math.log2(count) - alpha,
        "dp_memo_states": states, "generated_pair_count": len(pairs),
    }, pairs


def safe_pair(P: lb.Universe, L: tuple[int, ...], R: tuple[int, ...]) -> bool:
    return P.is_antichain(L) and P.is_antichain(R) and all(any(P.leq(r,y) for r in R) for l in L for y in P.right[l]) and all(any(P.leq(x,l) for l in L) for r in R for x in P.left[r])


def safe_profile_pairs() -> set[tuple[tuple[int, ...], tuple[int, ...]]]:
    data = json.loads((ROOT / "experiments/lower_bound/safe_profile/g2_exact.json").read_text())
    return {(tuple(L), tuple(R)) for row in data["profiles"] for L in row["C_pi"] for R in row["R_pi"]}


def run() -> dict:
    started = time.perf_counter(); P, metadata = lb.reconstruct(); ids = tuple(v for v, b in enumerate(P.birthdays) if b <= 2)
    antichains = [tuple(x) for x in lb.enumerate_antichains(P, ids)]
    assert len(ids) == 22 and len(antichains) == 98
    kernels = [(TL, TR) for TL in antichains for TR in antichains if lb.admissible(P, TL, TR, ids)]
    assert len(kernels) == 1448
    rows = []; all_pairs = set(); best = None; best_pairs = None
    aggregate_shapes = Counter(); k2_examples = []; k3_examples = []
    for kid, (TL, TR) in enumerate(kernels):
        left, right, paired = enumerate_parts(P, ids, TL, TR)
        base = left + right
        families = [("canonical_left_right_singletons", base)]
        used_l, used_r = {p.A[0] for p in left}, {p.B[0] for p in right}
        for mode in ("maximum", "lex", "reverse"):
            extra = select_pair_matching(paired, used_l, used_r, mode)
            families.append((f"private_marker_pair_{mode}", base + extra))
        frecs = []; kernel_union = set()
        for rule, parts in families:
            rec, pairs = graph_record(P, parts, TL, TR, rule); frecs.append(rec); kernel_union |= pairs; all_pairs |= pairs
            aggregate_shapes.update(rec["component_shapes"])
            if rec["component_shapes"].get("K2") and len(k2_examples) < 10:
                k2_examples.append({"kernel_id": kid, "rule": rule, "parts": rec["parts"], "edges": rec["edges"]})
            if rec["component_shapes"].get("K3") and len(k3_examples) < 10:
                k3_examples.append({"kernel_id": kid, "rule": rule, "parts": rec["parts"], "edges": rec["edges"]})
        ev = lb.evaluate_kernel(P, TL, TR, ids)
        canonical = frecs[0]
        assert canonical["maximum_independent_set_size"] == ev["exponent"]
        row = {
            "kernel_id": kid, "left_kernel": list(TL), "right_kernel": list(TR),
            "safe_component_counts": {"left_singleton": len(left), "right_singleton": len(right), "paired_singleton": len(paired)},
            "existing_kernel_exponent": ev["exponent"], "existing_kernel_bound": str(2**ev["exponent"]),
            "families": frecs, "kernel_generated_pair_union": len(kernel_union),
        }
        rows.append(row)
        score = max(int(x["independent_set_count"]) for x in frecs)
        if best is None or (score, len(kernel_union), -kid) > best:
            best = (score, len(kernel_union), -kid); best_pairs = (kid, frecs, kernel_union)
    assert all(safe_pair(P, L, R) for L, R in all_pairs)
    profile = safe_profile_pairs(); assert len(profile) == 1448
    inter = all_pairs & profile
    by_family = {}
    for fi, name in enumerate(["canonical", "pair_maximum", "pair_lex", "pair_reverse"]):
        fs = [r["families"][fi] for r in rows]
        shape_sum = Counter()
        for f in fs: shape_sum.update(f["component_shapes"])
        by_family[name] = {
            "kernels_with_strict_I_improvement": sum(int(f["independent_set_count"]) > int(f["baseline_subsets_of_maximum"]) for f in fs),
            "maximum_independent_set_count": str(max(int(f["independent_set_count"]) for f in fs)),
            "maximum_log2_gain": max(f["log2_gain_over_alpha"] for f in fs),
            "kernels_using_paired_singleton": sum(any(p["kind"] == "paired_singleton" for p in f["parts"]) for f in fs),
            "component_shapes": dict(sorted(shape_sum.items())),
        }
    empty_row = rows[0]
    source_paths = [ROOT.parent/"GUB/game_export/games.csv", ROOT.parent/"GUB/game_export/leq_rows.hex", ROOT.parent/"GUB/game_export/metadata.json"]
    result = {
        "status": "EXACT COMPLETE",
        "scope": "G_le_2_to_G_le_3",
        "definition_sources": ["memo/idea_20260727_review.md", "paper_fragments/local_safe_components.tex", "memo/idea_20260727_experiment_spec.md"],
        "counts": {"G_le_2": len(ids), "antichains": len(antichains), "antichain_pairs": len(antichains)**2, "admissible_kernel_pairs": len(kernels)},
        "kernels": rows,
        "best_kernel_id": -best[2], "best_family_independent_set_count": str(best[0]), "best_kernel_generated_pair_union": best[1],
        "all_kernel_generated_pair_union": len(all_pairs),
        "safe_profile_1448_size": len(profile), "intersection_with_safe_profile": len(inter),
        "local_only_not_safe_profile": len(all_pairs-profile), "safe_profile_only_not_local": len(profile-all_pairs), "combined_union": len(all_pairs|profile),
        "aggregate_component_shapes": dict(sorted(aggregate_shapes.items())), "K2_examples": k2_examples, "K3_examples": k3_examples,
        "comparison_summary": {
            "by_family": by_family,
            "kernels_where_any_family_strictly_improves_2alpha": sum(any(int(f["independent_set_count"]) > int(f["baseline_subsets_of_maximum"]) for f in r["families"]) for r in rows),
            "kernels_where_paired_extension_beats_canonical": sum(max(int(f["independent_set_count"]) for f in r["families"][1:]) > int(r["families"][0]["independent_set_count"]) for r in rows),
            "empty_kernel": {"kernel_id": empty_row["kernel_id"], "canonical_I": empty_row["families"][0]["independent_set_count"], "canonical_alpha": empty_row["families"][0]["maximum_independent_set_size"], "canonical_shapes": empty_row["families"][0]["component_shapes"], "best_extended_I": str(max(int(f["independent_set_count"]) for f in empty_row["families"]))},
        },
        "source_hashes": {str(p.relative_to(ROOT.parent)): sha256(p) for p in source_paths},
        "glb_commit": git_commit(ROOT), "gub_commit": git_commit(ROOT.parent/"GUB"),
        "metadata_counts_by_birthday": metadata.get("counts_by_birthday"),
        "runtime_seconds": time.perf_counter()-started,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True); CERT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    certificate_targets = []
    global_best = max(max(int(f["independent_set_count"]) for f in r["families"]) for r in rows)
    for row in rows:
        for rec in row["families"]:
            if int(rec["independent_set_count"]) == global_best:
                certificate_targets.append((row, rec, "best_count"))
    gain_row, gain_rec = max(
        ((row, rec) for row in rows for rec in row["families"]),
        key=lambda x: (x[1]["log2_gain_over_alpha"], int(x[1]["independent_set_count"]), -x[0]["kernel_id"]),
    )
    certificate_targets.append((gain_row, gain_rec, "best_gain"))
    for row, rec, tag in certificate_targets:
        cert = {
            "level": 2,
            "kernel_id": row["kernel_id"],
            "kernel": {"left": row["left_kernel"], "right": row["right_kernel"]},
            "components": rec["parts"], "identifiability_rule": rec["rule"]+": positional private markers",
            "conflict_graph": {k: rec[k] for k in ["vertex_count","edge_count","edges","component_sizes","graph_hash"]},
            "independent_set_count": rec["independent_set_count"], "maximum_independent_set_size": rec["maximum_independent_set_size"],
            "baseline_subsets_of_maximum": rec["baseline_subsets_of_maximum"], "generated_pair_count": rec["generated_pair_count"],
            "input_hashes": result["source_hashes"], "glb_commit": result["glb_commit"], "gub_commit": result["gub_commit"],
        }
        name = rec["rule"].replace("private_marker_pair_", "pair_")
        (CERT_DIR/f"{tag}_kernel_{row['kernel_id']}_{name}.json").write_text(json.dumps(cert,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k: result[k] for k in ["best_kernel_id","best_family_independent_set_count","all_kernel_generated_pair_union","intersection_with_safe_profile","combined_union","runtime_seconds"]},ensure_ascii=False))
    return result


if __name__ == "__main__":
    run()
