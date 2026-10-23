#!/usr/bin/env python3
"""継続実験の解を Gurobi から独立に正本データで厳格検証する。"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from pathlib import Path
import glb_lower_bound as lb

ROOT=Path(__file__).resolve().parent
BASE=ROOT/"experiments/lower_bound/general_safe_rectangle_ip"

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def parse(path):
    vals={f"{k}{g:04d}":0.0 for k in "abuv" for g in range(1474)}; errors=[]
    text=Path(path).read_text()
    if Path(path).suffix==".json":
        raw=json.loads(text)
        for name,value in raw.items():
            if re.fullmatch(r"[abuv]\d{4}",name): vals[name]=float(value)
        lines=[]
    else: lines=text.splitlines()
    for line in lines:
        if not line or line.startswith("#"): continue
        p=line.split()
        if len(p)>=2 and re.fullmatch(r"[abuv]\d{4}",p[0]): vals[p[0]]=float(p[1])
    sets={k:set() for k in "abuv"}
    for n,v in vals.items():
        if v<=1e-6: bit=0
        elif v>=1-1e-6: bit=1
        else: errors.append(f"non-binary {n}={v}"); continue
        if bit: sets[n[0]].add(int(n[1:]))
    return vals,sets,errors

def verify(path, threshold=None):
    P,_=lb.reconstruct(); vals,s,e=parse(path); A,B,TL,TR=(s[k] for k in "abuv")
    if not TL<=A:e.append("TL not subset A")
    if not TR<=B:e.append("TR not subset B")
    if not P.is_antichain(A):e.append("A not antichain")
    if not P.is_antichain(B):e.append("B not antichain")
    lh=rh=0
    for a in A:
        for y in P.right[a]:
            lh+=1
            if not any(P.leq(r,y) for r in TR):e.append(f"left hit {a},{y}")
    for b in B:
        for x in P.left[b]:
            rh+=1
            if not any(P.leq(x,l) for l in TL):e.append(f"right hit {b},{x}")
    z=len(A)+len(B)-len(TL)-len(TR)
    if threshold is not None and z<threshold:e.append(f"z={z} < {threshold}")
    hashes={x:sha(lb.DEFAULT_GUB/"game_export"/x) for x in ("games.csv","leq_rows.hex","metadata.json")}
    expected=json.loads((BASE/"certificate.json").read_text())["input_hashes"]
    if hashes!=expected:e.append("input hash mismatch")
    out={"status":"SOLUTION VERIFIED" if not e else "SOLUTION REJECTED","passed":not e,"errors":e[:100],
         "solution":str(path),"solution_sha256":sha(path),"base_model_sha256":sha(BASE/"models/general_max.mps"),
         "input_hashes":hashes,"sets":{k:sorted(v) for k,v in s.items()},"sizes":{"A":len(A),"B":len(B),"T_L":len(TL),"T_R":len(TR)},
         "z":z,"rectangle_size":str(1<<z),"left_hit_instances_checked":lh,"right_hit_instances_checked":rh,
         "linear_constraints_semantically_checked":True,
         "glb_commit":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
         "gub_commit":subprocess.check_output(["git","-C",str(lb.DEFAULT_GUB),"rev-parse","HEAD"],text=True).strip()}
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("solution");ap.add_argument("--threshold",type=int);ap.add_argument("--output");a=ap.parse_args()
    out=verify(a.solution,a.threshold)
    if a.output:Path(a.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(out,indent=2,ensure_ascii=False));raise SystemExit(0 if out["passed"] else 1)
if __name__=="__main__":main()
