"""Calibration and arithmetic tests for the algebraic PRAC criteria."""

from __future__ import annotations

import itertools
import unittest

from gf2 import (
    GF2n,
    gf2_null_vector,
    gf2_rank,
    irreducibles_with_exponent,
    is_irreducible,
    polynomial_exponent,
)
from prac_algebra import hypothesis_filter, theorem47_matrix


def p(*exponents: int) -> int:
    """Polynomial bitmask from exponents of nonzero terms."""
    return sum(1 << i for i in exponents)


class TestGF2Arithmetic(unittest.TestCase):
    def test_degree_3_field_axioms_and_trace(self) -> None:
        # x^3+x+1 is primitive.
        f = p(3, 1, 0)
        field = GF2n(f)
        self.assertEqual(field.multiplicative_order(field.alpha), 7)
        for a in range(8):
            for b in range(8):
                self.assertEqual(field.mul(a, b), field.mul(b, a))
                self.assertEqual(field.trace(a ^ b), field.trace(a) ^ field.trace(b))
        for a in range(1, 8):
            self.assertEqual(field.mul(a, field.inverse(a)), 1)
        # Absolute trace is Frobenius invariant and prime-field-valued.
        for a in range(8):
            self.assertIn(field.trace(a), (0, 1))
            self.assertEqual(field.trace(a), field.trace(field.mul(a, a)))

    def test_irreducible_counts(self) -> None:
        # Number of monic irreducibles: degree 6 -> 9, degree 8 -> 30.
        from gf2 import monic_irreducibles

        self.assertEqual(len(tuple(monic_irreducibles(6))), 9)
        self.assertEqual(len(tuple(monic_irreducibles(8))), 30)

    def test_null_vector(self) -> None:
        rows = (0b011, 0b110, 0b101)
        self.assertEqual(gf2_rank(rows, 3), 2)
        x = gf2_null_vector(rows, 3)
        self.assertIsNotNone(x)
        assert x is not None
        self.assertTrue(all((row & x).bit_count() % 2 == 0 for row in rows))

    def test_companion_and_recurrence_conventions(self) -> None:
        # Independent companion-action convention check.  For
        # f=x^n+sum(c_j*x^j), multiplying a coefficient column by alpha=x
        # shifts it left and replaces overflow x^n by sum(c_j*x^j).
        f = p(6, 5, 4, 2, 0)
        field = GF2n(f)
        n = 6
        mask = (1 << n) - 1
        for a in range(1 << n):
            companion = (a << 1) & mask
            if (a >> (n - 1)) & 1:
                companion ^= f & mask
            self.assertEqual(companion, field.mul(a, field.alpha))

        # The trace realization then satisfies the standard characteristic-
        # polynomial recurrence s_(i+n)=sum_j c_j*s_(i+j).
        coefficients = f & mask
        for theta in range(1 << n):
            seq = [field.trace(field.mul(theta, field.pow(field.alpha, i)))
                   for i in range(2 * n)]
            for i in range(n):
                rhs = 0
                for j in range(n):
                    if (coefficients >> j) & 1:
                        rhs ^= seq[i + j]
                self.assertEqual(seq[i + n], rhs)


