#!/usr/bin/env python3
"""Build the max-degree-12 admissible-tuple coverage manifest."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from sweep import enumerate_admissible_tuples


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parent
    run = root / "runs" / "pairs_d12"
    ledger = run / "ledger.jsonl"
    manifest = run / "admissible_manifest.csv"
    sidecar = run / "admissible_manifest.meta.json"

    ledger_rows = [json.loads(line) for line in ledger.read_text().splitlines() if line]
    reached = {int(row["tuple_index"]): row for row in ledger_rows}
    tuples = tuple(enumerate_admissible_tuples(12))
    if len(tuples) != 88 or len(reached) != 34:
        raise RuntimeError("unexpected tuple or frozen-ledger row count")
    if set(reached) != set(range(34)):
        raise RuntimeError("frozen ledger is not the expected 0..33 prefix")

    # This is the one-row-per-admissible-tuple coverage ledger requested by
    # the project brief.  Rows after the frozen first failure deliberately
    # retain blank outcome fields rather than implying that they were tested.
    fields = (
        "tuple_index", "degree", "n1", "n2", "r1", "r2", "exponent",
        "ell", "status", "filter_mode", "filter_complete", "filter_tested",
        "pool_size", "filter_failed", "subset_coverage_json",
        "subset_tests_total", "singular_subsets", "minimum_rank_defect",
        "certification_status",
    )
    with manifest.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for index, spec in enumerate(tuples):
            status = (
                "tested_before_stop"
                if index in reached
                else "not_reached_after_verified_candidate"
            )
            if index in reached:
                row = reached[index]
                expected = {
                    "degree": spec.degree, "n1": spec.n1, "n2": spec.n2,
                    "r1": spec.r1, "r2": spec.r2, "exponent": spec.exponent,
                    "factor_count": spec.factor_count,
                }
                if any(row[key] != value for key, value in expected.items()):
                    raise RuntimeError(f"tuple {index} disagrees with frozen ledger")
            source = reached.get(index)
            filter_data = source["filter"] if source is not None else None
            subset_coverage = (
                json.dumps(source["subsets"], sort_keys=True, separators=(",", ":"))
                if source is not None
                else ""
            )
            writer.writerow({
                "tuple_index": index,
                "degree": spec.degree,
                "n1": spec.n1,
                "n2": spec.n2,
                "r1": spec.r1,
                "r2": spec.r2,
                "exponent": spec.exponent,
                "ell": spec.factor_count,
                "status": status,
                "filter_mode": filter_data["mode"] if filter_data else "",
                "filter_complete": filter_data["complete"] if filter_data else "",
                "filter_tested": filter_data["tested"] if filter_data else "",
                "pool_size": filter_data["passed"] if filter_data else "",
                "filter_failed": filter_data["failed"] if filter_data else "",
                "subset_coverage_json": subset_coverage,
                "subset_tests_total": source["subset_tests"] if source else "",
                "singular_subsets": source["singular_subsets"] if source else "",
                "minimum_rank_defect": source["minimum_rank_defect"] if source else "",
                "certification_status": (
                    "verified_by_brute_force_counterexample"
                    if index == 33
                    else ("algebraically_indicated" if source else "not_tested")
                ),
            })

    metadata = {
        "claim_label": "machine-generated coverage accounting",
        "max_degree": 12,
        "admissible_tuple_count": len(tuples),
        "tested_before_stop": len(reached),
        "not_reached_after_verified_candidate": len(tuples) - len(reached),
        "manifest_file": manifest.name,
        "manifest_sha256": sha256(manifest),
        "frozen_ledger_file": ledger.name,
        "frozen_ledger_sha256": sha256(ledger),
        "generator_file": Path(__file__).name,
        "generator_sha256": sha256(Path(__file__)),
    }
    sidecar.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
