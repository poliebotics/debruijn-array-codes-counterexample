"""Emit a deterministic JSON calibration record for the algebraic tests."""

from __future__ import annotations

import hashlib
import itertools
import json
import platform
from pathlib import Path

from gf2 import irreducibles_with_exponent, polynomial_exponent, polynomial_string
from prac_algebra import hypothesis_filter, theorem47_matrix


def p(*exponents: int) -> int:
    return sum(1 << i for i in exponents)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parent
    source_files = ("gf2.py", "prac_algebra.py", "test_prac_algebra.py", "calibrate.py")
    exp85 = irreducibles_with_exponent(8, 85)
    pair_records = []
    for f, g in itertools.combinations(exp85, 2):
        result = theorem47_matrix((f, g), 5, 17, 4, 4)
        pair_records.append({"f": hex(f), "g": hex(g), "rank": result.rank,
                             "size": result.size, "passes": result.passes})
    all_subset_summary = []
    for k in range(1, len(exp85) + 1):
        ranks: dict[int, int] = {}
        passed = 0
        total = 0
        for subset in itertools.combinations(exp85, k):
            result = theorem47_matrix(subset, 5, 17, 4, 2 * k)
            total += 1
            passed += int(result.passes)
            ranks[result.rank] = ranks.get(result.rank, 0) + 1
        all_subset_summary.append({
            "k": k, "tested": total, "passed": passed,
            "rank_histogram": {str(rank): count for rank, count in sorted(ranks.items())},
        })

    e21_f1 = p(6, 5, 4, 2, 0)
    e21_f2 = p(6, 4, 2, 1, 0)
    prim_f1 = p(6, 5, 0)
    prim_f2 = p(6, 1, 0)
    e21_good = theorem47_matrix((e21_f1, e21_f2), 3, 7, 2, 6)
    e21_bad = theorem47_matrix((e21_f1, e21_f2), 7, 3, 3, 4)
    primitive_bad = theorem47_matrix((prim_f1, prim_f2), 7, 9, 3, 4)

    record = {
        "claim_label": "algebraically indicated",
        "implementation": "self-contained integer-bitset GF(2^n)",
        "python": platform.python_version(),
        "randomness": None,
        "source_sha256": {name: file_sha256(root / name) for name in source_files},
        "degree8_exponent85": {
            "count": len(exp85),
            "polynomials": [
                {
                    "bitmask": hex(f),
                    "expression": polynomial_string(f),
                    "single_rank": hypothesis_filter(f, 5, 17, 4, 2).rank,
                }
                for f in exp85
            ],
            "pairs": pair_records,
            "all_subsets_algebraic_support": all_subset_summary,
        },
        "example19_exponent21": {
            "polynomials": [hex(e21_f1), hex(e21_f2)],
            "exponents": [polynomial_exponent(e21_f1), polynomial_exponent(e21_f2)],
            "single_3x7_ranks": [
                hypothesis_filter(f, 3, 7, 2, 3).rank for f in (e21_f1, e21_f2)
            ],
            "product_3x7_2x6": {
                "rank": e21_good.rank, "size": e21_good.size,
                "passes": e21_good.passes,
            },
            "single_7x3_ranks": [
                hypothesis_filter(f, 7, 3, 3, 2).rank for f in (e21_f1, e21_f2)
            ],
            "product_7x3_3x4": {
                "rank": e21_bad.rank, "size": e21_bad.size,
                "passes": e21_bad.passes,
                "right_null_vector": hex(e21_bad.null_vector or 0),
            },
        },
        "example19_primitive63": {
            "polynomials": [hex(prim_f1), hex(prim_f2)],
            "exponents": [polynomial_exponent(prim_f1), polynomial_exponent(prim_f2)],
            "single_ranks": [
                hypothesis_filter(f, 7, 9, 3, 2).rank for f in (prim_f1, prim_f2)
            ],
            "product_7x9_3x4": {
                "rank": primitive_bad.rank, "size": primitive_bad.size,
                "passes": primitive_bad.passes,
                "right_null_vector": hex(primitive_bad.null_vector or 0),
            },
        },
    }
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