class TestPaperCalibration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.exp85 = irreducibles_with_exponent(8, 85)

    def test_exponent_85_polynomial_count(self) -> None:
        # phi(85)/ord_85(2) = 64/8 = 8.
        self.assertEqual(len(self.exp85), 8)
        self.assertTrue(all(is_irreducible(f) for f in self.exp85))
        self.assertTrue(all(polynomial_exponent(f) == 85 for f in self.exp85))

    def test_all_eight_5x17_single_factors_pass(self) -> None:
        # Paper motivating instance: degree 8, exponent 85,
        # (r1,r2;n1,n2) = (5,17;4,2).
        for f in self.exp85:
            with self.subTest(f=hex(f)):
                result = hypothesis_filter(f, 5, 17, 4, 2)
                self.assertTrue(result.passes)
                self.assertEqual(result.rank, 8)

    def test_all_28_exponent_85_pairs_pass(self) -> None:
        # The product target in Conjecture 1 is (5,17;4,4).
        for f, g in itertools.combinations(self.exp85, 2):
            with self.subTest(f=hex(f), g=hex(g)):
                result = theorem47_matrix((f, g), 5, 17, 4, 4)
                self.assertTrue(result.passes)
                self.assertEqual(result.rank, 16)

    def test_example19_degree6_exponent21(self) -> None:
        f1 = p(6, 5, 4, 2, 0)  # x^6+x^5+x^4+x^2+1
        f2 = p(6, 4, 2, 1, 0)  # x^6+x^4+x^2+x+1
        self.assertEqual(polynomial_exponent(f1), 21)
        self.assertEqual(polynomial_exponent(f2), 21)

        # Both single factors yield (3,7;2,3), and their product yields
        # (3,7;2,6), exactly as stated in Example 19.
        self.assertTrue(hypothesis_filter(f1, 3, 7, 2, 3).passes)
        self.assertTrue(hypothesis_filter(f2, 3, 7, 2, 3).passes)
        self.assertTrue(theorem47_matrix((f1, f2), 3, 7, 2, 6).passes)

        # The paper also says each single factor yields (7,3;3,2).  Its text
        # notes that the conjecture's side condition fails, but does not state
        # in that sentence whether this particular product passes or fails.
        self.assertTrue(hypothesis_filter(f1, 7, 3, 3, 2).passes)
        self.assertTrue(hypothesis_filter(f2, 7, 3, 3, 2).passes)
        outside = theorem47_matrix((f1, f2), 7, 3, 3, 4)
        self.assertFalse(outside.passes)
        self.assertEqual(outside.rank, 6)

    def test_example19_primitive_failure(self) -> None:
        f1 = p(6, 5, 0)  # x^6+x^5+1
        f2 = p(6, 1, 0)  # x^6+x+1
        self.assertEqual(polynomial_exponent(f1), 63)
        self.assertEqual(polynomial_exponent(f2), 63)
        self.assertTrue(hypothesis_filter(f1, 7, 9, 3, 2).passes)
        self.assertTrue(hypothesis_filter(f2, 7, 9, 3, 2).passes)
        product = theorem47_matrix((f1, f2), 7, 9, 3, 4)
        self.assertFalse(product.passes)
        self.assertLess(product.rank, 12)
        self.assertIsNotNone(product.null_vector)
        assert product.null_vector is not None
        self.assertTrue(
            all(
                (row & product.null_vector).bit_count() % 2 == 0
                for row in product.rows
            )
        )

    def test_all_six_degree6_primitives_pass_singly(self) -> None:
        primitives = irreducibles_with_exponent(6, 63)
        self.assertEqual(len(primitives), 6)
        for f in primitives:
            with self.subTest(f=hex(f)):
                result = hypothesis_filter(f, 7, 9, 3, 2)
                self.assertTrue(result.passes)
                self.assertEqual(result.rank, 6)

    def test_theorem47_k1_agrees_with_corollary48(self) -> None:
        for f in self.exp85:
            cor48 = hypothesis_filter(f, 5, 17, 4, 2)
            thm47 = theorem47_matrix((f,), 5, 17, 4, 2)
            self.assertEqual(cor48.passes, thm47.passes)
            self.assertEqual(cor48.rank, thm47.rank)

    def test_product_rank_is_factor_order_invariant(self) -> None:
        f, g = self.exp85[:2]
        forward = theorem47_matrix((f, g), 5, 17, 4, 4)
        reverse = theorem47_matrix((g, f), 5, 17, 4, 4)
        self.assertEqual(forward.rank, reverse.rank)
        self.assertEqual(forward.passes, reverse.passes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
