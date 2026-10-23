#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent; W=R/'experiments/lower_bound/z98_inverted_canonical_layer6'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=json.loads((W/'main/full.json').read_text());v=json.loads((W/'verifier/full.json').read_text());c=json.loads((W/'certificate.json').read_text())
 h=m['histogram'];r=sum(n*(1<<(78-i)) for i,n in enumerate(h));b5=561500558847364965813467832318868800;cl=319901739
 checks={'A6':m['leaves']==v['leaves']==415959237179,'h6':h==v['histogram'],'sum_h6':sum(h)==415959237179,
 'set_hash_sum':m['set_hash_sum']==v['set_hash_sum'],'set_hash_xor':m['set_hash_xor']==v['set_hash_xor'],
 'A7':m['A7']==v['A7']==8314543811017,'suffix_main':sum(i*n for i,n in enumerate(m['suffix_distribution']))==m['A7'],
 'suffix_reverse':sum(i*n for i,n in enumerate(v['suffix_distribution']))==v['A7'],
 'R6':str(r)==c['summary']['R6'],'bound_path1':b5+cl*r==int(c['summary']['B_can_06']),
 'bound_path2':cl*(sum([302231454903657293676544,4090778557548728898093061,27737794359383582463945133,125650324515053753130545549,427941401789859828515725619,1169505685970628430389353294])+r)==int(c['summary']['B_can_06'])}
 print(json.dumps({'status':'AUDIT PASSED' if all(checks.values()) else 'AUDIT FAILED','checks':checks},ensure_ascii=False,indent=2))
 return 0 if all(checks.values()) else 1
if __name__=='__main__': raise SystemExit(main())
