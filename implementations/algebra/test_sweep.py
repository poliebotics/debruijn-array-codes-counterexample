"""Tests for the cyclotomic-root sweep implementation."""

from __future__ import annotations

import itertools
import unittest

from gf2 import irreducibles_with_exponent
from prac_algebra import hypothesis_filter, theorem47_matrix
from sweep import DegreeContext, TupleSpec, enumerate_admissible_tuples


def p(*exponents: int) -> int:
    return sum(1 << i for i in exponents)


class TestSweepRepresentation(unittest.TestCase):
    def test_tuple_enumeration_counts(self) -> None:
        self.assertEqual(len(tuple(enumerate_admissible_tuples(12))), 88)
        self.assertEqual(len(tuple(enumerate_admissible_tuples(16))), 108)
        self.assertEqual(len(tuple(enumerate_admissible_tuples(24))), 680)

    def test_exponent85_factor_identity_and_filter(self) -> None:
        context = DegreeContext(8)
        reps = context.factor_representatives(85)
        self.assertEqual(len(reps), 8)
        reconstructed = tuple(sorted(context.minimal_polynomial(85, a) for a in reps))
        conventional = tuple(sorted(irreducibles_with_exponent(8, 85)))
        self.assertEqual(reconstructed, conventional)
        spec = TupleSpec(8, 4, 2, 5, 17, 85, 8)
        self.assertTrue(all(context.hypothesis_rank(spec, a) == 8 for a in reps))

    def test_common_field_product_ranks_match_polynomial_fields(self) -> None:
        context = DegreeContext(8)
        reps = context.factor_representatives(85)
        spec = TupleSpec(8, 4, 2, 5, 17, 85, 8)
        for factor_ids in itertools.combinations(reps, 2):
            polynomials = tuple(context.minimal_polynomial(85, a) for a in factor_ids)
            common_rank, _, _ = context.theorem47_result(spec, factor_ids)
            separate_rank = theorem47_matrix(polynomials, 5, 17, 4, 4).rank
            self.assertEqual(common_rank, separate_rank)

    def test_example19_failure_matches_and_polynomials_reconstruct(self) -> None:
        context = DegreeContext(6)
        reps = context.factor_representatives(63)
        polys_by_rep = {a: context.minimal_polynomial(63, a) for a in reps}
        wanted = {p(6, 5, 0), p(6, 1, 0)}
        factor_ids = tuple(a for a, f in polys_by_rep.items() if f in wanted)
        self.assertEqual(len(factor_ids), 2)
        spec = TupleSpec(6, 3, 2, 7, 9, 63, 6)
        rank, null, rows = context.theorem47_result(spec, factor_ids)
        conventional = theorem47_matrix(tuple(polys_by_rep[a] for a in factor_ids), 7, 9, 3, 4)
        self.assertEqual(rank, conventional.rank)
        self.assertEqual(rank, 10)
        self.assertIsNotNone(null)
        assert null is not None
        self.assertTrue(all((row & null).bit_count() % 2 == 0 for row in rows))

    def test_degree12_conjecture1_counterexample_algebra(self) -> None:
        # Found by the deterministic pair-first sweep.  This locks the exact
        # Corollary 48 hypotheses and Theorem 47 singularity into regression.
        context = DegreeContext(12)
        spec = TupleSpec(12, 3, 4, 5, 117, 585, 24)
        factor_ids = (1, 19)
        polynomials = tuple(
            context.minimal_polynomial(spec.exponent, a) for a in factor_ids
        )
        self.assertEqual(polynomials, (0x146B, 0x131B))
        self.assertEqual(
            tuple(context.hypothesis_rank(spec, a) for a in factor_ids),
            (12, 12),
        )
        rank, null, rows = context.theorem47_result(spec, factor_ids)
        self.assertEqual(rank, 23)
        self.assertEqual(null, 0x206632)
        self.assertTrue(all((row & null).bit_count() % 2 == 0 for row in rows))
        separate = theorem47_matrix(polynomials, 5, 117, 3, 8)
        self.assertEqual((separate.rank, separate.null_vector), (23, 0x206632))


if __name__ == "__main__":
    unittest.main(verbosity=2)
