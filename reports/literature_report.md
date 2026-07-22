# Literature audit for Conjecture 1 of Blackburn–Chee–Etzion–Lao

Date checked: 2026-07-21  
Scope: exact source statements, conventions, calibration examples, and prompt/source discrepancies.  

Epistemic labels follow the project vocabulary:

- **proved**: established by direct inspection of the cited source, or by the stated elementary argument;
- **verified by brute force**: reserved for an exhaustive PRAC window check (none was performed in this literature-only audit);
- **algebraically indicated**: exact finite-field/polynomial computation not yet cross-checked by the project’s other implementations;
- **conjectured**: the source’s unresolved claim.

## 1. Sources and provenance

**[proved]** The version of record is:

Simon R. Blackburn, Yeow Meng Chee, Tuvi Etzion, and Huimin Lao, “On de Bruijn Array Codes, Part II: Pseudo-Random Array Codes,” IEEE Transactions on Information Theory 72(8):6204-6221, August 2026, DOI 10.1109/TIT.2026.3686267. This audit was performed against the arXiv preprint: “On de Bruijn Array Codes, Part II: Linear Codes,” arXiv:2501.12124v4, last revised 19 August 2025. Result numbers below use print numbering with arXiv numbers in parentheses; page references are to the arXiv v4 PDF. See NUMBERING_MAP.md.

- Abstract/versions: <https://arxiv.org/abs/2501.12124>
- PDF: <https://arxiv.org/pdf/2501.12124>
- Length: 28 PDF pages
- Downloaded PDF SHA-256: `275995cab573f1b3360a8bdcd2d9f53bda809172650a9a60eef43f7d2ee887ce`

**[proved]** Part I is:

Tuvi Etzion, “On de Bruijn Array Codes—Part I: Nonlinear Codes,” *IEEE Transactions on Information Theory* 71(2) (February 2025), 1434–1449.

- DOI: <https://doi.org/10.1109/TIT.2024.3518434>
- IEEE record: <https://ieeexplore.ieee.org/document/10803089/>
- arXiv: <https://arxiv.org/abs/2407.18122>
- The 24-page arXiv v2 PDF was read in full.
- Downloaded arXiv PDF SHA-256: `16d3ddfe39e1d8339bcb9714fd97c88c497252c18bcfab69dfa2bf70ca5d6602`

**[proved]** The ISIT 2024 antecedent is:

Tuvi Etzion, “Pseduo-Random and de Bruijn Array Codes,” arXiv:2311.04451v4.

- Abstract/versions: <https://arxiv.org/abs/2311.04451>
- PDF: <https://arxiv.org/pdf/2311.04451>
- Downloaded PDF SHA-256: `462830c23af01b87e3a9847136d247f771b97ac42f48e81fd3ddd383142a7456`
- This six-page paper contains the early PRAC definition, folding construction, and the first degree-6/exponent-21 example. It does not contain the current Conjecture 1.

**[proved]** The ISIT 2025 antecedent is:

Yeow Meng Chee, Tuvi Etzion, and Huimin Lao, “Hierarchy of Pseudo-Random
Array Codes,” *2025 IEEE International Symposium on Information Theory
(ISIT)*, Ann Arbor, Michigan, pp. 551–556.

- DOI: <https://doi.org/10.1109/ISIT63088.2025.11195674>
- DBLP record: <https://dblp.org/rec/conf/isit/CheeEL25>
- Its six pages were read in full from arXiv:2501.12124v1, which is the
  authors' conference-preprint version of the same title.
- Downloaded v1 PDF SHA-256:
  `8753a8039c99165e5350c64f1e9519adb6dd8f7792949c7c1319da7288c69c31`.
- It contains the folding and \(\vee\)-product constructions and the two
  hierarchy statements, with most proofs deferred to the then-in-preparation
  Part II. It does not contain the current Conjecture 1 or the later
  Theorem 6/Corollary 15 (arXiv Theorem 47/Corollary 48) determinant criteria.

**[proved]** Etzion’s relevant book is *Sequences and the de Bruijn Graph: Properties, Constructions, and Applications*, Elsevier, 2024.

