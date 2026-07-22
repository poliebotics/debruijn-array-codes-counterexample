"""Corollary 48 and Theorem 47 tests from Blackburn et al. (2025).

Source: S. Blackburn, Y. M. Chee, T. Etzion, and H. Lao,
"On de Bruijn Array Codes Part II: Linear Codes", arXiv:2501.12124v4,
Corollary 48 and Theorem 47.

All computation is exact.  This implementation shares no code with an actual
sequence/folding checker; its results are *algebraic indications* until a
brute-force implementation independently verifies the corresponding PRAC.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence

from gf2 import GF2n, gf2_null_vector, gf2_rank, poly_degree, polynomial_exponent, xgcd


@dataclass(frozen=True)
class HypothesisResult:
    passes: bool
    rank: int
    degree: int
    vectors: tuple[int, ...]
    mu: int
    nu: int
    beta: int
    gamma: int


@dataclass(frozen=True)
class ProductResult:
    passes: bool
    rank: int
    size: int
    rows: tuple[int, ...]
    null_vector: int | None
    mu: int
    nu: int


def _bezout(r1: int, r2: int) -> tuple[int, int]:
    if r1 < 1 or r2 < 1:
        raise ValueError("r1 and r2 must be positive")
    g, mu, nu = xgcd(r1, r2)
    if g != 1:
        raise ValueError("r1 and r2 must be coprime")
    assert mu * r1 + nu * r2 == 1
    return mu, nu


def _validate_exponent(field: GF2n, r1: int, r2: int) -> None:
    expected = r1 * r2
    actual = polynomial_exponent(field.modulus)
    if actual != expected:
        raise ValueError(
            f"polynomial exponent is {actual}, expected r1*r2 = {expected}"
        )


def hypothesis_filter(
    polynomial: int,
    r1: int,
    r2: int,
    n1: int,
    n2: int,
    *,
    validate_exponent: bool = True,
) -> HypothesisResult:
    """Apply Corollary 48 using the polynomial-coordinate representation.

    ``polynomial`` is a bitmask (bit i is coefficient of x^i).  The chosen
    field is GF(2)[x]/(polynomial), and alpha is the residue of x.  If
    mu*r1 + nu*r2 = 1, beta = alpha^(nu*r2) and
    gamma = alpha^(mu*r1).  The test is whether all beta^i gamma^j,
    0 <= i < n1, 0 <= j < n2, have GF(2)-rank n=n1*n2.
    """
    if n1 < 1 or n2 < 1:
        raise ValueError("window dimensions must be positive")
    n = poly_degree(polynomial)
    if n != n1 * n2:
        raise ValueError(f"polynomial degree {n} != n1*n2 = {n1*n2}")
    field = GF2n(polynomial)
    if validate_exponent:
        _validate_exponent(field, r1, r2)
    mu, nu = _bezout(r1, r2)
    alpha = field.alpha
    beta = field.pow(alpha, nu * r2)
    gamma = field.pow(alpha, mu * r1)
    vectors = tuple(
        field.mul(field.pow(beta, i), field.pow(gamma, j))
        for i in range(n1)
        for j in range(n2)
    )
    rank = gf2_rank(vectors, n)
    return HypothesisResult(rank == n, rank, n, vectors, mu, nu, beta, gamma)


def theorem47_matrix(
    polynomials: Sequence[int],
    r1: int,
    r2: int,
    window_n1: int,
    window_n2: int,
    *,
    validate_exponent: bool = True,
) -> ProductResult:
    """Build and rank the concatenated trace matrix C of Theorem 47.

    The paper's theorem uses k distinct irreducibles, each of degree n, and a
    target n1-by-n2 window satisfying n1*n2 = k*n.  Here those target window
    dimensions are named ``window_n1`` and ``window_n2`` to avoid confusing
    the single-factor n2 with the product target k*n2 in Conjecture 1.

    For factor u, alpha_u is x modulo f_u and t_u is the absolute trace.  Bit
    (u*n+v) of row (i,j) is
        Tr(alpha_u^v * beta_u^i * gamma_u^j),
    with i outermost and j innermost in row order.
    """
    if not polynomials:
        raise ValueError("at least one polynomial is required")
    if len(set(polynomials)) != len(polynomials):
        raise ValueError("Theorem 47 requires distinct irreducible factors")
    if window_n1 < 1 or window_n2 < 1:
        raise ValueError("window dimensions must be positive")
    degrees = {poly_degree(f) for f in polynomials}
    if len(degrees) != 1:
        raise ValueError("all factors must have the same degree")
    n = degrees.pop()
    k = len(polynomials)
    size = k * n
    if window_n1 * window_n2 != size:
        raise ValueError(
            f"target window area {window_n1*window_n2} != k*n = {size}"
        )
    mu, nu = _bezout(r1, r2)

    for f in polynomials:
        field = GF2n(f)
        if validate_exponent:
            _validate_exponent(field, r1, r2)

    # Cache the per-factor C_u blocks.  During a subset sweep, each factor's
    # block at a fixed target window is reused in many pair/triple products.
    blocks = tuple(
        _theorem47_factor_rows(f, r1, r2, window_n1, window_n2, mu, nu)
        for f in polynomials
    )
    rows = [
        sum(blocks[u][row_index] << (u * n) for u in range(k))
        for row_index in range(size)
    ]

    frozen_rows = tuple(rows)
    rank = gf2_rank(frozen_rows, size)
    null = None if rank == size else gf2_null_vector(frozen_rows, size)
    return ProductResult(rank == size, rank, size, frozen_rows, null, mu, nu)


@lru_cache(maxsize=8192)
def _theorem47_factor_rows(
    polynomial: int,
    r1: int,
    r2: int,
    window_n1: int,
    window_n2: int,
    mu: int,
    nu: int,
) -> tuple[int, ...]:
    """One cached n-column C_u block, represented as bitset rows."""
    field = GF2n(polynomial)
    n = field.degree
    alpha = field.alpha
    beta = field.pow(alpha, nu * r2)
    gamma = field.pow(alpha, mu * r1)
    beta_powers = [1]
    gamma_powers = [1]
    for _ in range(1, window_n1):
        beta_powers.append(field.mul(beta_powers[-1], beta))
    for _ in range(1, window_n2):
        gamma_powers.append(field.mul(gamma_powers[-1], gamma))

    rows: list[int] = []
    for i in range(window_n1):
        for j in range(window_n2):
            multiplier = field.mul(beta_powers[i], gamma_powers[j])
            alpha_power = 1
            row = 0
            for v in range(n):
                if field.trace(field.mul(alpha_power, multiplier)):
                    row |= 1 << v
                alpha_power = field.mul(alpha_power, alpha)
            rows.append(row)
    return tuple(rows)
