"""
independent_recheck.py

Provenance: written by Anthropic Claude (Fable) on 21 July 2026 during the
audit round, reusing no source code from this repository, with state packing,
window bit order, and orbit numbering chosen independently wherever the
definitions leave freedom. Written with knowledge of the claimed witness and
expected counts: a reimplementation confirmation, not a blinded discovery.
Requires numpy. Expected runtime under one minute.
"""
import numpy as np, time

# ---------- F2 polynomial arithmetic (ints, bit i = coeff of X^i) ----------
def pmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
    return r

def pmod(a, m):
    dm = m.bit_length() - 1
    while a.bit_length() - 1 >= dm and a:
        a ^= m << (a.bit_length() - 1 - dm)
    return a

def pmulmod(a, b, m): return pmod(pmul(a, b), m)

def ppowmod(x, e, m):
    r, b = 1, pmod(x, m)
    while e:
        if e & 1: r = pmulmod(r, b, m)
        b = pmulmod(b, b, m); e >>= 1
    return r

def pgcd(a, b):
    while b: a, b = b, pmod(a, b)
    return a

f1 = sum(1 << i for i in (0, 1, 3, 5, 6, 10, 12))     # 0x146b
f2 = sum(1 << i for i in (0, 1, 3, 4, 8, 9, 12))      # 0x131b
assert f1 == 0x146b and f2 == 0x131b
X = 2

print("== Algebraic layer ==")
for name, f in (("f1", f1), ("f2", f2)):
    irr = (ppowmod(X, 1 << 12, f) == X
           and pgcd(ppowmod(X, 1 << 6, f) ^ X, f) == 1
           and pgcd(ppowmod(X, 1 << 4, f) ^ X, f) == 1)
    o585 = ppowmod(X, 585, f) == 1
    proper = all(ppowmod(X, 585 // p, f) != 1 for p in (3, 5, 13))
    print(f"  {name}: irreducible={irr}, X^585=1: {o585}, exact order 585: {proper}")

# Certificate Q and its consistency with the rectangle polynomial P
P_terms = [(0,0),(0,1),(0,2),(0,5),(0,7),
           (1,2),(1,3),(1,4),(1,5),(1,6),
           (2,0),(2,4),(2,5)]
Q_exps_paper = [0,5,6,117,121,122,235,236,356,470,471,472,475]
Q_from_P = sorted({(351*a + 235*b) % 585 for a, b in P_terms})
print("  Q support from P equals paper's Q:", Q_from_P == sorted(Q_exps_paper))
Q = sum(1 << e for e in Q_exps_paper)
print("  f1 | Q:", pmod(Q, f1) == 0, "  f2 | Q:", pmod(Q, f2) == 0)
print("  P nonzero with deg_X<3, deg_Y<8:", len(P_terms) > 0,
      max(a for a,_ in P_terms) < 3, max(b for _,b in P_terms) < 8)
# sanity: 47*5 - 2*117 = 1 and offset arithmetic
assert 47*5 - 2*117 == 1 and 351 % 5 == 1 and 351 % 117 == 0 \
       and 235 % 5 == 0 and 235 % 117 == 1

# ---------- Sequence machinery ----------
def support(f):
    return [i for i in range(f.bit_length()) if (f >> i) & 1]

def orbits(f, period):
    """All shift-orbits of nonzero sequences with characteristic polynomial f.
    State bit j = a_{k+j}; next bit = sum of state bits at support(f) minus top."""
    deg = f.bit_length() - 1
    taps = sum(1 << i for i in support(f) if i < deg)
    top = deg - 1
    nstates = 1 << deg
    visited = bytearray(nstates)
    out = []
    for seed in range(1, nstates):
        if visited[seed]: continue
        st, bits = seed, []
        for _ in range(period):
            visited[st] = 1
            bits.append(st & 1)
            nb = (st & taps).bit_count() & 1
            st = (st >> 1) | (nb << top)
        assert st == seed, "period mismatch"
        out.append(bits)
    return out

def offsets(h, w):
    return [(351*r + 235*c) % 585 for r in range(h) for c in range(w)]

def census(seqs, h, w):
    offs = offsets(h, w)
    idx = np.array([[(t + o) % 585 for o in offs] for t in range(585)],
                   dtype=np.int32)
    sh = np.arange(len(offs), dtype=np.uint32)
    nwin = 1 << (h * w)
    flat = np.empty(len(seqs) * 585, dtype=np.uint32)
    for k, s in enumerate(seqs):
        a = np.array(s, dtype=np.uint32)
        flat[k*585:(k+1)*585] = (a[idx] << sh).sum(axis=1, dtype=np.uint32)
    counts = np.bincount(flat, minlength=nwin)
    return flat, counts

print("== Single-factor brute force (hypothesis of the conjecture) ==")
for name, f in (("f1", f1), ("f2", f2)):
    seqs = orbits(f, 585)
    _, c = census(seqs, 3, 4)
    ok = (len(seqs) == 7 and c[0] == 0 and (c[1:] == 1).all())
    print(f"  {name}: orbits={len(seqs)}, every nonzero 3x4 window exactly once,"
          f" no zero window: {ok}")

print("== Product brute force (the failure) ==")
t0 = time.time()
fprod = pmul(f1, f2)
seqs = orbits(fprod, 585)
print(f"  orbit count: {len(seqs)} (expect 28679), gen {time.time()-t0:.0f}s")
flat, c = census(seqs, 3, 8)
nz = c[1:]
distinct = int((nz > 0).sum()); missing = int((nz == 0).sum())
dupes = int(nz.sum() - distinct); zerocc = int(c[0])
print(f"  distinct nonzero windows observed: {distinct}")
print(f"  missing nonzero windows:           {missing}")
print(f"  duplicate nonzero occurrences:     {dupes}")
print(f"  zero-window occurrences:           {zerocc}")
print(f"  max multiplicity: {int(c.max())} (rank 23/24 predicts 2)")
match = (distinct, missing, dupes, zerocc) == (8388607, 8388608, 8388607, 1)
print(f"  MATCHES PAPER TABLE: {match}")
# exhibit one collision from my own conventions
val = int(np.nonzero(nz == 2)[0][0]) + 1
locs = np.nonzero(flat == val)[0][:2]
print("  example repeated window value:", hex(val))
for L in locs:
    orb, t = int(L)//585, int(L)%585
    print(f"    orbit {orb}, torus position (row {t%5}, col {t%117})")
print(f"  total time {time.time()-t0:.0f}s")
