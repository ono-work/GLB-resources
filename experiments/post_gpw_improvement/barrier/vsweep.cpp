// Independent low-memory verifier: full bottom-up sweep (no meet-in-the-middle), 32-bit tables.
// Written separately from rank_transfer_mitm / cmp_mitm; meant to be run on a DIFFERENT split (Qa / orientation),
// so the tables, M and the coordinate structure differ from the producer's.
//
// Input (own format, produced by barrier/vsweep.py):
//   modulus q   (0 means 2^32: native wrap-around; otherwise an odd prime < 2^31)
//   nM, then the nM masks of M (a family of sets closed under | and &)
//   R, then K_0..K_{R-1}
//   for r < R-1, for each coordinate a of rank r: its upper covers (count, then indices in rank r+1)
//   for each r, the K_r allowed masks A (as masks, not indices)
// Output: #{f : JA -> M | f(a) ⊆ A_a, f(b) ∩ A_a ⊆ f(a) for every cover a<b}  mod q.
// Recurrence (bottom-up):  T_0 ≡ 1 on Π D_a,  D_a = {m ∈ M : m ⊆ A_a};
//   Z_r(v) = Σ_{w ∈ D_a, w ⊇ v} T_r(w)  (coordinate-wise);  T_{r+1}(u) = Z_r(need(u)),
//   need(u)_a = ⋃_{b ⊳ a} (u_b ∩ A_a);    answer = Σ T_{R-1}.
// Peak memory = max_r 4·(|Π_r D| + |Π_{r+1} D|) bytes; reported on stderr.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <map>
#include <unordered_map>
#include <thread>
#include <atomic>
using namespace std;
typedef uint64_t u64; typedef uint32_t u32;

static unsigned NTH = 16;
static u64 Q;  // 0 => 2^32
static inline u32 addm(u32 a, u32 b) { if (!Q) return a + b; u64 s = (u64)a + b; return s >= Q ? (u32)(s - Q) : (u32)s; }

template <class F> static void parallel(u64 n, F body) {
    vector<thread> ts; u64 per = n / NTH + 1;
    for (unsigned t = 0; t < NTH; t++) { u64 a = t * per, b = a + per < n ? a + per : n; if (a < b) ts.emplace_back(body, a, b); }
    for (auto &t : ts) t.join();
}

