#!/usr/bin/env python3
"""hit条件付き反鎖のexact counter。"""

from __future__ import annotations

import time
from collections import Counter

import glb_lower_bound as lb


class CountLimitExceeded(RuntimeError):
    def __init__(self, reason, stats):
        super().__init__(reason)
        self.reason = reason
        self.stats = stats


def popcount(x):
    return bin(x).count("1")


def preprocess_hits(vertex_mask, hit_masks):
    """重複と上位（包含する大きい）hit集合を除く。"""
    raw = [h & vertex_mask for h in hit_masks]
    if any(h == 0 for h in raw):
        return (), True, {"input": len(raw), "duplicates_removed": len(raw) - len(set(raw)),
                          "supersets_removed": 0, "output": 0}
    unique = sorted(set(raw), key=lambda h: (popcount(h), h))
    kept = []
    supersets = 0
    for h in unique:
        if any(k & ~h == 0 for k in kept):
            supersets += 1
        else:
            kept.append(h)
    return tuple(kept), False, {"input": len(raw),
        "duplicates_removed": len(raw) - len(unique),
        "supersets_removed": supersets, "output": len(kept)}


def components(vertex_mask, adjacency):
    remain = vertex_mask
    out = []
    while remain:
        seed = remain & -remain
        comp = seed
        frontier = seed
        remain ^= seed
        while frontier:
            neighbors = 0
            f = frontier
            while f:
                bit = f & -f
                neighbors |= adjacency[bit.bit_length() - 1]
                f ^= bit
            frontier = neighbors & remain
            remain &= ~frontier
            comp |= frontier
        out.append(comp)
    return tuple(sorted(out, key=lambda c: (-popcount(c), c)))


def or_convolve(left, right):
    out = Counter()
    for a, ca in left.items():
        for b, cb in right.items():
            out[a | b] += ca * cb
    return out


def prepare_graph(vertex_mask, adjacency):
    comps = components(vertex_mask, adjacency)
    order = tuple(sorted(lb.iter_bits(vertex_mask),
                         key=lambda v: (-popcount(adjacency[v] & vertex_mask), v)))
    return {"vertex_mask": vertex_mask, "components": comps, "vertex_order": order,
            "order_position": {v: i for i, v in enumerate(order)}}


