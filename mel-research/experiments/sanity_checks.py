#!/usr/bin/env python3
"""Computational sanity checks backing concrete examples in the MEL research notes.

Nothing here is a proof. Each block recomputes a small, finite instance of a claim
that the reports rely on, so that the example is *computed*, not merely asserted.

Run:  python3 sanity_checks.py        (needs numpy, scipy, sympy)
"""
import itertools

import numpy as np
import scipy.linalg as sla
from sympy import Matrix, ZZ
from sympy.matrices.normalforms import smith_normal_form

rng = np.random.default_rng(0)


def ok(cond, msg):
    print(("[OK]   " if cond else "[FAIL] ") + msg)
    assert cond, msg


def info(msg):
    print("       " + msg)


def rank_f2(M):
    """Rank of an integer matrix over F_2 by Gaussian elimination."""
    A = (np.array(M, dtype=np.int64) % 2).astype(np.uint8)
    r = 0
    rows, cols = A.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i, c]), None)
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        r += 1
        if r == rows:
            break
    return r


def rank_q(M):
    return Matrix(np.array(M, dtype=int).tolist()).rank()


def snf_diag(M):
    S = smith_normal_form(Matrix(np.array(M, dtype=int).tolist()), domain=ZZ)
    d = [abs(int(S[i, i])) for i in range(min(S.shape)) if S[i, i] != 0]
    return d


# ---------------------------------------------------------------------------
print("\n== S1  Corridor C: RP^2 (6-vertex triangulation) - Tor defect under coefficient change ==")
tris = [(1, 2, 3), (1, 3, 4), (1, 4, 5), (1, 5, 6), (1, 2, 6),
        (2, 3, 5), (3, 4, 6), (2, 4, 5), (3, 5, 6), (2, 4, 6)]
tris = [tuple(sorted(t)) for t in tris]
verts = sorted({v for t in tris for v in t})
edges = sorted({e for t in tris for e in itertools.combinations(t, 2)})
ecount = {e: 0 for e in edges}
for t in tris:
    for e in itertools.combinations(t, 2):
        ecount[e] += 1
ok(all(c == 2 for c in ecount.values()), "every edge lies in exactly two triangles (closed surface)")
ok(len(verts) - len(edges) + len(tris) == 1, f"Euler characteristic V-E+F = {len(verts)}-{len(edges)}+{len(tris)} = 1")

vi = {v: i for i, v in enumerate(verts)}
ei = {e: i for i, e in enumerate(edges)}
d1 = np.zeros((len(verts), len(edges)), dtype=int)
for (a, b), j in ei.items():
    d1[vi[b], j] += 1
    d1[vi[a], j] -= 1
d2 = np.zeros((len(edges), len(tris)), dtype=int)
for j, (a, b, c) in enumerate(tris):
    d2[ei[(b, c)], j] += 1
    d2[ei[(a, c)], j] -= 1
    d2[ei[(a, b)], j] += 1
ok(not (d1 @ d2).any(), "boundary of boundary is zero (d1 @ d2 = 0)")

nC = [len(verts), len(edges), len(tris)]
rQ = [rank_q(d1), rank_q(d2)]
rF = [rank_f2(d1), rank_f2(d2)]


def betti(r):
    return [nC[0] - r[0], nC[1] - r[0] - r[1], nC[2] - r[1]]


bQ, bF = betti(rQ), betti(rF)
info(f"Betti numbers over Q  : {bQ}")
info(f"Betti numbers over F2 : {bF}")
tors_H1 = [x for x in snf_diag(d2) if x > 1]
tors_H0 = [x for x in snf_diag(d1) if x > 1]
info(f"Smith normal form of d2 over Z: invariant factors > 1 = {tors_H1}  -> torsion of H_1(Z)")
ok(tors_H1 == [2] and tors_H0 == [], "H_*(RP^2;Z) = Z, Z/2, 0")
ok(bQ == [1, 0, 0] and bF == [1, 1, 1], "dim H_*(;Q) = (1,0,0) but dim H_*(;F2) = (1,1,1)")
ok(sum((-1) ** n * bQ[n] for n in range(3)) == sum((-1) ** n * bF[n] for n in range(3)) == 1,
   "Euler characteristic is coefficient-independent (= 1)")
