#!/usr/bin/env python3
"""Tiny independent recheck of the frozen collision; imports no project code.

This intentionally duplicates recurrence, polynomial multiplication, folding,
and window extraction with tuple/list operations rather than the optimized
integer-state and row-mask machinery in bruteforce.py.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys


F1 = 0x146B
F2 = 0x131B
EXPECTED_PRODUCT = 0x17BD455
R1, R2 = 5, 117
DEGREE = 24


def polynomial_product(left: int, right: int) -> int:
    answer = 0
    shift = 0
    while right:
        if right % 2:
            answer ^= left << shift
        right //= 2
        shift += 1
    return answer


def initial_tuple(integer: int) -> tuple[int, ...]:
    return tuple((integer >> index) & 1 for index in range(DEGREE))


def next_tuple(state: tuple[int, ...]) -> tuple[int, ...]:
    feedback = 0
    for coefficient_index in range(1, DEGREE + 1):
        if EXPECTED_PRODUCT & (1 << coefficient_index):
            feedback ^= state[DEGREE - coefficient_index]
    return state[1:] + (feedback,)


def cycle(representative: int) -> tuple[list[int], set[tuple[int, ...]]]:
    first = initial_tuple(representative)
    state = first
    digits: list[int] = []
    states: set[tuple[int, ...]] = set()
    while True:
        if state in states:
            raise AssertionError("cycle repeated before returning to its first state")
        states.add(state)
        digits.append(state[0])
        state = next_tuple(state)
        if state == first:
            break
    if len(digits) != R1 * R2:
        raise AssertionError(f"period {len(digits)} != {R1 * R2}")
    return digits, states


def fold(digits: list[int]) -> list[list[int]]:
    array = [[-1] * R2 for _ in range(R1)]
    for k, digit in enumerate(digits):
        row, column = k % R1, k % R2
        if array[row][column] != -1:
            raise AssertionError("CRT placement repeated a cell")
        array[row][column] = digit
    if any(digit == -1 for row in array for digit in row):
        raise AssertionError("CRT placement omitted a cell")
    return array


def window(array: list[list[int]], top: int, left: int) -> list[str]:
    return [
        "".join(str(array[(top + i) % R1][(left + j) % R2]) for j in range(8))
        for i in range(3)
    ]


def sequence_hash(digits: list[int]) -> str:
    return hashlib.sha256("".join(map(str, digits)).encode()).hexdigest()


def main() -> int:
    if polynomial_product(F1, F2) != EXPECTED_PRODUCT:
        raise AssertionError("independent polynomial multiplication failed")

    sequence_1, states_1 = cycle(1)
    sequence_8, states_8 = cycle(8)
    sequence_zero, _ = cycle(10_781)
    if not states_1.isdisjoint(states_8):
        raise AssertionError("the two collision sequences are shifts of one another")

    collision_1 = window(fold(sequence_1), 1, 40)
    collision_8 = window(fold(sequence_8), 4, 28)
    zero = window(fold(sequence_zero), 4, 14)
    expected = ["11110001", "00010011", "11100011"]
    if collision_1 != expected or collision_8 != expected:
        raise AssertionError("collision did not reproduce")
    if zero != ["00000000", "00000000", "00000000"]:
        raise AssertionError("zero window did not reproduce")

    print(
        json.dumps(
            {
                "status": "verified by direct recurrence recheck",
                "product_mask_hex": hex(EXPECTED_PRODUCT),
                "periods": [len(sequence_1), len(sequence_8), len(sequence_zero)],
                "orbits_1_and_8_disjoint": True,
                "collision_rows": expected,
                "occurrences": [
                    {"representative_state": 1, "top": 1, "left": 40},
                    {"representative_state": 8, "top": 4, "left": 28},
                ],
                "zero_occurrence": {
                    "representative_state": 10_781,
                    "top": 4,
                    "left": 14,
                },
                "sequence_sha256": {
                    "1": sequence_hash(sequence_1),
                    "8": sequence_hash(sequence_8),
                    "10781": sequence_hash(sequence_zero),
                },
                "python": sys.version,
                "platform": platform.platform(),
                "randomness": "none",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
