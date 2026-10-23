# z=98反転核：coverage Layer 4十分統計とexact union

## 結論

82-bit禁止集合そのものを保存せず、Layer 4 completion数を決定する十分統計へ圧縮することで、2,228,288,640個の四元反鎖をexactに処理した。

* 旧full-category推定：853246550
* 十分統計S1 signature：4501
* 圧縮倍率：約189568倍
* 主計算：102.52秒
* 降順独立verifier：117.02秒
* peak RAM：約1.25 MB

Layer 4寄与は

\[
C_4=5149221482392701998802598499334.
\]

old族とのLayer 4 weighted intersectionをexactに除いた新下界は

\[
\boxed{1416787082413573180019853416520646491}.
\]

statusは次の通りである。

```text
SUFFICIENT_STAT_LAYER4_VERIFIED
SUFFICIENT_STAT_LAYER4_HIGHLY_PROMISING
LAYER4_UNION_VERIFIED
LAYER4_UNION_HIGHLY_PROMISING
AUDIT PASSED
```

## 十分統計lemma

外側反鎖 \(Y\) の禁止集合を \(B(Y)\subseteq M\)、coverageを \(c(Y)\) とする。プロフィール \(\pi\) の残余条件は \(K_\pi(Y)=H_\pi\setminus c(Y)\) である。包除原理から

\[
N_\pi(Y)=
\sum_{J\subseteq K_\pi(Y)}(-1)^{|J|}
2^{82-|B(Y)|-|U_M(J)|+|B(Y)\cap U_M(J)|}.
\]

従って全プロフィールのcompletion数は、

\[
\left(c(Y), |B(Y)|,
(|B(Y)\cap U_M(J)|)_J\right)
\]

だけで決まる。これは固定最大反鎖、有限hit universe、有限プロフィール集合について一般に成立し、今回の30プロフィールに依存しない。

今回のデータでは \(M\) のcoverage pattern分布が

\[
0:79,qquad1:1,qquad4:1,qquad128:1
\]

である。全ての \(U_M(J)\) は後三者の相異なるsingleton hit元の部分集合なので、正式S1はさらに

\[
\sigma(Y)=(c(Y),,|B(Y)|,,\operatorname{blocked}(Y))
\]

へ可逆に表現できる。`blocked` は3-bitである。これは座標の経験的削除ではなく、正本から検証した \(U_M(J)\) の一致に基づく。

## relevant hit unions

30プロフィール全体から生じるdistinct \(J\) は空集合を含め48種類だった。Layer 4で実際に現れたcoverageは49種類であり、coverageごとの \(|\mathcal J(c)|\) は次の通りである。

* 最小：1
* 最大：48
* 平均：17.612244897959183
* 中央値：17

分布の完全表は `relevant_hit_unions.json` に保存した。

## S1とS2

S1はpacked表現でcoverage 2 byte、禁止数1 byte、blocked mask 2 byteの計5 byteである。S2はcoverageと4 coverage-pattern countで計6 byteとなる。

今回のpattern分布では、S2の \((n_0,n_1,n_4,n_{128})\) からS1は明らかに復元できる。逆にS1からsingleton patternの三係数はblocked bitで、\(n_0\) は禁止総数との差で復元できる。従って両者は同じ4501分割を与えるが、S1の方が短いのでS1を採用した。

5.3948% prefixでは120212690候補が3745 signatureへ圧縮され、圧縮率は約32099.5だった。fullでは2228288640候補が4501 signature、約495065倍に圧縮された。globalな82-bit category表もbounded cacheも不要だった。

## Layer 4 exact計数

昇順主計算と降順verifierは、四元反鎖数、4501 signatureの全multiplicity、30個の \(r_{\pi,4}\)、\(C_4\) で完全一致した。

\[
\frac{C_4}{C_3}=4.752048209505771,
\]

\[
C_{0:4}=6396270123883404800299907833974,
\]

\[
\frac{C_{0:4}}{C_{\rm old}}=4.106990935364918.
\]

profile別ではcommon 0--4がold族を上回るものが6、oldが上回るものが24、同値0だった。common優勢profileの左重みは865874431、profilewise max寄与は6564367343290482350460585730381である。

### 全30プロフィール

