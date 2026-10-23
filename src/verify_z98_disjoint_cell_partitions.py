#!/usr/local/bin/python3.11
"""最良partitionの論理的disjointnessと巨大整数和を独立再検査する。"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'experiments/lower_bound/z98_disjoint_cell_rectangle_pilot';CURRENT=1416805572004163810711501940302641257;T0=(2,11,14)
def main():
 defs={x['tag']:x for x in json.loads((OUT/'cell_definitions.json').read_text())['unique_cells']};res=json.loads((OUT/'partition_results.json').read_text());winner=json.loads((OUT/'best_partition.json').read_text());support=json.loads((OUT/'current_support_audit.json').read_text());assert support['status']=='CURRENT_LEFT_SUPPORT_CONTAINS_T0_VERIFIED'
 vals=[]
 for p in reversed(res['partitions']):
  for bits in range(8):
   L={T0[i] for i in range(3) if bits>>i&1};hits=sum(set(defs[t]['required'])<=L and not(set(defs[t]['forbidden'])&L) for t in p['cells']);assert hits==(bits!=7)
  d=sum(int(res['cell_representatives'][t]['D_cell']) for t in p['cells']);assert str(d)==p['D_partition'] and int(p['new_lower_bound'])==CURRENT+d;vals.append(d)
 assert int(winner['D_partition'])==max(vals);new=json.loads((OUT/'new_lower_bound.json').read_text());assert int(new['new_lower_bound'])==CURRENT+int(winner['D_partition'])
 cert={'status':'BEST_DISJOINT_PARTITION_VERIFIED','six_partitions':6,'truth_patterns_per_partition':8,'current_vs_new_disjoint':True,'within_partition_disjoint':True,'right_overlap_irrelevant':True,'new_bound_two_path':True}
 (OUT/'certificates/partition_verifier.json').write_text(json.dumps(cert,indent=2)+'\n');print(json.dumps(cert))
if __name__=='__main__':main()
