#!/usr/bin/env python3
"""Independent third-engine check of the Conjecture 1 counterexample.

This implementation uses the external ``galois`` computer-algebra package,
not either project arithmetic module.  It constructs each quotient field
separately and applies Corollary 48 and the literal trace matrix of Theorem 47.
Its output is algebraic corroboration; the recurrence/CRT checker is the
project's brute-force ground truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import galois
import numpy as np


FACTORS = (0x146B, 0x131B)
R1, R2 = 5, 117
BASE_ROWS, BASE_COLS = 3, 4


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t


def field_for(mask: int):
    base = galois.GF(2)
    polynomial = galois.Poly.Int(mask, field=base)
    degree = polynomial.degree
    field = galois.GF(2**degree, irreducible_poly=polynomial)
    alpha = field(2)  # polynomial-basis residue class x
    return polynomial, field, alpha


def parameters(alpha):
    gcd, mu, nu = extended_gcd(R1, R2)
    assert gcd == 1 and mu * R1 + nu * R2 == 1
    exponent = R1 * R2
    beta = alpha ** ((nu * R2) % exponent)
    gamma = alpha ** ((mu * R1) % exponent)
    return mu, nu, beta, gamma


def rank(matrix: list[list[int]]) -> int:
    return int(np.linalg.matrix_rank(galois.GF2(matrix)))


def single_rank(mask: int) -> dict:
    polynomial, field, alpha = field_for(mask)
    mu, nu, beta, gamma = parameters(alpha)
    rows = [
        [int(bit) for bit in (beta**i * gamma**j).vector()]
        for i in range(BASE_ROWS)
        for j in range(BASE_COLS)
    ]
    return {
        "mask_hex": hex(mask),
        "polynomial": str(polynomial),
        "irreducible": bool(polynomial.is_irreducible()),
        "alpha_order": int(alpha.multiplicative_order()),
        "corollary48_rank": rank(rows),
        "corollary48_size": polynomial.degree,
        "passes": rank(rows) == polynomial.degree,
        "field_irreducible_polynomial": str(field.irreducible_poly),
        "mu": mu,
        "nu": nu,
    }


def product_trace_rank(masks: tuple[int, ...]) -> dict:
    data = [field_for(mask) for mask in masks]
    degree = data[0][0].degree
    target_columns = len(masks) * BASE_COLS
    rows: list[list[int]] = []
    for i in range(BASE_ROWS):
        for j in range(target_columns):
            row: list[int] = []
            for _, _, alpha in data:
                _, _, beta, gamma = parameters(alpha)
                multiplier = beta**i * gamma**j
                row.extend(
                    int((alpha**v * multiplier).field_trace())
                    for v in range(degree)
                )
            rows.append(row)
    matrix_rank = rank(rows)
    return {
        "theorem47_rank": matrix_rank,
        "theorem47_size": len(masks) * degree,
        "passes": matrix_rank == len(masks) * degree,
        "matrix_rows_binary": ["".join(map(str, row)) for row in rows],
    }


def sparse_relation_check() -> dict:
    # Q(Z) = P(Z^351,Z^235) modulo Z^585-1 for the compact rectangle
    # relation recorded in proof_notes.md.
    exponents = (0, 5, 6, 117, 121, 122, 235, 236, 356, 470, 471, 472, 475)
    q_mask = sum(1 << exponent for exponent in exponents)
    base = galois.GF(2)
    q = galois.Poly.Int(q_mask, field=base)
    remainders = {}
    for mask in FACTORS:
        f = galois.Poly.Int(mask, field=base)
        remainders[hex(mask)] = str(q % f)
    return {
        "q_exponents": list(exponents),
        "q_degree": q.degree,
        "remainders": remainders,
        "both_zero": all(value == "0" for value in remainders.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = Path(__file__).read_bytes()
    payload = {
        "claim_label": "algebraically indicated (independent third engine)",
        "parameters": {
            "r1": R1,
            "r2": R2,
            "n1": BASE_ROWS,
            "n2": BASE_COLS,
            "product_target": [BASE_ROWS, 2 * BASE_COLS],
            "side_condition": BASE_ROWS < R1 < 2 * BASE_ROWS,
            "divisibility": (2 ** (BASE_ROWS * BASE_COLS) - 1) % (R1 * R2) == 0,
        },
        "single_factors": [single_rank(mask) for mask in FACTORS],
        "product": product_trace_rank(FACTORS),
        "sparse_relation": sparse_relation_check(),
        "provenance": {
            "python": sys.version,
            "platform": platform.platform(),
            "galois": galois.__version__,
            "numpy": np.__version__,
            "script_sha256": hashlib.sha256(source).hexdigest(),
            "randomness": "none",
        },
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        sys.stdout.write(rendered)
    return 0 if (
        all(item["passes"] for item in payload["single_factors"])
        and not payload["product"]["passes"]
        and payload["sparse_relation"]["both_zero"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
