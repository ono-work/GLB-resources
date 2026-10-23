#!/usr/local/bin/python3.11
from __future__ import annotations
import collections, hashlib, json
from pathlib import Path
import local_components_g3 as g3
import glb_lower_bound as lb
import hit_antichain_counter as hc
from z98_left_residual1_profile_pilot import masks, minmask

ROOT=Path(__file__).resolve().parent
W=ROOT/'experiments/lower_bound/z98_residual_profile_closure'
L1=ROOT/'experiments/lower_bound/z98_left_residual1_profile_pilot'
L2=ROOT/'experiments/lower_bound/z98_left_residual2_profile_pilot'
OLD=ROOT/'experiments/lower_bound/z98_inverted_kernel_layer_pilot/structure_comparison.json'
BASE=1416779128733115417932228068149714027
CURRENT=1416780373480236792809721068627852419
TL=(2,11,14)

def independent_profile_dp(vertices, adj, labels, yset, universe, basez):
    """Independent implementation: low-ID tie break and normalized states."""
    memo={}
    def norm(x): return minmask(universe,x)
    def multiply(a,b):
        out=collections.defaultdict(int)
        for (h,k),n in a.items():
            for (q,j),m in b.items(): out[norm(h|q),k+j]+=n*m
        return dict(out)
    def visit(mask):
        if not mask: return {(0,0):1}
        if mask in memo: return memo[mask]
        comps=hc.components(mask,adj)
        if len(comps)>1:
            out={(0,0):1}
            for c in reversed(comps): out=multiply(out,visit(c))
        else:
            verts=[i for i in range(mask.bit_length()) if mask>>i&1]
            v=max(verts,key=lambda x:(hc.popcount(adj[x]&mask),-x))
            out=collections.defaultdict(int)
            for key,n in visit(mask&~(1<<v)).items(): out[key]+=n
            lab=norm(basez|labels[v])
            for (h,k),n in visit(mask&~(1<<v)&~adj[v]).items():
                out[norm(h|lab),k+(v in yset)]+=n
            out=dict(out)
        memo[mask]=out
        return out
    raw=visit(sum(1<<v for v in vertices))
    out=collections.defaultdict(int)
    for (h,k),n in raw.items(): out[minmask(universe,basez|h),k]+=n
    return dict(out),len(memo)

def main():
    checks=[]
    def ck(name,ok):
        checks.append({'name':name,'passed':bool(ok)})
        if not ok: raise AssertionError(name)
    P,_=g3.load_fast_universe(); idx=lb.SearchIndex.build(P)
    adj=tuple(m&~(1<<i) for i,m in enumerate(idx.comparable_masks))
    old=json.loads(OLD.read_text())['inverted']; pl=tuple(old['P_L']); ql=set(old['Q_L_plus']); Y=set(pl)-ql
    labels={g:masks(P,g) for g in range(P.n)}; basez=baseg=0
    for t in TL: z,ga=labels[t];basez|=z;baseg|=ga
    ck('P_L_Q_L_Y_sizes',(len(pl),len(ql),len(Y))==(237,114,123))
    ck('Gamma_constant',all(not(labels[g][1]&~baseg) for g in pl))
    got,memos=independent_profile_dp(pl,adj,{g:labels[g][0] for g in pl},Y,P,basez)
    saved=json.loads((W/'all_layer_profile_distribution.json').read_text())
    expected={(row['H'],k):int(n) for row in saved['table'] for k,n in enumerate(row['coefficients']) if int(n)}
    ck('full_profile_polynomial',got==expected)
    layer={k:sum(n for (h,j),n in got.items() if j==k) for k in range(max(k for h,k in got)+1)}
    ck('layer_0_1_2',(layer[0],layer[1],layer[2])==(319901739,1011911791,2257514542))
    ck('all_left_antichains',sum(got.values())==27440861173)
    l1=json.loads((L1/'left_profile_distribution.json').read_text());l2=json.loads((L2/'profile_distribution.json').read_text())
    p1={(r['H'],r['Gamma']):int(r['count']) for r in l1['profiles']};p2={(r['H'],r['Gamma']):int(r['count']) for r in l2['profiles']}
    ck('layer1_profile_regression',all(got.get((h,1),0)==n for (h,g),n in p1.items()) and sum(p1.values())==layer[1])
    ck('layer2_profile_regression',all(got.get((h,2),0)==n for (h,g),n in p2.items()) and sum(p2.values())==layer[2])
    residual_profiles={h for (h,k),n in got.items() if k>=1 and n}; canonical_profiles={h for (h,k),n in got.items() if k==0 and n}
    ck('residual_profile_set_closed_30',residual_profiles=={h for h,g in p1} and len(residual_profiles)==30)
    ck('five_canonical_only_profiles',len(canonical_profiles-residual_profiles)==5 and all(not any(got.get((h,k),0) for k in range(1,19)) for h in canonical_profiles-residual_profiles))
    ip=json.loads((L1/'right_ip_summary.json').read_text()); r1=json.loads((L1/'right_layer1_summary.json').read_text())
    z={r['H']:r['z'] for r in ip['rows']}; rr={r['H']:int(r['r1']) for r in r1['rows']}; right={h:(1<<z[h])+rr[h] for h in residual_profiles}
    c2=sum(got[h,2]*right[h] for h in residual_profiles)
    ck('residual2_contribution',c2==219679667301784931273763828087)
    total=sum(n*right[h] for (h,k),n in got.items() if k>=1)
    savedc=json.loads((W/'all_layer_contribution.json').read_text())
    ck('all_residual_contribution',str(total)==savedc['all_residual_contribution'])
    ck('new_bound',BASE+total==int(savedc['new_bound']))
    ck('path_B',total==sum(sum(got.get((h,k),0) for k in range(1,19))*right[h] for h in residual_profiles))
    cert={'status':'AUDIT PASSED','checks':checks,'independent_memo_masks':memos,'all_left_antichains':str(sum(got.values())),'residual_profile_count':len(residual_profiles),'canonical_only_profile_count':5,'all_residual_contribution':str(total),'new_bound':str(BASE+total)}
    out=W/'certificates/independent_verifier.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(cert,ensure_ascii=False,separators=(',',':'))+'\n')
    print('AUDIT PASSED');print(json.dumps({k:cert[k] for k in ('all_left_antichains','residual_profile_count','all_residual_contribution','new_bound')}))
if __name__=='__main__': main()
