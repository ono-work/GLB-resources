// Meet-in-the-middle version of rank_transfer_gen (same input format, plus a final line "rstar").
// Counts (mod p) maps f: S -> M on a graded poset S (given rank by rank, covers between consecutive ranks) with
//   f(a) subseteq A_a                         (allowed set, an element of M)
//   f(b) & A_a subseteq f(a)  for covers a<b  (down-closure of the ideal of J(Q) encoded by f)
// Forward tables G_r (r < rstar) as in rank_transfer_gen; backward tables
//   B_r(w) = #assignments of ranks > r compatible with values w on rank r,
//   B_{r-1}(w) = [w allowed] * Bv_r(m(w)),  m(w)_b = AND_{a lower cover of b} mu(w_a, A_a),
//   mu(w, A) = largest element u of M with u & A subseteq w,   Bv = subset-sum transform.
// Result = sum_{w on rank rstar, allowed} Ghat_{rstar-1}(need(w)) * Bv_{rstar+1}(m(w))   (streamed, never stored).
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <thread>
#include <algorithm>
#include <unordered_map>
using namespace std;
typedef unsigned long long u64;
typedef unsigned __int128 u128;

static int NT = 16;
template <class F> void par_range(u64 n, F f) {
    vector<thread> th; u64 chunk = (n + NT - 1) / NT;
    for (int t = 0; t < NT; t++) { u64 lo = t * chunk, hi = min(n, lo + chunk); if (lo >= hi) break; th.emplace_back([=] { f(t, lo, hi); }); }
    for (auto &x : th) x.join();
}

