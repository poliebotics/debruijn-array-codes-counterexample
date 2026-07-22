"""Small from-scratch GF(2)[x] utilities used only to build calibration fixtures.

The exhaustive PRAC verdict in :mod:`bruteforce` does not call this module.
These routines enumerate the paper's degree-8/exponent-85 factors without a
finite-field library, so the explicit fixture list can be regenerated.
"""

from __future__ import annotations

from collections.abc import Iterator

from bruteforce import polynomial_degree


def divmod_poly(dividend: int, divisor: int) -> tuple[int, int]:
    if divisor == 0:
        raise ZeroDivisionError
    quotient = 0
    divisor_degree = polynomial_degree(divisor)
    while dividend and polynomial_degree(dividend) >= divisor_degree:
        shift = polynomial_degree(dividend) - divisor_degree
        quotient ^= 1 << shift
        dividend ^= divisor << shift
    return quotient, dividend


def mod_poly(dividend: int, modulus: int) -> int:
    return divmod_poly(dividend, modulus)[1]


def gcd_poly(left: int, right: int) -> int:
    while right:
        left, right = right, mod_poly(left, right)
    return left


def multiply_mod(left: int, right: int, modulus: int) -> int:
    result = 0
    modulus_degree = polynomial_degree(modulus)
    while right:
        if right & 1:
            result ^= left
        right >>= 1
        left <<= 1
        if left & (1 << modulus_degree):
            left ^= modulus
    return result


def pow_mod(base: int, exponent: int, modulus: int) -> int:
    result = 1
    while exponent:
        if exponent & 1:
            result = multiply_mod(result, base, modulus)
        exponent >>= 1
        base = multiply_mod(base, base, modulus)
    return result


def prime_divisors(integer: int) -> list[int]:
    result: list[int] = []
    candidate = 2
    while candidate * candidate <= integer:
        if integer % candidate == 0:
            result.append(candidate)
            while integer % candidate == 0:
                integer //= candidate
        candidate += 1
    if integer > 1:
        result.append(integer)
    return result


def divisors(integer: int) -> list[int]:
    return [candidate for candidate in range(1, integer + 1) if integer % candidate == 0]


def is_irreducible(polynomial: int) -> bool:
    """Rabin irreducibility test specialized to GF(2)."""
    degree = polynomial_degree(polynomial)
    if degree < 1 or polynomial & 1 == 0:
        return False
    x = 0b10
    for q in prime_divisors(degree):
        power = x
        for _ in range(degree // q):
            power = multiply_mod(power, power, polynomial)
        if gcd_poly(power ^ x, polynomial) != 1:
            return False
    power = x
    for _ in range(degree):
        power = multiply_mod(power, power, polynomial)
    return power == x


def order_of_x(polynomial: int) -> int:
    if not is_irreducible(polynomial):
        raise ValueError("order_of_x requires an irreducible polynomial")
    degree = polynomial_degree(polynomial)
    group_order = (1 << degree) - 1
    order = group_order
    for prime in prime_divisors(group_order):
        while order % prime == 0 and pow_mod(0b10, order // prime, polynomial) == 1:
            order //= prime
    return order


def monic_polynomials(degree: int, *, constant_one: bool = True) -> Iterator[int]:
    if degree < 1:
        return
    fixed = 1 << degree
    if constant_one:
        fixed |= 1
        for middle in range(1 << (degree - 1)):
            yield fixed | (middle << 1)
    else:
        for lower in range(1 << degree):
            yield fixed | lower


def irreducibles_of_degree_and_exponent(degree: int, exponent: int) -> list[int]:
    return [
        polynomial
        for polynomial in monic_polynomials(degree)
        if is_irreducible(polynomial) and order_of_x(polynomial) == exponent
    ]