# UCT: dim H_n(;F2) = dim(H_n(Z) (x) F2) + dim Tor(H_{n-1}(Z), F2)
free = bQ
even_tors = [0, len([t for t in tors_H1 if t % 2 == 0]), 0]
pred = [free[n] + even_tors[n] + (even_tors[n - 1] if n > 0 else 0) for n in range(3)]
ok(pred == bF, f"universal coefficient theorem prediction {pred} matches direct computation {bF}")
info("Defect of the 'commuting square' H_n(C;Z)(x)k -> H_n(C(x)k) in degree 2 with k=F2: Tor(Z/2,F2)=F2 (dim 1)")

# graph (1-dim) control: no torsion; beta_1 = E - V + c; orientation flips do not change ranks
gV = 7
gE = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3), (5, 6), (1, 5)]
g1 = np.zeros((gV, len(gE)), dtype=int)
for j, (a, b) in enumerate(gE):
    g1[b, j] += 1
    g1[a, j] -= 1
flip = np.diag(rng.choice([-1, 1], size=len(gE)))
ok(rank_q(g1) == rank_q(g1 @ flip) == rank_f2(g1) == gV - 1, "graph: boundary rank is orientation- and coefficient-independent (V-c)")
ok([x for x in snf_diag(g1) if x > 1] == [], "graph: no torsion (H_1 of a graph is free), so no Tor defect arises in 1-dim")
info(f"graph beta_1 = E - V + c = {len(gE)} - {gV} + 1 = {len(gE) - gV + 1}")

# ---------------------------------------------------------------------------
print("\n== S2  Corridor B: weighted graph -> Markov kernel (loss, gauge, lumping) ==")
n = 5
W = rng.random((n, n)) * (rng.random((n, n)) < 0.7)
for i in range(n):
    if W[i].sum() == 0:
        W[i, (i + 1) % n] = 0.5
Dg = W.sum(1)
P = W / Dg[:, None]
Lam = rng.random(n) + 0.5
P2 = (Lam[:, None] * W) / (Lam * Dg)[:, None]
ok(np.allclose(P, P2), "directed case: row-normalisation forgets W ~ Lambda*W (row scales are the lost information)")

S = rng.random((n, n)) + 0.1
Ws = S + S.T
Ds = Ws.sum(1)
Ps = Ws / Ds[:, None]
pi = Ds / Ds.sum()
ok(np.allclose(pi @ Ps, pi), "undirected case: stationary law pi ~ degree")
Wrec = np.diag(pi) @ Ps
ratio = Wrec / Ws
ok(np.allclose(ratio, ratio[0, 0]), "undirected case: W is recovered from (P, pi) up to ONE global scalar")
Nrm = Ws / np.sqrt(np.outer(Ds, Ds))
ok(np.allclose(np.sort(np.linalg.eigvals(Ps).real), np.sort(np.linalg.eigvalsh(Nrm))),
   "spectrum of P equals spectrum of symmetric normalisation D^-1/2 W D^-1/2 (similarity by D^1/2)")
# slow-mixing example (lazy ring, n=24) so that the spectral-gap check is not vacuous
nr = 24
Wr = 0.5 * np.eye(nr) + 0.25 * (np.roll(np.eye(nr), 1, 0) + np.roll(np.eye(nr), -1, 0))
Pr = Wr / Wr.sum(1, keepdims=True)
pir = np.ones(nr) / nr
lam2 = np.sort(np.abs(np.linalg.eigvalsh(Pr)))[::-1][1]
for t in (20, 60, 120):
    errt = np.abs(np.linalg.matrix_power(Pr, t) - np.outer(np.ones(nr), pir)).max()
    info(f"lazy ring n=24, t={t}: max|P^t - 1 pi| = {errt:.2e},  |lambda_2|^t = {lam2 ** t:.2e}")
errt = np.abs(np.linalg.matrix_power(Pr, 120) - np.outer(np.ones(nr), pir)).max()
ok(errt <= 5 * lam2 ** 120 and errt > 1e-6, "convergence rate of P^t is governed by |lambda_2| (spectral gap), non-vacuously (error is far above machine precision)")

# lumping
V = np.array([[1, 0], [1, 0], [0, 1], [0, 1]], dtype=float)


def lumpable_chain():
    """Rows 0,1 put mass 0.3 on block {0,1}; rows 2,3 put mass 0.4 on it (block-mass equal inside each block)."""
    a, c = 0.3, 0.6
    out = []
    for b in (a, a, 1 - c, 1 - c):
        x = rng.random(2)
        x = x / x.sum() * b
        y = rng.random(2)
        y = y / y.sum() * (1 - b)
        out.append(np.concatenate([x, y]))
    return np.array(out)


