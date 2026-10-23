#!/usr/local/bin/python3.11
from __future__ import annotations
import collections,hashlib,json,subprocess,time,sys
from pathlib import Path
import deficit_cover as dc
import glb_lower_bound as lb
import hit_antichain_counter as hc
import local_components_g3 as g3
ROOT=Path(__file__).resolve().parent;W=ROOT/'experiments/lower_bound/z98_left_residual1_profile_pilot';PREV=ROOT/'experiments/lower_bound/z98_inverted_kernel_layer_pilot/structure_comparison.json'
TL=(2,11,14);TR=(0,3,12,21);CAP=2_000_000
def stable(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def atom(p,x):p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix('.tmp');t.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n');t.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def masks(P,g):
 z=sum(1<<x for x in P.right[g]);ga=sum(1<<x for x in range(22) if P.leq(x,g));return z,ga
def minmask(P,z):
 return sum(1<<x for x in range(22) if z>>x&1 and not any(y!=x and z>>y&1 and P.leq(y,x) for y in range(22)))
def convolve(a,b,cap):
 o=collections.defaultdict(int)
 for (z,g),n in a.items():
  for (z2,g2),m in b.items():o[z|z2,g|g2]+=n*m
  if len(o)>cap:raise OverflowError(len(o))
 return dict(o)
def profile_counter(vertices,adj,labels,cap=CAP):
 memo={};stats={'calls':0,'max_states':0}
 def rec(mask):
  if not mask:return {(0,0):1}
  if mask in memo:return memo[mask]
  stats['calls']+=1
  comps=hc.components(mask,adj)
  if len(comps)>1:
   o={(0,0):1}
   for c in comps:o=convolve(o,rec(c),cap)
  else:
   vs=[i for i in range(mask.bit_length()) if mask>>i&1];v=max(vs,key=lambda x:(hc.popcount(adj[x]&mask),x))
   o=collections.defaultdict(int)
   for k,n in rec(mask&~(1<<v)).items():o[k]+=n
   z,g=labels[v]
   for (z0,g0),n in rec(mask&~(1<<v)&~adj[v]).items():o[z0|z,g0|g]+=n
   o=dict(o)
  stats['max_states']=max(stats['max_states'],len(o))
  if len(o)>cap:raise OverflowError(len(o))
  memo[mask]=o;return o
 root=sum(1<<v for v in vertices);out=rec(root);stats['memo_masks']=len(memo);return out,stats
def main():
 st=time.time();[ (W/d).mkdir(parents=True,exist_ok=True) for d in ('left_profiles','right_candidates','right_ip','right_layer1','certificates','logs')]
 P,_=g3.load_fast_universe();ids=tuple(range(P.n));idx=lb.SearchIndex.build(P);adj=tuple(x&~(1<<i) for i,x in enumerate(idx.comparable_masks));old=json.loads(PREV.read_text())['inverted']
 pl=tuple(old['P_L']);ql=tuple(old['Q_L_plus']);Y=tuple(x for x in pl if x not in set(ql));assert (len(pl),len(ql),len(Y))==(237,114,123)
 cl,_=hc.count_independent_sets(sum(1<<x for x in ql),adj,'max_degree');assert cl==319901739
 labels={g:masks(P,g) for g in ids}; qpos={q:i for i,q in enumerate(ql)};groups={}
 rows=[]
 for u in Y:
  neigh=tuple(q for q in ql if P.comparable(q,u));Q=tuple(q for q in ql if q not in set(neigh));sig=(neigh,*labels[u]);groups.setdefault(sig,[]).append(u)
  mask=sum(1<<q for q in Q);comps=hc.components(mask,adj);rows.append({'u':u,'Q_size':len(Q),'components':len(comps),'largest_component':max(map(hc.popcount,comps),default=0),'comparable_pairs':sum(hc.popcount(adj[q]&mask) for q in Q)//2})
 sigs=[]
 for sig,us in groups.items():
  neigh,z,g=sig;Q=tuple(q for q in ql if q not in set(neigh));sigs.append({'representative':us[0],'vertices':us,'multiplicity':len(us),'Q':Q,'Q_size':len(Q),'z':z,'gamma':g,'signature_sha256':stable([neigh,z,g])})
 sigs.sort(key=lambda x:(x['Q_size'],x['representative']))
 pre={'status':'LEFT_PROFILE_DP_PENDING','kernel':{'left':list(TL),'right':list(TR)},'sizes':{'P_L':len(pl),'Q_L_plus':len(ql),'Y_L':len(Y),'C_L':str(cl)},'sets':{'P_L':list(pl),'Q_L_plus':list(ql),'Y_L':list(Y)},'hashes':{'P_L':stable(pl),'Q_L_plus':stable(ql),'Y_L':stable(Y)},'signature_count':len(sigs),'signature_multiplicity_distribution':dict(collections.Counter(x['multiplicity'] for x in sigs)),'Q_stats':rows,'signatures':sigs}
 atom(W/'left_profiles'/'preflight.json',pre);print(json.dumps({'phase':'preflight','signatures':len(sigs),'Q_range':[sigs[0]['Q_size'],sigs[-1]['Q_size']]}),flush=True)
 # Deterministic exact attempt. Any cap hit invalidates all partial coefficients.
 total=collections.defaultdict(int);diag=[];basez=0;baseg=0
 for t in TL: z,g=labels[t];basez|=z;baseg|=g
 try:
  for no,s in enumerate(sigs):
   prof,stats=profile_counter(s['Q'],adj,labels);bz,bg=labels[s['representative']];loc=collections.defaultdict(int)
   for (z,g),n in prof.items():loc[minmask(P,basez|bz|z),baseg|bg|g]+=n*s['multiplicity']
   for k,n in loc.items():total[k]+=n
   diag.append({'signature':s['signature_sha256'],'raw_states':len(prof),'normalized_states':len(loc),**stats});print(json.dumps({'signature':no+1,'of':len(sigs),'states':len(prof),'profiles_total':len(total)}),flush=True)
  expected=sum(int(hc.count_independent_sets(sum(1<<q for q in s['Q']),adj,'max_degree')[0])*s['multiplicity'] for s in sigs)
  assert sum(total.values())==expected
  dist=[{'H':h,'Gamma':g,'count':str(n)} for (h,g),n in sorted(total.items())]
  out={'status':'LEFT_RESIDUAL1_PROFILE_VERIFIED','total_left_antichains':str(expected),'distinct_profiles':len(total),'distinct_H':len({h for h,g in total}),'distinct_Gamma':len({g for h,g in total}),'profiles':dist,'diagnostics':diag,'stable_hash':stable(dist),'runtime_seconds':time.time()-st}
 except OverflowError as e:
  out={'status':'LEFT_PROFILE_STATE_EXPLOSION','cap':CAP,'overflow_states':int(e.args[0]),'completed_signatures':len(diag),'total_signatures':len(sigs),'partial_coefficients_formally_usable':False,'diagnostics':diag,'runtime_seconds':time.time()-st}
 atom(W/'left_profile_distribution.json',out);atom(W/'summary.json',out);print(json.dumps({k:out[k] for k in out if k in ('status','total_left_antichains','distinct_profiles','completed_signatures','overflow_states')}))
if __name__=='__main__':main()
