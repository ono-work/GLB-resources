#!/usr/local/bin/python3.11
"""Gurobi非依存のcell安全直積解verifier。"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import local_components_g3 as g3
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'experiments/lower_bound/z98_disjoint_cell_rectangle_pilot'
def stable(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def check(P,s,required,forbidden,expected=None):
 A,B,TL,TR=(set(s[k]) for k in 'abuv');e=[]
 if not TL<=A:e.append('TL not subset A')
 if not TR<=B:e.append('TR not subset B')
 if not set(required)<=TL:e.append('required not in TL')
 if set(forbidden)&TL:e.append('forbidden in TL')
 if set(forbidden)&A:e.append('forbidden in A')
 if not P.is_antichain(A):e.append('A not antichain')
 if not P.is_antichain(B):e.append('B not antichain')
 lh=rh=0
 for a in A:
  for y in P.right[a]:
   lh+=1
   if not any(P.leq(r,y) for r in TR):e.append(f'left hit {a},{y}')
 for b in B:
  for x in P.left[b]:
   rh+=1
   if not any(P.leq(x,l) for l in TL):e.append(f'right hit {b},{x}')
 z=len(A)+len(B)-len(TL)-len(TR)
 if expected is not None and z!=expected:e.append(f'z {z} != {expected}')
 return {'passed':not e,'errors':e[:20],'z':z,'sizes':{'A':len(A),'B':len(B),'T_L':len(TL),'T_R':len(TR)},'left_hits':lh,'right_hits':rh,'hash':stable(s)}
def verify(tag):
 P,_=g3.load_fast_universe();opt=json.loads((OUT/'ip'/f'{tag}.json').read_text());pool=json.loads((OUT/'solution_pool'/f'{tag}.json').read_text());rows=[]
 best=check(P,opt['best_sets'],opt['required'],opt['forbidden'],opt['z_star']);assert best['passed']
 proof_kind='gurobi_gap_zero' if opt['status']=='OPTIMAL' else opt['status']
 if opt['status']=='OPTIMAL_BY_CELL_CONTAINMENT_CERTIFICATE':
  parent=json.loads((OUT/'ip'/f"{opt['parent_cell']}.json").read_text())
  assert parent['status']=='OPTIMAL' and parent['mip_gap']==0
  assert set(parent['required'])<=set(opt['required']) and set(parent['forbidden'])<=set(opt['forbidden'])
  assert parent['z_star']==opt['z_star']==best['z']
 elif opt['status']=='OPTIMAL_BY_GLOBAL_CERTIFICATE':
  assert opt['z_star']==98==best['z']
 elif opt['status']=='OPTIMAL_BY_THRESHOLD_INFEASIBILITY':
  assert opt['threshold_model_status']=='INFEASIBLE'
  assert opt['threshold']==opt['z_star']+1==best['z']+1
 elif opt['status']!='OPTIMAL':
  raise AssertionError(f'unknown exact proof status: {opt["status"]}')
 for c in pool['candidates']:
  x=check(P,c['sets'],opt['required'],opt['forbidden'],c['z']);assert x['passed'] and x['hash']==c['hash'];rows.append(x)
 cert={'status':'CELL_SAFE_RECTANGLE_IP_VERIFIED','tag':tag,'optimum_proved_by_gurobi':opt['status']=='OPTIMAL' and opt['mip_gap']==0,'optimum_proof_kind':proof_kind,
       'best':best,'pool_verified':len(rows),'all_pool_passed':True,'cell_membership_verified':True,'generated_boolean_rectangle_safe':True}
 (OUT/'certificates'/f'{tag}.json').write_text(json.dumps(cert,indent=2)+'\n');print(json.dumps({'tag':tag,'z':best['z'],'pool':len(rows),'status':cert['status']}));return cert
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cell');ap.add_argument('--all',action='store_true');a=ap.parse_args();defs=json.loads((OUT/'cell_definitions.json').read_text())['unique_cells'];tags=[x['tag'] for x in defs] if a.all else [a.cell]
 if not all(tags):ap.error('--cell or --all required')
 cs=[verify(t) for t in tags];
 if a.all:(OUT/'cell_ip_optima.json').write_text(json.dumps({'status':'CELL_SAFE_RECTANGLE_IP_VERIFIED','cells':[json.loads((OUT/'ip'/f'{t}.json').read_text()) for t in tags]},indent=2)+'\n');(OUT/'cell_solution_pool.json').write_text(json.dumps({'status':'CELL_SOLUTION_POOL_VERIFIED','cells':[json.loads((OUT/'solution_pool'/f'{t}.json').read_text()) for t in tags]},indent=2)+'\n')
if __name__=='__main__':main()