- Official page: <https://shop.elsevier.com/books/sequences-and-the-de-bruijn-graph/etzion/978-0-443-13517-0>
- Google Books record: <https://books.google.com/books?id=s8_hEAAAQBAJ>
- Chapter 2, “LFSR sequences,” starts at p. 53.
- Chapter 9, “Two-dimensional arrays,” starts at p. 279.
- Chapter 10, “Two-dimensional applications,” starts at p. 325.
- Full chapter text was not openly previewable. Part II specifically cites the book’s pp. 7–13 for the Chinese remainder theorem, p. 41 for irreducible-polynomial counts, pp. 61–63 and 66–67 for sequence/companion-field facts, and p. 85, Theorem 3.5.

## 2. Version-history warning

**[proved]** The conjecture must be cited from the version of record; among arXiv copies, from v4 or later, not from cached older versions.

- In v2, Conjecture 1 concludes with window width `k n1` where later versions have `k n2`. It also assumes only that one irreducible polynomial `g` gives the base PRAC.
- In v3, `k n2` is corrected, but the hypothesis still starts from one `g`; it does not explicitly require each selected irreducible polynomial to pass individually.
- In v4, the conjecture assumes that every `f_i` under consideration individually gives the base PRAC. It also adds the side-condition discussion and the current Example 19.

The report below therefore uses v4 exclusively for the conjecture and calibration claims.

## 3. Exact definitions and folding convention

### SDBA and SDBAC — Part II, Definition 3, PDF p. 2

**[proved]** An \((r_1,r_2;n_1,n_2)\)-SDBA is one binary doubly-periodic \(r_1\times r_2\) array with

\[
r_1r_2=2^{n_1n_2}-1,
\]

in which every nonzero binary \(n_1\times n_2\) matrix occurs exactly once as a toroidal window.

**[proved]** An SDBAC is a set of such-size arrays for which \(r_1r_2\mid 2^{n_1n_2}-1\), with every nonzero \(n_1\times n_2\) matrix occurring exactly once across all windows of all codewords.

### Necessary count and dimension conditions — Part II, Lemma 1, PDF p. 2

**[proved]** For a size-\(\Delta\) SDBAC,

\[
r_1>n_1\quad\text{or}\quad r_1=n_1=1,
\]

\[
r_2>n_2\quad\text{or}\quad r_2=n_2=1,
\]

and

\[
\Delta r_1r_2=2^{n_1n_2}-1.
\]

### PRAC — Part II, Definition 5, PDF p. 2

**[proved]** A PRAC is an SDBAC with shift-and-add closure. The paper’s cyclic-array convention treats codewords as representatives of shift-orbits. Its next paragraph makes the operational meaning explicit: the codewords, all their horizontal and vertical cyclic shifts, and the zero array together form a linear array code.

**[proved]** Consequently, an implementation must not insert every shift as a separate SDBAC codeword: doing so would repeat every window. The prompt’s formulation “the sum is a shift of a codeword” is the safe computational interpretation.

### Folding — Part II, Section III, PDF p. 7

**[proved]** If \(\gcd(r_1,r_2)=1\), sequence symbol \(s_k\) is placed at array coordinate \((i,j)\) determined by

\[
i\equiv k\pmod{r_1},\qquad j\equiv k\pmod{r_2}.
\]

This is exactly the southeast-diagonal/CRT convention in the research prompt.

## 4. The hierarchy statement and Conjecture 1

### Lemma 17 (arXiv Lemma 44) — Part II, PDF p. 22

**[proved]** Lemma 17 is narrower than a general hierarchy for products of equal-degree factors. Let \(f_1\) have degree \(n_1\), exponent \(r_1\), and let \(h_1,\ldots,h_\ell\) have degree \(n_2\), exponent \(r_2\). It states containment between the PRAC generated from

\[
f_1\vee\prod_{i=1}^{\ell}h_i
\]

and the one generated from

\[
f_1\vee\prod_{i=1}^{\ell-1}h_i.
\]

The larger has window \(n_1\times \ell n_2\); the smaller has window \(n_1\times(\ell-1)n_2\). This is about the paper’s \(\vee\)-product construction, not directly about arbitrary products of the degree-\(n_1n_2\), exponent-\(r_1r_2\) factors appearing in Conjecture 1.

