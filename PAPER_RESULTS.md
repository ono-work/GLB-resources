# Paper Results and Evidence Map

This file maps the paper's computational claims to the evidence frozen in this
artifact. All displayed counts are exact integers. Estimates and unfinished
searches are not included in the lower bound.

| Paper claim | Exact result | Primary evidence | Quick verification |
|---|---:|---|---|
| Calibration on `G_2 -> G_3` | 1,448 safe antichain pairs; `g(3)=1474` | `experiments/g2_calibration/safe_profile_g2_exact.json` | profile contributions and direct count agree |
| Maximum admissible-kernel run | `z=98`, hence `2^98 = 316912650057057350374175801344` | `experiments/lower_bound/general_safe_rectangle_ip_followup/certificate.json` | input, solution and log hashes; stored objective/bound/gap |
| Canonical thickening, right Layers 0--6 | `1416779128733115417932228068149714027` | `experiments/lower_bound/z98_inverted_canonical_layer6/certificate.json` | forward/reverse histograms and two arithmetic paths |
| Residual-profile closure | `1416780686143449296616167856189137167` | `experiments/lower_bound/z98_residual_profile_closure/certificate.json` | artifact hashes, layer distribution and contribution sum |
| Sufficient-statistic Layer 4 | `1416787082413573180019853416520646491` | `experiments/lower_bound/z98_right_layer4_sufficient_stats/summary.json` | certificate hashes and exact-union identities |
| Sufficient-statistic Layer 5 and old/common union | `1416805572004163810711501940302641257` | `experiments/lower_bound/z98_right_layer5_sufficient_stats/layer5_union.json` | weighted row sum and canonical-plus-union identity |
| Three disjoint residual cells | `+9128169669005694462519713793099402` | `experiments/lower_bound/z98_disjoint_cell_rectangle_pilot/best_partition.json` | six truth tables, cell sums and best-of-six comparison |
| Final certified lower bound | `1425933741673169505174021654095740659` | `experiments/lower_bound/z98_disjoint_cell_rectangle_pilot/new_lower_bound.json` | previous bound plus disjoint contribution |

## The final three cells

The adopted permutation is `(11, 2, 14)`. It partitions all left antichains
that do not contain the common kernel `T_0={2,11,14}` into the three cases

1. `11` is absent;
2. `11` is present and `2` is absent;
3. `11` and `2` are present and `14` is absent.

Their contributions are respectively

```text
4290068081433315295383046401526038
 548033506139063871753620990047326
4290068081433315295383046401526038
```

and sum to

```text
9128169669005694462519713793099402.
```

## Interpretation of `z=98`

The stored Gurobi run reports a global optimum of 98 for the stated integer
program. The lower-bound proof itself does not require this optimum assertion:
any verified feasible kernel yields a valid Boolean rectangle, and the
freedom-98 witness supplied here is checked independently as a construction.

## Scope note

`PARTIAL_STOP` applies only to three non-adopted cell candidates for which a
larger optional thickening was not completed. The reported final integer uses
only completed, verified contributions.