int main(int argc, char **argv) {
    if (argc > 1) NTH = atoi(argv[1]);
    if (scanf("%llu", (unsigned long long *)&Q) != 1) return 1;
    int nM; if (scanf("%d", &nM) != 1) return 1;
    vector<u64> M(nM); for (auto &m : M) if (scanf("%llu", (unsigned long long *)&m) != 1) return 1;
    map<u64, int> pos; for (int i = 0; i < nM; i++) pos[M[i]] = i;
    int R; if (scanf("%d", &R) != 1) return 1;
    vector<int> K(R); for (auto &k : K) if (scanf("%d", &k) != 1) return 1;
    vector<vector<vector<int>>> ups(R);
    for (int r = 0; r + 1 < R; r++) { ups[r].resize(K[r]); for (auto &v : ups[r]) { int c; if (scanf("%d", &c) != 1) return 1; v.resize(c); for (auto &x : v) if (scanf("%d", &x) != 1) return 1; } }
    vector<vector<u64>> Amask(R);
    for (int r = 0; r < R; r++) { Amask[r].resize(K[r]); for (auto &x : Amask[r]) if (scanf("%llu", (unsigned long long *)&x) != 1) return 1; }
    // per coordinate: domain as list of masks, position of each mask inside the domain
    struct Coord { vector<u64> dom; unordered_map<u64, u32> at; vector<vector<u32>> above; u64 A; };
    vector<vector<Coord>> C(R);
    vector<vector<u64>> mul(R); vector<u64> size(R);
    for (int r = 0; r < R; r++) {
        C[r].resize(K[r]); mul[r].resize(K[r]); u64 s = 1;
        for (int a = 0; a < K[r]; a++) {
            Coord &c = C[r][a]; c.A = Amask[r][a];
            if (!pos.count(c.A)) { fprintf(stderr, "allowed set not in M\n"); return 2; }
            for (u64 m : M) if (!(m & ~c.A)) { c.at[m] = c.dom.size(); c.dom.push_back(m); }
            c.above.resize(c.dom.size());
            for (u32 i = 0; i < c.dom.size(); i++) for (u32 j = 0; j < c.dom.size(); j++) if (!(c.dom[i] & ~c.dom[j])) c.above[i].push_back(j);
            mul[r][a] = s; s *= c.dom.size();
        }
        size[r] = s;
    }
    // slicing: a rank whose table exceeds CAP entries is never materialised; it is processed one value of its
    // largest-domain coordinate c at a time:  T_{r+1}(u) = Σ_{v ∈ D_c, v ⊇ need_c(u)} Zslice_v(need_{-c}(u)),
    // Zslice_v = (coordinate-wise superset sums over a ≠ c of) the slice x_c = v of T_r.
    u64 CAP = argc > 2 ? strtoull(argv[2], 0, 10) : ~0ull;
    vector<char> sliced(R, 0);
    for (int r = 1; r + 1 < R; r++) if (size[r] > CAP) sliced[r] = 1;
    for (int r = 1; r + 1 < R; r++) if (sliced[r] && sliced[r + 1]) { fprintf(stderr, "two consecutive sliced ranks\n"); return 3; }
    auto bigc = [&](int r) { int c = 0; for (int a = 1; a < K[r]; a++) if (C[r][a].dom.size() > C[r][c].dom.size()) c = a; return c; };
    u64 peak = 0;
    for (int r = 0; r + 1 < R; r++) {
        u64 cur = sliced[r] ? size[r] / C[r][bigc(r)].dom.size() + size[r - 1] : size[r];
        if (!sliced[r + 1]) peak = max(peak, cur + size[r + 1]); else peak = max(peak, cur);
    }
    fprintf(stderr, "vsweep: R=%d table sizes:", R); for (int r = 0; r < R; r++) fprintf(stderr, " %llu%s", (unsigned long long)size[r], sliced[r] ? "(sliced)" : "");
    fprintf(stderr, "  peak %.2f GiB\n", peak * 4.0 / (1ull << 30));
    auto zeta = [&](vector<u32> &T, int r, const vector<u64> &mm, u64 total, int skip) {
        for (int a = 0; a < K[r]; a++) {
            if (a == skip) continue;
            const Coord &c = C[r][a]; u64 d = c.dom.size(), m = mm[a], blocks = total / (d * m);
            parallel(blocks * m, [&](u64 lo, u64 hi) {
                vector<u32> in(d);
                for (u64 t = lo; t < hi; t++) {
                    u64 base = (t / m) * d * m + (t % m);
                    for (u64 i = 0; i < d; i++) in[i] = T[base + i * m];
                    for (u64 i = 0; i < d; i++) { u32 s = 0; for (u32 j : c.above[i]) s = addm(s, in[j]); T[base + i * m] = s; }
                }
            });
        }
    };
    // index into rank r's (possibly slice-) layout of need(u) for values u on rank r+1; c = skipped coordinate or -1
    auto need_index = [&](int r, const vector<u64> &u, const vector<u64> &mm, int skip, u64 *needc) {
        u64 id = 0;
        for (int a = 0; a < K[r]; a++) {
            u64 need = 0; for (int b : ups[r][a]) need |= u[b] & C[r][a].A;
            if (a == skip) { *needc = need; continue; }
            id += (u64)C[r][a].at.find(need)->second * mm[a];
        }
        return id;
    };
    auto decode = [&](int r, u64 x, vector<u64> &u, const vector<u64> &mm, int skip) {
        for (int b = K[r] - 1; b >= 0; b--) { if (b == skip) continue; u[b] = C[r][b].dom[x / mm[b]]; x %= mm[b]; }
    };
    vector<u32> T(size[0], 1u);
    for (int r = 0; r + 1 < R; r++) {
        const int k2 = K[r + 1];
        if (!sliced[r]) {
            zeta(T, r, mul[r], size[r], -1);
            if (sliced[r + 1]) { fprintf(stderr, "  rank %d transformed (next rank sliced)\n", r); continue; }
            vector<u32> N(size[r + 1]);
            parallel(size[r + 1], [&](u64 lo, u64 hi) {
                vector<u64> u(k2); u64 dummy;
                for (u64 x = lo; x < hi; x++) { decode(r + 1, x, u, mul[r + 1], -1); N[x] = T[need_index(r, u, mul[r], -1, &dummy)]; }
            });
            T.swap(N); vector<u32>().swap(N);
        } else {
            // T currently holds Z_{r-1}
            int c = bigc(r); const Coord &cc = C[r][c]; u64 d = cc.dom.size();
            vector<u64> m2(K[r]); u64 ss = 1;
            for (int a = 0; a < K[r]; a++) { if (a == c) { m2[a] = 0; continue; } m2[a] = ss; ss *= C[r][a].dom.size(); }
            vector<u32> N(size[r + 1], 0u), Sl(ss);
            for (u64 v = 0; v < d; v++) {
                parallel(ss, [&](u64 lo, u64 hi) {
                    vector<u64> u(K[r]); u64 dummy;
                    for (u64 x = lo; x < hi; x++) { decode(r, x, u, m2, c); u[c] = cc.dom[v]; Sl[x] = T[need_index(r - 1, u, mul[r - 1], -1, &dummy)]; }
                });
                zeta(Sl, r, m2, ss, c);
                const u64 vm = cc.dom[v];
                parallel(size[r + 1], [&](u64 lo, u64 hi) {
                    vector<u64> u(k2); u64 nc = 0;
                    for (u64 x = lo; x < hi; x++) {
                        decode(r + 1, x, u, mul[r + 1], -1);
                        u64 id = need_index(r, u, m2, c, &nc);
                        if (!(nc & ~vm)) N[x] = addm(N[x], Sl[id]);
                    }
                });
            }
            T.swap(N); vector<u32>().swap(N);
        }
        fprintf(stderr, "  rank %d -> %d done\n", r, r + 1);
    }
    u32 ans = 0; for (u32 x : T) ans = addm(ans, x);
    printf("%u\n", ans);
    return 0;
}
