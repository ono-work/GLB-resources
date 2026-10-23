#!/usr/bin/env python3
"""z98反転核pilotを探索側のcategory表に依存せず再計算する。"""
from __future__ import annotations
import argparse, collections, hashlib, json, math, subprocess
from pathlib import Path

import deficit_cover as dc
import glb_lower_bound as lb
import hit_antichain_counter as hc
import local_components_g3 as g3
from verify_general_safe_rectangle_followup import verify as verify_ip

ROOT=Path(__file__).resolve().parent
WORK=ROOT/'experiments/lower_bound/z98_inverted_kernel_layer_pilot'
BEST=ROOT/'experiments/lower_bound/general_safe_rectangle_ip_followup/best_solution.json'
SOL=ROOT/'experiments/lower_bound/general_safe_rectangle_ip_followup/solutions/max_seed0_focus1.sol'

def sh(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pc(x): return bin(x).count('1')
def sha_file(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def semantic(P,s):
 A,B,TL,TR=(set(s[k]) for k in 'abuv');e=[]
 if not TL<=A:e.append('TL subset')
 if not TR<=B:e.append('TR subset')
 if not P.is_antichain(A):e.append('A antichain')
 if not P.is_antichain(B):e.append('B antichain')
 if any(not any(P.leq(r,y) for r in TR) for a in A for y in P.right[a]):e.append('left hit')
 if any(not any(P.leq(x,l) for l in TL) for b in B for x in P.left[b]):e.append('right hit')
 return e,len(A)+len(B)-len(TL)-len(TR)

def triples_desc(P,X):
 total=0
 for k in range(len(X)-1,-1,-1):
  z=X[k]
  for j in range(k-1,-1,-1):
   y=X[j]
   if P.comparable(y,z):continue
   total+=sum(not P.comparable(X[i],y) and not P.comparable(X[i],z) for i in range(j))
 return total

def verify():
 P,_=g3.load_fast_universe();ids=tuple(range(P.n));best=json.loads(BEST.read_text());main=json.loads((WORK/'canonical_layer02.json').read_text());struct=json.loads((WORK/'structure_comparison.json').read_text());pre=json.loads((WORK/'deficit_preflight.json').read_text());errors=[]
 ia=verify_ip(SOL,98)
 if not ia['passed']:errors.append('z98 source audit')
 orig={'a':best['A'],'b':best['B'],'u':best['kernel']['left'],'v':best['kernel']['right']}
 inv={'a':sorted(P.negation[x] for x in orig['b']),'b':sorted(P.negation[x] for x in orig['a']),'u':sorted(P.negation[x] for x in orig['v']),'v':sorted(P.negation[x] for x in orig['u'])}
 e,z=semantic(P,inv);errors+=e
 if z!=98:errors.append('reflected z')
 tl=tuple(inv['u']);tr=tuple(inv['v']);pl=tuple(x for x in ids if x not in tl and all(not P.comparable(x,t) for t in tl));ql,qr=g3.q_sets(P,tl,tr)
 wl,al=lb.maximum_antichain(P,ql);wr,ar=lb.maximum_antichain(P,qr)
 if (len(pl),len(ql),len(qr),wl,wr)!=(237,114,598,20,78):errors.append('structure')
 M=tuple(sorted(set(inv['b'])-set(inv['v'])));X=tuple(x for x in qr if x not in set(M))
 if len(M)!=78 or not P.is_antichain(M) or len(X)!=520:errors.append('M/X')
 idx=lb.SearchIndex.build(P);adj=tuple(m&~(1<<i) for i,m in enumerate(idx.comparable_masks));mask=sum(1<<x for x in ql)
 # 探索側max-degreeとは異なる固定first pivot。
 CL,stats=hc.count_hit_antichains(mask,(),adj,branch_rule='first',time_limit=None,node_limit=None,memo_limit=None)
 pos={m:i for i,m in enumerate(M)};cm={x:sum(1<<pos[m] for m in M if P.comparable(x,m)) for x in X}
 R0=1<<78;R1=sum(1<<(78-pc(cm[x])) for x in reversed(X));cats=collections.Counter();pairs=0
 for i in range(len(X)-1,-1,-1):
  x=X[i]
  for j in range(i-1,-1,-1):
   y=X[j]
   if not P.comparable(x,y):pairs+=1;cats[cm[x]|cm[y]]+=1
 R2=sum(n*(1<<(78-pc(C))) for C,n in cats.items());T3=triples_desc(P,X)
 B0=CL*R0;B01=CL*(R0+R1);B02=CL*(R0+R1+R2)
 expected=(int(main['C_L']),int(main['layers']['R0']),int(main['layers']['R1']),int(main['layers']['R2']),int(main['bounds']['B_can_0']),int(main['bounds']['B_can_01']),int(main['bounds']['B_can_02']),main['layer3_structure']['antichain_triples'])
 actual=(CL,R0,R1,R2,B0,B01,B02,T3)
 if actual!=expected:errors.append('canonical totals')
 category=[(hex(C),n) for C,n in sorted(cats.items())]
 if len(cats)!=main['layers']['layer2_category_count'] or sh(category)!=main['layers']['layer2_union_mask_sha256']:errors.append('layer2 categories')
 delta={x:tuple(sorted(dc.delta_left(P,ids,tr,x))) for x in pl};U=tuple(sorted(set().union(*(set(v) for v in delta.values()))));reach=tuple(y for y in U if any(P.leq(r,y) for r in qr))
 if U!=tuple(pre['deficit_universe']) or reach or pre['reachable_deficits_by_Q_R_plus']!=[]:errors.append('deficit preflight')
 out={'status':'AUDIT PASSED' if not errors else 'AUDIT FAILED','passed':not errors,'errors':errors,
  'reflected_solution':inv,'z':z,'sizes':{'P_L':len(pl),'Q_L_plus':len(ql),'Q_R_plus':len(qr),'M':len(M),'X':len(X)},'widths':{'left':wl,'right':wr},
  'C_L':str(CL),'C_L_verifier_stats':stats,'R0':str(R0),'R1':str(R1),'R2':str(R2),'layer2_pairs':pairs,'layer2_categories':len(cats),'layer2_category_sha256':sh(category),'layer3_antichains':T3,
  'B_can_0':str(B0),'B_can_01':str(B01),'B_can_02':str(B02),'deficit_universe':list(U),'reachable_deficits':list(reach),
  'source_solution_sha256':ia['solution_sha256'],'source_model_sha256':ia['base_model_sha256'],'input_hashes':ia['input_hashes']}
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(WORK/'certificates/independent_audit.json'));a=ap.parse_args();out=verify();p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 if out['passed'] and p.resolve()==(WORK/'certificates/independent_audit.json').resolve():finalize(out,p)
 print(json.dumps({k:out[k] for k in ('status','C_L','R0','R1','R2','B_can_02')},ensure_ascii=False));raise SystemExit(0 if out['passed'] else 1)

def finalize(audit,audit_path):
 summary=json.loads((WORK/'summary.json').read_text());canonical=json.loads((WORK/'canonical_layer02.json').read_text());structure=json.loads((WORK/'structure_comparison.json').read_text());pre=json.loads((WORK/'deficit_preflight.json').read_text());manifest=json.loads((WORK/'input_manifest.json').read_text())
 summary['audit_status']='AUDIT PASSED';summary['independent_audit']=str(audit_path.relative_to(ROOT));summary['independent_audit_sha256']=sha_file(audit_path);(WORK/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 cert=json.loads((WORK/'certificate.json').read_text());cert['status']=summary['status'];cert['audit_status']='AUDIT PASSED';cert['independent_audit']=str(audit_path.relative_to(ROOT));cert['independent_audit_sha256']=sha_file(audit_path);cert['source_solution_sha256']=audit['source_solution_sha256'];cert['source_model_sha256']=audit['source_model_sha256'];(WORK/'certificate.json').write_text(json.dumps(cert,ensure_ascii=False,indent=2)+'\n')
 b=canonical['bounds'];L=canonical['layers'];t=canonical['layer3_structure'];old=int(b['old_bound']);new=int(b['B_can_02'])
 report=f'''# z=98 最適核の反転向き Layer pilot

## 結論

一般安全直積IPの監査済み最適解を正本の反転写像で反転し、右側78元最大反鎖を基底としてcanonical Layer 0--2をexactに数えた。結果は

\\[
B^{{\\mathrm{{can}}}}_{{0--2}}={new}
\\]

であり、旧核の監査済み値

\\[
B_{{\\mathrm{{old}}}}={old}
\\]

の約 `{new/old:.12f}` 倍となった。旧値との加算ではなく、新値による置換である。探索側と独立verifierは全主要整数、幅、反転解、Layer 2 category、三元反鎖数を一致させ、`AUDIT PASSED` となった。statusは `CANONICAL_LAYER02_BEATS_OLD` である。

## 反転と構造

反転核は

\\[
\\widehat T_L=[2,11,14],\\qquad \\widehat T_R=[0,3,12,21].
\\]

元向きでは `(|P_L|,|Q_L^+|,|Q_R^+|)=(676,598,114)`、反転向きでは `(237,114,598)` である。幅は元向き `(78,20)`、反転向き `(20,78)` と独立Dilworth計算で確認した。

反転IP解から得た `M=-(A\\setminus T_L)` は78元の反鎖であり、`Q_R^+` の幅78と一致するため最大反鎖である。外側集合は `|X|=598-78=520`。`Q_R^+` の比較可能pairは54346、`X` の比較不能pairは `{L['incomparable_pairs_X']}` である。最大matching certificateと全IDは [structure_comparison.json](../../experiments/lower_bound/z98_inverted_kernel_layer_pilot/structure_comparison.json) に保存した。

## canonical計数

反転向きの `Q_L^+` は114元・一連結成分で、独立集合include/exclude DPにより

\\[
C_L=|\\mathcal A(Q_L^+)|={audit['C_L']}.
\\]

固定20元自由反鎖の部分集合 `2^20` を含むという回帰も満たす。右Layerは

\\[
R_0={audit['R0']},\\quad
R_1={audit['R1']},\\quad
R_2={audit['R2']}.
\\]

従って

\\[
B^{{\\mathrm{{can}}}}_0={b['B_can_0']},
\\]
\\[
B^{{\\mathrm{{can}}}}_{{0--1}}={b['B_can_01']},
\\]
\\[
B^{{\\mathrm{{can}}}}_{{0--2}}={b['B_can_02']}.
\\]

`2^98` に対する倍率は順に `{b['multipliers_over_2^98']['layer0']}`、`{b['multipliers_over_2^98']['layer01']}`、`{b['multipliers_over_2^98']['layer02']}`。旧値へ必要な倍率はexactに `{b['old_over_2^98_fraction']}`、十進で約 `{b['old_over_2^98_decimal']}` である。Layer 2の89666 pairは昇順・降順の別列挙で一致した。

## Layer 3構造scan

`X` 上の三元反鎖数はexactに `{t['antichain_triples']}`。構造scanは `{t['structure_scan_seconds']:.6f}` 秒、約 `{t['structure_leaf_rate_per_second']:.3f}` leaf/秒であった。単純な同速度換算のcategory更新時間は約 `{t['estimated_streaming_category_seconds_at_scan_rate']:.6f}` 秒、比較不能bitsetの素朴な保持量は約 `{t['estimated_peak_memory_bytes_for_incomparability_bitsets']}` byteである。category数の安全な上界は `{t['estimated_category_count_upper_bound']}` で、実測category数は次実験に残す。これは構造scanだけであり、Layer 3寄与は計算・加算していない。次段階は十分現実的と見込まれるが、今回の停止規律に従い自動実行しなかった。

## 欠損集合preflight

`P_L` は237元で、空欠損114元、非空欠損123元。欠損universeは

`{pre['deficit_universe']}`

の9元、頂点signatureは26種類、最大頂点欠損サイズは3である。しかし、この9元はすべて `Q_R^+` 全体から到達不能だった。従って非空欠損を持つ左元はLayer番号にかかわらず救済不能で、欠損付きLayer 0--2はcanonical族を一つも拡張しない。よって `w_delta` の全exact計数は自動実行条件を満たさず、実行していない。これは計算困難性ではなく到達不能性による厳密な停止である。

## 最終的な問いへの回答

1. 反転向きのサイズは `(237,114,598)`。
2. 幅はexactに20と78。
3. IP由来78元反鎖は最大反鎖。
4. `|X|=520`。
5. `C_L={audit['C_L']}`。
6. `(R_0,R_1,R_2)=({audit['R0']},{audit['R1']},{audit['R2']})`。
7. canonical Layer 0--2下界は `{b['B_can_02']}`。
8. 旧下界の `{100*new/old:.9f}%`。
9. canonical領域だけで旧下界を更新した。
10. 欠損universeは9元だが全て到達不能。
11. 欠損別左全反鎖計数は不要であり、この右候補族では新規寄与を生まない。
12. 欠損付きLayer 0--2は実行条件を満たさず未実行。
13. したがって欠損側からの追加更新はない。
14. Layer 3は約792万三元反鎖で、次に進む価値がある。
15. 少なくともLayer 0--2では新しい反転核が旧核より強く、Layer展開に有望である。

判定に用いた10%・50%閾値は探索判断上の目安であり、数学的定理ではない。

## 再現

```bash
python3 z98_inverted_kernel_layer_pilot.py
python3 verify_z98_inverted_kernel_layer_pilot.py
python3 -m unittest tests.test_z98_inverted_kernel_layer_pilot
```

既存成果物、README、原稿、`../GUB` は変更せず、外部pushも行っていない。
'''
 rp=ROOT/'reports/lower_bound/z98_inverted_kernel_layer_pilot_ja.md';dp=ROOT/'docs/z98_inverted_kernel_layer_pilot.md';rp.write_text(report);dp.write_text('# z=98 inverted-kernel Layer pilot\n\n'+report.split('## 結論',1)[1])
 manifest['source_hashes'].update({'verify_z98_inverted_kernel_layer_pilot.py':sha_file(ROOT/'verify_z98_inverted_kernel_layer_pilot.py'),'tests/test_z98_inverted_kernel_layer_pilot.py':sha_file(ROOT/'tests/test_z98_inverted_kernel_layer_pilot.py'),str(rp.relative_to(ROOT)):sha_file(rp),str(dp.relative_to(ROOT)):sha_file(dp),str(audit_path.relative_to(ROOT)):sha_file(audit_path)})
 (WORK/'input_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
