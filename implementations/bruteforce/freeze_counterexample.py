#!/usr/bin/env python3
"""Freeze the independently brute-verified Conjecture 1 counterexample."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from bruteforce import (
    check_prac,
    decode_window,
    encode_window,
    feedback_state_mask,
    fold_sequence,
    multiply_factors,
    polynomial_exponents,
    polynomial_string,
    state_orbit,
)


HERE = Path(__file__).resolve().parent
FULL_SCAN = HERE / "counterexample_candidate_bruteforce.json"
FROZEN = HERE / "counterexample_frozen.json"
TRANSCRIPT = HERE / "counterexample_bruteforce_transcript.txt"

F1 = 0x146B
F2 = 0x131B
PRODUCT = 0x17BD455
R1, R2, N1, N2 = 5, 117, 3, 4
TARGET_ROWS, TARGET_COLUMNS = 3, 8


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def factor(polynomial: int) -> dict:
    return {
        "mask_hex": hex(polynomial),
        "exponents": polynomial_exponents(polynomial),
        "polynomial": polynomial_string(polynomial),
    }


def orbit_artifact(representative: int, top: int, left: int) -> dict:
    orbit = state_orbit(
        representative,
        24,
        feedback_state_mask(PRODUCT),
        expected_period=R1 * R2,
    )
    sequence = "".join(str(state & 1) for state in orbit)
    array = fold_sequence([int(bit) for bit in sequence], R1, R2)
    array_rows = ["".join(map(str, row)) for row in array]
    word = encode_window(array, top, left, TARGET_ROWS, TARGET_COLUMNS)
    return {
        "representative_state": representative,
        "period": len(orbit),
        "sequence_bits": sequence,
        "sequence_sha256": sha256_bytes(sequence.encode()),
        "array_rows": array_rows,
        "array_rows_sha256": sha256_bytes("\n".join(array_rows).encode()),
        "window_position": {"top": top, "left": left},
        "window_word": word,
        "window_rows": decode_window(word, TARGET_ROWS, TARGET_COLUMNS),
    }


def main() -> int:
    if multiply_factors([F1, F2]) != PRODUCT:
        raise AssertionError("frozen product polynomial mismatch")
    full_scan_bytes = FULL_SCAN.read_bytes()
    full_scan = json.loads(full_scan_bytes)
    result = full_scan["result"]
    if result["passed"]:
        raise AssertionError("full scan unexpectedly passed")
    if result["total_windows"] != (1 << 24) - 1:
        raise AssertionError("full scan was not exhaustive")

    singles = [asdict(check_prac(polynomial, R1, R2, N1, N2)) for polynomial in (F1, F2)]
    if not all(single["passed"] for single in singles):
        raise AssertionError("a conjecture hypothesis failed brute force")

    collision_first = orbit_artifact(1, 1, 40)
    collision_second = orbit_artifact(8, 4, 28)
    zero = orbit_artifact(10_781, 4, 14)
    expected_collision = 13_093_007
    if collision_first["window_word"] != expected_collision:
        raise AssertionError("first collision occurrence changed")
    if collision_second["window_word"] != expected_collision:
        raise AssertionError("second collision occurrence changed")
    if zero["window_word"] != 0:
        raise AssertionError("zero-window occurrence changed")

    first_states = set(
        state_orbit(1, 24, feedback_state_mask(PRODUCT), expected_period=585)
    )
    second_states = set(
        state_orbit(8, 24, feedback_state_mask(PRODUCT), expected_period=585)
    )
    if not first_states.isdisjoint(second_states):
        raise AssertionError("collision witnesses are not distinct cyclic sequences")

    payload = {
        "status": "verified by brute force",
        "scope": "counterexample to Blackburn--Chee--Etzion--Lao Conjecture 1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "r1": R1,
            "r2": R2,
            "n1": N1,
            "single_n2": N2,
            "k": 2,
            "product_window_rows": TARGET_ROWS,
            "product_window_columns": TARGET_COLUMNS,
            "side_condition": "3 < 5 < 6",
            "gcd_r1_r2": 1,
        },
        "factors": [factor(F1), factor(F2)],
        "product": factor(PRODUCT),
        "hypothesis_checks": singles,
        "full_product_scan": result,
        "collision_witness": {
            "word": expected_collision,
            "word_hex": hex(expected_collision),
            "rows": decode_window(expected_collision, TARGET_ROWS, TARGET_COLUMNS),
            "distinct_shift_orbits": True,
            "occurrences": [collision_first, collision_second],
        },
        "zero_window_witness": zero,
        "first_missing_nonzero_window": {
            "word": result["first_missing_word"],
            "word_hex": hex(result["first_missing_word"]),
            "rows": result["first_missing_rows"],
            "basis": "exhaustive full-product coverage bitset",
        },
        "commands": {
            "full_scan": "python3 bruteforce.py --factor 0x146b --factor 0x131b --r1 5 --r2 117 --window-rows 3 --window-cols 8 --output counterexample_candidate_bruteforce.json",
            "targeted_recheck": "python3 -m unittest -v test_bruteforce.CounterexampleWitnessTests",
            "calibration": "python3 calibrate.py",
        },
        "provenance": {
            "python": sys.version,
            "platform": platform.platform(),
            "randomness": "none",
            "checker_sha256": sha256_file(HERE / "bruteforce.py"),
            "test_sha256": sha256_file(HERE / "test_bruteforce.py"),
            "full_scan_json_sha256": sha256_bytes(full_scan_bytes),
            "calibration_json_sha256": sha256_file(HERE / "calibration.json"),
            **{
                f"{p.stem}_pdf_sha256": sha256_file(p)
                for p in (HERE / "part2.pdf", HERE / "part1.pdf")
                if p.exists()
            },
        },
    }
    FROZEN.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    transcript = [
        "STATUS: VERIFIED BY BRUTE FORCE",
        "",
        "HYPOTHESES",
        f"0x146b single: PASS; windows={singles[0]['total_windows']}; unique={singles[0]['unique_nonzero_windows']}; zero={singles[0]['zero_windows']}; duplicates={singles[0]['duplicate_nonzero_windows']}; missing={singles[0]['missing_nonzero_windows']}",
        f"0x131b single: PASS; windows={singles[1]['total_windows']}; unique={singles[1]['unique_nonzero_windows']}; zero={singles[1]['zero_windows']}; duplicates={singles[1]['duplicate_nonzero_windows']}; missing={singles[1]['missing_nonzero_windows']}",
        "",
        "PRODUCT",
        f"0x17bd455 product: FAIL; windows={result['total_windows']}; orbits={result['codeword_count']}; unique={result['unique_nonzero_windows']}; zero={result['zero_windows']}; duplicates={result['duplicate_nonzero_windows']}; missing={result['missing_nonzero_windows']}; seconds={result['elapsed_seconds']}",
        f"collision rows={result['first_collision_rows']}",
        f"collision occurrences={result['first_collision_occurrences']}",
        f"zero occurrence={result['first_zero_occurrence']}",
        f"first missing rows={result['first_missing_rows']} word={result['first_missing_word']}",
        "",
        "COMMANDS",
        payload["commands"]["full_scan"],
        payload["commands"]["targeted_recheck"],
        payload["commands"]["calibration"],
        "",
        "HASHES",
        f"checker_sha256={payload['provenance']['checker_sha256']}",
        f"full_scan_json_sha256={payload['provenance']['full_scan_json_sha256']}",
        f"calibration_json_sha256={payload['provenance']['calibration_json_sha256']}",
        f"frozen_json_sha256_pending=hash {FROZEN.name} externally",
        "",
        f"PYTHON={sys.version}",
        f"PLATFORM={platform.platform()}",
        "RANDOMNESS=none",
    ]
    TRANSCRIPT.write_text("\n".join(transcript) + "\n")
    print("\n".join(transcript))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
