#!/usr/bin/env python3
"""G_le_3 canonical singleton 部品の限定pilot。"""

from __future__ import annotations

import argparse, csv, gc, hashlib, json, math, platform, subprocess, time
from pathlib import Path

import glb_lower_bound as lb
import hit_antichain_counter as hc
from safe_profile_g3_pilot import load_export_chains

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "experiments/lower_bound/full_exact_1_1/exact_results.jsonl"
G2 = ROOT / "experiments/lower_bound/local_components/g2_pilot.json"
OUT = ROOT / "experiments/lower_bound/local_components/g3_canonical_pilot.json"
CERTDIR = ROOT / "experiments/lower_bound/local_components/g3_certificates"
OLD_CERTDIR = ROOT / "experiments/lower_bound/full_exact_1_1/certificates"
CACHE = ROOT / "experiments/lower_bound/local_components/g3_universe_cache.json"
B0 = 40304377900132122055529201664

def sha256(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def git_commit(path):
    return subprocess.check_output(["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()

def read_rows():
    rows=[]
    with RESULTS.open() as f:
        for line in f:
            r=json.loads(line)
            if r["exponent"] in (88,89): rows.append(r)
    return rows

def load_fast_universe():
    ed=lb.DEFAULT_GUB/"game_export"
    with (ed/"games.csv").open() as f: orig=[int(r["orig_gid"]) for r in csv.DictReader(f)]
    rows=[int(x,16) for x in (ed/"leq_rows.hex").read_text().splitlines() if x]
    meta=json.loads((ed/"metadata.json").read_text()); birthdays=[]
    for b,n in enumerate(meta["counts_by_birthday"]): birthdays += [b]*n
    c=json.loads(CACHE.read_text())
    assert c["orig_gids"]==orig
    return lb.Universe(birthdays,[tuple(x) for x in c["left"]],[tuple(x) for x in c["right"]],rows,orig,c["negation"]),meta

def certificate_for(tl,tr):
    paths=list(OLD_CERTDIR.glob("*z89.json"))
    for p in paths:
        d=json.loads(p.read_text())
        if d["left_kernel"]==list(tl) and d["right_kernel"]==list(tr): return p,d
    return None,None

def q_sets(P,tl,tr):
    ids=tuple(range(P.n))
    ql=tuple(sorted(g for g in lb.safe_left(P,tr,ids) if g not in tl and
                    all(not P.comparable(g,t) for t in tl)))
    qr=tuple(sorted(g for g in lb.safe_right(P,tl,ids) if g not in tr and
                    all(not P.comparable(g,t) for t in tr)))
    return ql,qr

def adj_global(index):
    return tuple(m & ~(1<<i) for i,m in enumerate(index.comparable_masks))

def stats(P,Q,adj,chains,width,anti):
    mask=sum(1<<x for x in Q)
    comps=hc.components(mask,adj)
    cs=sorted((hc.popcount(c) for c in comps),reverse=True)
    qset=set(Q); per=[sum(x in qset for x in c) for c in chains]
    # width/最大反鎖は全(1,1) exact結果（Dilworth matching）から読み、
    # 小さい側は後段で独立にmaximum_antichainを再計算する。
    return {"vertex_count":len(Q),"width":width,"maximum_antichain":list(anti),
      "comparable_edges":sum(hc.popcount(adj[x]&mask) for x in Q)//2,
      "component_count":len(comps),"component_sizes":cs,
      "largest_component":cs[0] if cs else 0,"second_component":cs[1] if len(cs)>1 else 0,
      "isolated_vertices":sum(x==1 for x in cs),"chain_counts":per,
      "used_chains":sum(x>0 for x in per),"chain_product":str(math.prod(x+1 for x in per))}

def count_exact(Q,adj,seconds=60):
    mask=sum(1<<x for x in Q)
    try:
        value,st=hc.count_hit_antichains(mask,(),adj,time_limit=seconds,
            node_limit=2_000_000,memo_limit=1_000_000)
        return value,"exact",st
    except hc.CountLimitExceeded as e:
        return None,e.reason,e.stats

def g2_cumulative():
    data=json.loads(G2.read_text())
    rows=data["kernels"]
    universe=set()
    out=[]
    for s in range(45):
        for r in rows:
            if len(r["left_kernel"])+len(r["right_kernel"])!=s: continue
            fam=next(x for x in r["families"] if x["rule"]=="canonical_left_right_singletons")
            parts=fam["parts"]
            edges={tuple(e) for e in fam["edges"]}
            n=len(parts)
            def rec(i,chosen):
                if i==n:
                    L=tuple(sorted(set(r["left_kernel"])|{x for j in chosen for x in parts[j]["A"]}))
                    R=tuple(sorted(set(r["right_kernel"])|{x for j in chosen for x in parts[j]["B"]}))
                    universe.add((L,R)); return
                rec(i+1,chosen)
                if all(tuple(sorted((i,j))) not in edges for j in chosen): rec(i+1,chosen+(i,))
            rec(0,())
        out.append({"max_kernel_total_size":s,"union_size":len(universe)})
        if len(universe)==1448: break
    return out

def z88_scan(P,adj,chains,rows):
    out=[]
    for r in rows:
        tl=tuple(r["left_kernel"]); tr=tuple(r["right_kernel"]); ql,qr=q_sets(P,tl,tr)
        out.append({"kernel":{"left":list(tl),"right":list(tr)},"q_left_size":len(ql),"q_right_size":len(qr),
          "left_structure":stats(P,ql,adj,chains,r["left_width"],r["left_free"]),
          "right_structure":stats(P,qr,adj,chains,r["right_width"],r["right_free"]),"old_exponent":88})
    return out

def integrate_frontiers(records):
    chosen=[0,17,1,2,9]
    for i in chosen:
        cp=OUT.parent/("g3_checkpoints/kernel_%02d_right.json"%i)
        if not cp.exists(): continue
        d=json.loads(cp.read_text()); r=records[i]; partial=int(d["certified_total"])
        r["stage2"]={"checkpoint":str(cp.relative_to(ROOT)),"checkpoint_sha256":sha256(cp),
          "certified_partial":str(partial),"completed_units":len(d["completed_units"]),
          "unresolved_frontier":len(d["unresolved_frontier"]),"seconds":d.get("last_run_seconds"),"target":d["target"]}
        base=1<<r["right_structure"]["width"]
        if partial>base: r["counts"]["right"]={"value":str(partial),"status":"certified_frontier_partial"}
        lv=int(r["counts"]["left"]["value"]); rv=int(r["counts"]["right"]["value"])
        r["counts"]["product"]=str(lv*rv); r["counts"]["exceeds_B0"]=lv*rv>B0
    return chosen

def write_certificates(payload):
    CERTDIR.mkdir(parents=True,exist_ok=True)
    top=sorted(payload["z89_kernels"],key=lambda r:int(r["counts"]["product"]),reverse=True)[:5]
    for rank,r in enumerate(top,1):
        cert={"schema_version":1,"level":3,"kernel":r["kernel"],"q_left":r["q_left"],"q_right":r["q_right"],
          "left_width":r["left_structure"]["width"],"right_width":r["right_structure"]["width"],
          "left_count":r["counts"]["left"]["value"],"left_status":r["counts"]["left"]["status"],
          "right_count":r["counts"]["right"]["value"],"right_status":r["counts"]["right"]["status"],
          "product":r["counts"]["product"],"old_exponent":89,"old_bound":str(1<<89),
          "improvement_factor":{"numerator":r["counts"]["product"],"denominator":str(1<<89)},
          "completed_units":[],"unresolved_frontier":[],"stage2_checkpoint":r.get("stage2",{}).get("checkpoint"),
          "input_hashes":payload["input_hashes"],"glb_commit":payload["glb_commit"],"gub_commit":payload["gub_commit"],
          "B0":str(B0),"exceeds_B0":r["counts"]["exceeds_B0"]}
        p=CERTDIR/("rank%02d_tl%d_tr%d.json"%(rank,r["kernel"]["left"][0],r["kernel"]["right"][0])); p.write_text(json.dumps(cert,ensure_ascii=False,indent=2)+"\n")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--stage",choices=["scan","stage1"],default="stage1")
    ap.add_argument("--kernel-index",type=int)
    args=ap.parse_args(); started=time.perf_counter()
    P,meta=load_fast_universe(); idx=lb.SearchIndex.build(P); adj=adj_global(idx); chains,_=load_export_chains(P)
    source=read_rows(); groups={z:sorted((r for r in source if r["exponent"]==z),key=lambda r:(r["left_kernel"],r["right_kernel"])) for z in (89,88)}
    assert len(groups[89])==24 and len(groups[88])==34
    records=[]
    selected=list(enumerate(groups[89],1))
    if args.kernel_index is not None: selected=[selected[args.kernel_index]]
    for ordinal,r in selected:
        tl=tuple(r["left_kernel"]); tr=tuple(r["right_kernel"])
        cp,cd=certificate_for(tl,tr)
        ql,qr=(tuple(cd["q_left"]),tuple(cd["q_right"])) if cd else q_sets(P,tl,tr)
        assert (len(ql),len(qr))==(r["q_left_size"],r["q_right_size"])
        sl=stats(P,ql,adj,chains,r["left_width"],r["left_free"])
        sr=stats(P,qr,adj,chains,r["right_width"],r["right_free"])
        assert (sl["width"],sr["width"])==(r["left_width"],r["right_width"])
        side="left" if (sl["largest_component"],len(ql)) <= (sr["largest_component"],len(qr)) else "right"
        counts={"left":{"value":str(1<<sl["width"]),"status":"maximum_antichain_subcube"},
                "right":{"value":str(1<<sr["width"]),"status":"maximum_antichain_subcube"}}
        if args.stage=="stage1":
            Q=ql if side=="left" else qr
            check_width,check_anti=lb.maximum_antichain(P,Q)
            assert check_width==(sl if side=="left" else sr)["width"]
            val,status,cst=count_exact(Q,adj)
            counts[side]={"value":str(val if val is not None else 1<<(sl if side=="left" else sr)["width"]),"status":status,"counter_stats":cst}
        lv=int(counts["left"]["value"]); rv=int(counts["right"]["value"])
        counts["product"]=str(lv*rv); counts["exceeds_B0"]=lv*rv>B0
        other="right" if side=="left" else "left"; exact=int(counts[side]["value"])
        counts["opposite_target"]=str(B0//exact+1)
        records.append({"kernel":{"left":list(tl),"right":list(tr)},"q_left":list(ql),"q_right":list(qr),
          "old_exponent":89,"old_bound":str(1<<89),"source_certificate":({"path":str(cp.relative_to(ROOT)),"sha256":sha256(cp)} if cp else None),
          "symmetry_kernel":{"left":[P.negation[tr[0]]],"right":[P.negation[tl[0]]]},
          "left_structure":sl,"right_structure":sr,"stage1_side":side,"counts":counts})
        print("kernel",ordinal,"/24",tl,tr,"side",side,"count",counts[side]["value"],flush=True)
        gc.collect()
    chosen=integrate_frontiers(records) if args.kernel_index is None else []
    exceeds=any(x["counts"]["exceeds_B0"] for x in records)
    payload={"schema_version":1,"status":"pilot_complete" if args.stage=="stage1" else "scan_complete",
      "B0":str(B0),"sources":{"exact_results":{"path":str(RESULTS.relative_to(ROOT)),"sha256":sha256(RESULTS)},
      "g2_pilot":{"path":str(G2.relative_to(ROOT)),"sha256":sha256(G2)}},
      "input_hashes":{x:sha256(lb.DEFAULT_GUB/"game_export"/x) for x in ("games.csv","leq_rows.hex","metadata.json")},
      "glb_commit":git_commit(ROOT),"gub_commit":git_commit(lb.DEFAULT_GUB),"environment":{"python":platform.python_version(),"platform":platform.platform()},
      "g2_kernel_size_cumulative_union":g2_cumulative() if args.kernel_index is None else [],"z89_kernels":records,
      "stage2_selected_indices":chosen,"z88_kernels":[],"z88_structure_pending":not exceeds,
      "maximum_certified_single_kernel":str(max(int(x["counts"]["product"]) for x in records)),
      "any_kernel_exceeds_B0":exceeds,"seconds":time.perf_counter()-started}
    out=OUT if args.kernel_index is None else OUT.parent/("g3_parts/part_%02d.json"%args.kernel_index)
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
    if args.kernel_index is None: write_certificates(payload)
    print(json.dumps({"output":str(out),"seconds":payload["seconds"],"max_product":max(int(x["counts"]["product"]) for x in records)},ensure_ascii=False))

if __name__=="__main__": main()
