#!/usr/bin/env python3
"""Reproducible admissible-tuple sweep for Blackburn et al. Conjecture 1.

This is an exact algebraic (Corollary 48 / Theorem 47) search.  It represents
all degree-n roots in one canonical polynomial-basis GF(2^n), indexed by their
discrete logarithm to a primitive element.  Irreducible factors of exponent e
are the binary cyclotomic cosets on (Z/eZ)^*.  This avoids materializing every
minimal polynomial merely to filter it; a minimal polynomial is reconstructed
exactly if a singular subset is found.

The emitted ledger carefully separates exhaustive and sampled coverage.  A
Theorem 47 singularity among sampled factors is still a valid algebraic
counterexample candidate because every participating single factor has first
passed the exact Corollary 48 filter.  It is not labelled brute-force verified.
"""

from __future__ import annotations

import argparse
from array import array
import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import itertools
import json
from math import comb, gcd
from pathlib import Path
import platform
import random
import sys
import time
from typing import Iterable, Iterator, Sequence

from gf2 import (
    GF2n,
    gf2_null_vector,
    gf2_rank,
    monic_irreducibles,
    poly_degree,
    polynomial_exponent,
    polynomial_string,
    xgcd,
)


IMPLEMENTATION_LABEL = "algebraically indicated"
DEFAULT_SEED = 0xC0DEC0DE_20250721


def integer_factorization(m: int) -> dict[int, int]:
    if m < 1:
        raise ValueError("expected positive integer")
    out: dict[int, int] = {}
    p = 2
    while p * p <= m:
        while m % p == 0:
            out[p] = out.get(p, 0) + 1
            m //= p
        p = 3 if p == 2 else p + 2
    if m > 1:
        out[m] = out.get(m, 0) + 1
    return out


def divisors_from_factorization(factors: dict[int, int]) -> tuple[int, ...]:
    divisors = [1]
    for p, multiplicity in sorted(factors.items()):
        divisors = [d * p**j for d in divisors for j in range(multiplicity + 1)]
    return tuple(sorted(divisors))


def euler_phi(m: int) -> int:
    result = m
    for p in integer_factorization(m):
        result = result // p * (p - 1)
    return result