| H | W | r4 | common 0--4 | old | 優勢 |
|---:|---:|---:|---:|---:|:---|
| 2 | 31136 | 14665328 | 18476564 | 13507071822 | old |
| 16 | 22551966 | 3215 | 4322 | 907 | common |
| 65 | 139655767 | 3952706213 | 5099861747 | 13992438251392 | old |
| 66 | 1480025126 | 295967 | 313661 | 97569198 | old |
| 512 | 30830 | 14333295010505 | 18803410900216 | 8086863282340233 | old |
| 576 | 1005476850 | 1859020 | 1971958 | 209671240639 | old |
| 1024 | 18089346 | 224348 | 239597 | 1343287 | old |
| 1026 | 178198142 | 34392 | 38320 | 138680 | old |
| 4098 | 150984586 | 9666740 | 11825040 | 6070974208 | old |
| 4608 | 142671919 | 7348969759073 | 9606124105155 | 3656207185547680 | old |
| 32776 | 225467 | 17645785194461648008064 | 21919431839955728442078 | 5023826447417311159039 | common |
| 32832 | 1772213756 | 71004387 | 83546248 | 15047382553611 | old |
| 36872 | 283016864 | 8831013267195226547932 | 10968429010495642368660 | 2347488054649372006643 | common |
| 65538 | 1480025126 | 295967 | 313661 | 100037650 | old |
| 65544 | 139655767 | 3952706213 | 5099861747 | 14282340723275 | old |
| 65600 | 1004447550 | 1343453 | 1410764 | 31499090505 | old |
| 65602 | 3236940354 | 158337 | 169533 | 24522630 | old |
| 66048 | 1005476850 | 1859020 | 1971958 | 209671240639 | old |
| 66112 | 1358264594 | 819966 | 862771 | 3293495629 | old |
| 131073 | 225467 | 17645785194461648008064 | 21919431839955728442078 | 5102038850611649475346 | common |
| 135169 | 283016864 | 8831013267195226547932 | 10968429010495642368660 | 2287487818231732224171 | common |
| 163840 | 218128 | 2996390752240233693 | 3492486591729665093 | 291401211771313091798 | old |
| 167936 | 721039556 | 1499720704854927399 | 1747817961211826180 | 139045522624225449112 | old |
| 196608 | 1772213756 | 71004387 | 83546248 | 15047382553611 | old |
| 524290 | 2134760381 | 1022164 | 1084855 | 6023485306 | old |
| 524297 | 276837803 | 510787082703099498139 | 637474207113229119594 | 266746608361465812224 | common |
| 524800 | 1775769680 | 6721492657 | 8095779634 | 494766880863439 | old |
| 557064 | 707286950 | 88606242696826116 | 103648607221796545 | 32723291649241516208 | old |
| 655361 | 707286950 | 88606242696826116 | 103648607221796545 | 33112302397567569080 | old |
| 688128 | 5324321903 | 95745363536328 | 104619500292892 | 4248128707302389092 | old |

## Layer 4 intersectionとunion

old Layer 0,1とcommon Layer 4のintersectionは、前回と同じ一般式

\[
\binom q{4-f}2^p
\]

で全30プロフィールをexactに計数した。old族は既存certificateによりhit条件を満たすため、intersectionでhit条件を二重適用していない。

* weighted Layer 4 intersection：1062248803547451
* intersection率：\(2.0629308861\times10^{-16}\)
* Layer 4新規率：0.999999999999999793707
* weighted新規Layer 4：5149221482392700936553794951883
* union 0--4残差寄与：7953680457762087625348370932464

監査恒等式

\[
C_{\rm union,0:4}=C_{\rm union,0:3}+C_4-I_4^{\rm weighted}
\]

および

\[
B_{\rm new}=B_{\rm current}+C_4-I_4^{\rm weighted}
\]

は二経路で一致した。

新下界の改善倍率は約1.0000036344488603、\(\log_2=120.0920343794\)、\(\log_{10}=36.1513045885\) である。\(10^{37}\)、\(10^{38}\) は超えない。

## 評価

十分統計式は正しく、82-bit禁止集合を3-field、packed 5-byteのS1へ落とせた。S1とS2は同じ分割だがS1が小さい。category保持方式を採用し、streaming direct accumulationは不要だった。

Layer 4はLayer 3の約4.75倍で、ほぼ全てがold族に対して新規だった。signature数も4501に留まり、計算時間は主・監査合計約220秒である。従って同じ十分統計法をcoverage Layer 5へ拡張する価値は高い。現時点ではweighted column generationよりLayer展開を優先する。ただしLayer 5へは自動的に進んでいない。

## 再現

```bash
/usr/local/bin/python3.11 benchmark_z98_right_layer4_sufficient_stats.py
/usr/local/bin/python3.11 run_z98_right_layer4_sufficient_stats.py
/usr/local/bin/python3.11 verify_z98_right_layer4_sufficient_stats.py
/usr/local/bin/python3.11 extend_z98_old_common_union_layer4.py
/usr/local/bin/python3.11 verify_z98_old_common_union_layer4.py
python3 -m pytest -q tests/test_z98_right_layer4_sufficient_stats.py tests/test_z98_old_common_union_layer4.py
/usr/local/bin/python3.11 finalize_z98_right_layer4_sufficient_stats.py
```
