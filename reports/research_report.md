# Research report: Conjecture 1 is false

Date: 21 July 2026  
Canonical source: Blackburn, Chee, Etzion and Lao, *On de Bruijn Array
Codes, Part II: Pseudo-Random Array Codes*, IEEE Transactions on
Information Theory 72(8):6204-6221, August 2026, DOI
10.1109/TIT.2026.3686267; secondary
[arXiv:2501.12124](https://arxiv.org/abs/2501.12124) (v4, last revised 19 August 2025).

Every substantive conclusion below is marked **proved**, **verified by brute
force**, **algebraically indicated**, or **conjectured**.

## Verdict

**[verified by brute force]** Conjecture 1 is false for \(k=2\). Take

\[
(r_1,r_2;n_1,n_2)=(5,117;3,4)
\]

and the two binary irreducibles

\[
\begin{aligned}
f_1(x)&=x^{12}+x^{10}+x^6+x^5+x^3+x+1 &&(\texttt{0x146b}),\\
f_2(x)&=x^{12}+x^9+x^8+x^4+x^3+x+1 &&(\texttt{0x131b}).
\end{aligned}
\]

**[proved]** The conjecture's arithmetic side conditions hold:

\[
\gcd(5,117)=1,\qquad 3<5<6,\qquad 5\cdot117=585\mid 2^{12}-1=4095.
\]

**[proved]** Exact Rabin and multiplicative-order certificates establish that
both displayed polynomials are irreducible of degree 12 and exponent 585.
The residues needed to reproduce those certificates are in
`reports/proof_notes.md`.

**[verified by brute force]** Each factor separately generates a
\((5,117;3,4)\)-PRAC. Each run covered all 4,095 nonzero \(3\times4\) matrices
once, using seven recurrence shift orbits, and encountered no zero or repeated
window.

**[verified by brute force]** The product \(f_1f_2=\texttt{0x17bd455}\) does
not generate a \((5,117;3,8)\)-PRAC. The exhaustive recurrence/CRT run classified
all \(2^{24}-1=16,777,215\) windows in all 28,679 shift-orbit arrays.

| Full product outcome | Count |
|---|---:|
| Total windows | 16,777,215 |
| Distinct nonzero windows observed | 8,388,607 |
| Zero windows | 1 |
| Repeated nonzero occurrences | 8,388,607 |
| Missing nonzero windows | 8,388,608 |

**[verified by brute force]** A concrete collision is

```text
11110001
00010011
11100011
```

at the following zero-based positions:

| Shift orbit | Representative state | Top | Left |
|---:|---:|---:|---:|
| 0 | 1 | 1 | 40 |
| 4 | 8 | 4 | 28 |

**[verified by brute force]** The two 585-state recurrence orbits are disjoint.
A second, standalone witness checker that imports no project code regenerates
both sequences, folds them through a separately written list-based CRT map,
and recovers the same collision. It also recovers the zero window at state
10,781 and position \((4,14)\).

## Verification chain

| Path | Independence | Result | Status |
|---|---|---|---|
| Corollary 15 filter (arXiv Corollary 48) | Custom `GF(2)[x]/(f)` arithmetic | Single ranks 12 and 12 | **algebraically indicated** |
| Theorem 6 matrix (arXiv Theorem 47) | Separate quotient fields; literal absolute traces | Product rank 23/24; null `0x206632` | **algebraically indicated** |
| Full recurrence checker | No fields, traces, ranks, or determinants | All 16,777,215 product windows classified | **verified by brute force** |
| Standalone witness checker | Imports no project module; duplicates recurrence, folding, extraction | Collision, disjoint orbits, and zero window reproduced | **verified by brute force** |
| Third engine | External `galois==0.4.7`, separate quotient fields | Ranks 12, 12, 23; sparse relation remainders zero | **algebraically indicated** |

**[proved]** The main brute checker uses only the paper's binary recurrence,
one representative from every nonzero state orbit, the CRT placement
\(k\mapsto(k\bmod r_1,k\bmod r_2)\), and literal toroidal window extraction.
It does not import or reimplement either algebraic decision criterion.

**[verified by brute force]** The frozen full scan took 92.84 seconds under
Python 3.12.13 on Linux 6.12.13. Runtime is provenance, not part of the
mathematical verdict.

## Compact algebraic certificate

**[proved]** Choose Bézout coefficients

\[
47\cdot5-2\cdot117=1.
\]

For a root \(\alpha_u\) of either factor, put
\(\beta_u=\alpha_u^{351}\) and \(\gamma_u=\alpha_u^{235}\). The nonzero
rectangle polynomial

\[
\begin{aligned}
P(X,Y)={}&1+Y+Y^2+Y^5+Y^7\\
&+X(Y^2+Y^3+Y^4+Y^5+Y^6)\\
&+X^2(1+Y^4+Y^5)
\end{aligned}
\]

has \(\deg_XP<3\), \(\deg_YP<8\), and satisfies
\(P(\beta_u,\gamma_u)=0\) for both \(u=1,2\).

**[proved]** Equivalently,

\[
\begin{aligned}
Q(Z)={}&P(Z^{351},Z^{235})\bmod(Z^{585}-1)\\
={}&1+Z^5+Z^6+Z^{117}+Z^{121}+Z^{122}+Z^{235}+Z^{236}\\
&+Z^{356}+Z^{470}+Z^{471}+Z^{472}+Z^{475},
\end{aligned}
\]

and direct binary polynomial division gives \(Q\bmod f_1=Q\bmod f_2=0\).
This is a basis-free row-dependence certificate for the product window. The
external `galois` run independently checks both zero remainders.

**[algebraically indicated]** In the paper's literal trace matrix, the rank is
23 and a right-null vector is `0x206632`. The low and high 12-bit components
are `0x632` and `0x206`.

## Calibration before search

**[verified by brute force]** All 45 calibration cases agreed before the
candidate was accepted:

| Calibration family | Cases | Outcome |
|---|---:|---|
| Degree 8, exponent 85, single factors at `(5,17;4,2)` | 8 | all pass |
| Degree 8, exponent 85, unordered pairs at `(5,17;4,4)` | 28 | all pass |
| Exponent 21, singles in both orientations | 4 | all pass |
| Exponent 21 product at `(3,7;2,6)` | 1 | pass |
| Exponent 21 product at `(7,3;3,4)` | 1 | fail |
| Named primitive exponent 63 singles | 2 | both pass |
| Named primitive exponent 63 product at `(7,9;3,4)` | 1 | fail |

**[proved]** Part II v4 does not actually print the eight exponent-85
polynomials or explicitly tabulate all 28 pairs. Their complete exhaustive
calibration is new work, not a claim that the paper itself supplied such a
table.

**[proved]** Example 19 explicitly states the primitive exponent-63 product
failure. Its exponent-21 transposed paragraph merely notes that the side
condition fails, although the product failure follows immediately because a
four-column toroidal window on a three-column array repeats a column.

## Sweep and coverage

**[algebraically indicated]** The deterministic search enumerated admissible
tuples in increasing total degree and then lexicographic parameter order. For
each tuple it regenerated exact-exponent irreducibles from binary cyclotomic
cosets, applied the complete single-factor filter, and tested unordered pairs.

**[algebraically indicated]** The frozen degree-at-most-12 run contains 88
admissible parameter tuples. In accordance with the instruction to freeze the
first failure, it processed 34 tuples, performed 5,516 subset tests, and
stopped on the singular pair. All factor filters and pair sets through the
candidate were exhaustive; no random sample was used. The remaining 54 tuples
are explicitly marked `not_reached_after_verified_candidate` in
`admissible_manifest.csv`.

**[algebraically indicated]** For the candidate tuple there are 24 degree-12,
exponent-585 irreducibles. Sixteen pass the single-factor filter. The failing
pair arose on the third unordered pair tested, with cyclotomic-coset IDs 1 and
19.

## Structural result retained from the failed proof attack

Let \(h=n_1\), \(r=r_1\), and \(d=\operatorname{ord}_r(2)\).

**[proved]** If one single factor passes and \(h<r<2h\), then
\(d=\varphi(r)\) and \(h\le d<2h\). Hence all primitive \(r\)-th roots are one
Frobenius orbit and the \(\beta\)-components can be normalized to a common
element \(b\in\mathbf F_{2^d}\).

**[proved]** Put
\(U=\operatorname{span}_{\mathbf F_2}\{1,b,\ldots,b^{h-1}\}\). If \(g_u(Y)\)
is the minimal polynomial of \(\gamma_u\) over \(\mathbf F_{2^d}\), the product
criterion becomes

\[
U[Y]_{<kw}\cap\left(\prod_{u=1}^k g_u\right)=\{0\}.
\]

**[proved]** Consequently Conjecture 1 is true for every \(k\) in the subfamily
\(\operatorname{ord}_{r_1}(2)=n_1\). There \(U=\mathbf F_{2^{n_1}}\), every
\(g_u\) has degree \(n_2\), and a nonzero polynomial of degree below
\(kn_2\) cannot be divisible by their degree-\(kn_2\) product.

**[proved]** The counterexample lies just outside that proof: \(h=3\),
\(r=5\), \(d=4\), so \(U\) is a proper coefficient subspace of
\(\mathbf F_{16}\). A low-degree multiple of the two cubic \(g_u\)'s can have
all coefficients in \(U\); the displayed \(P\) is exactly such a multiple.

## Source audit and implementation traps

**[proved]** The current statement is the one in the version of record,
identical in arXiv v4. Versions v2 and v3
have materially different or mistyped conjecture wording.

**[proved]** All implementations use the index range \(j=0,\ldots,n_2-1\)
in Corollary 15, following its proof and Theorem 6.

**[proved]** Section IX takes \(\alpha_u\) to be a root of \(f_u\), whereas an
earlier companion-matrix discussion uses a root of a reciprocal polynomial.
The repository keeps these conventions separate.

**[proved]** Full text of the relevant chapters of Etzion's 2024 book was not
openly accessible. The literature audit read Part II v4, Part I v2, and both
the ISIT 2024 and ISIT 2025 antecedents in full, and records the accessible
book contents and the specific pages cited by Part II.

## Scope and limitations

- **[proved]** The counterexample resolves only Conjecture 1 as stated in
  the version of record (identical in arXiv v4). It is not a classification of all product foldings.
- **[proved]** The sweep stopped at the first singular pair; the 54 later
  degree-at-most-12 tuples were not tested.
- **[verified by brute force]** The full exhaustive verdict covers this
  degree-24 product and the 45 calibration cases. Larger algebraically passing
  sweep instances were not brute-forced unless listed in calibration.
- **[algebraically indicated]** The custom and `galois` determinant paths are
  exact corroboration, but only the recurrence paths receive the project's
  `verified by brute force` label.
- **[proved]** No Lean formalization or second external computer algebra system
  was produced. The external `galois` engine and the standalone recurrence
  witness checker provide the requested separately written third checks.
- **[proved]** No human outside this research session has yet independently
  reviewed the mathematics or rerun the repository.

## Load-bearing hashes

| Artifact | SHA-256 |
|---|---|
| Full brute checker | `ed84442dc519ff07fc24c27f00d4b91366011c89a24e70562349351875ba23f0` |
| Original full scan | `feb790a96209d2f93d894fec368b417998516d9ba65b66bc77ad067dbbf01d36` |
| Frozen counterexample package | `ba098b857e2aeeccef726e3440736dd25969732cd6c0bac0cb984a43efaa3b97` |
| Standalone witness checker | `4884370163cd6634d5f2e8992b2e786a025bfcdeaa75e1dba38954209bdf689a` |
| Standalone witness output | `027e28cbdee1df2dda8184702bdcf2178df6016c3c0d9c24836811d94468cd45` |
| Brute calibration JSON | `9d563501adc180e1e05739d34e7af22d46e988f046168385aaaea5cad497f226` |
| Algebra candidate | `47a15624d8b542f55e7da66101cf89c874ac9ebfdbaf04c289c2ca6dd3bcc697` |
| Theorem 6 matrix rows | `4f08860045a7ff6951d0e0423e20242083da7ff20d0f0ea244c2501179d1ccac` |
| Sweep ledger JSONL | `c5a54ad22e2238df6aa1053559a43b7a7e9e7bd74fa09306d8ece925195ccd06` |
| One-row-per-tuple coverage ledger | `2bddecc200198b33d82928f5a3da48141b5ee4ada6fd7b2be6716e980e097a38` |
| Third-engine result | `fff7a61cf187d8c843acc37a70e2b7a5035e5ccb4994d72e173889f572a19b21` |
