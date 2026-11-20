# Certified: Psi(S, C) framework exhausted (B_Psi)

**g(4) ≥ 29247125847589399267405782004907476922410**

**log10 = 40.466083**   (2.924713 × 10^40); factor 20510.9 over GPW (1.426e36), 1.0922 over B0 (post_gpw_compressed_mitm, 2.678e40)

Compressed producer `bin/cmp_mitm` sha256 `5f08c8f0588b5b02eed5d487cd48ff34686fdc2bcabc4b66bb2608203e066d11`, verifier `bin/vsweep` sha256 `ba33f1f9d98176b1ec1260a4c19171489e9679a9238de402a5f8e8947305b56f` (Apple clang 21.0.0, `-O3 -std=c++17 -march=native`; binaries are not copied, they rebuild byte-identically from `barrier/*.cpp`, see COMPRESSED_MITM_BASELINE.md).

Frozen 2026-11-12 02:56 on Captain. HEAD at freeze: `2c49c11ed6511c211cd29b0671fc7314a02d4ee1` (branch `post-gpw-improvement`). The status line `PSI FRAMEWORK GLOBAL AUDIT PASSED` is in `psi_exhaustion/psi_framework_global_audit_record.json`; `GLOBAL AUDIT PASSED` is in `harvest/certificates/global_audit_record.json`. Key statuses (all 22 remaining keys): {"R_s_p_E2": "CERTIFIED", "R_p_s": "CERTIFIED", "RZ_s_0p_E2": "CERTIFIED", "R_0_sp_E2": "CERTIFIED", "R_0_p2_Es": "CERTIFIED", "R_s2_0": "CERTIFIED", "R_2_p_Es": "CERTIFIED", "R_p2_0": "CERTIFIED", "R_p_2": "CERTIFIED", "R_s_2": "CERTIFIED", "RZ_s_02_Ep": "CERTIFIED", "R_0_s2": "CERTIFIED", "RZ_s2_0_Ep": "CERTIFIED", "R_2_s": "CERTIFIED", "R_0_p_Es2": "CERTIFIED", "R_0_2": "CERTIFIED", "R_p_0": "CERTIFIED", "R_2_0": "CERTIFIED", "RZ_s_0_Ep2": "CERTIFIED", "R_s_0": "CERTIFIED", "R_0_s": "CERTIFIED", "R_0_0": "CERTIFIED"}

## Included families

