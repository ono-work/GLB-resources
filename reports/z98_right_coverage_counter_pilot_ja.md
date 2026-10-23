# z=98 反転最適核：共通右 coverage counter pilot

## 結論

30個の残差プロフィールを12-bit coverage maskへ圧縮する表現は正しく、既存の共通最大反鎖まわり Layer 0--2 を完全再現した。さらに Layer 3 を exact に計数し、昇順主計算と降順独立 verifier が一致した。

一方、1238頂点の共通右候補ポセットの**全反鎖**を coverage 別に数える計算は、branch-and-reduce と frontier DP の実測から現在の環境で安定して12時間以内に完了する見込みがない。このため full exact は開始せず、部分計数も正式値に用いていない。

status は次の通りである。

```text
COVERAGE_MODEL_VERIFIED
LAYER02_COVERAGE_REPRODUCED
FULL_COVERAGE_EXACT_TOO_LARGE
COVERAGE_LAYER3_VERIFIED
COVERAGE_COUNTER_PROMISING
AUDIT PASSED
```

## Coverage と Ω

到達条件 universe は

\[
U_H=\{0,1,3,4,6,9,10,12,15,16,17,19\},\qquad |U_H|=12.
\]

1238個の右候補が持つ coverage pattern は49種類であった。全左プロフィール重みから構成した4096項の \(\Omega(C)\) は、プロフィール直接和と zeta 変換の二経路で一致した。

* 正のmask：4034
* 0のmask：62
* 最大値：27120959434（full mask 4095）
* SHA-256：`aa67a68e56aa2e2df4ba4201122d7f45982bf6fc7b53dab51dce16aaac65f57d`

## Layer 0--3

coverage histogram と重み付き寄与は次の通りである。

| Layer | 右反鎖総数 | 重み付き残差寄与 |
|---:|---:|---:|
| 0 | 4835703278458516698824704 | 0 |
| 1 | 80115895914374240879248062 | 10777368195350123900411630720 |
| 2 | 659251960673642139952463147 | 152691887023040758403122277775 |
| 3 | （coverage histogram の総和としてcertificateに保存） | 1083579386272311919193775426145 |

Layer 0--2 の累積寄与は

\[
163469255218390882303533908495
\]

であり、既存値をexactに再現した。Layer 3では、\(X\) 上の三元反鎖を全列挙し、

* 三元反鎖数：32022499
* category数：17087769
* 最大category multiplicity：178447

を得た。Layer 0--3 の共通族単独寄与は

\[
C_{0:3}=1247048641490702801497309334640.
\]

これは既存プロフィール別残差寄与

\[
C_{\rm old}=1557410333878683939788039423140
\]

の約0.800719倍である。両右族は重なり得るため加算せず、プロフィール別maxを採る現行の監査済み下界

\[
1416780686143449296616167856189137167
\]

は変わらない。したがって今回の改善倍率は1であり、今回の結果だけでは \(10^{37}\) を超えない。

## Full exact preflight

branch-and-reduce の誘導部分グラフ試験は次の通りである。

* 100頂点：0.059秒、5643 memo states
* 200頂点：16.51秒、1138579 memo states
* 400、600、800頂点：各30秒capで未完了

frontier幅の最大値は、export順1232、逆export順1232、degree順1237、reverse-degree順1100であった。観測最小でも1100であり、coverage係数を持つfrontier tableには大きすぎる。既存ZDDライブラリはなく、比較可能グラフは単一の密な連結成分で、小さいbalanced separatorも確認できなかった。よって full run は実行していない。

## 構造圧縮

49 pattern間の1225組は、完全比較34、完全非比較361、mixed 830であった。mixed が支配的なので pattern quotient はexactな商として使えない。また、coverageと完全近傍を含むsignatureによる真のtwin classは1238クラス、非自明classは0であり、twin圧縮後も1238頂点である。

## 評価と次段階

Layer寄与は \(C_2/C_1\simeq14.168\)、\(C_3/C_2\simeq7.097\) と増加した。したがって coverage 集約は**固定Layerのexact計数方式としては有望**であり、Layer 4を専用category counterで試す価値がある。ただし全反鎖counterとしては現状弱く、pattern/twin圧縮だけでは突破できない。

次の優先順位は、(1) 共通coverage Layer 4の作業量benchmark、(2) weighted column generation、(3) canonical Layer 7高速化、とするのが自然である。Layer 4は自動実行していない。

## 再現

```bash
python3 z98_right_coverage_counter_pilot.py
python3 benchmark_z98_right_coverage_counters.py
python3 run_z98_right_coverage_layer3.py
python3 verify_z98_right_coverage_counter_pilot.py
python3 finalize_z98_right_coverage_counter_pilot.py
python3 -m pytest -q tests/test_z98_right_coverage_counter_pilot.py
```

主要なmachine-readable結果は `experiments/lower_bound/z98_right_coverage_counter_pilot/` 以下に保存した。
