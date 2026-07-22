"""Small, dependency-free exact arithmetic for GF(2^n).

Polynomials over GF(2) are represented by Python integers: bit i is the
coefficient of x^i.  A field element uses the same representation for its
unique residue of degree less than n modulo a monic irreducible polynomial.

This module is deliberately independent of the sequence/brute-force checker.
It is intended for the Corollary 48 and Theorem 47 algebraic tests only.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Iterator, Sequence


def poly_degree(a: int) -> int:
    """Return degree(a), with degree(0) = -1."""
    if a < 0:
        raise ValueError("polynomial encoding must be non-negative")
    return a.bit_length() - 1


def poly_divmod(a: int, b: int) -> tuple[int, int]:
    """Polynomial division over GF(2)."""
    if b == 0:
        raise ZeroDivisionError("polynomial division by zero")
    q = 0
    db = poly_degree(b)
    while a and poly_degree(a) >= db:
        shift = poly_degree(a) - db
        q ^= 1 << shift
        a ^= b << shift
    return q, a


def poly_mod(a: int, modulus: int) -> int:
    return poly_divmod(a, modulus)[1]


def poly_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, poly_mod(a, b)
    return a


def poly_mul(a: int, b: int) -> int:
    """Unreduced polynomial multiplication over GF(2)."""
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
    return out


def poly_mulmod(a: int, b: int, modulus: int) -> int:
    """Polynomial multiplication modulo ``modulus`` over GF(2)."""
    n = poly_degree(modulus)
    if n < 1 or not (modulus >> n) & 1:
        raise ValueError("modulus must be monic of positive degree")
    a = poly_mod(a, modulus)
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & (1 << n):
            a ^= modulus
    return out


def poly_powmod(a: int, exponent: int, modulus: int) -> int:
    if exponent < 0:
        raise ValueError("polynomial exponent must be non-negative")
    out = 1
    while exponent:
        if exponent & 1:
            out = poly_mulmod(out, a, modulus)
        a = poly_mulmod(a, a, modulus)
        exponent >>= 1
    return out


@lru_cache(maxsize=None)
def prime_divisors(m: int) -> tuple[int, ...]:
    """Distinct prime divisors, using deterministic trial division."""
    if m < 1:
        raise ValueError("expected a positive integer")
    factors: list[int] = []
    p = 2
    while p * p <= m:
        if m % p == 0:
            factors.append(p)
            while m % p == 0:
                m //= p
        p = 3 if p == 2 else p + 2
    if m > 1:
        factors.append(m)
    return tuple(factors)


@lru_cache(maxsize=None)
def is_irreducible(f: int) -> bool:
    """Rabin irreducibility test for a monic binary polynomial."""
    n = poly_degree(f)
    if n < 1:
        return False
    if n == 1:
        return True
    if not (f & 1):
        return False
    x = poly_mod(0b10, f)
    # x^(2^n) == x (mod f)
    z = x
    for _ in range(n):
        z = poly_mulmod(z, z, f)
    if z != x:
        return False
    # gcd(x^(2^(n/p)) - x, f) == 1 for each prime p | n.
    for p in prime_divisors(n):
        z = x
        for _ in range(n // p):
            z = poly_mulmod(z, z, f)
        if poly_gcd(z ^ x, f) != 1:
            return False
    return True


def monic_irreducibles(degree: int) -> Iterator[int]:
    """Yield all monic irreducible binary polynomials of a fixed degree."""
    if degree < 1:
        raise ValueError("degree must be positive")
    # An irreducible of degree > 1 has constant term one.
    if degree == 1:
        yield 0b10
        yield 0b11
        return
    leading = 1 << degree
    for middle in range(0, 1 << (degree - 1)):
        f = leading | (middle << 1) | 1
        if is_irreducible(f):
            yield f


@dataclass(frozen=True)
class GF2n:
    """The polynomial-basis field GF(2)[x]/(modulus)."""

    modulus: int

    def __post_init__(self) -> None:
        n = poly_degree(self.modulus)
        if n < 1 or not (self.modulus & (1 << n)):
            raise ValueError("modulus must be monic of positive degree")
        if not is_irreducible(self.modulus):
            raise ValueError("modulus must be irreducible over GF(2)")

    @property
    def degree(self) -> int:
        return poly_degree(self.modulus)

    @property
    def order(self) -> int:
        return 1 << self.degree

    @property
    def alpha(self) -> int:
        """The residue x, which is a root of ``modulus``."""
        return poly_mod(0b10, self.modulus)

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def mul(self, a: int, b: int) -> int:
        return poly_mulmod(a, b, self.modulus)

    def pow(self, a: int, exponent: int) -> int:
        """Field exponentiation, including negative powers of nonzero a."""
        if a == 0 and exponent < 0:
            raise ZeroDivisionError("negative power of zero")
        if a:
            exponent %= self.order - 1
        return poly_powmod(a, exponent, self.modulus)

    def inverse(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError("zero has no multiplicative inverse")
        return self.pow(a, -1)

    def trace(self, a: int) -> int:
        """Absolute trace Tr_GF(2^n)/GF(2), returned as integer 0 or 1."""
        a = poly_mod(a, self.modulus)
        total = 0
        term = a
        for _ in range(self.degree):
            total ^= term
            term = self.mul(term, term)
        if total not in (0, 1):
            raise ArithmeticError(
                f"trace escaped prime field: residue encoding {total:#x}"
            )
        return total

    def multiplicative_order(self, a: int) -> int:
        if a == 0:
            raise ValueError("zero has no multiplicative order")
        order = self.order - 1
        for p in prime_divisors(order):
            while order % p == 0 and self.pow(a, order // p) == 1:
                order //= p
        return order


@lru_cache(maxsize=None)
def polynomial_exponent(f: int) -> int:
    """Exponent of an irreducible f: multiplicative order of x mod f."""
    field = GF2n(f)
    return field.multiplicative_order(field.alpha)


def irreducibles_with_exponent(degree: int, exponent: int) -> tuple[int, ...]:
    if exponent < 1:
        raise ValueError("exponent must be positive")
    return tuple(
        f for f in monic_irreducibles(degree) if polynomial_exponent(f) == exponent
    )


def gf2_rank(rows: Iterable[int], ncols: int | None = None) -> int:
    """Rank over GF(2) of integer-bitset rows.

    Bit c of a row integer is matrix column c.  ``ncols`` is validation only;
    zero high columns are allowed.
    """
    work = list(rows)
    if any(row < 0 for row in work):
        raise ValueError("matrix rows must be non-negative bitsets")
    if ncols is not None:
        if ncols < 0:
            raise ValueError("ncols must be non-negative")
        if any(row >> ncols for row in work):
            raise ValueError("matrix row contains a bit beyond ncols")
    pivots: dict[int, int] = {}
    rank = 0
    for row in work:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                rank += 1
                break
    return rank


def gf2_null_vector(rows: Sequence[int], ncols: int) -> int | None:
    """Return one nonzero right-null vector, or None for full column rank."""
    if ncols < 0 or any(row < 0 or row >> ncols for row in rows):
        raise ValueError("invalid bitset matrix")

    # Each augmented row stores coefficients in low ncols bits and the same
    # row operation applied to an identity matrix in the next m bits.  We only
    # need RREF of the coefficient matrix to identify a free column and solve.
    a = list(rows)
    pivot_row = 0
    pivots: list[int] = []
    for col in range(ncols):
        found = next((r for r in range(pivot_row, len(a)) if (a[r] >> col) & 1), None)
        if found is None:
            continue
        a[pivot_row], a[found] = a[found], a[pivot_row]
        for r in range(len(a)):
            if r != pivot_row and ((a[r] >> col) & 1):
                a[r] ^= a[pivot_row]
        pivots.append(col)
        pivot_row += 1
        if pivot_row == len(a):
            break
    pivot_set = set(pivots)
    free = next((c for c in range(ncols) if c not in pivot_set), None)
    if free is None:
        return None
    x = 1 << free
    # RREF row r has pivot pivots[r].  Set that variable to the dot product of
    # the remaining row coefficients and the chosen free-variable vector.
    for r, pivot in enumerate(pivots):
        if ((a[r] & ~(1 << pivot)) & x).bit_count() & 1:
            x |= 1 << pivot
    if x == 0 or any((row & x).bit_count() & 1 for row in rows):
        raise ArithmeticError("internal null-vector construction failure")
    return x


def xgcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y) with ax + by = g = gcd(a,b), g >= 0."""
    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    if a < 0:
        old_s = -old_s
    if b < 0:
        old_t = -old_t
    return old_r, old_s, old_t


def polynomial_string(f: int) -> str:
    """Human-readable binary polynomial, highest term first."""
    if f == 0:
        return "0"
    terms: list[str] = []
    for i in range(poly_degree(f), -1, -1):
        if not ((f >> i) & 1):
            continue
        terms.append("1" if i == 0 else "x" if i == 1 else f"x^{i}")
    return " + ".join(terms)