| family | key (world; S; C; E) | exact original | mirror (= original, by negation) | ×2 included | verifier | producer commit | verifier commit |
|---|---|---:|---:|---|---|---|---|
| v5 (G1, G2 + mirrors) | (0; *±1*2; –; –), (0; *±1; –/*2; ·) with L ⊆ H_L | 1910895019390363935559973877007439048864 (total incl. mirrors) | incl. | – | verify_v5 AUDIT PASSED | – | – |
| N2 | (0; [3, 12]; [21]; []) | 493487524783195558377314979133320190779 | 493487524783195558377314979133320190779 | yes | verify_psi AUDIT PASSED | `62e44e7826` | `62e44e7826` |
| N4 | (0; [12, 21]; [3]; []) | 789191188948717705917614333988532013894 | 789191188948717705917614333988532013894 | yes | verify_psi AUDIT PASSED | `9975601c1d` | `e717a83660` |
| N5 | (0; [12]; [3, 21]; []) | 1031357479510084678164489779817476179310 | 1031357479510084678164489779817476179310 | yes | verify_psi AUDIT PASSED | `62e44e7826` | `7625593d47` |
| Z1 | (Z; [3, 12, 21]; [0]; []) | 789191188948717705917614333988532013894 | 789191188948717705917614333988532013894 | yes | verify_psi AUDIT PASSED | `62e44e7826` | `9d4b0d85f0` |
| Z2 | (Z; [3, 12]; [0, 21]; []) | 1031357479510084678164489779817476179310 | 1031357479510084678164489779817476179310 | yes | verify_psi AUDIT PASSED | `62e44e7826` | `add045531c` |
| ZG2 | (Z; [3, 12]; [0]; [21]) | 234090676789438332929918204237281734338 | 234090676789438332929918204237281734338 | yes | verify_psi AUDIT PASSED | `62e44e7826` | `23db7127ea` |
| N3 | (0; [3, 21]; [12]; []) | 755109627863156479070333611405948737314 | 755109627863156479070333611405948737314 | yes | verify_psi AUDIT PASSED | `62e44e7826` | `9d4b0d85f0` |
| N6 | (0; [3]; [12, 21]; []) | 893190625048779089530048319525964210249 | 893190625048779089530048319525964210249 | yes | verify_psi AUDIT PASSED | `62e44e7826` | `18421cce77` |
| N7 | (0; [21]; [3, 12]; []) | 1219198574355894293908221739832178001593 | 1219198574355894293908221739832178001593 | yes | verify_psi AUDIT PASSED | `23db7127ea` | `23db7127ea` |
| Z3 | (Z; [3, 21]; [0, 12]; []) | 1219198574355894293908207162508344440731 | 1219198574355894293908207162508344440731 | yes | verify_psi AUDIT PASSED | `23db7127ea` | `5c88ada4d7` |
| N8 | (0; []; [3, 12, 21]; []) | 1989391910383901020003500436216175933379 | 1989391910383901020003500436216175933379 | yes | verify_psi AUDIT PASSED | `94bd094b8b` | `93b5f84df0` |
| Z4 | (Z; [3]; [0, 12, 21]; []) | 1989391910383901020001931053993907936163 | 1989391910383901020001931053993907936163 | yes | verify_psi AUDIT PASSED | `94bd094b8b` | `a73a3b0228` |
| R_s_p_E2 | (0; [3]; [12]; [21]) | 231151158950498278060921910460730637668 | 231151158950498278060921910460730637668 | yes | verify_psi AUDIT PASSED | `ffc21ad274` | `ffc21ad274` |
| R_p_s | (0; [12]; [3]; [21]) | 234090676789438332929918204237281734338 | 234090676789438332929918204237281734338 | yes | verify_psi AUDIT PASSED | `ffc21ad274` | `b82282fb5a` |
| RZ_s_0p_E2 | (Z; [3]; [0, 12]; [21]) | 336086638048784623888438835464364234501 | 336086638048784623888438835464364234501 | yes | verify_psi AUDIT PASSED | `a9774a1ab4` | `a9774a1ab4` |
| R_0_sp_E2 | (0; []; [3, 12]; [21]) | 336086638048784623888439246982700650413 | 336086638048784623888439246982700650413 | yes | verify_psi AUDIT PASSED | `a9774a1ab4` | `1b9e49fdf0` |
| R_0_p2_Es | (0; []; [12, 21]; [3]) | 8520674777465663492223585922514488078 | 8520674777465663492223585922514488078 | yes | verify_psi AUDIT PASSED | `26d2bb151e` | `26d2bb151e` |
| R_s2_0 | (0; [3, 21]; []; [12]) | 8972957188370073722063363333257700474 | 8972957188370073722063363333257700474 | yes | verify_psi AUDIT PASSED | `26d2bb151e` | `44c81fa5fe` |
| R_2_p_Es | (0; [21]; [12]; [3]) | 8118672638055922302032992552501734639 | 8118672638055922302032992552501734639 | yes | verify_psi AUDIT PASSED | `26d2bb151e` | `44c81fa5fe` |
| R_p2_0 | (0; [12, 21]; []; [3]) | 7869231256113870368516345931396048463 | 7869231256113870368516345931396048463 | yes | verify_psi AUDIT PASSED | `26d2bb151e` | `44c81fa5fe` |
| R_p_2 | (0; [12]; [21]; [3]) | 6669517962471583718118234156112777268 | 6669517962471583718118234156112777268 | yes | verify_psi AUDIT PASSED | `26d2bb151e` | `ef737e5a36` |
| R_s_2 | (0; [3]; [21]; [12]) | 7974292488706389540090025918578544813 | 7974292488706389540090025918578544813 | yes | verify_psi AUDIT PASSED | `26d2bb151e` | `ef737e5a36` |
| RZ_s_02_Ep | (Z; [3]; [0, 21]; [12]) | 12005933644220659110202703206191772715 | 12005933644220659110202703206191772715 | yes | verify_psi AUDIT PASSED | `26d2bb151e` | `ef737e5a36` |
| R_0_s2 | (0; []; [3, 21]; [12]) | 12005933644220659110219052618796322880 | 12005933644220659110219052618796322880 | yes | verify_psi AUDIT PASSED | `44c81fa5fe` | `ef737e5a36` |
| RZ_s2_0_Ep | (Z; [3, 21]; [0]; [12]) | 9948746686923549149530479989836104522 | 9948746686923549149530479989836104522 | yes | verify_psi AUDIT PASSED | `44c81fa5fe` | `ef737e5a36` |
| R_2_s | (0; [21]; [3]; [12]) | 9948746686923549149530979119991024908 | 9948746686923549149530979119991024908 | yes | verify_psi AUDIT PASSED | `44c81fa5fe` | `2c49c11ed6` |
| R_0_p_Es2 | (0; []; [12]; [3, 21]) | 613255696710939187377022523120436728 | 613255696710939187377022523120436728 | yes | verify_psi AUDIT PASSED | `ef737e5a36` | `2c49c11ed6` |
| R_0_2 | (0; []; [21]; [3, 12]) | 940383775439070702723908755240582575 | 940383775439070702723908755240582575 | yes | verify_psi AUDIT PASSED | `ef737e5a36` | `2c49c11ed6` |
| R_p_0 | (0; [12]; []; [3, 21]) | 706427808114693050310509464476385031 | 706427808114693050310509464476385031 | yes | verify_psi AUDIT PASSED | `ef737e5a36` | `2c49c11ed6` |
| R_2_0 | (0; [21]; []; [3, 12]) | 1240030519175962985170349147247918577 | 1240030519175962985170349147247918577 | yes | verify_psi AUDIT PASSED | `ef737e5a36` | `2c49c11ed6` |
| RZ_s_0_Ep2 | (Z; [3]; [0]; [12, 21]) | 321426237071384851585720897496191743 | 321426237071384851585720897496191743 | yes | verify_psi AUDIT PASSED | `ef737e5a36` | `2c49c11ed6` |
| R_s_0 | (0; [3]; []; [12, 21]) | 358243551044634078593410892442688996 | 358243551044634078593410892442688996 | yes | verify_psi AUDIT PASSED | `ef737e5a36` | `2c49c11ed6` |
| R_0_s | (0; []; [3]; [12, 21]) | 321426237071384851585731588369450284 | 321426237071384851585731588369450284 | yes | verify_psi AUDIT PASSED | `ef737e5a36` | `2c49c11ed6` |
| R_0_0 | (0; []; []; [3, 12, 21]) | 7640582146961891627716322233936205 | 7640582146961891627716322233936205 | yes | verify_psi AUDIT PASSED | `ef737e5a36` | `2c49c11ed6` |

Sum: B_v5 + Σ 2·exact = 29247125847589399267405782004907476922410.

Families that are produced but not used in this milestone (verification pending or not needed) are listed in `COUNTED_FAMILIES.json` with `included: false`.

## Proof of disjointness (summary)

1. **Safe pairs are canonical.** Every counted pair `{L|R}` is a safe pair of antichains of G_3. Safe pairs are canonical forms (v5 theory; machine-checked on samples by `audit_v5_structure.py` and `audit_psi_structure.py`). So distinct option pairs give distinct games of birthday ≤ 4.
2. **Within a family.** A pair is determined by `(L, B)`, where `R = T ∪ B`. The count is `Σ_D e(D)·c(D)` with `D = dom(L)` a function of `L`, so nothing is counted twice. The inclusion–exclusion over `U ⊆ C` counts exactly the `B` that cover every `m ∈ C` strictly below.
3. **Between originals.** The key `(world, S, C, E)` is a function of `R`. Here `S = R ∩ {*,±1,*2}`, `C` is the set covered strictly below by `R`, and `E` is the set not covered. The world is 0 if `0 ∈ R` and Z if `0 ∉ R` with 0 covered strictly below.
   - All included Ψ families have distinct keys, and none of them has v5 G1's key.
   - N2 shares v5 G2's `R`-key but has `L ⊄ H_L([0,*,±1])`, while G2 has `L ⊆ H_L([0,*,±1])`.
   - The P-cells (`P = R ∩ G_2`) spanned by each family are listed in the ledger. N5, Z2 and N6 each span two cells, because `B` may contain one extra day-2 game. The key, and so the disjointness, does not depend on `P`.
4. **Mirrors.** Negation `{L|R} ↦ {−R|−L}` is an involution, so it is injective, and it preserves canonicality. It fixes 0 and *.
   - Originals lie in `O0 = {0 ∈ R ∖ L}` or `OZ = {0 ∉ L ∪ R, * ∈ R ∖ L}`.
   - Mirrors lie in `−O0 = {0 ∈ L ∖ R}` or `−OZ = {0 ∉ L ∪ R, * ∈ L ∖ R}`.
   - These four classes are pairwise disjoint. So mirrors never meet originals, and mirrors of disjoint families are disjoint. Hence each family contributes exactly 2 × its original count.
5. **Completeness.** The 36-key universe is exhausted: see `psi_exhaustion/PSI_FRAMEWORK_EXHAUSTIVENESS.md` and `psi_exhaustion/psi_framework_global_audit.py`.
6. **Machine checks.** `harvest/global_audit.py` re-checks all of the above from `COUNTED_FAMILIES.json` (hashes, verifier status, keys, P-cells, mirror classes) and recomputes the sum.

## Files

- `SHA256SUMS` lists the checksums of every file in this directory.
- `REPRODUCE.md` gives the commands to reproduce.