PL = lumpable_chain()
Phat = np.linalg.pinv(V) @ PL @ V
ok(np.allclose(PL @ V, V @ Phat), "lumpable chain: intertwining P V = V P^ holds exactly (Kemeny-Snell)")
PN = PL.copy()
PN[1] = np.array([0.45, 0.05, 0.2, 0.3])  # block mass now 0.5 != 0.3 -> not lumpable
PN /= PN.sum(1, keepdims=True)
Ph0 = np.linalg.pinv(V) @ PN @ V
defect = np.abs(PN @ V - V @ Ph0).max()
ok(defect > 1e-3, f"non-lumpable chain: intertwining defect = {defect:.3f} > 0 (naive aggregation is NOT a Markov kernel on blocks)")
# Galerkin / pi-weighted compression = conditional expectation in L2(pi)
w, vec = np.linalg.eig(PN.T)
piN = np.real(vec[:, np.argmin(np.abs(w - 1))])
piN = piN / piN.sum()
Pi = np.diag(piN)
Ph = np.linalg.inv(V.T @ Pi @ V) @ V.T @ Pi @ PN @ V
ok(np.allclose(Ph.sum(1), 1) and (Ph >= -1e-12).all(), "pi-weighted compression gives a genuine stochastic matrix on blocks")
ok(np.allclose((piN @ V) @ Ph, piN @ V), "...and its stationary law is the lumped stationary law  (same mechanism as Galerkin / conditional expectation)")

# ---------------------------------------------------------------------------
print("\n== S3  Corridor A/D: a matrix is typed by its gauge action, not by its shape ==")
m = 6
A = rng.standard_normal((m, m))
Q = rng.standard_normal((m, m)) + 3 * np.eye(m)
sim = Q @ A @ np.linalg.inv(Q)
con = Q.T @ A @ Q
ev = lambda X: np.sort_complex(np.linalg.eigvals(X))
ok(np.allclose(ev(sim), ev(A)), "Endo (similarity P A P^-1): eigenvalues are gauge-invariant")
ok(not np.allclose(ev(con), ev(A)), "Bil (congruence P^T A P): eigenvalues are NOT gauge-invariant -> 'eigenvalues of a Gram/Hessian matrix' need a declared metric")
G = rng.standard_normal((m, m))
G = G + G.T
Gc = Q.T @ G @ Q
inert = lambda X: (int((np.linalg.eigvalsh(X) > 0).sum()), int((np.linalg.eigvalsh(X) < 0).sum()))
ok(inert(G) == inert(Gc), f"Bil: inertia (signature) {inert(G)} is the congruence invariant (Sylvester)")


def fem(nn):
    h = 1 / (nn + 1)
    K = (2 * np.eye(nn) - np.eye(nn, k=1) - np.eye(nn, k=-1)) / h
    Mm = h * (4 * np.eye(nn) + np.eye(nn, k=1) + np.eye(nn, k=-1)) / 6
    return K, Mm, h


conds = []
for nn in (16, 32, 64, 128):
    K, Mm, h = fem(nn)
    conds.append(np.linalg.cond(K))
info("cond(K) for n=16,32,64,128 : " + ", ".join(f"{c:.0f}" for c in conds) + "  (ratio ~4 per doubling => O(h^-2))")
ok(all(3.5 < conds[i + 1] / conds[i] < 4.5 for i in range(3)), "stiffness-matrix conditioning grows like h^-2")
K, Mm, h = fem(8)
Sg = rng.standard_normal((8, 8)) + 3 * np.eye(8)
Kp, Mp = Sg.T @ K @ Sg, Sg.T @ Mm @ Sg
ok(not np.allclose(np.sort(np.linalg.eigvalsh(K)), np.sort(np.linalg.eigvalsh(Kp))), "eigenvalues of the stiffness matrix alone change with the basis")
g1_ = sla.eigh(K, Mm, eigvals_only=True)
g2_ = sla.eigh(Kp, Mp, eigvals_only=True)
ok(np.allclose(g1_, g2_), "generalised eigenvalues of the pencil (K, M) are basis-invariant")
info(f"smallest generalised eigenvalue {g1_[0]:.4f}  vs  pi^2 = {np.pi ** 2:.4f}")
x = rng.standard_normal(8)
xp = np.linalg.solve(Sg, x)
ok(np.isclose(x @ K @ x, xp @ Kp @ xp), "energy a(u_h,u_h) is gauge-invariant (x^T K x = x'^T K' x')")
ok(np.linalg.cond(Kp) > 2 * np.linalg.cond(K) or np.linalg.cond(Kp) < 0.5 * np.linalg.cond(K),
   f"conditioning is basis-dependent: cond(K)={np.linalg.cond(K):.1f}, cond(K')={np.linalg.cond(Kp):.1f} -> cost is NOT a gauge-invariant observable")

