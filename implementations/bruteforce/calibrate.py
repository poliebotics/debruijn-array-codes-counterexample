#!/usr/bin/env python3
"""Run all paper calibration instances and emit a reproducible transcript."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from bruteforce import (
    check_prac,
    multiply_factors,
    polynomial_exponents,
    polynomial_from_exponents,
    polynomial_string,
)
from poly_enumeration import irreducibles_of_degree_and_exponent, order_of_x


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def factor_record(polynomial: int) -> dict:
    return {
        "mask_hex": hex(polynomial),
        "exponents": polynomial_exponents(polynomial),
        "polynomial": polynomial_string(polynomial),
        "degree": polynomial.bit_length() - 1,
        "exponent": order_of_x(polynomial),
    }


def make_cases() -> tuple[list[dict], list[int]]:
    exponent_21 = [
        polynomial_from_exponents([6, 5, 4, 2, 0]),
        polynomial_from_exponents([6, 4, 2, 1, 0]),
    ]
    primitive_63 = [
        polynomial_from_exponents([6, 5, 0]),
        polynomial_from_exponents([6, 1, 0]),
    ]
    exponent_85 = irreducibles_of_degree_and_exponent(8, 85)
    if len(exponent_85) != 8:
        raise AssertionError(f"expected 8 exponent-85 factors, got {len(exponent_85)}")

    cases: list[dict] = []

    def add(
        name: str,
        factors: list[int],
        parameters: tuple[int, int, int, int],
        expected: bool,
        paper_claim: str,
    ) -> None:
        cases.append(
            {
                "name": name,
                "factors": factors,
                "parameters": parameters,
                "expected": expected,
                "paper_claim": paper_claim,
            }
        )

    for index, factor in enumerate(exponent_21, start=1):
        add(
            f"example19-e21-single-{index}-3x7",
            [factor],
            (3, 7, 2, 3),
            True,
            "Example 19 single-factor (3,7;2,3)-PRAC",
        )
    add(
        "example19-e21-product-3x7",
        exponent_21,
        (3, 7, 2, 6),
        True,
        "Example 19 product (3,7;2,6)-PRAC",
    )
    for index, factor in enumerate(exponent_21, start=1):
        add(
            f"example19-e21-single-{index}-7x3",
            [factor],
            (7, 3, 3, 2),
            True,
            "Example 19 single-factor (7,3;3,2)-PRAC",
        )
    add(
        "example19-e21-product-7x3",
        exponent_21,
        (7, 3, 3, 4),
        False,
        "Example 19 side-condition-violating product configuration",
    )

    for index, factor in enumerate(primitive_63, start=1):
        add(
            f"example19-e63-single-{index}",
            [factor],
            (7, 9, 3, 2),
            True,
            "Example 19 primitive single-factor (7,9;3,2)-PRAC",
        )
    add(
        "example19-e63-product-failure",
        primitive_63,
        (7, 9, 3, 4),
        False,
        "Example 19 stated failure of primitive-polynomial product",
    )

    for index, factor in enumerate(exponent_85):
        add(
            f"degree8-e85-single-{index + 1}",
            [factor],
            (5, 17, 4, 2),
            True,
            "Conjecture 1 motivating degree-8 single-factor instance",
        )
    for left_index, left in enumerate(exponent_85):
        for right_index in range(left_index + 1, len(exponent_85)):
            add(
                f"degree8-e85-pair-{left_index + 1}-{right_index + 1}",
                [left, exponent_85[right_index]],
                (5, 17, 4, 4),
                True,
                "Conjecture 1 motivating degree-8 pair instance",
            )
    return cases, exponent_85


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=HERE / "calibration.json")
    parser.add_argument(
        "--transcript", type=Path, default=HERE / "calibration_transcript.txt"
    )
    args = parser.parse_args()

    cases, exponent_85 = make_cases()
    records: list[dict] = []
    transcript: list[str] = []
    overall = True
    for case in cases:
        r1, r2, rows, columns = case["parameters"]
        result = check_prac(
            multiply_factors(case["factors"]), r1, r2, rows, columns
        )
        agrees = result.passed == case["expected"]
        overall &= agrees
        records.append(
            {
                "name": case["name"],
                "paper_claim": case["paper_claim"],
                "factor_masks_hex": [hex(factor) for factor in case["factors"]],
                "expected_pass": case["expected"],
                "agrees_with_expected": agrees,
                "result": asdict(result),
            }
        )
        transcript.append(
            f"{'OK' if agrees else 'MISMATCH'} {case['name']}: "
            f"expected={'PASS' if case['expected'] else 'FAIL'} "
            f"observed={'PASS' if result.passed else 'FAIL'}; "
            f"windows={result.total_windows}; codewords={result.codeword_count}; "
            f"zero={result.zero_windows}; duplicates={result.duplicate_nonzero_windows}; "
            f"missing={result.missing_nonzero_windows}; seconds={result.elapsed_seconds:.6f}"
        )

    source_files = [
        HERE / "bruteforce.py",
        HERE / "poly_enumeration.py",
        HERE / "calibrate.py",
        HERE / "test_bruteforce.py",
    ]
    paper_files = [HERE / "part2.pdf", HERE / "part1.pdf"]
    payload = {
        "calibration_passed": overall,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "randomness": "none",
        "python": sys.version,
        "platform": platform.platform(),
        "sources": {path.name: sha256(path) for path in source_files},
        "papers": {
            path.name: sha256(path) for path in paper_files if path.exists()
        },
        "paper_versions": {
            "part2": "arXiv:2501.12124v4, 19 August 2025",
            "part1": "arXiv:2407.18122 (downloaded 21 July 2026)",
        },
        "degree8_exponent85_factors": [
            factor_record(factor) for factor in exponent_85
        ],
        "cases": records,
    }
    args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    transcript.extend(
        [
            "",
            f"OVERALL: {'PASS' if overall else 'FAIL'}",
            f"cases={len(records)}",
            f"json_sha256_pending=hash the completed {args.json.name} externally",
        ]
    )
    args.transcript.write_text("\n".join(transcript) + "\n")
    print("\n".join(transcript))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
