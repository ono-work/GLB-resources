#!/usr/bin/env python3
"""PDF/正本定義による G_le_3 小部分ポセット safe-profile 完全pilot。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from collections import Counter
from pathlib import Path

import glb_lower_bound as lb


ROOT = Path(__file__).resolve().parent
PDF = ROOT / "docs/GPW_LB (1).pdf"
DEFINITIONS = ROOT / "docs/safe_profile_definitions.md"
CHAINS = lb.DEFAULT_GUB / "chains86_ls.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_export_chains(P: lb.Universe):
    data = json.loads(CHAINS.read_text(encoding="utf-8"))
    raw = data["chains"] if isinstance(data, dict) else data
    id_type = data.get("id_type", "orig_gid") if isinstance(data, dict) else "orig_gid"
    if id_type == "export_id":
        chains = [list(map(int, c)) for c in raw]
    elif id_type == "orig_gid":
        inverse = {gid: i for i, gid in enumerate(P.orig_gids)}
        chains = [[inverse[int(g)] for g in c] for c in raw]
    else:
        raise ValueError(f"未知のchain id_type: {id_type}")
    flat = [x for c in chains for x in c]
    if len(chains) != 86 or len(flat) != P.n or len(set(flat)) != P.n:
        raise AssertionError("86鎖がG_le_3を重複なく被覆しない")
    if not all(P.comparable(c[i], c[j]) for c in chains for i in range(len(c))
               for j in range(i + 1, len(c))):
        raise AssertionError("chain内に比較不能対がある")
    return chains, id_type


def profile_support(P: lb.Universe, G_le_2):
    index2 = {x: i for i, x in enumerate(G_le_2)}
    z_contrib = []
    gamma_contrib = []
    for l in range(P.n):
        if any(y not in index2 for y in P.right[l]):
            raise AssertionError("l^RがG_le_2外")
        z_contrib.append(sum(1 << index2[y] for y in P.right[l]))
        gamma_contrib.append(sum(1 << i for i, x in enumerate(G_le_2) if P.leq(x, l)))
    downsets = []
    for y in G_le_2:
        downsets.append(sum(1 << g for g in range(P.n) if P.leq(g, y)))
    return index2, z_contrib, gamma_contrib, downsets


def h_from_z(z_mask: int, downsets):
    """min_subset {D_3(y): y bit is in z_mask} をdownset mask族で返す。"""
    unique = sorted({downsets[i] for i in range(len(downsets)) if (z_mask >> i) & 1})
    return tuple(d for d in unique if not any(e != d and e & ~d == 0 for e in unique))


def h_y_ids(H, downsets, G_le_2):
    return [min(G_le_2[i] for i, d in enumerate(downsets) if d == h) for h in H]


def direct_antichains(P, elements):
    return tuple(lb.enumerate_antichains(P, tuple(elements)))


def direct_profile(P, L, index2, z_contrib, gamma_contrib, downsets):
    z = gamma = 0
    for l in L:
        z |= z_contrib[l]
        gamma |= gamma_contrib[l]
    return h_from_z(z, downsets), gamma, z


def left_profile_dp(P, elements, z_contrib, gamma_contrib, downsets):
    n = len(elements)
    comp = []
    for x in elements:
        comp.append(sum(1 << j for j, y in enumerate(elements) if P.comparable(x, y)))
    memo = {}
    calls = hits = 0

    def visit(residual, z_mask, gamma_mask):
        nonlocal calls, hits
        calls += 1
        key = residual, z_mask, gamma_mask
        if key in memo:
            hits += 1
            return memo[key]
        if not residual:
            out = Counter({(h_from_z(z_mask, downsets), gamma_mask): 1})
        else:
            bit = residual & -residual
            i = bit.bit_length() - 1
            rest = residual ^ bit
            out = visit(rest, z_mask, gamma_mask).copy()
            out.update(visit(rest & ~comp[i], z_mask | z_contrib[elements[i]],
                             gamma_mask | gamma_contrib[elements[i]]))
        memo[key] = out
        return out

    counts = visit((1 << n) - 1, 0, 0)
    return counts, {"memo_states": len(memo), "calls": calls, "memo_hits": hits,
                    "merge_count": hits}


def b_gamma_local(P, elements, G_le_2, gamma_mask):
    index2 = {x: i for i, x in enumerate(G_le_2)}
    gamma = {x for x, i in index2.items() if (gamma_mask >> i) & 1}
    return tuple(r for r in elements if set(P.left[r]) <= gamma)


def hits_profile_on_p(R, H, p_mask):
    rmask = sum(1 << r for r in R)
    return all(bool(rmask & h & p_mask) for h in H)


def right_dp_count(P, elements, eligible, H):
    n = len(elements)
    p_index = {x: i for i, x in enumerate(elements)}
    requirement_local = []
    for h in H:
        requirement_local.append(sum(1 << p_index[x] for x in elements if (h >> x) & 1))
    if any(m == 0 for m in requirement_local):
        return 0, {"memo_states": 0, "calls": 0, "memo_hits": 0}
    full_hit = (1 << len(H)) - 1
    comp = [sum(1 << j for j, y in enumerate(elements) if P.comparable(x, y))
            for x in elements]
    add_hit = [sum(1 << k for k, req in enumerate(requirement_local) if (req >> i) & 1)
               for i in range(n)]
    initial = sum(1 << p_index[x] for x in eligible)
    memo = {}
    calls = hits = 0

    def visit(residual, hit_mask):
        nonlocal calls, hits
        calls += 1
        key = residual, hit_mask
        if key in memo:
            hits += 1
            return memo[key]
        if not residual:
            value = int(hit_mask == full_hit)
        else:
            bit = residual & -residual
            i = bit.bit_length() - 1
            rest = residual ^ bit
            value = visit(rest, hit_mask) + visit(rest & ~comp[i], hit_mask | add_hit[i])
        memo[key] = value
        return value

    value = visit(initial, 0)
    return value, {"memo_states": len(memo), "calls": calls, "memo_hits": hits}


def run_one(P, chain_count, chains, G_le_2, support, include_profile_table=False):
    index2, z_contrib, gamma_contrib, downsets = support
    # 決定規則: chain JSONの先頭k鎖から、各鎖の末尾（<=順の最大側）を1元取る。
    selected_chains = [c for c in chains if c][:chain_count]
    elements = tuple(c[-1] for c in selected_chains)
    started = time.perf_counter()
    ants = direct_antichains(P, elements)
    direct_counts = Counter()
    direct_meta = {}
    for L in ants:
        H, gamma, z = direct_profile(P, L, index2, z_contrib, gamma_contrib, downsets)
        direct_counts[(H, gamma)] += 1
        direct_meta[L] = H, gamma, z
    direct_seconds = time.perf_counter() - started

    dp_started = time.perf_counter()
    dp_counts, dp_stats = left_profile_dp(P, elements, z_contrib, gamma_contrib, downsets)
    dp_seconds = time.perf_counter() - dp_started
    if direct_counts != dp_counts:
        raise AssertionError("左profile別DPが直接列挙と不一致")

    p_mask = sum(1 << x for x in elements)
    profile_rows = []
    profile_sum = right_states = 0
    for profile_id, ((H, gamma), c) in enumerate(sorted(direct_counts.items(),
            key=lambda kv: (kv[0][1], kv[0][0]))):
        eligible = b_gamma_local(P, elements, G_le_2, gamma)
        direct_R = tuple(R for R in ants if set(R) <= set(eligible)
                         and hits_profile_on_p(R, H, p_mask))
        right_count, right_stats = right_dp_count(P, elements, eligible, H)
        if right_count != len(direct_R):
            raise AssertionError("右hit DPが直接列挙と不一致")
        contribution = c * len(direct_R)
        profile_sum += contribution
        right_states += right_stats["memo_states"]
        profile_rows.append({
            "profile_id": profile_id,
            "H_y_ids": h_y_ids(H, downsets, G_le_2),
            "H_downset_masks_hex": [hex(h) for h in H],
            "gamma_mask": gamma, "gamma_ids": [G_le_2[i] for i in range(22)
                                                   if (gamma >> i) & 1],
            "direct_left_count": c, "dp_left_count": dp_counts[(H, gamma)],
            "B_gamma_P": list(eligible), "right_family_size": len(direct_R),
            "right_antichains": [list(R) for R in direct_R] if include_profile_table else None,
            "contribution": contribution, "right_dp_stats": right_stats,
        })

    pair_started = time.perf_counter()
    direct_pairs = 0
    for L in ants:
        H, gamma, _ = direct_meta[L]
        eligible = set(b_gamma_local(P, elements, G_le_2, gamma))
        direct_pairs += sum(set(R) <= eligible and hits_profile_on_p(R, H, p_mask) for R in ants)
    pair_seconds = time.perf_counter() - pair_started
    if direct_pairs != profile_sum:
        raise AssertionError("直接pair走査とprofile積和が不一致")
    largest_class = max(profile_rows, key=lambda r: (r["direct_left_count"], -r["profile_id"]))
    largest_contribution = max(profile_rows, key=lambda r: (r["contribution"], -r["profile_id"]))
    return {
        "name": f"first_{chain_count}_chain_maxima", "selection_rule":
            "chains86_ls.jsonの非空鎖を記録順に取り、各鎖の末尾要素を1個選ぶ",
        "chain_count": chain_count, "element_count": len(elements), "element_ids": list(elements),
        "antichain_count": len(ants), "distinct_profile_count": len(direct_counts),
        "profile_rows": profile_rows,
        "left_dp": dp_stats, "right_dp_total_memo_states": right_states,
        "direct_enumeration_seconds": direct_seconds, "left_dp_seconds": dp_seconds,
        "direct_pair_seconds": pair_seconds, "total_seconds": time.perf_counter() - started,
        "direct_pair_count": direct_pairs, "profile_product_sum": profile_sum,
        "pair_count_matches": True, "profiles_match_direct_vs_dp": True,
        "largest_profile_class": {k: largest_class[k] for k in
                                  ("profile_id", "direct_left_count", "right_family_size")},
        "largest_contribution_profile": {k: largest_contribution[k] for k in
                                         ("profile_id", "contribution", "direct_left_count",
                                          "right_family_size")},
    }


def build_pilots(chain_counts=(8, 10, 12)):
    P, metadata = lb.reconstruct()
    G_le_2 = tuple(g for g, b in enumerate(P.birthdays) if b <= 2)
    if len(G_le_2) != 22 or P.n != 1474:
        raise AssertionError("ground size不一致")
    chains, id_type = load_export_chains(P)
    support = profile_support(P, G_le_2)
    pilots = [run_one(P, k, chains, G_le_2, support, include_profile_table=(i == 0))
              for i, k in enumerate(chain_counts)]
    return pilots, metadata, id_type


def render_md(result):
    lines = [
        "# `G_le_3 -> G_le_4` safe-profile小部分ポセットpilot", "",
        "## 理論上の正本とPDF確認", "",
        "`GPW_LB (1).pdf` §4.1は一般profile `(S,H)` と `R(S,H)`、§4.2は",
        "`Pi_0(L)=(H_i(L),Gamma_i(L))`, `B_Gamma`, `C_pi`, `R_pi`、§4.3は",
        "hit条件付き反鎖数え上げへの帰着を記述する。本pilotはPDFを最優先し、",
        "`docs/safe_profile_definitions.md` が具体化する", "",
        "```text", "Z(L)=union l^R",
        "Gamma_3(L)={x in G_le_2: exists l in L, x<=l}",
        "H_3(L)=min_subset {D_3(y): y in Z(L)}", "```", "",
        "を直接実装した。PDF §4.3の左側hit付き反鎖式だけでは `H_3(L)=H` を",
        "課していないため、その式を左profile classのexact countには使用していない。",
        "完成した各左反鎖から `Z,H,Gamma` を復元し、等号で分類した。", "",
        "GUB由来の `Ymin/Hmin/trig/up/hit/residual` およびreversible-type DPは",
        "使用していない。", "",
        "## 結果", "",
        "|pilot|`|P|`|反鎖数|profile数|左memo state|merge|右memo state合計|直接pair|profile積和|一致|総秒|",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for p in result["pilots"]:
        lines.append(
            f"|{p['name']}|{p['element_count']}|{p['antichain_count']}|"
            f"{p['distinct_profile_count']}|{p['left_dp']['memo_states']}|"
            f"{p['left_dp']['merge_count']}|{p['right_dp_total_memo_states']}|"
            f"{p['direct_pair_count']}|{p['profile_product_sum']}|yes|{p['total_seconds']:.6f}|"
        )
    lines += ["", "全pilotでprofile別左個数、右hit族、直接pair数とprofile積和が整数で",
              "完全一致した。これらは小部分ポセット上の回帰値であり、正式な",
              "`G_le_4` 下界ではない。", "", "## pilot構成", ""]
    for p in result["pilots"]:
        lines += [f"### `{p['name']}`", "",
                  f"- 選択規則: {p['selection_rule']}。",
                  f"- export ID: `{p['element_ids']}`",
                  f"- 最大class: `{p['largest_profile_class']}`",
                  f"- 最大寄与profile: `{p['largest_contribution_profile']}`", ""]
    first = result["pilots"][0]
    lines += ["## 8鎖pilotの全profile", "",
              "`H` は `D_3(y)` の包含極小族。pilotのhit判定では各downsetと `P` の",
              "共通部分を使用した。", "",
              "|profile|Hのy ID|Gamma ID|左直接|左DP|`|R_pi^P|`|寄与|",
              "|---:|---|---|---:|---:|---:|---:|"]
    for row in first["profile_rows"]:
        lines.append(f"|{row['profile_id']}|`{row['H_y_ids']}`|`{row['gamma_ids']}`|"
                     f"{row['direct_left_count']}|{row['dp_left_count']}|"
                     f"{row['right_family_size']}|{row['contribution']}|")
    lines += ["", "## 状態と検査", "",
              "左DPのmemo keyは `(residual_candidates,z_mask,gamma_mask)`。候補の",
              "exclude/include分枝を固定ID順で行い、include時に比較可能候補を除いた。",
              "完成時だけ `z_mask` から包含極小downset族 `H` を作る。右DPはprofileごとに",
              "`(residual_candidates,local_requirement_hit_mask)` を用いた。", "",
              "直接列挙とDPは同じprofile keyを用いるだけでなく、直接pair走査を別に行い、",
              "profile積和との一致もassertした。状態をresidualだけでmergeしていない。", "",
              "## 入力hash", ""]
    for path, digest in result["source_hashes"].items():
        lines.append(f"- `{path}`: `{digest}`")
    lines += ["", "## 再現", "", "```bash", "python3 safe_profile_g3_pilot.py",
              "python3 -m unittest tests.test_safe_profile_g3_pilot -v", "```", "",
              f"環境: Python `{result['environment']['python']}`, `{result['environment']['platform']}`。",
              "乱数不使用。full 86鎖DP、G_le_3全反鎖列挙、大規模探索は未実施。", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-output", type=Path,
                    default=ROOT / "experiments/lower_bound/safe_profile/g3_pilot.json")
    ap.add_argument("--md-output", type=Path,
                    default=ROOT / "reports/lower_bound/safe_profile_g3_pilot_ja.md")
    args = ap.parse_args()
    started = time.perf_counter()
    pilots, metadata, id_type = build_pilots()
    result = {
        "status": "PILOT PASSED", "scope": "small induced subsets only; no G_le_4 bound claim",
        "theory_priority": ["docs/GPW_LB (1).pdf", "docs/safe_profile_definitions.md",
                            "reports/lower_bound/safe_profile_g2_exact_ja.md",
                            "reports/lower_bound/safe_profile_g2_alignment_ja.md"],
        "pdf_sections_checked": ["4.1", "4.2", "4.3"],
        "pdf_left_hit_caveat": "section 4.3 left hit count alone does not impose H_i(L)=H",
        "legacy_GUB_reversible_type_code_used": False,
        "chain_id_type": id_type, "pilots": pilots,
        "metadata_counts_by_birthday": metadata["counts_by_birthday"],
        "runtime_seconds": time.perf_counter() - started,
        "source_hashes": {
            "docs/GPW_LB (1).pdf": sha256(PDF),
            "docs/safe_profile_definitions.md": sha256(DEFINITIONS),
            "../GUB/chains86_ls.json": sha256(CHAINS),
            "../GUB/game_export/games.csv": sha256(lb.DEFAULT_GUB / "game_export/games.csv"),
            "../GUB/game_export/leq_rows.hex": sha256(lb.DEFAULT_GUB / "game_export/leq_rows.hex"),
            "../GUB/game_export/metadata.json": sha256(lb.DEFAULT_GUB / "game_export/metadata.json"),
        },
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.md_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.md_output.write_text(render_md(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "pilots": [
        {k: p[k] for k in ("name", "antichain_count", "distinct_profile_count",
                           "direct_pair_count", "profile_product_sum")}
        for p in pilots]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
