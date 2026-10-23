#!/usr/bin/env python3
"""正本 docs/safe_profile_definitions.md による G_le_2 safe-profile 完全計数。"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path

import glb_lower_bound as lb


ROOT = Path(__file__).resolve().parent
DEFINITIONS = ROOT / "docs/safe_profile_definitions.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def inclusion_minimal(sets):
    """重複を除き、包含関係の極小集合だけを決定的順序で返す。"""
    unique = set(frozenset(s) for s in sets)
    minimal = [s for s in unique if not any(t < s for t in unique)]
    return tuple(sorted((tuple(sorted(s)) for s in minimal), key=lambda s: (len(s), s)))


def profile_direct(P: lb.Universe, left_antichain, G_le_1, G_le_2):
    # Z(L) = union l^R
    Z = tuple(sorted({y for l in left_antichain for y in P.right[l]}))
    # Gamma_2(L) = {x in G_le_1 | exists l in L: x <= l}
    gamma = tuple(sorted(x for x in G_le_1 if any(P.leq(x, l) for l in left_antichain)))
    # H_2(L) = inclusion-minimal members of {D_2(y) | y in Z(L)}
    downsets = [{g for g in G_le_2 if P.leq(g, y)} for y in Z]
    H = inclusion_minimal(downsets)
    # B_Gamma = {r in G_le_2 | r^L subset Gamma}
    gamma_set = set(gamma)
    B = tuple(sorted(r for r in G_le_2 if set(P.left[r]) <= gamma_set))
    return Z, H, gamma, B


def profile_key(H, gamma):
    return H, gamma


def hits_all(right_antichain, H):
    R = set(right_antichain)
    return all(bool(R.intersection(h)) for h in H)


def render_md(result):
    lines = [
        "# `G_le_2 -> G_le_3` safe-profile直接定義による完全計数", "",
        "## 結論", "",
        "理論上の正本 `docs/safe_profile_definitions.md` の定義を直接実装し、",
        "`G_le_2` の98左反鎖を全て分類した。GUB由来の",
        "`Ymin/Hmin/trig/up/hit/residual` は使用していない。", "",
        f"- `|A(G_le_2)|`: `{result['antichain_count']}`",
        f"- distinct profile数: `{result['profile_count']}`",
        f"- `sum_pi |C_pi|`: `{result['sum_class_sizes']}`",
        f"- `sum_pi |C_pi| |R_pi|`: `{result['profile_aggregated_total']}`",
        f"- 左反鎖ごとの直接計数: `{result['direct_left_total']}`",
        f"- 二つの計数の一致: `{result['totals_match']}`", "",
        "既知値 `516,623,817,1448` への適合は行っていない。上記は現在の正本定義から",
        "得られた値をそのまま報告したものである。", "",
        "## 実装した定義", "",
        "各 `L` について `Z(L)`、`Gamma_2(L)`、包含極小な下集合族",
        "`H_2(L)`、`B_Gamma` を元データの左右選択肢と順序から直接計算した。",
        "profileは `(H_2(L),Gamma_2(L))`。各profileについて `C_pi` を左反鎖のlist、",
        "`R_pi` を `B_Gamma` に含まれ、全 `H` をhitする反鎖のlistとして保存した。", "",
        "## profile一覧", "",
        "|ID|`|C_pi|`|`|R_pi|`|積|`|Gamma|`|`|H|`|`|B_Gamma|`|",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in result["profiles"]:
        lines.append(
            f"|{p['profile_id']}|{p['class_size']}|{p['right_family_size']}|"
            f"{p['contribution']}|{len(p['gamma'])}|{len(p['H'])}|{len(p['B_gamma'])}|"
        )
    lines += ["", "## 独立な一致確認", "",
              "profile集約では `sum |C_pi|*|R_pi|` を計算した。直接計数では各左反鎖",
              "`L` ごとに98個の `G_le_2` 反鎖を再走査し、`R subseteq B_Gamma_2(L)`",
              "かつ全 `H in H_2(L)` をhitするものを数え、その和を取った。両者を整数で",
              "assertし一致した。さらに各profileの `R_pi` は、`B_Gamma` 上で直接",
              "列挙した反鎖族とも一致することをassertした。", "",
              "## 入力", ""]
    for path, digest in result["source_hashes"].items():
        lines.append(f"- `{path}`: `{digest}`")
    lines += ["", "## 再現コマンド", "", "```bash",
              "python3 safe_profile_g2_exact.py", "```", "",
              f"実行時間: `{result['runtime_seconds']:.6f}` 秒。",
              f"実行環境: Python `{result['environment']['python']}`, "
              f"`{result['environment']['platform']}`。", "",
              "## 制限", "",
              "- `G_le_2 -> G_le_3` の小ケースだけを対象とした。",
              "- safe-profile DP、12鎖pilot、`G_le_3` 全反鎖列挙は行っていない。",
              "- この計数の理論的解釈は正本文書に従い、旧reversible-type実装との",
              "  同値性を仮定していない。", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path,
                        default=ROOT / "experiments/lower_bound/safe_profile/g2_exact.json")
    parser.add_argument("--md-output", type=Path,
                        default=ROOT / "reports/lower_bound/safe_profile_g2_exact_ja.md")
    args = parser.parse_args()
    started = time.perf_counter()
    if not DEFINITIONS.is_file():
        raise FileNotFoundError(DEFINITIONS)
    P, metadata = lb.reconstruct()
    G_le_1 = tuple(g for g, b in enumerate(P.birthdays) if b <= 1)
    G_le_2 = tuple(g for g, b in enumerate(P.birthdays) if b <= 2)
    antichains = tuple(lb.enumerate_antichains(P, G_le_2))
    if (len(G_le_1), len(G_le_2), len(antichains)) != (4, 22, 98):
        raise AssertionError((len(G_le_1), len(G_le_2), len(antichains)))

    computed = {}
    classes = defaultdict(list)
    for L in antichains:
        Z, H, gamma, B = profile_direct(P, L, G_le_1, G_le_2)
        key = profile_key(H, gamma)
        computed[L] = (Z, H, gamma, B, key)
        classes[key].append(L)

    profiles = []
    right_by_key = {}
    ordered_keys = sorted(classes, key=lambda k: (k[1], k[0]))
    for profile_id, key in enumerate(ordered_keys):
        H, gamma = key
        B_values = {computed[tuple(L)][3] for L in classes[key]}
        if len(B_values) != 1:
            raise AssertionError("同じGammaでB_Gammaが一致しない")
        B = next(iter(B_values))
        B_set = set(B)
        # 全ground反鎖をfilterする列挙。
        R_filtered = tuple(R for R in antichains if set(R) <= B_set and hits_all(R, H))
        # A(B_Gamma)を別に列挙して同じhitting条件でfilterするクロスチェック。
        R_from_B = tuple(R for R in lb.enumerate_antichains(P, B) if hits_all(R, H))
        if R_filtered != R_from_B:
            raise AssertionError((profile_id, R_filtered, R_from_B))
        right_by_key[key] = R_filtered
        contribution = len(classes[key]) * len(R_filtered)
        profiles.append({
            "profile_id": profile_id, "H": [list(h) for h in H], "gamma": list(gamma),
            "B_gamma": list(B), "C_pi": [list(L) for L in classes[key]],
            "R_pi": [list(R) for R in R_filtered], "class_size": len(classes[key]),
            "right_family_size": len(R_filtered), "contribution": contribution,
        })

    profile_total = sum(p["contribution"] for p in profiles)
    direct_details = []
    direct_total = 0
    for L in antichains:
        Z, H, gamma, B, key = computed[L]
        B_set = set(B)
        right = tuple(R for R in antichains if set(R) <= B_set and hits_all(R, H))
        if right != right_by_key[key]:
            raise AssertionError("同一profileの右族が一致しない")
        direct_total += len(right)
        direct_details.append({
            "L": list(L), "Z": list(Z), "H": [list(h) for h in H],
            "gamma": list(gamma), "B_gamma": list(B),
            "right_count": len(right),
        })
    if sum(len(v) for v in classes.values()) != 98 or profile_total != direct_total:
        raise AssertionError((profile_total, direct_total))

    sources = {
        "docs/safe_profile_definitions.md": sha256(DEFINITIONS),
        "../GUB/game_export/games.csv": sha256(lb.DEFAULT_GUB / "game_export/games.csv"),
        "../GUB/game_export/leq_rows.hex": sha256(lb.DEFAULT_GUB / "game_export/leq_rows.hex"),
        "../GUB/game_export/metadata.json": sha256(lb.DEFAULT_GUB / "game_export/metadata.json"),
    }
    result = {
        "status": "EXACT COMPLETE",
        "definition_source": "docs/safe_profile_definitions.md",
        "legacy_reversible_type_code_used": False,
        "ground_set": "G_le_2", "G_le_1_size": len(G_le_1),
        "G_le_2_size": len(G_le_2), "antichain_count": len(antichains),
        "profile_count": len(profiles), "sum_class_sizes": sum(p["class_size"] for p in profiles),
        "profile_aggregated_total": profile_total, "direct_left_total": direct_total,
        "totals_match": True, "profiles": profiles,
        "left_antichain_direct_counts": direct_details,
        "source_hashes": sources, "metadata_counts_by_birthday": metadata["counts_by_birthday"],
        "runtime_seconds": time.perf_counter() - started,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.md_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.md_output.write_text(render_md(result), encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "status", "antichain_count", "profile_count", "sum_class_sizes",
        "profile_aggregated_total", "direct_left_total", "totals_match")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
