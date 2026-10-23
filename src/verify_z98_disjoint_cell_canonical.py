#!/usr/local/bin/python3.11
"""canonical thickeningとLayer 0--2を独立な逆順走査で再検査する。"""
from __future__ import annotations
import collections,json
from pathlib import Path
import glb_lower_bound as lb
import hit_antichain_counter as hc
import local_components_g3 as g3
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'experiments/lower_bound/z98_disjoint_cell_rectangle_pilot'
def pc(x):return x.bit_count()
def verify_row(P,adj,row):
 TL=tuple(row['kernel']['left']);TR=tuple(row['kernel']['right']);forbidden=set(row['forbidden']);ql0,qr=g3.q_sets(P,TL,TR);ql=tuple(x for x in ql0 if x not in forbidden)
 assert ql==tuple(row['Q_L_plus']) and qr==tuple(row['Q_R_plus'])
 if not row.get('canonical_exact_completed',True):
  assert row['C_L'] is None and row['adopted_depth']=='boolean_ip' and int(row['D_adoptable'])==1<<row['z']
  assert not(forbidden&set(TL)) and not(forbidden&set(ql));return 'boolean_fallback'
 CL,st=hc.count_independent_sets(sum(1<<x for x in ql),adj,'max_degree');assert str(CL)==row['C_L']
 width,_=lb.maximum_antichain(P,reversed(qr));M=tuple(row['right']['M']);assert width==row['right']['M_size']==len(M) and P.is_antichain(M);ms=set(M);X=tuple(x for x in reversed(qr) if x not in ms);pos={m:i for i,m in enumerate(M)};cm={x:sum(1<<pos[m] for m in M if P.comparable(x,m)) for x in X}
 R0=1<<width;assert str(R0)==row['right']['R0']
 if row['adopted_depth']>=2:
  R1=sum(1<<(width-pc(cm[x])) for x in X);cats=collections.Counter();pairs=0
  for i,x in enumerate(X):
   for y in X[i+1:]:
    if not P.comparable(x,y):pairs+=1;cats[cm[x]|cm[y]]+=1
  R2=sum(n*(1<<(width-pc(mask))) for mask,n in cats.items());assert (str(R1),str(R2),pairs)==(row['right']['R1'],row['right']['R2'],row['right']['incomparable_pairs']);assert int(row['D02'])==CL*(R0+R1+R2)
 else:assert int(row['D0'])==CL*R0
 assert set(TL)<=set(row['kernel']['left']) and not(forbidden&set(TL)) and not(forbidden&set(ql));return True
def main():
 P,_=g3.load_fast_universe();idx=lb.SearchIndex.build(P);adj=tuple(mask&~(1<<i) for i,mask in enumerate(idx.comparable_masks));data=json.loads((OUT/'cell_canonical_results.json').read_text());n=0
 fallback=0
 for rows in reversed(list(data['cells'].values())):
  for row in reversed(rows):
   kind=verify_row(P,adj,row);n+=1;fallback+=kind=='boolean_fallback'
 cert={'status':'CELL_CANONICAL_THICKENING_VERIFIED' if fallback==0 else 'PARTIAL_STOP','candidates_verified':n,'canonical_candidates_verified':n-fallback,'boolean_fallback_candidates_verified':fallback,'reverse_QR_scan':True,'left_antichain_counts_recomputed':True,'layer02_recomputed':True}
 (OUT/'certificates/canonical_verifier.json').write_text(json.dumps(cert,indent=2)+'\n');print(json.dumps(cert))
if __name__=='__main__':main()
