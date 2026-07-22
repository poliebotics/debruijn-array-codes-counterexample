# Conjecture 1 counterexample certificate

## Status and scope

- **Verified by exhaustive brute force:** the explicit product construction
  below is not a `(5,117;3,8)` PRAC. The separately written checker scanned all
  `2^24-1 = 16,777,215` product windows and produced duplicate, missing, and
  zero-window witnesses.
- **Algebraically indicated, twice over:** the Corollary 15 and
  Theorem 6 calculations (arXiv Corollary 48 and Theorem 47) were performed both in separate quotient fields and
  in a common primitive field/cyclotomic-coset representation.
- This settles only Conjecture 1 as stated in the version of record, DOI
  10.1109/TIT.2026.3686267 (arXiv:2501.12124v4). It makes no
  broader priority or structural claim.

## Parameters

Take

```text
(r1,r2;n1,n2) = (5,117;3,4),       k = 2,
n = n1*n2 = 12,                    e = r1*r2 = 585.
```

The conjecture's side condition holds strictly: `3 < 5 < 6`. Also
`gcd(5,117)=1`, `585 | (2^12-1)=4095`, and `ord_585(2)=12`. There are
`phi(585)/12 = 24` irreducible degree-12 polynomials of exponent 585; 16 pass
the single-factor filter for this tuple.

Choose

```text
f(x) = x^12 + x^10 + x^6 + x^5 + x^3 + x + 1       (bitmask 0x146b)
g(x) = x^12 + x^9 + x^8 + x^4 + x^3 + x + 1        (bitmask 0x131b).
```

Both are irreducible of degree 12 and exponent 585.

## Single-factor hypotheses

Using `mu=47`, `nu=-2`, so that `47*5 - 2*117 = 1`, the Corollary 15 sets

```text
{ beta^i gamma^j : 0 <= i < 3, 0 <= j < 4 }
```

have binary rank 12 for both `f` and `g`. Thus each factor separately passes
the paper's necessary-and-sufficient criterion for a `(5,117;3,4)` PRAC.
The separate brute-force checker additionally verified exactly 4,095 of
4,095 distinct nonzero `3 x 4` windows for each single factor, with no zero,
duplicate, or missing window.

## Product failure

The product is

```text
f(x)g(x)
 = x^24 + x^22 + x^21 + x^20 + x^19 + x^17 + x^16 + x^15
   + x^14 + x^12 + x^10 + x^6 + x^4 + x^2 + 1
```

with bitmask `0x17bd455`. For target window `3 x 8`, the Theorem 6 trace
matrix has rank 23 rather than 24. In the ordered polynomial bases
`(1,alpha_f,...,alpha_f^11 | 1,alpha_g,...,alpha_g^11)`, an explicit nonzero
right-null vector is `0x206632`; its two 12-bit blocks are `0x632` and `0x206`.
Every one of the 24 recorded matrix rows has even dot product with this vector.

The exhaustive recurrence/folding scan found:

- total product windows: `16,777,215`;
- unique nonzero windows: `8,388,607`;
- duplicate occurrences: `8,388,607`;
- missing nonzero windows: `8,388,608`;
- zero windows: `1`.

One explicit duplicate `3 x 8` window has rows

```text
11110001
00010011
11100011
```

at `(representative 1, codeword 0, top 1, left 40)` and
`(representative 8, codeword 4, top 4, left 28)` in the brute-force checker's
canonical enumeration. Its first missing nonzero window has rows
`[00100000, 00000000, 00000000]` (packed word `4`). The unique zero window is
at `(representative 10781, codeword 4935, top 4, left 14)`.

## Reproduction

```sh
cd implementations/algebra
python3 -m unittest -v
python3 sweep.py \
  --max-degree 12 \
  --complete-filter-limit 10000 \
  --sample-factors 4096 \
  --pair-budget 50000 \
  --triple-budget 1 \
  --larger-budget 1 \
  --max-k 2 \
  --output runs/pairs_d12
```

The sweep stops at the first singular subset and writes the exact 24 matrix
rows, source hashes, matrix hash, and null vector to
`runs/pairs_d12/counterexample_candidate.json`. The run ledger records 5,516
product subset tests before stopping; all factor filters through the stopping
tuple were exhaustive. The brute-force evidence is maintained by
the separate checker at
`../bruteforce/counterexample_candidate_bruteforce.json`, SHA-256
`feb790a96209d2f93d894fec368b417998516d9ba65b66bc77ad067dbbf01d36`.
Its checker source was
`../bruteforce/bruteforce.py`, SHA-256
`ed84442dc519ff07fc24c27f00d4b91366011c89a24e70562349351875ba23f0`
at verification time. These files should travel together in the frozen final
counterexample package.