int main(int argc, char **argv) {
    if (argc > 1) NT = atoi(argv[1]);
    u64 p; int nM;
    if (scanf("%llu %d", &p, &nM) != 2) return 1;
    vector<u64> M(nM);
    for (auto &x : M) if (scanf("%llu", &x) != 1) return 1;
    unordered_map<u64, int> idx; for (int i = 0; i < nM; i++) idx[M[i]] = i;
    vector<int> JT((size_t)nM * nM), IT((size_t)nM * nM);
    for (int i = 0; i < nM; i++) for (int j = 0; j < nM; j++) {
        auto a = idx.find(M[i] | M[j]), b = idx.find(M[i] & M[j]);
        if (a == idx.end() || b == idx.end()) { fprintf(stderr, "M not a lattice of sets\n"); return 2; }
        JT[(size_t)i * nM + j] = a->second; IT[(size_t)i * nM + j] = b->second;
    }
    vector<vector<int>> sup(nM), sub(nM);
    for (int v = 0; v < nM; v++) for (int w = 0; w < nM; w++) {
        if ((M[v] & ~M[w]) == 0) sup[v].push_back(w);
        if ((M[w] & ~M[v]) == 0) sub[v].push_back(w);
    }
    int R; if (scanf("%d", &R) != 1) return 1;
    vector<int> K(R); for (auto &k : K) if (scanf("%d", &k) != 1) return 1;
    vector<vector<vector<int>>> uc(R), lc(R);
    for (int r = 0; r < R; r++) { uc[r].resize(K[r]); lc[r].resize(K[r]); }
    for (int r = 0; r + 1 < R; r++) for (int a = 0; a < K[r]; a++) {
        int c; if (scanf("%d", &c) != 1) return 1; uc[r][a].resize(c);
        for (auto &b : uc[r][a]) { if (scanf("%d", &b) != 1) return 1; lc[r + 1][b].push_back(a); }
        if (c == 0) { fprintf(stderr, "non-top element without upper cover\n"); return 3; }
    }
    vector<vector<int>> AL(R);
    for (int r = 0; r < R; r++) { AL[r].resize(K[r]); for (auto &x : AL[r]) if (scanf("%d", &x) != 1) return 1; }
    int rs; if (scanf("%d", &rs) != 1 || rs < 0 || rs >= R) { fprintf(stderr, "bad rstar\n"); return 1; }
    for (int r = 1; r < R; r++) for (int b = 0; b < K[r]; b++) if (lc[r][b].empty()) { fprintf(stderr, "element without lower cover\n"); return 3; }
    auto pw = [&](int k) { u64 s = 1; for (int i = 0; i < k; i++) s *= nM; return s; };
    auto inA = [&](int v, int a_idx) { return (M[v] & ~M[a_idx]) == 0; };
    // mu[A][w] = largest u in M with u & M[A] subseteq M[w]
    unordered_map<int, vector<int>> mu;
    for (int r = 0; r < R; r++) for (int A : AL[r]) if (!mu.count(A)) {
        vector<int> t(nM);
        for (int w = 0; w < nM; w++) { u64 o = 0; for (int u = 0; u < nM; u++) if ((M[u] & M[A] & ~M[w]) == 0) o |= M[u]; t[w] = idx.at(o); }
        mu[A] = t;
    }
    auto transform = [&](vector<u64> &G, int k, const vector<vector<int>> &L) {  // L = sup (superset sums) or sub
        u64 N = pw(k);
        for (int c = 0; c < k; c++) {
            u64 stride = pw(c), lines = N / nM;
            par_range(lines, [&](int, u64 lo, u64 hi) {
                vector<u64> buf(nM), out(nM);
                for (u64 Lx = lo; Lx < hi; Lx++) {
                    u64 low = Lx % stride, high = Lx / stride, base = high * stride * nM + low;
                    for (int v = 0; v < nM; v++) buf[v] = G[base + v * stride];
                    for (int v = 0; v < nM; v++) { u64 s = 0; for (int w : L[v]) { s += buf[w]; if (s >= p) s -= p; } out[v] = s; }
                    for (int v = 0; v < nM; v++) G[base + v * stride] = out[v];
                }
            });
        }
    };
    // ---------- forward: Ghat_{rs-1} ----------
    vector<u64> Gh;
    if (rs > 0) {
        vector<u64> G(pw(K[0]));
        for (u64 x = 0; x < G.size(); x++) { u64 t = x; bool ok = true; for (int a = 0; a < K[0]; a++) { if (!inA(t % nM, AL[0][a])) ok = false; t /= nM; } G[x] = ok ? 1 % p : 0; }
        for (int r = 0; r + 1 < rs; r++) {
            transform(G, K[r], sup);
            int k = K[r], k2 = K[r + 1]; u64 N2 = pw(k2);
            vector<u64> H(N2), strideR(k); for (int a = 0; a < k; a++) strideR[a] = pw(a);
            auto &U = uc[r];
            par_range(N2, [&](int, u64 lo, u64 hi) {
                vector<int> u(k2);
                for (u64 x = lo; x < hi; x++) {
                    u64 t = x; for (int b = 0; b < k2; b++) { u[b] = t % nM; t /= nM; }
                    bool ok = true; for (int b = 0; b < k2; b++) if (!inA(u[b], AL[r + 1][b])) { ok = false; break; }
                    if (!ok) { H[x] = 0; continue; }
                    u64 id = 0;
                    for (int a = 0; a < k; a++) {
                        const size_t Aa = (size_t)AL[r][a] * nM;
                        int j = IT[Aa + u[U[a][0]]];
                        for (size_t q = 1; q < U[a].size(); q++) j = JT[(size_t)j * nM + IT[Aa + u[U[a][q]]]];
                        id += (u64)j * strideR[a];
                    }
                    H[x] = G[id];
                }
            });
            G.swap(H);
            fprintf(stderr, "fwd rank %d -> %d (table %llu)\n", r, r + 1, (unsigned long long)N2);
        }
        transform(G, K[rs - 1], sup);
        Gh.swap(G);
    }
    // ---------- backward: Bv_{rs+1} ----------
    vector<u64> Bv;
    if (rs < R - 1) {
        vector<u64> B(pw(K[R - 1]));
        for (u64 x = 0; x < B.size(); x++) { u64 t = x; bool ok = true; for (int a = 0; a < K[R - 1]; a++) { if (!inA(t % nM, AL[R - 1][a])) ok = false; t /= nM; } B[x] = ok ? 1 % p : 0; }
        for (int r = R - 1; r > rs + 1; r--) {
            transform(B, K[r], sub);
            int k = K[r], k0 = K[r - 1]; u64 N0 = pw(k0);
            vector<u64> H(N0), strideR(k); for (int b = 0; b < k; b++) strideR[b] = pw(b);
            par_range(N0, [&](int, u64 lo, u64 hi) {
                vector<int> wv(k0);
                for (u64 x = lo; x < hi; x++) {
                    u64 t = x; for (int a = 0; a < k0; a++) { wv[a] = t % nM; t /= nM; }
                    bool ok = true; for (int a = 0; a < k0; a++) if (!inA(wv[a], AL[r - 1][a])) { ok = false; break; }
                    if (!ok) { H[x] = 0; continue; }
                    u64 id = 0;
                    for (int b = 0; b < k; b++) {
                        auto &Lb = lc[r][b];
                        int j = mu[AL[r - 1][Lb[0]]][wv[Lb[0]]];
                        for (size_t q = 1; q < Lb.size(); q++) j = IT[(size_t)j * nM + mu[AL[r - 1][Lb[q]]][wv[Lb[q]]]];
                        id += (u64)j * strideR[b];
                    }
                    H[x] = B[id];
                }
            });
            B.swap(H);
            fprintf(stderr, "bwd rank %d -> %d (table %llu)\n", r, r - 1, (unsigned long long)N0);
        }
        transform(B, K[rs + 1], sub);
        Bv.swap(B);
    }
    // ---------- streamed combination over rank rs ----------
    int k = K[rs]; u64 N = pw(k);
    int kd = rs > 0 ? K[rs - 1] : 0, ku = rs < R - 1 ? K[rs + 1] : 0;
    vector<u64> sd(kd), su(ku); for (int i = 0; i < kd; i++) sd[i] = pw(i); for (int i = 0; i < ku; i++) su[i] = pw(i);
    vector<u64> part(NT, 0);
    vector<const int*> muA(k); for (int a = 0; a < k; a++) muA[a] = mu[AL[rs][a]].data();
    par_range(N, [&](int tid, u64 lo, u64 hi) {
        vector<int> wv(k); u128 acc = 0; u64 s = 0;
        u64 t = lo; for (int a = 0; a < k; a++) { wv[a] = t % nM; t /= nM; }
        for (u64 x = lo; x < hi; x++) {
            bool ok = true; for (int a = 0; a < k; a++) if (!inA(wv[a], AL[rs][a])) { ok = false; break; }
            if (ok) {
                u64 g = 1 % p, b = 1 % p;
                if (rs > 0) {
                    u64 id = 0;
                    for (int a = 0; a < kd; a++) {
                        auto &U = uc[rs - 1][a]; const size_t Aa = (size_t)AL[rs - 1][a] * nM;
                        int j = IT[Aa + wv[U[0]]];
                        for (size_t q = 1; q < U.size(); q++) j = JT[(size_t)j * nM + IT[Aa + wv[U[q]]]];
                        id += (u64)j * sd[a];
                    }
                    g = Gh[id];
                }
                if (g && rs < R - 1) {
                    u64 id = 0;
                    for (int bb = 0; bb < ku; bb++) {
                        auto &Lb = lc[rs + 1][bb];
                        int j = muA[Lb[0]][wv[Lb[0]]];
                        for (size_t q = 1; q < Lb.size(); q++) j = IT[(size_t)j * nM + muA[Lb[q]][wv[Lb[q]]]];
                        id += (u64)j * su[bb];
                    }
                    b = Bv[id];
                }
                acc = (acc + (u128)g * b) % p;
            }
            for (int a = 0; a < k; a++) { if (++wv[a] < nM) break; wv[a] = 0; }
        }
        s = (u64)acc; part[tid] = s;
    });
    u64 s = 0; for (u64 x : part) { s += x; s %= p; }
    printf("%llu\n", s);
    return 0;
}
