# A counterexample to Conjecture 1 of On de Bruijn Array Codes, Part II

Conjecture 1 of Blackburn, Chee, Etzion and Lao, On de Bruijn Array Codes, Part II: Pseudo-Random Array Codes (IEEE Transactions on Information Theory 72(8):6204-6221, August 2026, DOI 10.1109/TIT.2026.3686267; also arXiv:2501.12124v4, last revised 19 August 2025), is false as stated. The witness lives at (r1, r2; n1, n2) = (5, 117; 3, 4), degree 12, exponent 585, with

    f1(x) = x^12 + x^10 + x^6 + x^5 + x^3 + x + 1    (0x146b)
    f2(x) = x^12 + x^9 + x^8 + x^4 + x^3 + x + 1     (0x131b)

Each factor alone folds into a (5, 117; 3, 4)-PRAC: all 4095 nonzero 3x4 windows appear exactly once across its seven folded orbits. The product f1 f2 does not fold into a (5, 117; 3, 8)-PRAC: of the 16,777,215 windows, 8,388,608 nonzero values never appear, one all-zero window appears, and every realized nonzero value appears exactly twice, the fingerprint of a rank defect of exactly one in the Theorem 6 matrix (Theorem 47 in the arXiv version). The accompanying manuscript also proves a sufficient condition for product closure, holding for any selection of factors whenever ord_{r1}(2) = n1; it covers the exponent-85 motivating family and identifies a broad sufficient regime; outside it the note gives a coefficient-space intersection criterion, not a complete classification. This result was found and verified on 21 July 2026; the version of record (current version dated 16 July 2026) still requests a proof or a counterexample, so to our knowledge the conjecture was open until this release. No claim of global minimality is made, and the verification chain is documented rather than blinded, as described in audit/README.md.

## The ten minute check

You do not need to trust anything in this repository. Let Q(z) be the binary polynomial with support exponents 0, 5, 6, 117, 121, 122, 235, 236, 356, 470, 471, 472, 475. Divide Q by f1 and by f2 over F2 in any computer algebra system: both remainders are zero. Since Q(z) = P(z^351, z^235) mod (z^585 - 1) for a nonzero P with deg_X < 3 and deg_Y < 8, and 47*5 - 2*117 = 1, Theorem 6 of the source paper in evaluation form rules out the window property for the product. The exhaustive side, every one of the 16,777,215 windows enumerated from the raw recurrences, is frozen in implementations/bruteforce/counterexample_frozen.json with SHA-256 hashes recorded in the manifest, and can be regenerated from source.

## What is in this repository

The manuscript in paper/, tex and PDF, stating the counterexample, the sparse certificate, and the sufficient-condition theorem. Three implementations in implementations/: an exact-algebra evaluation engine, an exhaustive recurrence-and-folding checker with its frozen output, and a third engine built on the galois library, together with the calibration transcripts that reproduce the source paper's own worked examples and the coverage ledger of the parameter sweep. An additional full-census reimplementation in audit/, written separately during verification, reusing no code from the rest of the repository. Tests, manifests, and hashes throughout; a fresh clone should pass the full test suite.

## Credit

Produced by an AI research pipeline directed by Cathal Ryan Hynes at P.I.G.M.I.E. Ltd., Ireland. From a research brief written by Anthropic's Claude (Fable), OpenAI's Sol Ultra, running in the ChatGPT web interface, found the counterexample and the sufficient-condition theorem; Fable separately rebuilt the entire verification, reusing no source code, and matched every count; a separate Sol Ultra session contributed two further audit rounds. Cathal Ryan Hynes set the target and the verification standard, checked the certificate himself, and stands behind this release. Scope of claims: resolution of Conjecture 1 as stated in the version of record and the explicit sufficient-condition theorem in the manuscript, nothing broader.

## Licensing

Everything outside paper/ and reports/ other than this README --
implementations/, audit/, certificates/, the hash manifests, and the
top-level scripts and support files -- is licensed under the MIT License;
see LICENSE-MIT. The manuscript (paper/), the reports
(reports/), and this README are licensed under the Creative Commons
Attribution 4.0 International License; see LICENSE-CC-BY-4.0. Attribution to
Cathal Ryan Hynes is a condition of the CC BY license.

## Citing this

Please cite this repository release. If the counterexample is folded into a revision of the source paper, an acknowledgment of the pipeline and systems named above is warmly appreciated.
