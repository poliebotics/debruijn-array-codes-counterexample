# Literal-recurrence PRAC checker

This directory is the ground-truth path for Conjecture 1. It is deliberately
separate from the Corollary 15 and Theorem 6 implementations
(arXiv Corollary 48 and Theorem 47). All
implementations in this repository are separately written, reuse no source
code from one another, and were written with knowledge of the claimed
witness.

## Epistemic status

- **[verified by brute force]** Conjecture 1 is false. The in-scope tuple
  `(r1,r2;n1,n2)=(5,117;3,4)` and factors `0x146b`, `0x131b` satisfy both
  single-factor hypotheses, but their product fails for the `3x8` window.
- **[proved]** `bruteforce.py` contains no finite-field construction, trace,
  determinant, rank, resultant, or invocation of either algebraic criterion.
  It uses only Equation (1)'s binary recurrence, the paper's southeast-diagonal
  CRT placement, and literal toroidal window extraction.
- **[verified by brute force]** The full 45-case calibration suite agrees with
  the published examples and the requested side-condition failure checks.
- **[verified by brute force]** Every one of the eight degree-8, exponent-85
  factors passes at `(5,17;4,2)`, and all `C(8,2)=28` distinct pair products
  pass at `(5,17;4,4)`.
- **[verified by brute force]** Both degree-6, exponent-21 factors pass at
  `(3,7;2,3)`, their product passes at `(3,7;2,6)`, and the corresponding
  swapped-orientation product fails at `(7,3;3,4)`.
- **[verified by brute force]** The two stated primitive degree-6 factors pass
  singly at `(7,9;3,2)`, while their product fails at `(7,9;3,4)`.

The only verdict below labelled “algebraically indicated” is the fixture
utility's polynomial classification, which is delegated to the algebra
implementation; every window verdict in this directory is verified by
brute force.

## Counterexample

- **[proved]** The integer side conditions hold:
  `gcd(5,117)=1`, `3<5<2*3`, and `5*117=585` divides `2^12-1=4095`.
- **[algebraically indicated]** The fixture utility's exact Rabin
  and order calculations classify both `0x146b` and `0x131b` as irreducible
  degree-12 polynomials of exponent 585. The separate algebra implementation
  is responsible for the project's primary algebraic certification.
- **[verified by brute force]** Each factor separately produces exactly seven
  orbit arrays and all 4,095 nonzero `3x4` matrices exactly once, with no zero,
  duplicate, or missing window.
- **[verified by brute force]** The product `0x17bd455` was checked over all
  28,679 recurrence orbits and all 16,777,215 window positions. It produces
  8,388,607 unique nonzero matrices, one zero occurrence, 8,388,607 duplicate
  nonzero occurrences, and 8,388,608 missing nonzero matrices.
- **[verified by brute force]** A concrete collision is the matrix
  `['11110001','00010011','11100011']`, occurring in two distinct recurrence
  orbits: representative state 1 at `(top=1,left=40)`, and representative state
  8 at `(top=4,left=28)`.
- **[verified by brute force]** A targeted test regenerates those two 585-bit
  sequences directly from the recurrence, proves their state orbits disjoint
  by exhaustive set comparison, folds them separately, and recovers the
  same collision without consulting the coverage bitset.
- **[verified by brute force]** `standalone_witness_recheck.py` repeats that
  finite witness using its own tuple-state recurrence, polynomial multiplier,
  list-based CRT fold, and nested-loop window reader. It imports no project
  code; its output is frozen in `standalone_witness_transcript.json`.

The frozen full evidence is `counterexample_frozen.json`; the original full
scan is `counterexample_candidate_bruteforce.json`; exact commands and summary
are in `counterexample_bruteforce_transcript.txt`. `HASHES.sha256` fixes every
load-bearing artifact.

## Sources consulted

The source papers are not redistributed in this repository. The version
of record of Part II is IEEE Transactions on Information Theory
72(8):6204-6221, August 2026, DOI 10.1109/TIT.2026.3686267; the
research consulted the arXiv copies cited below.

- **[proved]** Part II was read in full as arXiv:2501.12124v4
  (19 August 2025), <https://arxiv.org/abs/2501.12124>; SHA-256 of the
  consulted PDF:
  `275995cab573f1b3360a8bdcd2d9f53bda809172650a9a60eef43f7d2ee887ce`.
  Local text extractions were used during development to disambiguate
  superscripts in Example 19.
- **[proved]** Part I was read in full as arXiv:2407.18122v2
  (5 December 2024), <https://arxiv.org/abs/2407.18122>; SHA-256 of the
  consulted PDF:
  `16d3ddfe39e1d8339bcb9714fd97c88c497252c18bcfab69dfa2bf70ca5d6602`.
  Its state-diagram convention confirms that a cycle's emitted sequence is
  formed from the first bit of each successive state.
- **[proved]** A public search found the table of contents and publisher page
  for Etzion's 2024 book, including Chapter 2 (“LFSR sequences”), but not
  accessible chapter text. The code therefore does not claim book-text
  calibration beyond what Parts I and II reproduce explicitly.

## What is enumerated

Let the product characteristic polynomial have degree `d`, with claimed uniform
period `e=r1*r2`.

1. **[proved]** A register state stores
   `(a_t,...,a_{t+d-1})`; the next digit is calculated directly from
   `a_{t+d}=sum(c_i*a_{t+d-i}) mod 2`, exactly Equation (1).
