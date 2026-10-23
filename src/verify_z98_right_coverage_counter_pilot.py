#!/usr/local/bin/python3.11
import collections,gzip,json
from pathlib import Path
import local_components_g3 as g3
ROOT=Path(__file__).resolve().parent;W=ROOT/'experiments/lower_bound/z98_right_coverage_counter_pilot';PREV=ROOT/'experiments/lower_bound/z98_weighted_common_right_pilot';CLOS=ROOT/'experiments/lower_bound/z98_residual_profile_closure'
def bits(x):
 while x:b=x&-x;yield b.bit_length()-1;x^=b
def mobius(g):
 f=list(g)
 for b in range(12):
  for c in range(4096):
   if c>>b&1:f[c]-=f[c^(1<<b)]
 return f
def main():
 checks=[]
 def ck(n,x):checks.append({'name':n,'passed':bool(x)});assert x,n
 P,_=g3.load_fast_universe();right=json.loads((PREV/'right_poset.json').read_text());M=tuple(json.loads((PREV/'best_max_antichain.json').read_text())['ids']);PR=tuple(right['vertices']);X=sorted(set(PR)-set(M));U=right['U_H'];up={y:i for i,y in enumerate(U)};cov={r:sum(1<<up[y] for y in U if P.leq(r,y)) for r in PR}
 pats=json.loads((W/'coverage_patterns.json').read_text());ck('coverage_1238_49',len(pats['vertices'])==1238 and len(set(cov.values()))==49 and all(cov[r['id']]==r['coverage'] for r in pats['vertices']))
 d=json.loads((CLOS/'all_layer_profile_distribution.json').read_text());weights={r['H']:sum(map(int,r['coefficients'][1:])) for r in d['table'] if sum(map(int,r['coefficients'][1:]))};hw={sum(1<<up[y] for y in bits(h)):v for h,v in weights.items()};omega=[sum(v for h,v in hw.items() if h&~c==0) for c in range(4096)];saved_o=list(map(int,json.loads((W/'omega_table.json').read_text())['table']));ck('omega_4096',omega==saved_o and omega[-1]==27120959434)
 mc=[cov[m] for m in M];g0=[1<<sum((q&~c)==0 for q in mc) for c in range(4096)];f0=mobius(g0);s0=list(map(int,json.loads((W/'layer0_coverage.json').read_text())['histogram']));ck('layer0',f0==s0)
 mi={m:i for i,m in enumerate(M)};comp={x:sum(1<<mi[m] for m in M if P.comparable(x,m)) for x in X};allowed=[sum(1<<i for i,q in enumerate(mc) if q&~c==0) for c in range(4096)];g1=[sum(1<<(bin(allowed[c]&~comp[x]).count('1')) for x in reversed(X) if cov[x]&~c==0) for c in range(4096)];f1=mobius(g1);s1=list(map(int,json.loads((W/'layer1_coverage.json').read_text())['histogram']));ck('layer1_descending',f1==s1)
 # Independent Layer 2 histogram: category table, direct 79-zero + 3-singleton expansion.
 with gzip.open(PREV/'layer2/categories.json.gz','rt') as f:cats=json.load(f)
 zero=[i for i,q in enumerate(mc) if q==0];special=[i for i,q in enumerate(mc) if q];f2=[0]*4096
 for cs,cv,mult in reversed(cats):
  ban=int(cs);ez=sum(not(ban>>i&1) for i in zero);base=int(mult)<<ez
  for s in range(1<<len(special)):
   c=cv;ok=True
   for j,i in enumerate(special):
    if s>>j&1:
     if ban>>i&1:ok=False;break
     c|=mc[i]
   if ok:f2[c]+=base
 s2=list(map(int,json.loads((W/'layer2_coverage.json').read_text())['histogram']));ck('layer2_independent',f2==s2)
 weighted=[sum(f[c]*omega[c] for c in range(4096)) for f in (f0,f1,f2)];ck('layer02_weighted',weighted==[0,10777368195350123900411630720,152691887023040758403122277775])
 l3=json.loads((W/'layer3_coverage.json').read_text());a=json.loads((W/'layer3_fallback/asc.json').read_text());b=json.loads((W/'layer3_fallback/desc.json').read_text());ck('layer3_two_directions',all(a[k]==b[k] for k in ('triples','categories','max_multiplicity','hash_sum','hash_xor','F')));ck('layer3_total',a['triples']==32022499 and sum(map(int,a['F']))==int(l3['total_right_antichains']));ck('layer3_weighted',sum(int(v)*omega[i] for i,v in enumerate(a['F']))==int(l3['weighted_layer3']))
 cert={'status':'AUDIT PASSED','checks':checks,'U_H':U,'patterns':49,'omega_positive':sum(x>0 for x in omega),'layer_totals':[str(sum(f)) for f in (f0,f1,f2)],'weighted_0_2':str(sum(weighted)),'layer3_triples':a['triples'],'layer3_categories':a['categories'],'weighted_layer3':l3['weighted_layer3'],'weighted_0_3':l3['weighted_0_3']};p=W/'certificates/independent_verifier.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(cert,separators=(',',':'))+'\n');print('AUDIT PASSED');print(json.dumps(cert))
if __name__=='__main__':main()
