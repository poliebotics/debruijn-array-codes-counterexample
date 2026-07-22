#!/usr/bin/env python3
"""Unit and paper-calibration tests for the independent checker."""

from __future__ import annotations

import unittest

from bruteforce import (
    check_prac,
    crt_index_grid,
    encode_window,
    encode_window_from_row_masks,
    feedback_state_mask,
    fold_sequence,
    fold_sequence_row_masks,
    iter_folded_codewords,
    iter_codewords,
    multiply_factors,
    polynomial_from_exponents,
    recurrence_step,
    state_orbit,
)
from poly_enumeration import irreducibles_of_degree_and_exponent


def canonical_rotation(bits: list[int] | str) -> str:
    text = bits if isinstance(bits, str) else "".join(map(str, bits))
    return min(text[i:] + text[:i] for i in range(len(text)))


class LiteralMechanicsTests(unittest.TestCase):
    def test_crt_grid_matches_paper_example_1(self) -> None:
        self.assertEqual(
            crt_index_grid(3, 5),
            [[0, 6, 12, 3, 9], [10, 1, 7, 13, 4], [5, 11, 2, 8, 14]],
        )

    def test_fold_matches_paper_example_1(self) -> None:
        sequence = [int(bit) for bit in "000111101011001"]
        self.assertEqual(
            fold_sequence(sequence, 3, 5),
            [[0, 1, 0, 1, 0], [1, 0, 0, 0, 1], [1, 1, 0, 1, 1]],
        )

    def test_recurrence_equation_1_convention(self) -> None:
        # x^4+x+1 gives a_{t+4}=a_{t+3}+a_t.  State bits are
        # (a_t,a_{t+1},a_{t+2},a_{t+3}) = (1,0,0,0).
        polynomial = polynomial_from_exponents([4, 1, 0])
        taps = (1 << 0) | (1 << 3)
        self.assertEqual(recurrence_step(0b0001, 4, taps), 0b1000)

    def test_optimized_window_extraction_matches_literal_arrays(self) -> None:
        for r1, r2 in [(3, 5), (5, 17), (7, 9)]:
            sequence = [((k * k + 3 * k + 1) >> 1) & 1 for k in range(r1 * r2)]
            array = fold_sequence(sequence, r1, r2)
            row_masks = fold_sequence_row_masks(sequence, r1, r2)
            for rows in range(1, min(4, r1) + 1):
                for columns in range(1, min(5, r2) + 1):
                    for top in range(r1):
                        for left in range(r2):
                            self.assertEqual(
                                encode_window(array, top, left, rows, columns),
                                encode_window_from_row_masks(
                                    row_masks, r2, top, left, rows, columns
                                ),
                            )

    def test_paper_example_3_exact_cycles_up_to_shift(self) -> None:
        polynomial = polynomial_from_exponents([6, 5, 4, 2, 0])
        actual = {
            canonical_rotation(sequence)
            for _, sequence in iter_codewords(polynomial, 21)
        }
        printed = {
            canonical_rotation(sequence)
            for sequence in [
                "000001010010011001011",
                "010000111101101010111",
                "001000110111111001110",
            ]
        }
        self.assertEqual(actual, printed)

    def test_streaming_fold_matches_materialized_sequences(self) -> None:
        polynomial = polynomial_from_exponents([6, 5, 4, 2, 0])
        materialized = {
            representative: fold_sequence_row_masks(sequence, 3, 7)
            for representative, sequence in iter_codewords(polynomial, 21)
        }
        streamed = dict(iter_folded_codewords(polynomial, 3, 7))
        self.assertEqual(streamed, materialized)

    def test_degree_8_exponent_85_count(self) -> None:
        factors = irreducibles_of_degree_and_exponent(8, 85)
        self.assertEqual(len(factors), 8)


class PaperGroundTruthTests(unittest.TestCase):
    F21_A = polynomial_from_exponents([6, 5, 4, 2, 0])
    F21_B = polynomial_from_exponents([6, 4, 2, 1, 0])
    F63_A = polynomial_from_exponents([6, 5, 0])
    F63_B = polynomial_from_exponents([6, 1, 0])

    def assertVerdict(
        self,
        factors: list[int],
        parameters: tuple[int, int, int, int],
        expected: bool,
    ) -> None:
        result = check_prac(multiply_factors(factors), *parameters)
        self.assertEqual(result.passed, expected, result)

    def test_example_19_degree_6_exponent_21(self) -> None:
        # Each factor and their product pass in the paper's 3x7 orientation.
        for factor in [self.F21_A, self.F21_B]:
            self.assertVerdict([factor], (3, 7, 2, 3), True)
        self.assertVerdict([self.F21_A, self.F21_B], (3, 7, 2, 6), True)

        # Each factor also passes after swapping the orientation, but their
        # product fails once the side condition n1<r1<2*n1 is violated.
        for factor in [self.F21_A, self.F21_B]:
            self.assertVerdict([factor], (7, 3, 3, 2), True)
        self.assertVerdict([self.F21_A, self.F21_B], (7, 3, 3, 4), False)

    def test_example_19_degree_6_primitive_failure(self) -> None:
        for factor in [self.F63_A, self.F63_B]:
            self.assertVerdict([factor], (7, 9, 3, 2), True)
        self.assertVerdict([self.F63_A, self.F63_B], (7, 9, 3, 4), False)

    def test_all_degree_8_exponent_85_singles_and_pairs(self) -> None:
        factors = irreducibles_of_degree_and_exponent(8, 85)
        for factor in factors:
            self.assertVerdict([factor], (5, 17, 4, 2), True)
        for left_index, left in enumerate(factors):
            for right in factors[left_index + 1 :]:
                self.assertVerdict([left, right], (5, 17, 4, 4), True)


class CounterexampleWitnessTests(unittest.TestCase):
    """Direct witness checks that do not use the coverage bitset."""

    F1 = 0x146B
    F2 = 0x131B
    PRODUCT = 0x17BD455

    def folded_array_from_state(self, representative: int) -> list[list[int]]:
        self.assertEqual(multiply_factors([self.F1, self.F2]), self.PRODUCT)
        orbit = state_orbit(
            representative,
            24,
            feedback_state_mask(self.PRODUCT),
            expected_period=585,
        )
        sequence = [state & 1 for state in orbit]
        return fold_sequence(sequence, 5, 117)

    def test_two_distinct_recurrence_orbits_have_the_frozen_collision(self) -> None:
        first_orbit = set(
            state_orbit(1, 24, feedback_state_mask(self.PRODUCT), 585)
        )
        second_orbit = set(
            state_orbit(8, 24, feedback_state_mask(self.PRODUCT), 585)
        )
        self.assertTrue(first_orbit.isdisjoint(second_orbit))

        first = encode_window(self.folded_array_from_state(1), 1, 40, 3, 8)
        second = encode_window(self.folded_array_from_state(8), 4, 28, 3, 8)
        self.assertEqual(first, 13_093_007)
        self.assertEqual(second, 13_093_007)
        self.assertEqual(
            [
                "".join(str((first >> (i * 8 + j)) & 1) for j in range(8))
                for i in range(3)
            ],
            ["11110001", "00010011", "11100011"],
        )

    def test_frozen_zero_window_directly_from_recurrence(self) -> None:
        zero = encode_window(self.folded_array_from_state(10_781), 4, 14, 3, 8)
        self.assertEqual(zero, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