### Conjecture 1 — Part II, PDF p. 22

**[conjectured]** Let

\[
n_1<r_1<2n_1,
\]

and let \(f_1,\ldots,f_\ell\) be irreducible polynomials of degree \(n_1n_2\) and exponent \(r_1r_2\). Assume each \(f_i\), by itself, produces an \((r_1,r_2;n_1,n_2)\)-PRAC when its sequences are folded. Then the product of any \(k\) of them, for \(1\le k\le\ell\), is asserted to produce an

\[
(r_1,r_2;n_1,k n_2)\text{-PRAC}.
\]

## 5. Degree-8, exponent-85 motivating instance

### What the paper actually says — Part II, PDF p. 22

**[algebraically indicated]** The paper reports:

- exactly eight irreducible polynomials have degree 8 and exponent 85;
- one such factor produces a \((5,17;4,2)\)-PRAC, covered by Theorem 5 (arXiv Theorem 30);
- multiplying two such factors produces a \((5,17;4,4)\)-PRAC, not covered by a theorem proved in the paper.

The example claim is paper-reported here, not classified here as “verified by brute force.”

**[proved]** The paper does not print the eight polynomials. It also does not literally say “all 28 unordered pairs.” The generic phrase “two such polynomials” plausibly intends arbitrary pairs, but demanding that all 28 pairs pass is a new exhaustive calibration, not a literal replication of a published table.

### Explicit factors reconstructed over \(\mathbf F_2\)

**[algebraically indicated]** Exact monic enumeration gives the following eight degree-8 polynomials of exact exponent 85:

| Integer | Polynomial |
|---:|---|
| `0x13f` | \(x^8+x^5+x^4+x^3+x^2+x+1\) |
| `0x177` | \(x^8+x^6+x^5+x^4+x^2+x+1\) |
| `0x17b` | \(x^8+x^6+x^5+x^4+x^3+x+1\) |
| `0x18b` | \(x^8+x^7+x^3+x+1\) |
| `0x1a3` | \(x^8+x^7+x^5+x+1\) |
| `0x1bd` | \(x^8+x^7+x^5+x^4+x^3+x^2+1\) |
| `0x1dd` | \(x^8+x^7+x^6+x^4+x^3+x^2+1\) |
| `0x1f9` | \(x^8+x^7+x^6+x^5+x^4+x^3+1\) |

Here bit \(i\) of the integer is the coefficient of \(x^i\). Reciprocal pairs are

\[
(13f,1f9),\ (177,1dd),\ (17b,1bd),\ (18b,1a3).
\]

**[proved]** The expected count is

\[
\frac{\varphi(85)}{\operatorname{ord}_{85}(2)}=\frac{64}{8}=8.
\]

**[algebraically indicated]** Their product divides \(x^{85}+1\) over \(\mathbf F_2\), and every listed factor has exact order 85. This literature-only audit recorded those facts as algebraically indicated; the repository’s separately written brute-force enumeration subsequently cross-checked them.

### Why every single factor passes

**[proved]** Theorem 5 (arXiv Theorem 30), PDF pp. 16–17, applies uniformly, independent of which degree-8 exponent-85 irreducible is selected:

- \(85\mid 2^8-1\);
- \(\gcd(5,17)=1\);
- \(5\mid2^4-1\);
- \(2^0,2^1,2^2,2^3\equiv1,2,4,3\pmod5\) are distinct.

Thus every single factor produces a \((5,17;4,2)\)-PRAC. The theorem does not prove the pair products.

### Expected codeword counts

**[proved]** A degree-8 single-factor code has

\[
\frac{2^8-1}{85}=3
\]

shift-orbit representatives. A degree-16 two-factor product has

\[
\frac{2^{16}-1}{85}=771.
\]

Sliding 85 positions in each of the 771 arrays yields 65,535 candidate windows, exactly the number of nonzero 16-bit matrices.

## 6. Exact Example 19 calibration cases

All statements below refer to Part II v4, PDF p. 22.

### Degree 6, exponent 21

**[algebraically indicated]** The paper reports the two irreducibles

