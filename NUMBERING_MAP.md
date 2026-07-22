# Numbering map: arXiv preprint vs. version of record

The source paper is S. R. Blackburn, Y. M. Chee, T. Etzion, and H. Lao,
"On de Bruijn Array Codes, Part II: Pseudo-Random Array Codes," IEEE
Transactions on Information Theory 72(8):6204-6221, August 2026, DOI
10.1109/TIT.2026.3686267 (version of record; current version dated 16 July
2026). The arXiv preprint is arXiv:2501.12124. Result numbering differs
between the two:

| arXiv (2501.12124) | Version of record (print) |
|---|---|
| Theorem 47 | Theorem 6 (pp. 6218-6219) |
| Corollary 48 | Corollary 15 (p. 6219) |
| Theorem 30 | Theorem 5 (p. 6213) |
| Lemma 44 | Lemma 17 (p. 6217) |

Editable documentation in this repository uses print numbering, with arXiv
numbers in parenthesized cross-references.

The frozen artifacts retain arXiv numbering by design. The following are
byte-locked by their recorded hashes: the hash-locked checker
implementations/bruteforce/bruteforce.py, the frozen census
implementations/bruteforce/counterexample_frozen.json, the frozen
calibration record and transcripts, the frozen sweep run records, and the
five source files whose exact bytes are hash-recorded inside those frozen
records (implementations/algebra/gf2.py, prac_algebra.py, sweep.py,
test_sweep.py, and implementations/third_engine_galois.py). Their comments
and recorded strings cite arXiv numbering, and code identifiers such as
`theorem47_matrix` likewise keep their arXiv-numbered names.

Across those five files, a line-based grep for the four legacy labels
listed above produces 14 matching lines, comprising 20 literal label
occurrences.
