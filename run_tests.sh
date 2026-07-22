#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "$0")" && pwd)"

(
  cd "$repo"
  sha256sum -c FROZEN_SHA256SUMS
)

(
  cd "$repo/implementations/algebra"
  python3 -m unittest -v test_prac_algebra.py test_sweep.py
)

(
  cd "$repo/implementations/bruteforce"
  python3 -m unittest -v test_bruteforce.py
  sha256sum -c HASHES.sha256
)
