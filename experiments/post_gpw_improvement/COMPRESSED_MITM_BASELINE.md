# Compressed mixed-radix MITM: reference implementation (N7 776 region)

Frozen 2026-11-08. This is the reference implementation for the compressed campaign (N7, Z3, N8, Z4).

## Code

| item | value |
|---|---|
| git commit | `36b0521b023d8d2a89b3301c61c79adc6f21e9d9` (local tag `compressed-mitm-baseline`) |
| producer source | `barrier/cmp_mitm.cpp`, sha256 `0f4e0c300e86b7d6e9243a885048d3f75802353a5cdb35e0454a775ef765c242` |
| producer binary | `bin/cmp_mitm`, sha256 `5f08c8f0588b5b02eed5d487cd48ff34686fdc2bcabc4b66bb2608203e066d11` |
| verifier source | `barrier/vsweep.cpp`, sha256 `1a82d223d225f27046a290dd858fabd0964f2033741d70310bb90374e9f98ff4` |
| verifier binary | `bin/vsweep`, sha256 `ba33f1f9d98176b1ec1260a4c19171489e9679a9238de402a5f8e8947305b56f` |
| compiler | Apple clang version 21.0.0 (clang-2100.1.1.101), target x86_64-apple-darwin25.5.0 |
| flags | `clang++ -O3 -std=c++17 -march=native` (`std::thread`, 16 threads) |
| reproducibility | rebuilding both sources with these flags gives byte-identical binaries (same sha256) |
| machine | Captain: Mac Pro 2019, Xeon W-3223 @ 3.5 GHz (8C/16T), 48 GB RAM, macOS 26 (Darwin 25.5.0) |
| drivers | `barrier/cmp.py` (producer), `barrier/vsweep.py` (verifier), region from `barrier/anatomy.py` (`CASES["N7"]`) |

## Commands

```
# producer: compressed MITM, split chosen by minimal compressed memory, u64 with 61-bit primes
.venv/bin/python barrier/test718.py N7          > barrier/cmp_N7_776.out
# verifier: full bottom-up sweep, u32, dual orientation, moduli 2^32 + 31-bit primes
.venv/bin/python barrier/vtest3.py  N7 7.1e9    > barrier/vtest_N7.out
```

Each modulus is one process `/usr/bin/time -l bin/<binary> 16`. The maximum RSS comes from `/usr/bin/time -l`.

## Region and decompositions

The region is the N7 `U = ∅` region of profile D = all of REQ: 776 elements. `J(Q)` has 20 join-irreducibles.

| | producer (`cmp_mitm`) | verifier (`vsweep`) |
|---|---|---|
| orientation | primal | dual |
| `|Qa|` | 11 | 9 |
| `|M|` | 171 | 714 |
| ranks `K` | 1,3,5,5,5,5,4,4,3,2,1,1 | 1,3,3,4,4,4,3,2,1,1 |
| scheme | MITM, stream rank 5 | full sweep, no MITM |
| widest compressed rank `S(B)` | 171·171·171·171·9 = 7.70e9 (streamed) | 7.01e9 peak (two live tables) |
| `w_eff = log_171 max S(B)` | 4.43 | – |
| dense estimate on the same split | `171^5 = 1.46e11` per table, memory 2.92e11 entries = **2.1 TiB** | – |
| words / moduli | u64, 5 primes `2^61−1, …` (61-bit) | u32, `2^32` + 7 primes `2^31−1, …` |
| a-priori bound | `|M|^{|JA|} = 171^{20}`; product of moduli > 2·bound (asserted) | `714^{11}`; product > 2·bound (asserted) |

Domain sizes on the producer split, per rank:

```
rank 2: 171,16,16,9,9   rank 3-4: 171,171,171,16,9   rank 5: 171,171,171,171,9   rank 6-7: 171^4
```

## Measured

| | wall clock | per modulus | max RSS | output |
|---|---:|---:|---:|---|
| producer | 2560 s | 446–537 s | **18.17 GiB** | 47521522721017059017745700795827 |
| verifier | 4076 s | 456–710 s | **26.14 GiB** | 47521522721017059017745700795827 |

The two results agree exactly. Residues are in `barrier/cmp_N7_776.out` and `barrier/vtest_N7.out`.

The producer peak is `Ĝ_{r*−1}` (7.2e8) plus two `171^4` tables (8.55e8 each). That is 2.43e9 u64 entries = 18.1 GiB, which matches the measured 18.17 GiB.

## Validation history

- On 17 N3 sub-regions (156–354 elements), `cmp_mitm` (u64 and w32) and `vsweep` both agree with certified counts.
- Both agree with the N3 718-region value 23274146661487257322073705873832.
- `vsweep` reproduces the certified v5 676-region (26×26) count.
- The sliced mode of `vsweep` passed 12 forced-slice cases.