def multiplicative_order_2(modulus: int) -> int:
    if modulus < 1 or gcd(2, modulus) != 1:
        raise ValueError("modulus must be positive and odd")
    if modulus == 1:
        return 1
    phi = euler_phi(modulus)
    order = phi
    for p in integer_factorization(phi):
        while order % p == 0 and pow(2, order // p, modulus) == 1:
            order //= p
    return order


@dataclass(frozen=True, order=True)
class TupleSpec:
    degree: int
    n1: int
    n2: int
    r1: int
    r2: int
    exponent: int
    factor_count: int

    @property
    def key(self) -> str:
        return f"n{self.degree}_w{self.n1}x{self.n2}_t{self.r1}x{self.r2}_e{self.exponent}"


def enumerate_admissible_tuples(max_degree: int) -> Iterator[TupleSpec]:
    """Enumerate exactly the number-theoretic tuples in the prompt.

    Ordering is deterministic: total degree, n1, r1, then r2.  ``n2`` is
    determined by n=n1*n2.  The exponent-one degenerate case cannot have
    order n>=2 and therefore never appears.
    """
    if max_degree < 2:
        return
    for n in range(2, max_degree + 1):
        mersenne = (1 << n) - 1
        divisors = divisors_from_factorization(integer_factorization(mersenne))
        rows: list[TupleSpec] = []
        for n1 in range(2, n + 1):
            if n % n1:
                continue
            n2 = n // n1
            for r1 in range(n1 + 1, 2 * n1):
                if mersenne % r1:
                    continue
                for r2 in divisors:
                    e = r1 * r2
                    if mersenne % e or gcd(r1, r2) != 1:
                        continue
                    if multiplicative_order_2(e) != n:
                        continue
                    count = euler_phi(e) // n
                    rows.append(TupleSpec(n, n1, n2, r1, r2, e, count))
        yield from sorted(rows, key=lambda row: (row.n1, row.r1, row.r2))


def first_primitive_polynomial(degree: int) -> int:
    target = (1 << degree) - 1
    for f in monic_irreducibles(degree):
        if polynomial_exponent(f) == target:
            return f
    raise ArithmeticError(f"failed to locate primitive polynomial of degree {degree}")


class DegreeContext:
    """Canonical primitive GF(2^n), with an O(1) exponent-to-vector table."""

    def __init__(self, degree: int):
        if not 2 <= degree <= 32:
            raise ValueError("power table currently supports 2 <= degree <= 32")
        self.degree = degree
        self.group_order = (1 << degree) - 1
        self.modulus = first_primitive_polynomial(degree)
        self.field = GF2n(self.modulus)
        if polynomial_exponent(self.modulus) != self.group_order:
            raise ArithmeticError("selected modulus is not primitive")
        typecode = "I" if degree <= 32 else "Q"
        self.powers = array(typecode)
        mask = (1 << degree) - 1
        modulus_tail = self.modulus & mask
        value = 1
        for _ in range(self.group_order):
            self.powers.append(value)
            overflow = (value >> (degree - 1)) & 1
            value = (value << 1) & mask
            if overflow:
                value ^= modulus_tail
        if value != 1 or len(set(self.powers[: min(len(self.powers), 4096)])) != min(len(self.powers), 4096):
            raise ArithmeticError("primitive power-table construction failed")
        trace_mask = 0
        for bit in range(degree):
            if self.field.trace(1 << bit):
                trace_mask |= 1 << bit
        if trace_mask == 0:
            raise ArithmeticError("absolute trace unexpectedly trivial")
        self.trace_mask = trace_mask
        self._cosets: dict[int, tuple[int, ...]] = {}

    def element_at_log(self, exponent: int) -> int:
        return self.powers[exponent % self.group_order]

    def trace_at_log(self, exponent: int) -> int:
        return (self.element_at_log(exponent) & self.trace_mask).bit_count() & 1

    def factor_representatives(self, exponent: int) -> tuple[int, ...]:
        """Canonical least representatives of 2-cyclotomic unit cosets mod e."""
        cached = self._cosets.get(exponent)
        if cached is not None:
            return cached
        if self.group_order % exponent:
            raise ValueError("factor exponent must divide 2^n-1")
        if multiplicative_order_2(exponent) != self.degree:
            raise ValueError("factor exponent does not have order n")
        seen = bytearray(exponent)
        reps: list[int] = []
        for a in range(1, exponent):
            if seen[a]:
                continue
            orbit: list[int] = []
            z = a
            while not seen[z]:
                seen[z] = 1
                orbit.append(z)
                z = (2 * z) % exponent
            if gcd(a, exponent) == 1:
                if len(orbit) != self.degree:
                    raise ArithmeticError("unit coset has unexpected size")
                reps.append(a)  # increasing scan makes a the orbit minimum
        answer = tuple(reps)
        expected = euler_phi(exponent) // self.degree
        if len(answer) != expected:
            raise ArithmeticError(
                f"coset count {len(answer)} != phi(e)/n = {expected}"
            )
        self._cosets[exponent] = answer
        return answer

    def root_log(self, exponent: int, factor_id: int) -> int:
        if gcd(factor_id, exponent) != 1:
            raise ValueError("factor_id must be a unit modulo exponent")
        return (self.group_order // exponent) * factor_id % self.group_order

    def hypothesis_rank(self, spec: TupleSpec, factor_id: int) -> int:
        """Corollary 48 rank for the root indexed by factor_id."""
        g, mu, nu = xgcd(spec.r1, spec.r2)
        if g != 1:
            raise ValueError("torus side lengths must be coprime")
        root = self.root_log(spec.exponent, factor_id)
        vectors = [
            self.element_at_log(root * (nu * spec.r2 * i + mu * spec.r1 * j))
            for i in range(spec.n1)
            for j in range(spec.n2)
        ]
        return gf2_rank(vectors, spec.degree)

    def theorem47_rows(self, spec: TupleSpec, factor_ids: Sequence[int]) -> tuple[int, ...]:
        """Theorem 47 trace matrix for target window n1 by k*n2."""
        k = len(factor_ids)
        if k < 1 or len(set(factor_ids)) != k:
            raise ValueError("factor IDs must be nonempty and distinct")
        g, mu, nu = xgcd(spec.r1, spec.r2)
        if g != 1:
            raise ValueError("torus side lengths must be coprime")
        n = spec.degree
        target_n2 = k * spec.n2
        roots = [self.root_log(spec.exponent, a) for a in factor_ids]
        rows: list[int] = []
        for i in range(spec.n1):
            for j in range(target_n2):
                row = 0
                offset = nu * spec.r2 * i + mu * spec.r1 * j
                for u, root in enumerate(roots):
                    block = 0
                    for v in range(n):
                        if self.trace_at_log(root * (v + offset)):
                            block |= 1 << v
                    row |= block << (u * n)
                rows.append(row)
        if len(rows) != k * n:
            raise ArithmeticError("Theorem 47 matrix is not square")
        return tuple(rows)

    def theorem47_result(
        self, spec: TupleSpec, factor_ids: Sequence[int]
    ) -> tuple[int, int | None, tuple[int, ...]]:
        rows = self.theorem47_rows(spec, factor_ids)
        size = len(factor_ids) * spec.degree
        rank = gf2_rank(rows, size)
        null = None if rank == size else gf2_null_vector(rows, size)
        return rank, null, rows

    def minimal_polynomial(self, exponent: int, factor_id: int) -> int:
        """Reconstruct the explicit minimal polynomial for a factor ID."""
        root_log = self.root_log(exponent, factor_id)
        roots = [self.element_at_log(root_log * (1 << i)) for i in range(self.degree)]
        coefficients = [1]
        for root in roots:
            product = [0] * (len(coefficients) + 1)
            for d, coefficient in enumerate(coefficients):
                product[d] ^= self.field.mul(coefficient, root)
                product[d + 1] ^= coefficient
            coefficients = product
        encoded = 0
        for i, coefficient in enumerate(coefficients):
            if coefficient not in (0, 1):
                raise ArithmeticError("minimal-polynomial coefficient escaped GF(2)")
            encoded |= coefficient << i
        if poly_degree(encoded) != self.degree:
            raise ArithmeticError("minimal polynomial has wrong degree")
        return encoded


def derived_seed(global_seed: int, *parts: object) -> int:
    payload = "|".join([str(global_seed), *(str(part) for part in parts)]).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def hash_integer_sequence(values: Iterable[int]) -> str:
    digest = hashlib.sha256()
    for value in values:
        encoded = str(value).encode()
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def iter_sampled_combinations(
    population_size: int, k: int, budget: int, seed: int
) -> tuple[str, int, Iterator[tuple[int, ...]]]:
    universe = comb(population_size, k)
    if universe <= budget:
        return "exhaustive", universe, itertools.combinations(range(population_size), k)
    rng = random.Random(seed)
    selected: set[tuple[int, ...]] = set()
    while len(selected) < budget:
        selected.add(tuple(sorted(rng.sample(range(population_size), k))))
    return "sampled", universe, iter(sorted(selected))


def safe_output_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if root.resolve() not in path.parents and path != root.resolve():
        raise ValueError("output path must remain under agent_algebra")
    return path


def source_hashes(root: Path) -> dict[str, str]:
    names = ("gf2.py", "prac_algebra.py", "sweep.py", "test_sweep.py")
    return {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in names
        if (root / name).exists()
    }


def write_json_atomic(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_sweep(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parent
    output_dir = safe_output_path(root, args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = output_dir / "ledger.jsonl"
    csv_path = output_dir / "ledger.csv"
    meta_path = output_dir / "run_meta.json"
    counterexample_path = output_dir / "counterexample_candidate.json"
    tuples = list(enumerate_admissible_tuples(args.max_degree))
    started = datetime.now(timezone.utc).isoformat()
    meta = {
        "claim_label": IMPLEMENTATION_LABEL,
        "started_utc": started,
        "status": "running",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "parameters": vars(args),
        "source_sha256": source_hashes(root),
        "admissible_tuple_count": len(tuples),
        "sampling": "Python random.Random(MT19937), tuple/k seeds derived by SHA-256",
    }
    write_json_atomic(meta_path, meta)

    csv_fields = [
        "degree", "n1", "n2", "r1", "r2", "exponent", "factor_count",
        "filter_complete", "filter_tested", "filter_passed", "filter_failed",
        "subset_tests", "singular_subsets", "minimum_rank_defect",
    ]
    rows_written = 0
    total_subset_tests = 0
    total_singular = 0
    current_degree = None
    context: DegreeContext | None = None
    coset_cache: dict[int, tuple[int, ...]] = {}
    with ledger_path.open("w", encoding="utf-8") as ledger_file, csv_path.open(
        "w", encoding="utf-8", newline=""
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
        writer.writeheader()
        for tuple_index, spec in enumerate(tuples):
            tuple_started = time.monotonic()
            if spec.degree != current_degree:
                context = DegreeContext(spec.degree)
                current_degree = spec.degree
                coset_cache = {}
            assert context is not None
            reps = coset_cache.get(spec.exponent)
            if reps is None:
                reps = context.factor_representatives(spec.exponent)
                coset_cache[spec.exponent] = reps
            if len(reps) != spec.factor_count:
                raise ArithmeticError("enumerated factor count mismatch")

            filter_seed = derived_seed(args.seed, spec.key, "filter")
            if len(reps) <= args.complete_filter_limit:
                tested_reps = reps
                filter_mode = "exhaustive"
                filter_complete = True
            else:
                rng = random.Random(filter_seed)
                indices = sorted(rng.sample(range(len(reps)), args.sample_factors))
                tested_reps = tuple(reps[i] for i in indices)
                filter_mode = "sampled"
                filter_complete = False
            passing = tuple(
                factor_id
                for factor_id in tested_reps
                if context.hypothesis_rank(spec, factor_id) == spec.degree
            )

            subset_records: list[dict[str, object]] = []
            singular_count = 0
            minimum_rank_defect = 0
            if len(passing) >= 2:
                maximum_k = min(args.max_k, len(passing))
                for k in range(2, maximum_k + 1):
                    budget = (
                        args.pair_budget if k == 2 else
                        args.triple_budget if k == 3 else
                        args.larger_budget
                    )
                    subset_seed = derived_seed(args.seed, spec.key, "subsets", k)
                    subset_mode, universe, selections = iter_sampled_combinations(
                        len(passing), k, budget, subset_seed
                    )
                    rank_histogram: dict[int, int] = {}
                    tested = 0
                    selection_digest = hashlib.sha256()
                    for indices in selections:
                        factor_ids = tuple(passing[index] for index in indices)
                        selection_digest.update(
                            (",".join(map(str, factor_ids)) + "\n").encode()
                        )
                        rank, null, matrix_rows = context.theorem47_result(spec, factor_ids)
                        tested += 1
                        rank_histogram[rank] = rank_histogram.get(rank, 0) + 1
                        size = k * spec.degree
                        minimum_rank_defect = max(minimum_rank_defect, size - rank)
                        if rank != size:
                            singular_count += 1
                            total_singular += 1
                            polynomials = [
                                context.minimal_polynomial(spec.exponent, factor_id)
                                for factor_id in factor_ids
                            ]
                            candidate = {
                                "claim_label": IMPLEMENTATION_LABEL,
                                "warning": "Requires independent brute-force verification",
                                "tuple": asdict(spec),
                                "factor_ids": factor_ids,
                                "polynomials_bitmask": [hex(f) for f in polynomials],
                                "polynomials_expression": [polynomial_string(f) for f in polynomials],
                                "single_filter_ranks": [
                                    context.hypothesis_rank(spec, a) for a in factor_ids
                                ],
                                "product_k": k,
                                "target_window": [spec.n1, k * spec.n2],
                                "matrix_rank": rank,
                                "matrix_size": size,
                                "right_null_vector": hex(null or 0),
                                "matrix_rows_hex": [hex(row) for row in matrix_rows],
                                "matrix_sha256": hash_integer_sequence(matrix_rows),
                                "global_seed": args.seed,
                                "subset_seed": subset_seed,
                                "source_sha256": source_hashes(root),
                            }
                            write_json_atomic(counterexample_path, candidate)
                            subset_records.append({
                                "k": k, "mode": subset_mode,
                                "universe_in_tested_pool": universe,
                                "tested_before_stop": tested,
                                "seed": subset_seed,
                                "rank_histogram": {str(r): c for r, c in sorted(rank_histogram.items())},
                                "selection_sha256": selection_digest.hexdigest(),
                                "singular": singular_count,
                            })
                            row = _ledger_row(
                                spec, tuple_index, context, filter_mode, filter_complete,
                                filter_seed, tested_reps, passing, subset_records,
                                singular_count, minimum_rank_defect, tuple_started,
                            )
                            ledger_file.write(json.dumps(row, sort_keys=True) + "\n")
                            ledger_file.flush()
                            rows_written += 1
                            total_subset_tests += tested
                            writer.writerow(_csv_row(row))
                            csv_file.flush()
                            meta.update({
                                "status": "stopped_on_singular_subset",
                                "finished_utc": datetime.now(timezone.utc).isoformat(),
                                "rows_written": rows_written,
                                "subset_tests": total_subset_tests,
                                "singular_subsets": total_singular,
                                "ledger_sha256": file_sha256(ledger_path),
                                "csv_sha256": file_sha256(csv_path),
                                "counterexample_sha256": file_sha256(counterexample_path),
                            })
                            write_json_atomic(meta_path, meta)
                            print(json.dumps(candidate, indent=2, sort_keys=True), flush=True)
                            return 2
                    subset_records.append({
                        "k": k,
                        "mode": subset_mode,
                        "universe_in_tested_pool": universe,
                        "tested": tested,
                        "seed": subset_seed,
                        "rank_histogram": {
                            str(rank): count for rank, count in sorted(rank_histogram.items())
                        },
                        "selection_sha256": selection_digest.hexdigest(),
                        "singular": 0,
                    })
                    total_subset_tests += tested

            row = _ledger_row(
                spec, tuple_index, context, filter_mode, filter_complete,
                filter_seed, tested_reps, passing, subset_records,
                singular_count, minimum_rank_defect, tuple_started,
            )
            ledger_file.write(json.dumps(row, sort_keys=True) + "\n")
            writer.writerow(_csv_row(row))
            ledger_file.flush()
            csv_file.flush()
            rows_written += 1
            if args.progress_every and rows_written % args.progress_every == 0:
                print(
                    f"rows={rows_written}/{len(tuples)} degree={spec.degree} "
                    f"pool={len(passing)}/{len(tested_reps)} subset_tests={total_subset_tests}",
                    file=sys.stderr,
                    flush=True,
                )

    meta.update({
        "status": "completed_no_singular_subset",
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "rows_written": rows_written,
        "subset_tests": total_subset_tests,
        "singular_subsets": total_singular,
        "ledger_sha256": file_sha256(ledger_path),
        "csv_sha256": file_sha256(csv_path),
    })
    write_json_atomic(meta_path, meta)
    print(json.dumps(meta, indent=2, sort_keys=True), flush=True)
    return 0


def _ledger_row(
    spec: TupleSpec,
    tuple_index: int,
    context: DegreeContext,
    filter_mode: str,
    filter_complete: bool,
    filter_seed: int,
    tested_reps: Sequence[int],
    passing: Sequence[int],
    subset_records: Sequence[dict[str, object]],
    singular_count: int,
    minimum_rank_defect: int,
    tuple_started: float,
) -> dict[str, object]:
    return {
        "claim_label": IMPLEMENTATION_LABEL,
        "tuple_index": tuple_index,
        **asdict(spec),
        "primitive_modulus_bitmask": hex(context.modulus),
        "primitive_modulus_expression": polynomial_string(context.modulus),
        "filter": {
            "mode": filter_mode,
            "complete": filter_complete,
            "seed": filter_seed,
            "tested": len(tested_reps),
            "passed": len(passing),
            "failed": len(tested_reps) - len(passing),
            "factor_ids_tested_sha256": hash_integer_sequence(tested_reps),
            "factor_ids_passed_sha256": hash_integer_sequence(passing),
        },
        "subsets": list(subset_records),
        "subset_tests": sum(
            int(record.get("tested", record.get("tested_before_stop", 0)))
            for record in subset_records
        ),
        "singular_subsets": singular_count,
        "minimum_rank_defect": minimum_rank_defect,
        "elapsed_seconds": round(time.monotonic() - tuple_started, 6),
    }


def _csv_row(row: dict[str, object]) -> dict[str, object]:
    filt = row["filter"]
    assert isinstance(filt, dict)
    return {
        "degree": row["degree"], "n1": row["n1"], "n2": row["n2"],
        "r1": row["r1"], "r2": row["r2"], "exponent": row["exponent"],
        "factor_count": row["factor_count"],
        "filter_complete": filt["complete"], "filter_tested": filt["tested"],
        "filter_passed": filt["passed"], "filter_failed": filt["failed"],
        "subset_tests": row["subset_tests"],
        "singular_subsets": row["singular_subsets"],
        "minimum_rank_defect": row["minimum_rank_defect"],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-degree", type=int, default=24)
    parser.add_argument("--complete-filter-limit", type=int, default=10_000)
    parser.add_argument("--sample-factors", type=int, default=4_096)
    parser.add_argument("--pair-budget", type=int, default=20_000)
    parser.add_argument("--triple-budget", type=int, default=10_000)
    parser.add_argument("--larger-budget", type=int, default=2_000)
    parser.add_argument("--max-k", type=int, default=6)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", default="runs/sweep_d24")
    parser.add_argument("--progress-every", type=int, default=10)
    args = parser.parse_args(argv)
    for name in (
        "max_degree", "complete_filter_limit", "sample_factors", "pair_budget",
        "triple_budget", "larger_budget", "max_k",
    ):
        if getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    if args.sample_factors > args.complete_filter_limit:
        parser.error("--sample-factors cannot exceed --complete-filter-limit")
    return args


if __name__ == "__main__":
    raise SystemExit(run_sweep(parse_args()))