2. **[proved]** Since the coefficient `c_d` is one, this transition is
   invertible. Iterating every unseen nonzero state partitions all `2^d-1`
   nonzero states into shift orbits. The checker additionally rejects an input
   if any orbit has length other than the claimed `e`.
3. **[proved]** One orbit representative is one cyclic sequence/codeword up to
   shift. Position `k` is placed at `(k mod r1, k mod r2)`. Coprimality makes
   this a bijection onto the `r1*r2` cells.
4. **[proved]** Sliding a window over all `e` array positions covers exactly the
   windows arising from every shift of that orbit. Across all orbits the
   checker therefore examines exactly `2^d-1` windows.
5. **[proved]** With exactly `2^d-1` observations, the PRAC window property is
   equivalent to: no zero window, no repeated nonzero window, and all
   `2^d-1` nonzero `d`-bit matrices seen. The implementation checks all three
   conditions and the accounting identity
   `missing = duplicate occurrences + zero occurrences`.

The optimized row-mask extractor is only a bit-packed form of the literal
array operation. **[verified by brute force]** Unit tests compare it cell for
cell against a simple nested-loop toroidal extractor over several array and
window sizes.

## Calibration details

The explicit exponent-85 factor masks regenerated from scratch are:

| index | mask | polynomial |
|---:|---:|---|
| 1 | `0x13f` | `x^8+x^5+x^4+x^3+x^2+x+1` |
| 2 | `0x177` | `x^8+x^6+x^5+x^4+x^2+x+1` |
| 3 | `0x17b` | `x^8+x^6+x^5+x^4+x^3+x+1` |
| 4 | `0x18b` | `x^8+x^7+x^3+x+1` |
| 5 | `0x1a3` | `x^8+x^7+x^5+x+1` |
| 6 | `0x1bd` | `x^8+x^7+x^5+x^4+x^3+x^2+1` |
| 7 | `0x1dd` | `x^8+x^7+x^6+x^4+x^3+x^2+1` |
| 8 | `0x1f9` | `x^8+x^7+x^6+x^5+x^4+x^3+1` |

- **[proved]** `poly_enumeration.py` uses polynomial long division, Rabin's
  irreducibility test, and modular powering over `GF(2)[x]` to regenerate this
  fixture list. The verdict path does not call this module.
- **[verified by brute force]** The factor count is eight and each factor's
  computed order is 85.
- **[verified by brute force]** The CRT index grid and folded array exactly
  match Part II, Example 1.
- **[verified by brute force]** For
  `x^6+x^5+x^4+x^2+1`, the three recurrence cycles exactly match all three
  sequences printed in Part II, Example 3, up to cyclic rotation. This pins the
  characteristic-polynomial and state-bit conventions independently of the
  algebraic implementations.

Full per-case counts, witnesses, timings, source hashes, paper hashes, and
runtime versions are in `calibration.json`; the concise run log is
`calibration_transcript.txt`. No random sampling is used.

## Frozen failure witnesses

Window strings below are in top-to-bottom row order and left-to-right column
order. Codeword numbering follows increasing smallest unseen register state.

### Exponent-21 product, `(7,3;3,4)`

- **[verified by brute force]** The colliding matrix is
  `['1101','0000','0000']`. It occurs at `(top=0,left=2)` in codeword 0
  (representative state 1), and at `(top=1,left=0)` in codeword 1
  (representative state 2).
- **[verified by brute force]** The first missing nonzero matrix is
  `['1000','0000','0000']`; the run contains 63 zero windows, 3,969 duplicate
  nonzero occurrences, and 4,032 missing nonzero matrices.

### Primitive exponent-63 product, `(7,9;3,4)`

- **[verified by brute force]** The colliding matrix is
  `['1011','1000','1110']`. It occurs at `(top=4,left=3)` and
  `(top=6,left=5)` in codeword 0 (representative state 1).
- **[verified by brute force]** The first missing nonzero matrix is
  `['1000','0000','0000']`; the run contains 3 zero windows, 3,069 duplicate
  nonzero occurrences, and 3,072 missing nonzero matrices.

## Reproduction

From this directory:

```bash
python3 -m unittest -v test_bruteforce.py
python3 calibrate.py
```

Check an arbitrary product by repeating `--factor`; a factor may be a bit mask
or a comma-separated exponent list:

```bash
python3 bruteforce.py \
  --factor 6,5,0 --factor 6,1,0 \
  --r1 7 --r2 9 --window-rows 3 --window-cols 4
```

Exit status is zero for PASS and one for a completed FAIL. Malformed or
non-uniform inputs raise an error rather than producing a verdict.

## Feasibility

- **[proved]** Exhaustive work is intrinsically exponential here: the checker
  must classify exactly `2^d-1` windows for recurrence/window degree `d`.
- **[proved]** Its two dominant dense bitsets occupy approximately
  `2 * 2^d / 8 = 2^(d-2)` bytes in total. The recurrence is folded in a
  streaming pass, so a full period is not retained as Python integers.
- **[verified by brute force]** On Python 3.12.13 in the recorded container, a
  degree-18 triple checked 262,143 windows in 1.59 seconds; a degree-24
  four-factor check classified 16,777,215 windows in 105.31 seconds.
- **[conjectured]** Based on those measurements, degree 24 is a comfortable
  certification target, degree 26 is a several-minute job, degree 28 is on the
  order of half an hour, and degree 32 is not a sensible routine brute-force
  target in this pure-Python implementation. Determinant failures should be
  prioritized for brute certification in increasing total degree.
