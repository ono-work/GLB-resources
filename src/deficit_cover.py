#!/usr/bin/env python3
"""局所安全部品のdeficit/被覆既約性ユーティリティ。"""
from __future__ import annotations
import itertools
import local_components_g2 as lc

def E_left(P,ids,TL): return tuple(a for a in ids if P.is_antichain(set(TL)|{a}))
def E_right(P,ids,TR): return tuple(b for b in ids if P.is_antichain(set(TR)|{b}))
def delta_left(P,ids,TR,a): return tuple(y for y in P.right[a] if not any(P.leq(r,y) for r in TR))
def delta_right(P,ids,TL,b): return tuple(x for x in P.left[b] if not any(P.leq(x,l) for l in TL))
def rescue(P,b,dL): return all(P.leq(b,y) for y in dL)
def coverage(P,a,dR): return tuple(x for x in dR if P.leq(x,a))

def deficit_safe_2_1(P,ids,TL,TR,A,b):
 if not(P.is_antichain(set(TL)|set(A)) and P.is_antichain(set(TR)|{b})):return False
 dLs=[delta_left(P,ids,TR,a) for a in A];dR=delta_right(P,ids,TL,b)
 return all(rescue(P,b,d) for d in dLs) and set(coverage(P,A[0],dR))|set(coverage(P,A[1],dR))==set(dR)

def theory_irreducibility(P,ids,TL,TR,A,b):
 dLs=[delta_left(P,ids,TR,a) for a in A];dR=delta_right(P,ids,TL,b)
 p=[not x for x in dLs];c=[set(coverage(P,a,dR))==set(dR) for a in A]
 partition=not(p[0] and c[1]) and not(p[1] and c[0])
 cover=partition and not(c[0] and c[1])
 return partition,cover,p,c

def positioned_subpart(A,b,mask):
 pos=[('L',A[0]),('L',A[1]),('R',b)]
 return tuple(x for i,(s,x) in enumerate(pos) if s=='L' and mask>>i&1),tuple(x for i,(s,x) in enumerate(pos) if s=='R' and mask>>i&1)

def partition_checks(P,ids,TL,TR,A,b):
 out=[]
 for m in (1,3,5):
  p1=positioned_subpart(A,b,m);p2=positioned_subpart(A,b,7^m)
  out.append((p1,p2,lc.part_safe(P,ids,TL,TR,*p1),lc.part_safe(P,ids,TL,TR,*p2)))
 return out

def cover_checks(P,ids,TL,TR,A,b):
 # 3 complementary partitions + 3 overlapping two-element covers = 全6 unordered covers。
 masks=((1,6),(2,5),(4,3),(3,5),(3,6),(5,6));out=[]
 for m,n in masks:
  p1=positioned_subpart(A,b,m);p2=positioned_subpart(A,b,n)
  out.append((p1,p2,lc.part_safe(P,ids,TL,TR,*p1),lc.part_safe(P,ids,TL,TR,*p2)))
 return out

def direct_partition_irreducible(P,ids,TL,TR,A,b): return not any(x[2] and x[3] for x in partition_checks(P,ids,TL,TR,A,b))
def direct_cover_irreducible(P,ids,TL,TR,A,b): return not any(x[2] and x[3] for x in cover_checks(P,ids,TL,TR,A,b))