def count_hit_antichains(vertex_mask, hit_masks, adjacency, *, branch_rule="max_degree",
                         time_limit=60.0, node_limit=2_000_000,
                         memo_limit=1_000_000, prepared_graph=None):
    """hit mask別独立集数を成分ごとに計算しOR convolutionする。"""
    started = time.perf_counter()
    hits, impossible, prep = preprocess_hits(vertex_mask, hit_masks)
    stats = {"status": "running", "branch_rule": branch_rule, "input_vertex_count":
             popcount(vertex_mask), "preprocessing": prep, "recursive_nodes": 0,
             "memo_hits": 0, "peak_memo_entries": 0, "component_count": 0,
             "component_sizes": [], "component_memo_entries": []}
    if impossible:
        stats.update(status="complete", seconds=time.perf_counter() - started,
                     result_histogram_size=0)
        return 0, stats
    full = (1 << len(hits)) - 1
    vertex_hit = [0] * len(adjacency)
    for j, h in enumerate(hits):
        for v in lb.iter_bits(h):
            vertex_hit[v] |= 1 << j
    prepared = prepared_graph or prepare_graph(vertex_mask, adjacency)
    if prepared["vertex_mask"] != vertex_mask:
        raise ValueError("prepared graph vertex mask mismatch")
    comps = prepared["components"]
    order_position = prepared["order_position"]
    stats["component_count"] = len(comps)
    stats["component_sizes"] = [popcount(c) for c in comps]
    deadline = None if time_limit is None else started + time_limit
    global_memo = 0

    def check_limits():
        if deadline is not None and time.perf_counter() > deadline:
            raise CountLimitExceeded("time_limit", stats.copy())
        if node_limit is not None and stats["recursive_nodes"] >= node_limit:
            raise CountLimitExceeded("node_limit", stats.copy())
        if memo_limit is not None and global_memo >= memo_limit:
            raise CountLimitExceeded("memo_limit", stats.copy())

    combined = Counter({0: 1})
    try:
        for comp in comps:
            memo = {}

            def visit(residual):
                nonlocal global_memo
                if residual in memo:
                    stats["memo_hits"] += 1
                    return memo[residual]
                check_limits()
                stats["recursive_nodes"] += 1
                if not residual:
                    ans = Counter({0: 1})
                else:
                    if branch_rule == "max_degree":
                        v = max(lb.iter_bits(residual),
                                key=lambda x: (popcount(adjacency[x] & residual),
                                               -order_position[x]))
                    elif branch_rule == "first":
                        v = next(lb.iter_bits(residual))
                    else:
                        raise ValueError(branch_rule)
                    bit = 1 << v
                    excluded = visit(residual ^ bit)
                    selected = visit(residual & ~adjacency[v] & ~bit)
                    mv = vertex_hit[v]
                    ans = excluded.copy()
                    for mask, count in selected.items():
                        ans[mask | mv] += count
                memo[residual] = ans
                global_memo += 1
                stats["peak_memo_entries"] = max(stats["peak_memo_entries"], global_memo)
                return ans

            hist = visit(comp)
            stats["component_memo_entries"].append(len(memo))
            combined = or_convolve(combined, hist)
    except CountLimitExceeded as exc:
        stats.update(exc.stats)
        stats.update(status="limit_exceeded", limit_reason=exc.reason,
                     seconds=time.perf_counter() - started)
        raise CountLimitExceeded(exc.reason, stats)
    value = combined.get(full, 0)
    stats.update(status="complete", seconds=time.perf_counter() - started,
                 result_histogram_size=len(combined), preprocessed_hit_count=len(hits))
    return value, stats


def find_hit_antichain_witness(vertex_mask, hit_masks, adjacency, *,
                               time_limit=0.05, node_limit=50_000,
                               prepared_graph=None):
    """存在判定に特化し、一つ見つけたらwitnessを返す。"""
    started = time.perf_counter()
    hits, impossible, prep = preprocess_hits(vertex_mask, hit_masks)
    stats = {"status": "running", "recursive_nodes": 0, "failed_memo_entries": 0,
             "memo_hits": 0, "preprocessing": prep}
    if impossible:
        stats.update(status="nonexistent", seconds=time.perf_counter() - started)
        return "nonexistent", None, stats
    if not hits:
        stats.update(status="witness", seconds=time.perf_counter() - started)
        return "witness", (), stats
    prepared = prepared_graph or prepare_graph(vertex_mask, adjacency)
    if prepared["vertex_mask"] != vertex_mask:
        raise ValueError("prepared graph vertex mask mismatch")
    vertex_hit = [0] * len(adjacency)
    for j, h in enumerate(hits):
        for v in lb.iter_bits(h):
            vertex_hit[v] |= 1 << j
    full = (1 << len(hits)) - 1
    failed = set()
    deadline = None if time_limit is None else started + time_limit

    def visit(residual, met, chosen):
        if met == full:
            return chosen
        if deadline is not None and time.perf_counter() > deadline:
            raise CountLimitExceeded("time_limit", stats.copy())
        if node_limit is not None and stats["recursive_nodes"] >= node_limit:
            raise CountLimitExceeded("node_limit", stats.copy())
        key = residual, met
        if key in failed:
            stats["memo_hits"] += 1
            return None
        stats["recursive_nodes"] += 1
        unmet = [j for j in range(len(hits)) if not ((met >> j) & 1)]
        j = min(unmet, key=lambda q: (popcount(hits[q] & residual), q))
        choices = hits[j] & residual
        if not choices:
            failed.add(key)
            return None
        ordered = sorted(lb.iter_bits(choices),
                         key=lambda v: (-popcount(vertex_hit[v] & ~met),
                                        prepared["order_position"][v]))
        for v in ordered:
            answer = visit(residual & ~adjacency[v] & ~(1 << v),
                           met | vertex_hit[v], chosen + (v,))
            if answer is not None:
                return answer
        failed.add(key)
        return None
    try:
        witness = visit(vertex_mask, 0, ())
    except CountLimitExceeded as exc:
        stats.update(exc.stats)
        stats.update(status="unknown", limit_reason=exc.reason,
                     failed_memo_entries=len(failed), seconds=time.perf_counter() - started)
        return "unknown", None, stats
    status = "witness" if witness is not None else "nonexistent"
    stats.update(status=status, failed_memo_entries=len(failed),
                 seconds=time.perf_counter() - started)
    return status, witness, stats


