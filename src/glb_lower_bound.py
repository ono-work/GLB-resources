#!/usr/bin/env python3
"""short partizan games の下界計算用の小規模回帰 CLI。"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parent
DEFAULT_GUB = ROOT.parent / "GUB"


def _load_gub_module(gub_dir: Path):
    sys.path.insert(0, str(gub_dir))
    try:
        import game_universe as gu  # type: ignore
    finally:
        sys.path.pop(0)
    return gu


@dataclass
class Universe:
    birthdays: List[int]
    left: List[Tuple[int, ...]]
    right: List[Tuple[int, ...]]
    leq_rows: List[int]
    orig_gids: List[int]
    negation: List[int]

    @property
    def n(self) -> int:
        return len(self.left)

    def leq(self, i: int, j: int) -> bool:
        return bool((self.leq_rows[i] >> j) & 1)

    def comparable(self, i: int, j: int) -> bool:
        return self.leq(i, j) or self.leq(j, i)

    def is_antichain(self, xs: Iterable[int]) -> bool:
        values = list(xs)
        return all(
            not self.comparable(values[i], values[j])
            for i in range(len(values))
            for j in range(i + 1, len(values))
        )


def reconstruct(gub_dir: Path = DEFAULT_GUB) -> Tuple[Universe, dict]:
    """GUB の構成コードを読み、export ID へ変換して正本データと照合する。"""
    gu = _load_gub_module(gub_dir)
    U = gu.GameUniverse()
    g1_raw = U.generate_exact_birthday_raw(1)
    g1 = U.quotient_new_classes(g1_raw, [0])
    g2_raw = U.generate_exact_birthday_raw(2)
    g2 = U.quotient_new_classes(g2_raw, [0] + g1)
    G_le_2_orig = [0] + g1 + g2
    leq2 = gu.build_leq_dict(U, G_le_2_orig)
    antichains2 = gu.enumerate_antichains(G_le_2_orig, leq2)
    g3_raw = gu.generate_raw_from_antichains(U, antichains2, 3)
    g3 = U.quotient_new_classes(g3_raw, G_le_2_orig)
    reps = G_le_2_orig + g3

    export_dir = gub_dir / "game_export"
    with (export_dir / "games.csv").open(encoding="utf-8") as f:
        next(f)
        exported_orig = [int(line.strip().split(",")[1]) for line in f if line.strip()]
    with (export_dir / "leq_rows.hex").open(encoding="utf-8") as f:
        exported_rows = [int(line.strip(), 16) for line in f if line.strip()]
    metadata = json.loads((export_dir / "metadata.json").read_text(encoding="utf-8"))
    if reps != exported_orig:
        raise ValueError("再構成した orig_gid 列が games.csv と一致しない")

    orig_to_export = {gid: i for i, gid in enumerate(reps)}
    left = [tuple(orig_to_export[x] for x in U.games[g].left) for g in reps]
    right = [tuple(orig_to_export[x] for x in U.games[g].right) for g in reps]
    birthdays = [U.games[g].birthday for g in reps]
    neg_orig: Dict[int, int] = {}
    negation: List[int] = []
    for gid in reps:
        form = (
            tuple(sorted(neg_orig[x] for x in U.games[gid].right)),
            tuple(sorted(neg_orig[x] for x in U.games[gid].left)),
        )
        formal_gid = U._add_game(form[0], form[1], U.games[gid].birthday)
        U.clear_comparison_cache()
        matches = [j for j, rep in enumerate(reps) if U.eq(formal_gid, rep)]
        if len(matches) != 1:
            raise ValueError("反転ゲーム値の代表が一意に定まらない")
        neg_orig[gid] = reps[matches[0]]
        negation.append(matches[0])
    rebuilt_rows = [
        sum(1 << j for j, gj in enumerate(reps) if U.leq(gi, gj))
        for gi in reps
    ]
    if rebuilt_rows != exported_rows:
        raise ValueError("再構成した順序が leq_rows.hex と一致しない")
    return Universe(birthdays, left, right, exported_rows, reps, negation), metadata


def subsets(xs: Sequence[int]) -> Iterable[Tuple[int, ...]]:
    for k in range(len(xs) + 1):
        yield from itertools.combinations(xs, k)


def enumerate_antichains(P: Universe, ids: Sequence[int]) -> List[Tuple[int, ...]]:
    out: List[Tuple[int, ...]] = []

    def visit(pos: int, current: List[int]) -> None:
        if pos == len(ids):
            out.append(tuple(current))
            return
        visit(pos + 1, current)
        x = ids[pos]
        if all(not P.comparable(x, y) for y in current):
            current.append(x)
            visit(pos + 1, current)
            current.pop()

    visit(0, [])
    return out


def hopcroft_karp(nodes: Sequence[int], edges: Dict[int, List[int]]):
    pair_l = {u: -1 for u in nodes}
    pair_r = {v: -1 for v in nodes}
    inf = 10**9
    while True:
        q = deque()
        dist = {}
        for u in nodes:
            dist[u] = 0 if pair_l[u] == -1 else inf
            if pair_l[u] == -1:
                q.append(u)
        found = False
        while q:
            u = q.popleft()
            for v in edges[u]:
                mate = pair_r[v]
                if mate == -1:
                    found = True
                elif dist[mate] == inf:
                    dist[mate] = dist[u] + 1
                    q.append(mate)
        if not found:
            break

        def dfs(u: int) -> bool:
            for v in edges[u]:
                mate = pair_r[v]
                if mate == -1 or (dist[mate] == dist[u] + 1 and dfs(mate)):
                    pair_l[u], pair_r[v] = v, u
                    return True
            dist[u] = inf
            return False

        for u in nodes:
            if pair_l[u] == -1:
                dfs(u)
    return pair_l, pair_r


def maximum_antichain(P: Universe, ids: Sequence[int]) -> Tuple[int, Tuple[int, ...]]:
    nodes = list(ids)
    edges = {
        u: [v for v in nodes if u != v and P.leq(u, v) and not P.leq(v, u)]
        for u in nodes
    }
    pair_l, pair_r = hopcroft_karp(nodes, edges)
    z_l = {u for u in nodes if pair_l[u] == -1}
    z_r = set()
    q = deque(z_l)
    while q:
        u = q.popleft()
        for v in edges[u]:
            if pair_l[u] == v or v in z_r:
                continue
            z_r.add(v)
            mate = pair_r[v]
            if mate != -1 and mate not in z_l:
                z_l.add(mate)
                q.append(mate)
    antichain = tuple(sorted(z_l - z_r))
    width = len(nodes) - sum(1 for u in nodes if pair_l[u] != -1)
    if len(antichain) != width or not P.is_antichain(antichain):
        raise AssertionError("matching からの最大反鎖復元に失敗")
    return width, antichain


def iter_bits(mask: int) -> Iterable[int]:
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def popcount(mask: int) -> int:
    return bin(mask).count("1")


@dataclass
class SearchIndex:
    P: Universe
    all_mask: int
    down_masks: List[int]
    comparable_masks: List[int]
    left_option_signatures: List[int]
    right_option_signatures: List[int]
    lambda_signatures: List[int]
    rho_signatures: List[int]
    safe_left_cache: Dict[int, int]
    safe_right_cache: Dict[int, int]

    @classmethod
    def build(cls, P: Universe) -> "SearchIndex":
        n = P.n
        all_mask = (1 << n) - 1
        down = [0] * n
        for g, row in enumerate(P.leq_rows):
            for h in iter_bits(row):
                down[h] |= 1 << g
        comparable = [P.leq_rows[g] | down[g] for g in range(n)]
        left_sig = [sum(1 << x for x in P.left[g]) for g in range(n)]
        right_sig = [sum(1 << x for x in P.right[g]) for g in range(n)]
        low22 = (1 << 22) - 1
        lambdas = [down[g] & low22 for g in range(n)]
        rhos = [P.leq_rows[g] & low22 for g in range(n)]
        return cls(P, all_mask, down, comparable, left_sig, right_sig,
                   lambdas, rhos, {}, {})

    def safe_left_mask(self, rho: int) -> int:
        if rho not in self.safe_left_cache:
            self.safe_left_cache[rho] = sum(
                1 << g for g, options in enumerate(self.right_option_signatures)
                if options & ~rho == 0
            )
        return self.safe_left_cache[rho]

    def safe_right_mask(self, lam: int) -> int:
        if lam not in self.safe_right_cache:
            self.safe_right_cache[lam] = sum(
                1 << g for g, options in enumerate(self.left_option_signatures)
                if options & ~lam == 0
            )
        return self.safe_right_cache[lam]

    def kernel_masks(self, tl: Optional[int], tr: Optional[int]):
        lam = 0 if tl is None else self.lambda_signatures[tl]
        rho = 0 if tr is None else self.rho_signatures[tr]
        s_l = self.safe_left_mask(rho)
        s_r = self.safe_right_mask(lam)
        admissible_early = (
            (tl is None or bool(s_l & (1 << tl))) and
            (tr is None or bool(s_r & (1 << tr)))
        )
        if not admissible_early:
            return lam, rho, s_l, s_r, 0, 0, False
        q_l = s_l if tl is None else s_l & ~self.comparable_masks[tl]
        q_r = s_r if tr is None else s_r & ~self.comparable_masks[tr]
        return lam, rho, s_l, s_r, q_l & self.all_mask, q_r & self.all_mask, True


def maximum_antichain_mask(index: SearchIndex, vertex_mask: int):
    """整数 bitset の induced poset に対する exact Dilworth 計算。"""
    nodes = list(iter_bits(vertex_mask))
    edges = {
        u: list(iter_bits(index.P.leq_rows[u] & vertex_mask & ~(1 << u)))
        for u in nodes
    }
    pair_l, pair_r = hopcroft_karp(nodes, edges)
    z_l = {u for u in nodes if pair_l[u] == -1}
    z_r = set()
    q = deque(z_l)
    while q:
        u = q.popleft()
        for v in edges[u]:
            if pair_l[u] == v or v in z_r:
                continue
            z_r.add(v)
            mate = pair_r[v]
            if mate != -1 and mate not in z_l:
                z_l.add(mate)
                q.append(mate)
    antichain = tuple(sorted(z_l - z_r))
    width = len(nodes) - sum(pair_l[u] != -1 for u in nodes)
    if len(antichain) != width or not index.P.is_antichain(antichain):
        raise AssertionError("bitset matching からの最大反鎖復元に失敗")
    return width, antichain


def evaluate_kernel_indexed(index: SearchIndex, tl: Optional[int], tr: Optional[int]):
    lam, rho, s_l, s_r, q_l, q_r, ok = index.kernel_masks(tl, tr)
    if not ok:
        raise ValueError("許容核ではない")
    started = time.perf_counter()
    left_started = time.perf_counter()
    w_l, free_l = maximum_antichain_mask(index, q_l)
    left_seconds = time.perf_counter() - left_started
    right_started = time.perf_counter()
    w_r, free_r = maximum_antichain_mask(index, q_r)
    right_seconds = time.perf_counter() - right_started
    tl_tuple = () if tl is None else (tl,)
    tr_tuple = () if tr is None else (tr,)
    return {
        "left_kernel": tl_tuple, "right_kernel": tr_tuple,
        "left_free": free_l, "right_free": free_r,
        "left_antichain": tuple(sorted(tl_tuple + free_l)),
        "right_antichain": tuple(sorted(tr_tuple + free_r)),
        "q_left_size": popcount(q_l), "q_right_size": popcount(q_r),
        "s_left_size": popcount(s_l), "s_right_size": popcount(s_r),
        "lambda_signature": lam, "rho_signature": rho,
        "left_matching_seconds": left_seconds,
        "right_matching_seconds": right_seconds,
        "left_width": w_l, "right_width": w_r,
        "matching_seconds": left_seconds + right_seconds,
        "evaluation_seconds": time.perf_counter() - started,
        "exponent": w_l + w_r,
    }


def downset(P: Universe, y: int, ids: Sequence[int]) -> set:
    return {g for g in ids if P.leq(g, y)}


def upset(P: Universe, x: int, ids: Sequence[int]) -> set:
    return {g for g in ids if P.leq(x, g)}


def safe_left(P: Universe, T_R: Sequence[int], ids: Sequence[int]) -> set:
    tr = set(T_R)
    return {g for g in ids if all(tr & downset(P, y, ids) for y in P.right[g])}


def safe_right(P: Universe, T_L: Sequence[int], ids: Sequence[int]) -> set:
    tl = set(T_L)
    return {g for g in ids if all(tl & upset(P, x, ids) for x in P.left[g])}


def admissible(P: Universe, T_L: Sequence[int], T_R: Sequence[int], ids: Sequence[int]) -> bool:
    return (
        P.is_antichain(T_L)
        and P.is_antichain(T_R)
        and set(T_L) <= safe_left(P, T_R, ids)
        and set(T_R) <= safe_right(P, T_L, ids)
    )


def negation_map(P: Universe) -> List[int]:
    """再構成時にゲーム値の同値性で同定した反転写像を返す。"""
    return list(P.negation)


def evaluate_kernel(P: Universe, T_L: Sequence[int], T_R: Sequence[int], ids: Sequence[int]):
    if not admissible(P, T_L, T_R, ids):
        raise ValueError("許容核ではない")
    q_l = [
        g for g in safe_left(P, T_R, ids)
        if g not in T_L and all(not P.comparable(g, t) for t in T_L)
    ]
    q_r = [
        g for g in safe_right(P, T_L, ids)
        if g not in T_R and all(not P.comparable(g, t) for t in T_R)
    ]
    w_l, free_l = maximum_antichain(P, q_l)
    w_r, free_r = maximum_antichain(P, q_r)
    return {
        "left_kernel": tuple(T_L),
        "right_kernel": tuple(T_R),
        "left_free": free_l,
        "right_free": free_r,
        "left_antichain": tuple(sorted(tuple(T_L) + free_l)),
        "right_antichain": tuple(sorted(tuple(T_R) + free_r)),
        "exponent": w_l + w_r,
    }


def solve_by_kernel_enumeration(P: Universe, ids: Sequence[int]):
    ants = enumerate_antichains(P, ids)
    best = None
    checked = 0
    for tl in ants:
        for tr in ants:
            if admissible(P, tl, tr, ids):
                checked += 1
                sol = evaluate_kernel(P, tl, tr, ids)
                if best is None or sol["exponent"] > best["exponent"]:
                    best = sol
    return best, checked


def solve_original_exhaustive(P: Universe, ids: Sequence[int]):
    """元 IP の変数意味を A,B,T_L,T_R の全列挙で直接解く。"""
    ants = enumerate_antichains(P, ids)
    best = None
    feasible = 0
    for A in ants:
        for B in ants:
            for tl in subsets(A):
                for tr in subsets(B):
                    if set(A) <= safe_left(P, tr, ids) and set(B) <= safe_right(P, tl, ids):
                        feasible += 1
                        z = len(A) + len(B) - len(tl) - len(tr)
                        if best is None or z > best["exponent"]:
                            best = {
                                "left_kernel": tl, "right_kernel": tr,
                                "left_antichain": A, "right_antichain": B,
                                "exponent": z,
                            }
    return best, feasible


def verify_rectangle(P: Universe, certificate: dict, ids: Sequence[int]) -> None:
    allowed = set(ids)
    tl = tuple(certificate["left_kernel"])
    tr = tuple(certificate["right_kernel"])
    A = tuple(certificate["left_antichain"])
    B = tuple(certificate["right_antichain"])
    for name, values in [("T_L", tl), ("T_R", tr), ("A", A), ("B", B)]:
        if len(values) != len(set(values)) or not set(values) <= allowed:
            raise ValueError("%s の ID が不正" % name)
        if not P.is_antichain(values):
            raise ValueError("%s が反鎖でない" % name)
    if not set(tl) <= set(A) or not set(tr) <= set(B):
        raise ValueError("核が反鎖に含まれない")
    if not set(A) <= safe_left(P, tr, ids):
        raise ValueError("左側の安全条件違反")
    if not set(B) <= safe_right(P, tl, ids):
        raise ValueError("右側の安全条件違反")
    z = len(A) + len(B) - len(tl) - len(tr)
    if certificate["exponent"] != z:
        raise ValueError("指数が集合サイズと一致しない")

    if "left_free_antichain" in certificate:
        if set(certificate["left_free_antichain"]) != set(A) - set(tl):
            raise ValueError("left_free_antichain が A\\T_L と一致しない")
    if "right_free_antichain" in certificate:
        if set(certificate["right_free_antichain"]) != set(B) - set(tr):
            raise ValueError("right_free_antichain が B\\T_R と一致しない")
    if "q_left" in certificate or "q_right" in certificate:
        q_l = {
            g for g in safe_left(P, tr, ids)
            if g not in tl and all(not P.comparable(g, t) for t in tl)
        }
        q_r = {
            g for g in safe_right(P, tl, ids)
            if g not in tr and all(not P.comparable(g, t) for t in tr)
        }
        if set(certificate.get("q_left", [])) != q_l:
            raise ValueError("q_left が元データからの再計算と一致しない")
        if set(certificate.get("q_right", [])) != q_r:
            raise ValueError("q_right が元データからの再計算と一致しない")


def symmetric_kernel(P: Universe, tl: Optional[int], tr: Optional[int]):
    return (None if tr is None else P.negation[tr],
            None if tl is None else P.negation[tl])


def canonical_kernel(P: Universe, tl: Optional[int], tr: Optional[int]):
    original = (-1 if tl is None else tl, -1 if tr is None else tr)
    sym_tl, sym_tr = symmetric_kernel(P, tl, tr)
    symmetric = (-1 if sym_tl is None else sym_tl, -1 if sym_tr is None else sym_tr)
    return min(original, symmetric)


def source_hashes(gub_dir: Path) -> dict:
    base = gub_dir / "game_export"
    return {name: sha256(base / name) for name in
            ["games.csv", "leq_rows.hex", "metadata.json"]}


def certificate_from_result(result: dict, index: SearchIndex, gub_dir: Path) -> dict:
    tl = result["left_kernel"]
    tr = result["right_kernel"]
    _, _, _, _, q_l, q_r, ok = index.kernel_masks(
        None if not tl else tl[0], None if not tr else tr[0])
    if not ok:
        raise AssertionError("certificate 化する核が許容されない")
    return {
        "ground_set": "G_le_3",
        "left_kernel": list(tl), "right_kernel": list(tr),
        "left_antichain": list(result["left_antichain"]),
        "right_antichain": list(result["right_antichain"]),
        "left_free_antichain": list(result["left_free"]),
        "right_free_antichain": list(result["right_free"]),
        "q_left": list(iter_bits(q_l)), "q_right": list(iter_bits(q_r)),
        "q_left_size": popcount(q_l), "q_right_size": popcount(q_r),
        "lambda_signature": result["lambda_signature"],
        "rho_signature": result["rho_signature"],
        "exponent": result["exponent"],
        "lower_bound_statement": "|G_le_4| >= 2^%d" % result["exponent"],
        "source_data_hashes": source_hashes(gub_dir),
        "program_version": "GLB working tree 2026-07-26; GUB %s" %
            _gub_commit(gub_dir),
    }


def _gub_commit(gub_dir: Path) -> str:
    head = gub_dir / ".git" / "HEAD"
    if not head.exists():
        return "unknown"
    value = head.read_text(encoding="utf-8").strip()
    if value.startswith("ref: "):
        ref = gub_dir / ".git" / value[5:]
        if ref.exists():
            return ref.read_text(encoding="utf-8").strip()
    return value


def candidate_at(n: int, left_size: int, right_size: int, ordinal: int):
    if left_size == 1 and right_size == 0:
        return ordinal, None
    if left_size == 0 and right_size == 1:
        return None, ordinal
    if left_size == 1 and right_size == 1:
        return ordinal // n, ordinal % n
    raise ValueError("今回サポートする核サイズは (1,0),(0,1),(1,1) のみ")


def search_kernels(
    P: Universe,
    gub_dir: Path,
    left_size: int,
    right_size: int,
    checkpoint_path: Path,
    output_dir: Path,
    max_exact: int,
    resume: bool,
    use_symmetry: bool,
    checkpoint_every: int,
):
    if (left_size, right_size) not in {(1, 0), (0, 1), (1, 1)}:
        raise ValueError("対象外の核サイズ")
    n = P.n
    generated = n if left_size + right_size == 1 else n * n
    state = {
        "schema": 1, "left_size": left_size, "right_size": right_size,
        "generated_candidates": generated, "scan_next": 0,
        "antichain_passed": 0, "admissible_passed": 0,
        "symmetry_representatives": 0, "signatures": [],
        "cheap_top": [], "scan_seconds": 0.0, "scan_complete": False,
        "exact_next": 0, "exact_evaluated": 0, "exact_seconds": 0.0,
        "matching_seconds": 0.0, "exact_top": [], "exact_complete": False,
    }
    if resume and checkpoint_path.exists():
        state = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if (state["left_size"], state["right_size"]) != (left_size, right_size):
            raise ValueError("checkpoint の核サイズが要求と異なる")
    index = SearchIndex.build(P)
    signatures = {tuple(x) for x in state["signatures"]}

    def save() -> None:
        state["signatures"] = [list(x) for x in sorted(signatures)]
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    if not state["scan_complete"]:
        started = time.perf_counter()
        for ordinal in range(state["scan_next"], generated):
            tl, tr = candidate_at(n, left_size, right_size, ordinal)
            state["antichain_passed"] += 1  # singleton は常に反鎖
            lam, rho, s_l, s_r, q_l, q_r, ok = index.kernel_masks(tl, tr)
            if ok:
                state["admissible_passed"] += 1
                signatures.add((lam, rho))
                canonical = (not use_symmetry or
                             canonical_kernel(P, tl, tr) ==
                             (-1 if tl is None else tl, -1 if tr is None else tr))
                if canonical:
                    state["symmetry_representatives"] += 1
                    cheap = {
                        "ordinal": ordinal, "left_kernel": [] if tl is None else [tl],
                        "right_kernel": [] if tr is None else [tr],
                        "lambda_signature": lam, "rho_signature": rho,
                        "s_left_size": popcount(s_l), "s_right_size": popcount(s_r),
                        "q_left_size": popcount(q_l), "q_right_size": popcount(q_r),
                        "heuristic_score": popcount(q_l) + popcount(q_r),
                    }
                    state["cheap_top"].append(cheap)
                    state["cheap_top"] = sorted(
                        state["cheap_top"], key=lambda x: (-x["heuristic_score"], x["ordinal"]))[:200]
            state["scan_next"] = ordinal + 1
            if state["scan_next"] % checkpoint_every == 0:
                state["scan_seconds"] += time.perf_counter() - started
                save()
                started = time.perf_counter()
        state["scan_seconds"] += time.perf_counter() - started
        state["scan_complete"] = True
        save()

    exact_candidates = state["cheap_top"] if max_exact >= 0 else []
    if max_exact < 0:
        exact_candidates = []
        for ordinal in range(generated):
            tl, tr = candidate_at(n, left_size, right_size, ordinal)
            *_, ok = index.kernel_masks(tl, tr)
            canonical = (not use_symmetry or
                         canonical_kernel(P, tl, tr) ==
                         (-1 if tl is None else tl, -1 if tr is None else tr))
            if ok and canonical:
                exact_candidates.append({"ordinal": ordinal})
    else:
        exact_candidates = exact_candidates[:max_exact]
    if max_exact != 0 and not state["exact_complete"]:
        exact_started = time.perf_counter()
        for pos in range(state["exact_next"], len(exact_candidates)):
            ordinal = exact_candidates[pos]["ordinal"]
            tl, tr = candidate_at(n, left_size, right_size, ordinal)
            result = evaluate_kernel_indexed(index, tl, tr)
            state["exact_evaluated"] += 1
            state["matching_seconds"] += result["matching_seconds"]
            serial = {k: list(v) if isinstance(v, tuple) else v for k, v in result.items()}
            serial["ordinal"] = ordinal
            state["exact_top"].append(serial)
            state["exact_top"] = sorted(
                state["exact_top"], key=lambda x: (-x["exponent"], x["ordinal"]))[:20]
            state["exact_next"] = pos + 1
            state["exact_seconds"] += time.perf_counter() - exact_started
            save()
            exact_started = time.perf_counter()
        state["exact_seconds"] += time.perf_counter() - exact_started
        state["exact_complete"] = True
        save()

    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / ("search_%d_%d_summary.json" % (left_size, right_size))
    summary_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    for rank, result in enumerate(state["exact_top"][:10], 1):
        cert = certificate_from_result(result, index, gub_dir)
        cert_path = ROOT / "experiments/lower_bound/certificates" / (
            "g_le_3_k%d_%d_rank%02d_z%d.json" %
            (left_size, right_size, rank, result["exponent"]))
        cert_path.parent.mkdir(parents=True, exist_ok=True)
        cert_path.write_text(json.dumps(cert, ensure_ascii=False, indent=2), encoding="utf-8")
        verify_rectangle(P, cert, list(range(P.n)))
    return state


def regression(gub_dir: Path) -> dict:
    P, meta = reconstruct(gub_dir)
    ids2 = [i for i, b in enumerate(P.birthdays) if b <= 2]
    ants2 = enumerate_antichains(P, ids2)
    width3, max_antichain3 = maximum_antichain(P, list(range(P.n)))
    kernel_best, kernel_pairs = solve_by_kernel_enumeration(P, ids2)
    ip_best, ip_feasible = solve_original_exhaustive(P, ids2)
    if kernel_best["exponent"] != ip_best["exponent"]:
        raise AssertionError("固定核簡約と元 IP 全列挙の最適値が不一致")
    return {
        "counts_by_birthday": meta["counts_by_birthday"],
        "num_G_le_2": len(ids2),
        "num_antichains_G_le_2": len(ants2),
        "num_g3_raw": meta["num_g3_raw"],
        "num_G_le_3": P.n,
        "width_G_le_3": width3,
        "maximum_matching_G_le_3": P.n - width3,
        "maximum_antichain_G_le_3": list(max_antichain3),
        "admissible_kernel_pairs_G_le_2": kernel_pairs,
        "feasible_original_assignments": ip_feasible,
        "kernel_solution": {k: list(v) if isinstance(v, tuple) else v for k, v in kernel_best.items()},
        "original_solution": {k: list(v) if isinstance(v, tuple) else v for k, v in ip_best.items()},
        "python": platform.python_version(),
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gub-dir", type=Path, default=DEFAULT_GUB)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("audit-data")
    sub.add_parser("regression-g2")
    e = sub.add_parser("evaluate-kernel")
    e.add_argument("--left", default="")
    e.add_argument("--right", default="")
    e.add_argument("--level", type=int, default=2)
    v = sub.add_parser("verify-certificate")
    v.add_argument("path", type=Path)
    s = sub.add_parser("search-kernels")
    s.add_argument("--left-kernel-size", type=int, required=True)
    s.add_argument("--right-kernel-size", type=int, required=True)
    s.add_argument("--checkpoint", type=Path, required=True)
    s.add_argument("--output-dir", type=Path,
                   default=ROOT / "experiments/lower_bound/search")
    s.add_argument("--max-exact", type=int, default=0,
                   help="0=scan only, -1=全許容代表, 正数=heuristic 上位数")
    s.add_argument("--resume", action="store_true")
    s.add_argument("--use-symmetry", action="store_true")
    s.add_argument("--checkpoint-every", type=int, default=10000)
    args = parser.parse_args()
    if args.command == "audit-data":
        P, meta = reconstruct(args.gub_dir)
        print(json.dumps({"num_games": P.n, "metadata": meta}, ensure_ascii=False, indent=2))
    elif args.command == "regression-g2":
        print(json.dumps(regression(args.gub_dir), ensure_ascii=False, indent=2))
    elif args.command == "evaluate-kernel":
        P, _ = reconstruct(args.gub_dir)
        ids = [i for i, b in enumerate(P.birthdays) if b <= args.level]
        parse = lambda s: tuple(int(x) for x in s.split(",") if x.strip())
        print(json.dumps(evaluate_kernel(P, parse(args.left), parse(args.right), ids),
                         ensure_ascii=False, indent=2))
    elif args.command == "verify-certificate":
        P, _ = reconstruct(args.gub_dir)
        cert = json.loads(args.path.read_text(encoding="utf-8"))
        if "source_data_hashes" in cert:
            actual = source_hashes(args.gub_dir)
            if cert["source_data_hashes"] != actual:
                raise ValueError("certificate の入力 hash が現在の正本データと一致しない")
        level = int(cert["ground_set"].rsplit("_", 1)[1])
        ids = [i for i, b in enumerate(P.birthdays) if b <= level]
        verify_rectangle(P, cert, ids)
        print("証明書の検証に成功しました: |G_le_%d| から |G_le_%d| >= 2^%d"
              % (level, level + 1, cert["exponent"]))
    else:
        P, _ = reconstruct(args.gub_dir)
        result = search_kernels(
            P, args.gub_dir, args.left_kernel_size, args.right_kernel_size,
            args.checkpoint, args.output_dir, args.max_exact, args.resume,
            args.use_symmetry, args.checkpoint_every)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