\[
f_1=x^6+x^5+x^4+x^2+1 \quad (`0x75`),
\]

\[
f_2=x^6+x^4+x^2+x+1 \quad (`0x57`).
\]

It reports that each individually produces a \((3,7;2,3)\)-PRAC and their product produces a \((3,7;2,6)\)-PRAC. Here \(2<3<4\), so the side condition holds.

**[algebraically indicated]** It also reports that each single factor produces a \((7,3;3,2)\)-PRAC. The paper then says only that the side condition fails for the product; it does not explicitly print the sentence “the product fails to produce a \((7,3;3,4)\)-PRAC.”

**[proved]** That transposed product must fail anyway: the target window has width 4 on a torus with only 3 columns. Every such window repeats its first column as its fourth, contradicting the SDBAC window requirement and Lemma 1’s necessary inequality \(r_2>n_2\).

### Primitive degree 6, exponent 63

**[algebraically indicated]** The paper reports that there are six primitive degree-6 polynomials and each produces a \((7,9;3,2)\)-PRA/PRAC. For the explicit reciprocal pair

\[
f_1=x^6+x^5+1 \quad (`0x61`),
\]

\[
f_2=x^6+x+1 \quad (`0x43`),
\]

it explicitly reports that the product does **not** produce a \((7,9;3,4)\)-PRAC. The paper gives no determinant null vector, colliding window pair, or missing-window witness; the repository’s subsequent brute-force calibration records a collision, a missing window, and a zero-window occurrence in `implementations/bruteforce/calibration.json` under `example19-e63-product-failure`.

### Complete degree-6 lists

**[algebraically indicated]** Exact monic enumeration gives:

- exponent 21: `0x57`, `0x75`;
- exponent 63: `0x43`, `0x5b`, `0x61`, `0x67`, `0x6d`, `0x73`.

### Sequence representatives that pin the recurrence convention

**[algebraically indicated]** Part II Example 3, PDF pp. 9–10, prints these three representatives for `0x75`:

```text
000001010010011001011
010000111101101010111
001000110111111001110
```

Their CRT folds are reported to form a \((3,7;2,3)\)-PRAC. The ISIT-2024 antecedent prints different cyclic representatives for the same three orbits; differing strings are therefore not by themselves evidence of a recurrence mismatch.

### Expected codeword counts

**[proved]** The counts are:

| Calibration | Codewords |
|---|---:|
| exponent-21, one degree-6 factor | \((2^6-1)/21=3\) |
| exponent-21, two factors | \((2^{12}-1)/21=195\) |
| exponent-63, one primitive factor | \((2^6-1)/63=1\) |
| exponent-63, two factors | \((2^{12}-1)/63=65\) |

## 7. Exact algebraic decision criteria

### Theorem 6 (arXiv Theorem 47) — Part II, PDF pp. 23–25

**[proved]** Let \(f_1,\ldots,f_k\) be distinct irreducible polynomials of common degree \(n\) and common exponent

\[
e=r_1r_2,
\]

with \(\gcd(r_1,r_2)=1\). Choose \(\mu,\nu\in\mathbf Z\) with

\[
\mu r_1+\nu r_2=1.
\]

For a root \(\alpha_u\) of \(f_u\), define

\[
\beta_u=\alpha_u^{\nu r_2},\qquad
\gamma_u=\alpha_u^{\mu r_1}.
\]

For any nontrivial \(\mathbf F_2\)-linear map \(t_u:\mathbf F_{2^n}\to\mathbf F_2\), and target dimensions satisfying

\[
kn=n_1n_2,
\]

form the \(n_1n_2\times n\) block \(C_u\) with

\[
(C_u)_{(i,j),v}=t_u(\alpha_u^v\beta_u^i\gamma_u^j),
\]

where \(0\le i<n_1\), \(0\le j<n_2\), and \(0\le v<n\). Let

\[
C=(C_1\mid C_2\mid\cdots\mid C_k).
\]

Then folding all nonzero sequences whose characteristic polynomial divides \(\prod_u f_u\) produces an \((r_1,r_2;n_1,n_2)\)-PRAC if and only if