def count_independent_sets(vertex_mask, adjacency, branch_rule="first"):
    memo = {}
    def visit(residual):
        if residual in memo:
            return memo[residual]
        if not residual:
            value = 1
        else:
            if branch_rule == "max_degree":
                v = max(lb.iter_bits(residual),
                        key=lambda x: (popcount(adjacency[x] & residual), -x))
            else:
                v = next(lb.iter_bits(residual))
            bit = 1 << v
            value = visit(residual ^ bit) + visit(residual & ~adjacency[v] & ~bit)
        memo[residual] = value
        return value
    return visit(vertex_mask), {"memo_entries": len(memo)}


def count_hit_antichains_inclusion_exclusion(vertex_mask, hit_masks, adjacency,
                                               max_hits=12):
    hits, impossible, prep = preprocess_hits(vertex_mask, hit_masks)
    if impossible:
        return 0, {"status": "complete", "preprocessing": prep, "terms": 1}
    if len(hits) > max_hits:
        raise ValueError("inclusion-exclusion hit limit exceeded")
    value = 0
    total_memo = 0
    for subset in range(1 << len(hits)):
        removed = 0
        for j, h in enumerate(hits):
            if (subset >> j) & 1:
                removed |= h
        count, st = count_independent_sets(vertex_mask & ~removed, adjacency, "first")
        total_memo += st["memo_entries"]
        value += (-1 if popcount(subset) & 1 else 1) * count
    return value, {"status": "complete", "preprocessing": prep,
                   "terms": 1 << len(hits), "total_memo_entries": total_memo}


def graph_statistics(vertex_mask, hit_masks, adjacency, chain_of, width_function):
    hits, impossible, prep = preprocess_hits(vertex_mask, hit_masks)
    comps = components(vertex_mask, adjacency)
    sizes = sorted((popcount(c) for c in comps), reverse=True)
    edges = sum(popcount(adjacency[v] & vertex_mask) for v in lb.iter_bits(vertex_mask)) // 2
    isolated = sum(s == 1 for s in sizes)
    comp_hit_bits = []
    for comp in comps:
        comp_hit_bits.append(sum(bool(comp & h) for h in hits))
    width = width_function(vertex_mask)
    used_chains = len({chain_of[v] for v in lb.iter_bits(vertex_mask)})
    max_size = sizes[0] if sizes else 0
    second = sizes[1] if len(sizes) > 1 else 0
    score = max_size * max_size + 4 * len(hits) + used_chains - isolated
    return {"vertex_count": popcount(vertex_mask), "preprocessing": prep,
            "preprocessed_hit_count": len(hits), "obviously_empty": impossible,
            "component_count": len(comps), "largest_component_size": max_size,
            "second_largest_component_size": second, "component_sizes": sizes,
            "comparable_edge_count": edges, "isolated_vertex_count": isolated,
            "component_hit_bit_counts": comp_hit_bits, "used_chain_count": used_chains,
            "width": width, "difficulty_score": score}
