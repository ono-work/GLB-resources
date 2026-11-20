// Compressed meet-in-the-middle rank transfer (producer).
// Same input format as harvest/rank_transfer_mitm.cpp (p, |M|, M, R, K, upper covers, allowed, rstar), argv: threads [w32]
// Counts (mod p) maps f: JA -> M with f(a) subseteq A_a and f(b) & A_a subseteq f(a) for covers a < b.
// Difference to rank_transfer_mitm: coordinate a ranges only over its domain D_a = {m in M : m subseteq A_a}
// (mixed radix), instead of all of M.  Every tuple in prod D_a is reachable, so this is the exact state space.
//  forward:  G_r over prod_{a in rank r} D_a;  Ghat = superset sums inside D_a;
//            G_{r+1}(u) = Ghat_r(need(u)),  need_a = OR_{b upper cover of a} (A_a & u_b)  (subseteq A_a)
//  backward: B_r over prod D_b; Bv = subset sums inside D_b;
//            B_{r-1}(w) = Bv_r(m(w)),  m_b = (AND_{a lower cover of b} mu(w_a, A_a)) & A_b
//  stream over rank rstar:  sum_w Ghat_{rs-1}(need(w)) * Bv_{rs+1}(m(w)).
// Template T = uint64_t (p < 2^62) or uint32_t (p < 2^31, "w32").
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
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
struct Rank {  // coordinates of one rank, mixed radix
    int k; vector<int> A; vector<u64> rad, stride; u64 N;
};
template <class T> int run(u64 p) {
    int nM; if (scanf("%d", &nM) != 1) return 1;
    vector<u64> M(nM); for (auto &x : M) if (scanf("%llu", &x) != 1) return 1;
    unordered_map<u64, int> idx; for (int i = 0; i < nM; i++) idx[M[i]] = i;
    vector<int> JT((size_t)nM * nM), IT((size_t)nM * nM);
    for (int i = 0; i < nM; i++) for (int j = 0; j < nM; j++) {
        auto a = idx.find(M[i] | M[j]), b = idx.find(M[i] & M[j]);
        if (a == idx.end() || b == idx.end()) { fprintf(stderr, "M not a lattice of sets\n"); return 2; }
        JT[(size_t)i * nM + j] = a->second; IT[(size_t)i * nM + j] = b->second;
    }
    int R; if (scanf("%d", &R) != 1) return 1;
    vector<int> K(R); for (auto &k : K) if (scanf("%d", &k) != 1) return 1;
    vector<vector<vector<int>>> uc(R), lc(R);
    for (int r = 0; r < R; r++) { uc[r].resize(K[r]); lc[r].resize(K[r]); }
    for (int r = 0; r + 1 < R; r++) for (int a = 0; a < K[r]; a++) {
        int c; if (scanf("%d", &c) != 1) return 1; uc[r][a].resize(c);
        for (auto &b : uc[r][a]) { if (scanf("%d", &b) != 1) return 1; lc[r + 1][b].push_back(a); }
    }
    vector<Rank> rk(R);
    for (int r = 0; r < R; r++) { rk[r].k = K[r]; rk[r].A.resize(K[r]); for (auto &x : rk[r].A) if (scanf("%d", &x) != 1) return 1; }
    int rs; if (scanf("%d", &rs) != 1 || rs < 0 || rs >= R) return 1;
    // domains D_A (global indices, sorted), local index maps, in-domain superset / subset lists
    unordered_map<int, vector<int>> Dom, Loc; unordered_map<int, vector<vector<int>>> Sup, Sub;
    for (int r = 0; r < R; r++) for (int A : rk[r].A) if (!Dom.count(A)) {
        vector<int> D, L(nM, -1);
        for (int v = 0; v < nM; v++) if ((M[v] & ~M[A]) == 0) { L[v] = D.size(); D.push_back(v); }
        vector<vector<int>> sp(D.size()), sb(D.size());
        for (size_t i = 0; i < D.size(); i++) for (size_t j = 0; j < D.size(); j++) {
            if ((M[D[i]] & ~M[D[j]]) == 0) sp[i].push_back(j);   // D[j] ⊇ D[i]
            if ((M[D[j]] & ~M[D[i]]) == 0) sb[i].push_back(j);   // D[j] ⊆ D[i]
        }
        Dom[A] = D; Loc[A] = L; Sup[A] = sp; Sub[A] = sb;
    }
    for (int r = 0; r < R; r++) {
        auto &q = rk[r]; q.rad.resize(q.k); q.stride.resize(q.k); u64 s = 1;
        for (int a = 0; a < q.k; a++) { q.rad[a] = Dom[q.A[a]].size(); q.stride[a] = s; s *= q.rad[a]; }
        q.N = s;
        fprintf(stderr, "rank %d k=%d compressed=%llu dense=%.3g\n", r, q.k, (unsigned long long)s, __builtin_powi((double)nM, q.k));
    }
    // mu[A][w] = largest u in M with u & A subseteq w  (global index)
    unordered_map<int, vector<int>> mu;
    for (int r = 0; r < R; r++) for (int A : rk[r].A) if (!mu.count(A)) {
        vector<int> t(nM);
        for (int w = 0; w < nM; w++) { u64 o = 0; for (int u = 0; u < nM; u++) if ((M[u] & M[A] & ~M[w]) == 0) o |= M[u]; t[w] = idx.at(o); }
        mu[A] = t;
    }
    auto transform = [&](vector<T> &G, const Rank &q, bool superset) {
        for (int c = 0; c < q.k; c++) {
            u64 n = q.rad[c], st = q.stride[c], lines = q.N / n;
            auto &L = superset ? Sup[q.A[c]] : Sub[q.A[c]];
            par_range(lines, [&](int, u64 lo, u64 hi) {
                vector<T> buf(n), out(n);
                for (u64 Lx = lo; Lx < hi; Lx++) {
                    u64 low = Lx % st, high = Lx / st, base = high * st * n + low;
                    for (u64 v = 0; v < n; v++) buf[v] = G[base + v * st];
                    for (u64 v = 0; v < n; v++) { u64 s = 0; for (int w : L[v]) { s += buf[w]; if (s >= p) s -= p; } out[v] = (T)s; }
                    for (u64 v = 0; v < n; v++) G[base + v * st] = out[v];
                }
            });
        }
    };
    // decode helpers: odometer over a rank, producing global values
    auto start_digits = [&](const Rank &q, u64 x, vector<int> &dg) { for (int a = 0; a < q.k; a++) { dg[a] = x % q.rad[a]; x /= q.rad[a]; } };
    auto step_digits = [&](const Rank &q, vector<int> &dg) { for (int a = 0; a < q.k; a++) { if ((u64)++dg[a] < q.rad[a]) return; dg[a] = 0; } };
    // need-index into rank r (lower) from global values gu on rank r+1
    auto need_idx = [&](int r, const vector<int> &gu) {
        const Rank &q = rk[r]; u64 id = 0;
        for (int a = 0; a < q.k; a++) {
            const size_t Aa = (size_t)q.A[a] * nM; auto &U = uc[r][a];
            int j = IT[Aa + gu[U[0]]];
            for (size_t t = 1; t < U.size(); t++) j = JT[(size_t)j * nM + IT[Aa + gu[U[t]]]];
            id += (u64)Loc[q.A[a]][j] * q.stride[a];
        }
        return id;
    };
    // m-index into rank r (upper) from global values gw on rank r-1
    auto m_idx = [&](int r, const vector<int> &gw) {
        const Rank &q = rk[r], &ql = rk[r - 1]; u64 id = 0;
        for (int b = 0; b < q.k; b++) {
            auto &Lb = lc[r][b];
            int j = mu[ql.A[Lb[0]]][gw[Lb[0]]];
            for (size_t t = 1; t < Lb.size(); t++) j = IT[(size_t)j * nM + mu[ql.A[Lb[t]]][gw[Lb[t]]]];
            j = IT[(size_t)j * nM + q.A[b]];
            id += (u64)Loc[q.A[b]][j] * q.stride[b];
        }
        return id;
    };
    vector<T> Gh, Bv;
    if (rs > 0) {
        vector<T> G(rk[0].N, (T)(1 % p));
        for (int r = 0; r + 1 < rs; r++) {
            transform(G, rk[r], true);
            const Rank &q2 = rk[r + 1]; vector<T> H(q2.N);
            par_range(q2.N, [&](int, u64 lo, u64 hi) {
                vector<int> dg(q2.k), gu(q2.k); start_digits(q2, lo, dg);
                for (u64 x = lo; x < hi; x++) {
                    for (int b = 0; b < q2.k; b++) gu[b] = Dom[q2.A[b]][dg[b]];
                    H[x] = G[need_idx(r, gu)];
                    step_digits(q2, dg);
                }
            });
            G.swap(H); vector<T>().swap(H);
            fprintf(stderr, "fwd %d -> %d (%llu)\n", r, r + 1, (unsigned long long)q2.N);
        }
        transform(G, rk[rs - 1], true); Gh.swap(G);
    }
    if (rs < R - 1) {
        vector<T> B(rk[R - 1].N, (T)(1 % p));
        for (int r = R - 1; r > rs + 1; r--) {
            transform(B, rk[r], false);
            const Rank &q0 = rk[r - 1]; vector<T> H(q0.N);
            par_range(q0.N, [&](int, u64 lo, u64 hi) {
                vector<int> dg(q0.k), gw(q0.k); start_digits(q0, lo, dg);
                for (u64 x = lo; x < hi; x++) {
                    for (int a = 0; a < q0.k; a++) gw[a] = Dom[q0.A[a]][dg[a]];
                    H[x] = B[m_idx(r, gw)];
                    step_digits(q0, dg);
                }
            });
            B.swap(H); vector<T>().swap(H);
            fprintf(stderr, "bwd %d -> %d (%llu)\n", r, r - 1, (unsigned long long)q0.N);
        }
        transform(B, rk[rs + 1], false); Bv.swap(B);
    }
    const Rank &qs = rk[rs];
    vector<u64> part(NT, 0);
    par_range(qs.N, [&](int tid, u64 lo, u64 hi) {
        vector<int> dg(qs.k), gw(qs.k); start_digits(qs, lo, dg); u128 acc = 0; u64 cnt = 0;
        for (u64 x = lo; x < hi; x++) {
            for (int a = 0; a < qs.k; a++) gw[a] = Dom[qs.A[a]][dg[a]];
            u64 g = rs > 0 ? (u64)Gh[need_idx(rs - 1, gw)] : 1 % p;
            if (g) { u64 b = rs < R - 1 ? (u64)Bv[m_idx(rs + 1, gw)] : 1 % p; acc += (u128)g * b; if (++cnt == 8) { acc %= p; cnt = 0; } }
            step_digits(qs, dg);
        }
        part[tid] = (u64)(acc % p);
    });
    u64 s = 0; for (u64 x : part) s = (s + x) % p;
    printf("%llu\n", s);
    return 0;
}
int main(int argc, char **argv) {
    if (argc > 1) NT = atoi(argv[1]);
    bool w32 = argc > 2 && !strcmp(argv[2], "w32");
    u64 p; if (scanf("%llu", &p) != 1) return 1;
    if (w32) { if (p >= (1ULL << 31)) { fprintf(stderr, "w32 needs p < 2^31\n"); return 1; } return run<uint32_t>(p); }
    if (p >= (1ULL << 62)) { fprintf(stderr, "p < 2^62 required\n"); return 1; }
    return run<u64>(p);
}