\[
\det_{\mathbf F_2}C\ne0.
\]

**[proved]** The trace map is a valid choice of every \(t_u\). The basis \(1,\alpha_u,\ldots,\alpha_u^{n-1}\) may be replaced by any \(\mathbf F_2\)-basis. The prompt’s product substitution, holding height fixed and taking target width \(k n_2\), correctly satisfies the theorem’s dimension equation.

### Corollary 15 (arXiv Corollary 48) — Part II, PDF pp. 25–26

**[proved]** For one irreducible factor of degree \(n=n_1n_2\), folding gives a PRAC if and only if

\[
\{\beta^i\gamma^j:0\le i<n_1,\ 0\le j<n_2\}
\]

is linearly independent over \(\mathbf F_2\).

**[proved]** The proof of Corollary 15 uses the range \(0\le j<n_2\), and the project follows the proof.

### Root/basis convention warning

**[proved]** Section IX takes \(\alpha_u\) to be a root of \(f_u\) itself. Earlier, PDF pp. 5–6, the paper discusses a root of a reciprocal “companion polynomial” in connection with a separate companion-matrix representation. Those conventions must not be silently mixed.

## 8. Source conventions relevant to implementation

**[proved]** In the proof of Theorem 6, the project reads the window index bounds as `0 ≤ i < n1` and `0 ≤ j < n2` throughout, following the surrounding equations and the converse direction.

**[proved]** Part I arXiv v2, Definition 2, says a DBAC covers every “nonzero” matrix, while its abstract speaks of every matrix and its Lemma 1 gives \(\Delta rs=2^{nm}\). Part II’s distinct DBAC/SDBAC terminology is the one this project uses.

## 9. Arithmetic support for the sweep


**[proved]** Lemma 37, PDF p. 20, gives the number of degree-\(n\), exponent-\(e\) irreducibles as

\[
\frac{\varphi(e)}{n}
\]

when \(n\) is the least positive integer for which \(2^n\equiv1\pmod e\). This supports the prompt’s cyclotomic-coset enumeration.

## 10. Prompt/source discrepancies to preserve in the repository

1. **[proved]** Corollary 15 is applied with the range \(j=0,\ldots,n_2-1\), following its proof.
2. **[proved]** The paper does not provide the eight degree-8 polynomials; any explicit list is newly generated and must record its coefficient convention.
3. **[proved]** The paper does not unambiguously certify all 28 degree-8 pairs. Testing all 28 is a valuable new exhaustive calibration.
4. **[proved]** Example 19 does not explicitly state the exponent-21 transposed product failure, although width \(4>3\) proves it immediately.
5. **[proved]** Only the primitive exponent-63 pair’s product failure is explicitly stated, and the paper supplies no collision witness.
6. **[proved]** Lemma 17 concerns the \(\vee\)-construction and cannot be quoted as an already-proved hierarchy for arbitrary products in Conjecture 1.
7. **[proved]** Codewords are shift-orbit representatives. Treating every cyclic shift as a separate SDBAC codeword duplicates windows.
8. **[proved]** Current arXiv v4 materially strengthens/corrects the v2/v3 conjecture wording; the version of record is the canonical source, with arXiv v4 or later as secondary.

## 11. Direct source locations

| Item | Part II v4 PDF location |
|---|---:|
| SDBA/SDBAC/PRAC definitions | p. 2 |
| recurrence, exponent, zero factor, order facts | pp. 4–6 |
| CRT folding convention | p. 7 |
| degree-6/exponent-21 Example 3 | pp. 9–10 |
| set-polynomial criterion, Theorem 26 | pp. 12–14 |
| Theorem 5 (arXiv Theorem 30) | pp. 16–17 |
| count Lemma 37 | p. 20 |
| Lemma 17 (arXiv Lemma 44), degree-8/85 paragraph, Conjecture 1, Example 19 | p. 22 |
| sequence representation Lemma 46 | pp. 23–24 |
| determinant criterion Theorem 6 (arXiv Theorem 47) | pp. 24–25 |
| independence criterion Corollary 15 (arXiv Corollary 48) | pp. 25–26 |
| request for proof or counterexample | p. 27 |
