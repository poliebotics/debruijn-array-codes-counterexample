# Algebraic tests for Conjecture 1

This directory contains a dependency-free implementation of the hypothesis
filter in Corollary 15 and the product determinant test in Theorem 6
(arXiv Corollary 48 and Theorem 47) of:

S. Blackburn, Y. M. Chee, T. Etzion, and H. Lao, *On de Bruijn Array
Codes, Part II: Pseudo-Random Array Codes*, IEEE Transactions on
Information Theory 72(8):6204-6221, August 2026, DOI
10.1109/TIT.2026.3686267; arXiv:2501.12124v4 (2025), pp. 23–25 of the
arXiv PDF.

These tests are exact finite-field calculations. Their outputs are
**algebraically indicated**, not **verified by brute force**, under the
epistemic labels in the project brief.

## Representation conventions

- A binary polynomial is a nonnegative integer; bit `i` is its coefficient of
  `x^i`. For example, `x^6+x+1` is `0b1000011` (`0x43`).
- For an irreducible `f` of degree `n`, the field is the polynomial-basis
  quotient `GF(2)[x]/(f)`. A field element is the `n`-bit coefficient vector of
  its canonical residue.
- `alpha` is the residue class of `x`, hence a root of `f`. Its ordered basis
  in Theorem 6 is `(1, alpha, ..., alpha^(n-1))`.
- Extended Euclid returns `(mu, nu)` satisfying `mu*r1 + nu*r2 = 1`. Then
  `beta = alpha^(nu*r2)` and `gamma = alpha^(mu*r1)`. Negative exponents are
  reduced modulo `2^n-1` for nonzero elements.
- The absolute trace is computed literally as
  `z + z^2 + ... + z^(2^(n-1))` in the quotient field and checked to be `0`
  or `1`.
- A binary matrix row is an integer bitset. In Theorem 6, column `u*n+v`
  belongs to factor `u` and basis element `alpha_u^v`. Rows are ordered
  lexicographically with `i` outer and `j` inner.
- Nonsingularity is determined by self-contained integer-bitset Gaussian
  elimination over GF(2). A singular product matrix also returns one explicit
  nonzero right-null vector.

This implementation uses the index range `0 <= j < n2` in Corollary 15,
following the preceding matrix definition and the proof's equations.

## API

```python
from prac_algebra import hypothesis_filter, theorem47_matrix

# x^6+x^5+x^4+x^2+1
f1 = sum(1 << i for i in (6, 5, 4, 2, 0))
# x^6+x^4+x^2+x+1
f2 = sum(1 << i for i in (6, 4, 2, 1, 0))

single = hypothesis_filter(f1, r1=3, r2=7, n1=2, n2=3)
product = theorem47_matrix((f1, f2), 3, 7, window_n1=2, window_n2=6)
assert single.passes and product.passes
```

Function names retain the arXiv numbering by design: `theorem47_matrix`
implements the print Theorem 6 test.

Inputs are validated for irreducibility, common degree, distinctness, target
window area, coprime side lengths, and (by default) exponent `r1*r2`.

## Run calibration

```sh
cd implementations/algebra
python3 -m unittest -v
python3 calibrate.py
```

`calibrate.py` emits a deterministic JSON record containing every calibration
rank, explicit polynomial bitmask, failure null vector, Python version, and
SHA-256 hash of the implementation sources. It uses no randomness.

The suite checks:

1. all eight degree-8 exponent-85 polynomials pass Corollary 15 for
   `(5,17;4,2)`;
2. all 28 pairs pass Theorem 6 for `(5,17;4,4)`;
3. both degree-6 exponent-21 polynomials in Example 19 pass singly at
   `(3,7;2,3)` and jointly at `(3,7;2,6)`;
4. both also pass singly at `(7,3;3,2)`, as stated;
5. their product at `(7,3;3,4)` is singular (rank 6 of 12), algebraically
   confirming the first outside-the-side-condition failure in Example 19;
6. all six degree-6 primitive polynomials pass singly at `(7,9;3,2)`, and the
   two named primitive polynomials fail jointly at `(7,9;3,4)`, with a checked
   null vector; and
7. Theorem 6 at `k=1` agrees with Corollary 15, and product rank is invariant
   under reordering the factors.

The JSON calibration additionally records **algebraic support**, not
brute-force verification, for every one of the 255 nonempty subsets of the
eight exponent-85 factors: all have full Theorem 6 rank at target window
`(4,2k)`.

## Reproducible tuple sweep

`sweep.py` enumerates the prompt's number-theoretically admissible tuples and
writes both a detailed JSONL ledger and a flat CSV summary. It uses a canonical
primitive `GF(2^n)` and binary cyclotomic cosets to enumerate the irreducible
factors of each exponent exactly. For large factor sets, filtering and subset
coverage are deterministically sampled and are explicitly marked incomplete.

```sh
python3 sweep.py --max-degree 24 --output runs/sweep_d24
```

Every tuple row records filtering coverage, per-`k` subset coverage, derived
seeds, rank histograms, factor/subset hashes, and elapsed time. `run_meta.json`
records invocation parameters, versions, source hashes, and final ledger
hashes. On the first singular subset, the sweep stops with exit status 2 and
writes `counterexample_candidate.json`, including explicit reconstructed
polynomials, the full matrix, a right-null vector, and hashes. Such a result is
only **algebraically indicated** pending the separate brute-force checker.