# Galerkin orthogonality + best approximation (-u'' = 1 on (0,1), exact u = x(1-x)/2)
nn = 9
K, Mm, h = fem(nn)
b = h * np.ones(nn)
uc = np.linalg.solve(K, b)
mq = 40
xs = np.linspace(0, 1, (nn + 1) * mq + 1)
xm = 0.5 * (xs[1:] + xs[:-1])
dx = xs[1] - xs[0]
nodes = np.linspace(0, 1, nn + 2)


def hat_deriv(coef):
    full = np.concatenate([[0], coef, [0]])
    slope = np.diff(full) / h
    return slope[np.minimum((xm / h).astype(int), nn)]


du = (0.5 - xm)  # derivative of x(1-x)/2
r = du - hat_deriv(uc)
orth = max(abs(np.sum(r * hat_deriv(rng.standard_normal(nn))) * dx) for _ in range(200))
ok(orth < 1e-10, f"Galerkin orthogonality a(u-u_h, v_h) = 0 (max |.| = {orth:.1e})")
e0 = np.sum(r ** 2) * dx
worse = all(np.sum((du - hat_deriv(uc + 0.1 * rng.standard_normal(nn))) ** 2) * dx > e0 for _ in range(500))
ok(worse, "u_h is the energy-norm best approximation in V_h (all 500 perturbations are worse)")

# ---------------------------------------------------------------------------
print("\n== S4  Composition of graded claims: affine error monoid and a rejected composition ==")
def comp(second, first):  # (L2,e2) after (L1,e1) = (L2 L1, e2 + L2 e1)
    return (second[0] * first[0], second[1] + second[0] * first[1])


trip = [(rng.random() * 3, rng.random()) for _ in range(3)]
lhs = comp(trip[2], comp(trip[1], trip[0]))
rhs = comp(comp(trip[2], trip[1]), trip[0])
ok(np.allclose(lhs, rhs) and comp((1, 0), trip[0]) == trip[0] and comp(trip[0], (1, 0)) == trip[0],
   "(L,eps) composition is associative with unit (1,0)  [monoid of affine error bounds]")

eps = 1e-6
xs_ = np.linspace(0.3, 2.7, 2000)
rows = []
for hh in (1e-1, 1e-2, 1e-3, 1e-4):
    noise = rng.uniform(-eps, eps, size=(2, xs_.size))
    noisy = lambda s, k: np.sin(s) + noise[k]
    fd = (noisy(xs_ + hh, 0) - noisy(xs_ - hh, 1)) / (2 * hh)
    err = np.abs(fd - np.cos(xs_)).max()
    bound = hh ** 2 / 6 + eps / hh  # eps2 + L2*eps1  with L2 = 1/h, eps2 = truncation h^2/6*sup|g'''|
    rows.append((hh, err, bound))
    ok(err <= bound * 1.0001, f"h={hh:g}: observed {err:.2e} <= composed bound {bound:.2e}")
ok(rows[-1][1] > 100 * eps, "stage 1 error 1e-6 is amplified to ~1e-2 by a downstream map with L ~ 1/h: composition needs a declared stability constant")

# ---------------------------------------------------------------------------
print("\n== S5  Composition of loss: observable flow ==")
trials, lost_by_g, mono_ok = 2000, 0, True
for _ in range(trials):
    nx, ny, nz = 8, 5, 3
    f = rng.integers(0, ny, nx)
    g = rng.integers(0, nz, ny)
    q = rng.integers(0, 3, nx)

    def recoverable(h):
        return all(q[i] == q[j] for i in range(nx) for j in range(nx) if h[i] == h[j])

    gf = g[f]
    rf, rgf = recoverable(f), recoverable(gf)
    mono_ok &= (not rgf) or rf          # recoverable after g.f  =>  recoverable after f
    lost_by_g += (rf and not rgf)
ok(mono_ok, "kernel pair of g.f contains kernel pair of f: information lost never returns (monotone)")
info(f"in {trials} random finite trials, g destroyed an observable that f still preserved {lost_by_g} times -> composition must be checked per observable")

print("\nAll sanity checks passed.")
