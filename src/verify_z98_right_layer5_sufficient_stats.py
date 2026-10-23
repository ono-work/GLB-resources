#!/usr/local/bin/python3.11
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'experiments/lower_bound/z98_right_layer5_sufficient_stats';COMMON=ROOT/'experiments/lower_bound/z98_weighted_common_right_pilot';CLOS=ROOT/'experiments/lower_bound/z98_residual_profile_closure'
def pc(x):return bin(x).count('1')
def stable(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 a=json.loads((OUT/'layer5/asc.json').read_text());d=json.loads((OUT/'layer5/desc.json').read_text());result=json.loads((OUT/'layer5_contribution.json').read_text());assert a['quints']==d['quints']==104366998061;assert sorted(a['table'])==sorted(d['table']);cats=sorted(d['table'],reverse=True);U=json.loads((COMMON/'right_poset.json').read_text())['U_H'];up={y:i for i,y in enumerate(U)};base=[r for r in json.loads((CLOS/'all_layer_profile_distribution.json').read_text())['table'] if sum(map(int,r['coefficients'][1:]))>0];expected={r['H']:r['r5'] for r in result['profiles']};vals={}
 for r in reversed(sorted(base,key=lambda x:x['H'])):
  h=sum(1<<up[y] for y in U if r['H']>>y&1);s=0
  for c,b0,blocked,mult in cats:
   need=h&~c
   if need&~133 or need&blocked:continue
   s+=mult*(1<<(82-b0-pc(need)))
  vals[r['H']]=str(s);assert str(s)==expected[r['H']]
 C5=sum(sum(map(int,r['coefficients'][1:]))*int(vals[r['H']]) for r in base);assert str(C5)==result['C5'];cert={'status':'AUDIT PASSED','enumeration':'descending','quints':d['quints'],'signatures':d['signatures'],'signature_table_match':True,'profile_counts_match':True,'C5':str(C5),'profile_hash':stable(sorted(vals.items()))};(OUT/'certificates/layer5_verifier.json').write_text(json.dumps(cert,indent=2)+'\n');print('AUDIT PASSED');print(json.dumps(cert))
if __name__=='__main__':main()
