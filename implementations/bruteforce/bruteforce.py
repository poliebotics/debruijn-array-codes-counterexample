#!/usr/bin/env python3
"""Independent exhaustive PRAC checker.

This module deliberately uses only the binary recurrence and literal CRT
folding from Blackburn--Chee--Etzion--Lao.  It does not construct a finite
field and does not use either of the paper's algebraic decision criteria.

Polynomial representation
-------------------------
An integer ``p`` represents a polynomial over GF(2): bit i is the
coefficient of x**i.  Thus x^6 + x^5 + 1 is ``(1<<6)|(1<<5)|1``.

Register convention
-------------------
For c(x) = 1 + sum_{i=1}^N c_i x^i, Equation (1) of the paper is

    a_k = sum_{i=1}^N c_i a_{k-i}  (mod 2).

A state integer stores (a_t, ..., a_{t+N-1}) in bits 0, ..., N-1.
The next state drops bit 0 and appends a_{t+N} in bit N-1.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, Sequence


def polynomial_from_exponents(exponents: Sequence[int]) -> int:
    """Return the GF(2) polynomial having exactly these nonzero terms."""
    value = 0
    for exponent in exponents:
        if exponent < 0:
            raise ValueError("polynomial exponents must be nonnegative")
        value ^= 1 << exponent
    return value


def polynomial_degree(polynomial: int) -> int:
    if polynomial <= 0:
        raise ValueError("the zero polynomial has no degree here")
    return polynomial.bit_length() - 1


def polynomial_exponents(polynomial: int) -> list[int]:
    return [i for i in range(polynomial.bit_length()) if polynomial & (1 << i)]


def polynomial_string(polynomial: int) -> str:
    terms: list[str] = []
    for exponent in reversed(polynomial_exponents(polynomial)):
        if exponent == 0:
            terms.append("1")
        elif exponent == 1:
            terms.append("x")
        else:
            terms.append(f"x^{exponent}")
    return " + ".join(terms) if terms else "0"


def polynomial_multiply(left: int, right: int) -> int:
    """Multiply polynomials over GF(2), without reduction."""
    result = 0
    while right:
        if right & 1:
            result ^= left
        right >>= 1
        left <<= 1
    return result


def multiply_factors(factors: Sequence[int]) -> int:
    result = 1
    for factor in factors:
        result = polynomial_multiply(result, factor)
    return result


def validate_characteristic_polynomial(polynomial: int) -> int:
    degree = polynomial_degree(polynomial)
    if degree < 1:
        raise ValueError("characteristic polynomial must be nonconstant")
    if polynomial & 1 == 0:
        raise ValueError("nonsingular recurrence requires constant term 1")
    if polynomial & (1 << degree) == 0:
        raise AssertionError("internal degree inconsistency")
    return degree


def feedback_state_mask(polynomial: int) -> int:
    """Map c_i to the state bit holding a_{t+N-i}."""
    degree = validate_characteristic_polynomial(polynomial)
    mask = 0
    for i in range(1, degree + 1):
        if polynomial & (1 << i):
            mask |= 1 << (degree - i)
    return mask


def recurrence_step(state: int, degree: int, state_tap_mask: int) -> int:
    feedback = (state & state_tap_mask).bit_count() & 1
    return (state >> 1) | (feedback << (degree - 1))


def state_orbit(
    initial_state: int,
    degree: int,
    state_tap_mask: int,
    expected_period: int | None = None,
) -> list[int]:
    """Return the complete shift orbit beginning at initial_state."""
    if initial_state <= 0 or initial_state >= (1 << degree):
        raise ValueError("initial_state must be a nonzero register state")
    orbit: list[int] = []
    state = initial_state
    while True:
        orbit.append(state)
        state = recurrence_step(state, degree, state_tap_mask)
        if state == initial_state:
            break
        if state == 0:
            raise ValueError("nonzero state entered zero state; recurrence is singular")
        if len(orbit) > (1 << degree) - 1:
            raise ValueError("register orbit did not return to its initial state")
    if expected_period is not None and len(orbit) != expected_period:
        raise ValueError(
            f"state {initial_state} has period {len(orbit)}, expected {expected_period}; "
            "the supplied product is not uniform with the claimed exponent"
        )
    return orbit


class BitSet:
    """Compact fixed-size bit set used for state and window coverage."""

    __slots__ = ("_data", "size")

    def __init__(self, size: int):
        self.size = size
        self._data = bytearray((size + 7) // 8)

    def __contains__(self, item: int) -> bool:
        if item < 0 or item >= self.size:
            raise IndexError(item)
        return bool(self._data[item >> 3] & (1 << (item & 7)))

    def add(self, item: int) -> bool:
        """Add item; return True exactly when it was newly added."""
        if item < 0 or item >= self.size:
            raise IndexError(item)
        byte_index = item >> 3
        bit = 1 << (item & 7)
        was_new = not (self._data[byte_index] & bit)
        self._data[byte_index] |= bit
        return was_new


@dataclass(frozen=True)
class Occurrence:
    codeword_index: int
    representative_state: int
    top: int
    left: int


@dataclass
class CheckResult:
    passed: bool
    r1: int
    r2: int
    window_rows: int
    window_cols: int
    characteristic_polynomial: str
    polynomial_mask_hex: str
    recurrence_degree: int
    claimed_period: int
    codeword_count: int
    expected_codeword_count: int
    total_windows: int
    expected_total_windows: int
    unique_nonzero_windows: int
    duplicate_nonzero_windows: int
    zero_windows: int
    missing_nonzero_windows: int
    first_zero_occurrence: dict | None
    first_collision_word: int | None
    first_collision_rows: list[str] | None
    first_collision_occurrences: list[dict] | None
    first_missing_word: int | None
    first_missing_rows: list[str] | None
    elapsed_seconds: float
    implementation: str = "literal-recurrence-crt-v1"


def crt_index_grid(r1: int, r2: int) -> list[list[int]]:
    """Grid cell (i,j) contains the unique k with k=i mod r1, k=j mod r2."""
    if r1 <= 1 or r2 <= 1 or math.gcd(r1, r2) != 1:
        raise ValueError("r1 and r2 must be coprime integers greater than one")
    period = r1 * r2
    grid = [[-1 for _ in range(r2)] for _ in range(r1)]
    for k in range(period):
        row, column = k % r1, k % r2
        if grid[row][column] != -1:
            raise AssertionError("CRT map was not injective")
        grid[row][column] = k
    if any(index < 0 for row in grid for index in row):
        raise AssertionError("CRT map was not surjective")
    return grid


def fold_sequence(sequence: Sequence[int], r1: int, r2: int) -> list[list[int]]:
    if len(sequence) != r1 * r2:
        raise ValueError("sequence length must equal r1*r2")
    index_grid = crt_index_grid(r1, r2)
    return [[sequence[index_grid[i][j]] for j in range(r2)] for i in range(r1)]


def fold_sequence_row_masks(sequence: Sequence[int], r1: int, r2: int) -> list[int]:
    """Fold literally, representing each resulting array row as an integer."""
    if len(sequence) != r1 * r2:
        raise ValueError("sequence length must equal r1*r2")
    rows = [0] * r1
    # This is the same southeast-diagonal placement as fold_sequence, written
    # directly rather than obtained from either algebraic criterion.
    for k, digit in enumerate(sequence):
        if digit & 1:
            rows[k % r1] |= 1 << (k % r2)
    return rows


def encode_window(
    array: Sequence[Sequence[int]], top: int, left: int, rows: int, columns: int
) -> int:
    """Encode window row-major, with its first entry as bit zero."""
    r1 = len(array)
    r2 = len(array[0])
    result = 0
    bit = 0
    for i in range(rows):
        for j in range(columns):
            result |= (array[(top + i) % r1][(left + j) % r2] & 1) << bit
            bit += 1
    return result


def encode_window_from_row_masks(
    array_rows: Sequence[int],
    array_columns: int,
    top: int,
    left: int,
    rows: int,
    columns: int,
) -> int:
    """Row-major toroidal window extraction from literal folded row masks."""
    if columns > array_columns:
        # The paper's SDBAC necessary conditions exclude this for relevant
        # inputs.  Keep a literal fallback so this helper remains total.
        value = 0
        bit = 0
        for i in range(rows):
            row_mask = array_rows[(top + i) % len(array_rows)]
            for j in range(columns):
                value |= ((row_mask >> ((left + j) % array_columns)) & 1) << bit
                bit += 1
        return value
    row_mask_limit = (1 << array_columns) - 1
    window_mask = (1 << columns) - 1
    value = 0
    for i in range(rows):
        row_mask = array_rows[(top + i) % len(array_rows)]
        rotated = ((row_mask >> left) | (row_mask << (array_columns - left))) & row_mask_limit
        value |= (rotated & window_mask) << (i * columns)
    return value


def decode_window(word: int, rows: int, columns: int) -> list[str]:
    return [
        "".join(str((word >> (i * columns + j)) & 1) for j in range(columns))
        for i in range(rows)
    ]


def iter_codewords(
    polynomial: int, period: int
) -> Iterator[tuple[int, list[int]]]:
    """Yield one literal period sequence for every nonzero shift orbit."""
    degree = validate_characteristic_polynomial(polynomial)
    taps = feedback_state_mask(polynomial)
    visited = BitSet(1 << degree)
    visited.add(0)
    for representative in range(1, 1 << degree):
        if representative in visited:
            continue
        orbit = state_orbit(representative, degree, taps, expected_period=period)
        for state in orbit:
            if not visited.add(state):
                raise AssertionError("distinct register orbits intersected")
        # The emitted digit at this clock is a_t, stored in state bit zero.
        yield representative, [state & 1 for state in orbit]


def iter_folded_codewords(
    polynomial: int, r1: int, r2: int
) -> Iterator[tuple[int, list[int]]]:
    """Generate each recurrence cycle and fold it in one streaming pass.

    This is logically the same literal sequence generation as
    :func:`iter_codewords`, but avoids retaining a full period of Python
    integers.  It matters when the claimed period itself is large.
    """
    period = r1 * r2
    degree = validate_characteristic_polynomial(polynomial)
    taps = feedback_state_mask(polynomial)
    visited = BitSet(1 << degree)
    visited.add(0)
    for representative in range(1, 1 << degree):
        if representative in visited:
            continue
        state = representative
        rows = [0] * r1
        k = 0
        while True:
            if not visited.add(state):
                raise AssertionError("register orbit intersected an earlier orbit")
            if state & 1:
                rows[k % r1] |= 1 << (k % r2)
            k += 1
            state = recurrence_step(state, degree, taps)
            if state == representative:
                break
            if state == 0:
                raise ValueError("nonzero state entered zero state; recurrence is singular")
            if k > (1 << degree) - 1:
                raise ValueError("register orbit did not return to its initial state")
        if k != period:
            raise ValueError(
                f"state {representative} has period {k}, expected {period}; "
                "the supplied product is not uniform with the claimed exponent"
            )
        yield representative, rows


def iter_window_occurrences(
    polynomial: int,
    r1: int,
    r2: int,
    window_rows: int,
    window_cols: int,
) -> Iterator[tuple[int, Occurrence]]:
    for codeword_index, (representative, array_rows) in enumerate(
        iter_folded_codewords(polynomial, r1, r2)
    ):
        for top in range(r1):
            for left in range(r2):
                yield (
                    encode_window_from_row_masks(
                        array_rows,
                        r2,
                        top,
                        left,
                        window_rows,
                        window_cols,
                    ),
                    Occurrence(codeword_index, representative, top, left),
                )


def find_first_occurrence(
    target_word: int,
    polynomial: int,
    r1: int,
    r2: int,
    window_rows: int,
    window_cols: int,
) -> Occurrence | None:
    for word, occurrence in iter_window_occurrences(
        polynomial, r1, r2, window_rows, window_cols
    ):
        if word == target_word:
            return occurrence
    return None


def check_prac(
    polynomial: int,
    r1: int,
    r2: int,
    window_rows: int,
    window_cols: int,
    *,
    locate_witnesses: bool = True,
) -> CheckResult:
    """Exhaustively check every folded window from every nonzero orbit.

    This is exponential in ``window_rows*window_cols`` and is intended as
    finite ground truth, not as a search filter.
    """
    started = time.perf_counter()
    degree = validate_characteristic_polynomial(polynomial)
    period = r1 * r2
    window_bits = window_rows * window_cols
    if degree != window_bits:
        raise ValueError(
            f"recurrence degree {degree} must equal window area {window_bits}"
        )
    if math.gcd(r1, r2) != 1:
        raise ValueError("folding requires gcd(r1,r2)=1")
    if period <= window_rows or period <= window_cols:
        # This is not the paper's exact side condition, but catches obvious
        # malformed inputs while still allowing toroidal windows.
        pass
    state_count = (1 << degree) - 1
    if state_count % period:
        raise ValueError("r1*r2 must divide 2^degree-1")

    seen = BitSet(1 << window_bits)
    total_windows = 0
    unique_nonzero = 0
    duplicate_nonzero = 0
    zero_windows = 0
    codeword_count = 0
    first_zero: Occurrence | None = None
    first_collision_word: int | None = None
    first_collision_second: Occurrence | None = None

    for word, occurrence in iter_window_occurrences(
        polynomial, r1, r2, window_rows, window_cols
    ):
        codeword_count = max(codeword_count, occurrence.codeword_index + 1)
        total_windows += 1
        if word == 0:
            zero_windows += 1
            if first_zero is None:
                first_zero = occurrence
            continue
        if seen.add(word):
            unique_nonzero += 1
        else:
            duplicate_nonzero += 1
            if first_collision_word is None:
                first_collision_word = word
                first_collision_second = occurrence

    expected_codeword_count = state_count // period
    if total_windows != state_count:
        raise AssertionError(
            f"enumerated {total_windows} windows but expected {state_count}"
        )
    if codeword_count != expected_codeword_count:
        raise AssertionError(
            f"enumerated {codeword_count} codewords but expected {expected_codeword_count}"
        )

    missing_count = state_count - unique_nonzero
    if missing_count != duplicate_nonzero + zero_windows:
        raise AssertionError("coverage accounting identity failed")
    first_missing: int | None = None
    if missing_count:
        for word in range(1, 1 << window_bits):
            if word not in seen:
                first_missing = word
                break

    collision_occurrences: list[dict] | None = None
    if locate_witnesses and first_collision_word is not None:
        first_collision_first = find_first_occurrence(
            first_collision_word,
            polynomial,
            r1,
            r2,
            window_rows,
            window_cols,
        )
        if first_collision_first is None or first_collision_second is None:
            raise AssertionError("failed to recover collision witness")
        collision_occurrences = [
            asdict(first_collision_first),
            asdict(first_collision_second),
        ]

    passed = (
        zero_windows == 0
        and duplicate_nonzero == 0
        and unique_nonzero == state_count
        and missing_count == 0
    )
    return CheckResult(
        passed=passed,
        r1=r1,
        r2=r2,
        window_rows=window_rows,
        window_cols=window_cols,
        characteristic_polynomial=polynomial_string(polynomial),
        polynomial_mask_hex=hex(polynomial),
        recurrence_degree=degree,
        claimed_period=period,
        codeword_count=codeword_count,
        expected_codeword_count=expected_codeword_count,
        total_windows=total_windows,
        expected_total_windows=state_count,
        unique_nonzero_windows=unique_nonzero,
        duplicate_nonzero_windows=duplicate_nonzero,
        zero_windows=zero_windows,
        missing_nonzero_windows=missing_count,
        first_zero_occurrence=asdict(first_zero) if first_zero else None,
        first_collision_word=first_collision_word,
        first_collision_rows=(
            decode_window(first_collision_word, window_rows, window_cols)
            if first_collision_word is not None
            else None
        ),
        first_collision_occurrences=collision_occurrences,
        first_missing_word=first_missing,
        first_missing_rows=(
            decode_window(first_missing, window_rows, window_cols)
            if first_missing is not None
            else None
        ),
        elapsed_seconds=time.perf_counter() - started,
    )


def provenance() -> dict:
    source = Path(__file__).read_bytes()
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "script_sha256": hashlib.sha256(source).hexdigest(),
    }


def parse_polynomial(text: str) -> int:
    """Parse either an integer mask or comma-separated exponent list."""
    if "," in text:
        return polynomial_from_exponents([int(part) for part in text.split(",")])
    return int(text, 0)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--factor",
        action="append",
        required=True,
        help="factor as an integer bit mask (e.g. 0x61) or exponent list (e.g. 6,5,0)",
    )
    parser.add_argument("--r1", type=int, required=True)
    parser.add_argument("--r2", type=int, required=True)
    parser.add_argument("--window-rows", type=int, required=True)
    parser.add_argument("--window-cols", type=int, required=True)
    parser.add_argument("--no-witnesses", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    factors = [parse_polynomial(text) for text in args.factor]
    product = multiply_factors(factors)
    payload = {
        "factors": [
            {
                "polynomial": polynomial_string(factor),
                "mask_hex": hex(factor),
                "exponents": polynomial_exponents(factor),
            }
            for factor in factors
        ],
        "result": asdict(
            check_prac(
                product,
                args.r1,
                args.r2,
                args.window_rows,
                args.window_cols,
                locate_witnesses=not args.no_witnesses,
            )
        ),
        "provenance": provenance(),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        sys.stdout.write(rendered)
    return 0 if payload["result"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
