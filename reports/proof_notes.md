# Structural notes and an explicit certificate for Conjecture 1

Date: 2026-07-21  
Source convention: Blackburn--Chee--Etzion--Lao; version of record IEEE Transactions on Information Theory 72(8):6204-6221, August 2026, DOI 10.1109/TIT.2026.3686267 (read as arXiv:2501.12124v4; print numbering below, arXiv numbers in parentheses).  
Status vocabulary: **proved**, **verified by brute force**, **algebraically indicated**, and **conjectured** have exactly the meanings required by the project brief.

## 1. Evaluation form of Theorem 6 (arXiv Theorem 47)

**Proved.** Put $h=n_1$, $w=n_2$, $e=r_1r_2$, and $n=hw$.  For selected roots $\alpha_u$, put

\[
  \beta_u=\alpha_u^{\nu r_2},\qquad
  \gamma_u=\alpha_u^{\mu r_1},\qquad
  \mu r_1+\nu r_2=1.
\]

For a target window \(h\times kw\), Theorem 6 is equivalently the assertion that the \(kn\) vectors

\[
 v_{ij}=\bigl(\beta_1^i\gamma_1^j,\ldots,
                  \beta_k^i\gamma_k^j\bigr)\in
                  \bigoplus_{u=1}^k \mathbf F_{2^n},
 \quad 0\le i<h,\ 0\le j<kw,
\]

are linearly independent over $\mathbf F_2$.  Indeed, the $u$-th block of row $(i,j)$ of $C$ consists of the trace pairings of $\beta_u^i\gamma_u^j$ with the basis $1,\alpha_u,\ldots,\alpha_u^{n-1}$.  The absolute trace pairing is nondegenerate, so this replaces each component by an invertible change of coordinates and preserves row rank.

**Proved.** Equivalently, let

\[
 \mathcal R_{h,L}=\{P(X,Y)\in\mathbf F_2[X,Y]:
                       \deg_XP<h,\ \deg_YP<L\}.
\]

The \(k\)-factor product passes precisely when the simultaneous evaluation map

\[
 \operatorname{ev}_S:\mathcal R_{h,kw}\longrightarrow
       \bigoplus_{u=1}^k\mathbf F_{2^n},\qquad
 P\longmapsto \bigl(P(\beta_u,\gamma_u)\bigr)_{u=1}^k
\]

is injective (and hence bijective, since both sides have dimension $kn$).  A single factor passes precisely when the analogous map from $\mathcal R_{h,w}$ is injective.

This is the useful group-algebra formulation: after choosing a primitive $e$-th root $\zeta$, every $\alpha_u$ is $\zeta^{a_u}$, and the rectangle is a set of characters on $C_{r_1}\times C_{r_2}$.

## 2. Exact \(k=2\) Schur-complement obstruction

**Proved.** Assume the two single-factor maps $E_u:\mathcal R_{h,w}\to K_u$ are isomorphisms, where $K_u=\mathbf F_2(\alpha_u)$.  Split

\[
 P(X,Y)=P_0(X,Y)+Y^wP_1(X,Y),\qquad P_0,P_1\in\mathcal R_{h,w}.
\]

Let $M_u$ denote multiplication by $\gamma_u^w$ on $K_u$, and let $T=E_2E_1^{-1}:K_1\to K_2$.  Eliminating $P_0$ from the two evaluation equations shows that the pair product passes if and only if

\[
       T M_1+M_2T:K_1\longrightarrow K_2
\]

is nonsingular as an $\mathbf F_2$-linear map.  Thus the individual hypotheses only say that $T$ is invertible; they do not prohibit a nonzero vector on which $T$ intertwines the two multiplication maps.  The explicit certificate in Section 5 supplies exactly such an obstruction in polynomial form.

## 3. What the side condition really forces

Write $r=r_1$, and set $d=\operatorname{ord}_r(2)$.

**Proved (normalisation lemma).** If even one single factor passes and \(h<r<2h\), then

\[
 d=\varphi(r)\quad\text{and}\quad h\le d<2h.
\]

Proof: the single-factor basis contains $1,\beta,\ldots,\beta^{h-1}$, so these powers are independent and $d=[\mathbf F_2(\beta):\mathbf F_2]\ge h$.  Since $d\mid\varphi(r)$ and
$\varphi(r)\le r-1<2h$, the positive integer $\varphi(r)/d$ is less than two and hence equals one.

**Proved.** Consequently all primitive $r$-th roots form one Frobenius orbit.  For every selected irreducible factor one may replace its chosen root by a conjugate so that

\[
             \beta_1=\cdots=\beta_k=b.
\]

This is the genuine contribution of $h<r<2h$.  It does **not** imply $d=h$; the verified counterexample below has $h=3$, $r=5$, and $d=4$.

## 4. Coefficient-space reduction and a proved subfamily

Let \(F=\mathbf F_2(b)=\mathbf F_{2^d}\), let \(K=\mathbf F_{2^n}\), and put

\[
 U=\operatorname{span}_{\mathbf F_2}\{1,b,\ldots,b^{h-1}\}\subseteq F,
 \qquad m=[K:F]=n/d.
\]

After the normalisation above, let $g_u(Y)\in F[Y]$ be the minimal polynomial of $\gamma_u$ over $F$.

**Proved.** Each \(g_u\) has degree \(m\), and distinct binary factors give distinct \(g_u\).  Since \(F\subseteq K\), \(b\gamma_u=\alpha_u\), and \(K=\mathbf F_2(\alpha_u)\), we have \(F(\gamma_u)=K\), so the degree is \(m=n/d\).  Equivalently, if \(a=\operatorname{ord}_{r_2}(2)\), then

\[
 [F(\gamma_u):F]
 =\frac{a}{\gcd(a,d)}
 =\frac{\operatorname{lcm}(d,a)}{d}
 =n/d.
\]

If $g_u=g_v$, then $\gamma_v=\gamma_u^{2^{dq}}$ for some $q$; since $b\in F$, this gives
$\alpha_v=(b\gamma_u)^{2^{dq}}$, contradicting the distinctness of the binary minimal polynomials.

**Proved (exact reduction).** Under the identification

\[
 P(X,Y)=\sum_{i,j}c_{ij}X^iY^j
 \quad\longmapsto\quad
 A(Y)=P(b,Y)=\sum_j\left(\sum_i c_{ij}b^i\right)Y^j,
\]

the rectangle $\mathcal R_{h,L}$ is exactly $U[Y]_{<L}$.  Hence:

* factor $u$ passes singly iff $U[Y]_{<w}\cap(g_u)=\{0\}$;
* a selected \(k\)-factor product passes iff

\[
 U[Y]_{<kw}\cap\left(\prod_{u=1}^k g_u\right)=\{0\}.
\]

The ideals here are taken in $F[Y]$, while the coefficient restriction is to the $\mathbf F_2$-subspace $U$.

**Proved (partial theorem, all \(k\)).** If, in addition, $d=h$, Conjecture 1 holds for every selected subset, even without separately assuming the single-factor tests.  In this case $U=F$, each $g_u$ has degree $w$, and the product of $k$ distinct $g_u$'s has degree $kw$.  No nonzero polynomial of degree less than $kw$ can be divisible by it.

This proves the conjectured hierarchy for the entire Theorem 5 (arXiv Theorem 30) subfamily
$\operatorname{ord}_{r_1}(2)=n_1$ under $n_1<r_1<2n_1$.  It includes the motivating $(5,17;4,2)$ family and the exponent-21 $(3,7;2,3)$ family.

**Proved (paper-ready partial theorem).** Let \(h,w,r,s\) be positive integers such that
\(\gcd(r,s)=1\), \(h<r<2h\), and
\(\operatorname{ord}_{rs}(2)=hw\).  If
\(\operatorname{ord}_r(2)=h\), then for every collection of \(k\) distinct
degree-\(hw\), exponent-\(rs\) irreducible polynomials, folding the sequences
generated by their product yields an \((r,s;h,kw)\)-PRAC.

Indeed, \(\operatorname{ord}_r(2)=h\) divides
\(\varphi(r)\le r-1<2h\), so it equals \(\varphi(r)\); hence all primitive
\(r\)-th roots form one Frobenius orbit without needing a single-factor
hypothesis. After normalising their \(r\)-components to \(b\), the
\(s\)-components have distinct degree-\(w\) minimal polynomials over
\(\mathbf F_{2^h}\), whose product has degree \(kw\).

**Proved (exact obstruction to extending that proof).** When \(d>h\), \(U\) is a proper, nonmultiplicatively-closed subspace of \(F\), and \(m=hw/d<w\).  The product \(\prod g_u\) then has degree \(km<kw\), leaving room for a low-degree multiple whose coefficients happen to fall in \(U\).  The displayed side condition alone does not rule this out.  Section 5 gives such a multiple with \((d,h,m,w,k)=(4,3,3,4,2)\).

## 5. Verified counterexample: \((5,117;3,4)\)

**Verified by brute force (paper-ready counterexample theorem).** Let

\[
\begin{aligned}
 f_1(X)&=X^{12}+X^{10}+X^6+X^5+X^3+X+1,\\
 f_2(X)&=X^{12}+X^9+X^8+X^4+X^3+X+1.
\end{aligned}
\]

Both are irreducible of degree 12 and exponent \(5\cdot117=585\).
Folding the sequences generated by either factor yields a
\((5,117;3,4)\)-PRAC, but folding the sequences generated by \(f_1f_2\)
does not yield a \((5,117;3,8)\)-PRAC.  Since \(3<5<2\cdot3\), this is a
counterexample to Conjecture 1.

### 5.1 Parameters and binary factors

**Verified by brute force.** Take

\[
 (r_1,r_2;n_1,n_2)=(5,117;3,4),\qquad e=585,\qquad n=12,
\]

and

\[
\begin{aligned}
 f_1(Z)&=Z^{12}+Z^{10}+Z^6+Z^5+Z^3+Z+1 &&(\texttt{0x146b}),\\
 f_2(Z)&=Z^{12}+Z^9+Z^8+Z^4+Z^3+Z+1 &&(\texttt{0x131b}).
\end{aligned}
\]

The numerical conditions are \(3<5<6\), \(\gcd(5,117)=1\), and
\(585\mid 2^{12}-1\).

**Proved finite certificate.** Rabin's irreducibility test and the exact-order test reduce to the following polynomial remainders.  Integers encode binary polynomials by coefficient bitmasks.

| identity | modulo `0x146b` | modulo `0x131b` |
|---|---:|---:|
| $Z^{2^{12}}$ | `0x002` | `0x002` |
| $\gcd(Z^{2^6}+Z,f_u)$ | `0x001` | `0x001` |
| $\gcd(Z^{2^4}+Z,f_u)$ | `0x001` | `0x001` |
| $Z^{585}$ | `0x001` | `0x001` |
| $Z^{195}$ | `0xab8` | `0x520` |
| $Z^{117}$ | `0x4a8` | `0x7ce` |
| $Z^{45}$ | `0x19c` | `0x73d` |

Thus both polynomials are irreducible of degree 12, and their roots have exact order \(585\): the \(Z^{585}\) row equals `0x001`, while \(Z^{585/p}\not\equiv1\pmod{f_u}\) for each prime divisor \(p\in\{3,5,13\}\), as the last three rows show.

### 5.2 A common-field proof of both single hypotheses

**Proved, conditional only on the displayed finite-field identities (which are mechanically checkable by polynomial reduction).** Work in

\[
 K=\mathbf F_2[a]/(f_1(a)).
\]

The element \(a_2=a^{46}\) is a root of \(f_2\).  With

\[
 47\cdot5-2\cdot117=1,
\]

choose

\[
 b=a^{351}=a_2^{351},\qquad
 c_1=a^{235},\qquad c_2=a_2^{235}=a^{280}.
\]

Here \(b\) has order 5 and

\[
 F=\mathbf F_2(b)\cong
 \mathbf F_2[B]/(B^4+B^3+B^2+B+1)=\mathbf F_{16}.
\]

Both \(c_1,c_2\) have degree three over \(F\).  Their distinct minimal polynomials over \(F\) are

\[
\begin{aligned}
 m_1(Y)&=Y^3+(1+b+b^2+b^3)Y^2+b^2Y+(b^2+b^3),\\
 m_2(Y)&=Y^3+(1+b+b^2+b^3)Y^2+(1+b+b^3)Y+(b^2+b^3).
\end{aligned}
\]

For a direct coordinate check in \(K\), the residues are

| element | 12-bit polynomial residue |
|---|---:|
| $a_2$ | `0x338` |
| $b$ | `0x0f2` |
| $c_1$ | `0x0ff` |
| $c_2$ | `0x0fa` |

and the coefficient lists of $m_1,m_2$, from constant to leading coefficient, are respectively

```text
[0xab9, 0x4a8, 0xa4a, 0x001]
[0xab9, 0xee2, 0xa4a, 0x001].
```

**Proved.** Let $U=\langle1,b,b^2\rangle_{\mathbf F_2}$.  A nonzero member of $U[Y]$ of degree below four divisible by $m_u$ would have to be $q m_u$, with $q=q_0+q_1b+q_2b^2\in U\setminus\{0\}$.  Requiring the $b^3$-coordinate of every coefficient to vanish gives, for both $u$,

\[
 q_0=0\quad(Y^2\text{ coefficient}),\qquad
 q_0+q_2=0\quad(\text{constant coefficient}),
\]

and then \(q_1+q_2=0\) for \(m_1\), or \(q_0+q_1+q_2=0\) for \(m_2\), from the \(Y\)-coefficient.  Hence \(q_0=q_1=q_2=0\), a contradiction.  By the reduction in Section 4, each factor therefore satisfies Corollary 15 (arXiv Corollary 48) for a \(3\times4\) window.

As a redundant coordinate certificate, the twelve vectors
\(b^ic_u^j\), ordered by \(i=0,1,2\) and then \(j=0,1,2,3\), are

```text
f1: 001 0ff 4f9 d96  0f2 002 1fe 9f2  4a8 1e4 004 3fc
f2: 001 dc1 bbc b5d  a4d 002 899 463  7ce 781 004 229
```

in their respective polynomial bases; exact binary Gaussian elimination gives rank 12 in each case.

### 5.3 A compact product-failure certificate

**Proved.** Multiplying the two cubic polynomials over \(F\) gives

\[
\begin{aligned}
 M(Y)=m_1(Y)m_2(Y)
 &=Y^6+(1+b+b^2)Y^4+b^3Y^3\\
 &\quad +(1+b^2+b^3)Y^2+(b+b^2)Y+(1+b^2+b^3).
\end{aligned}
\]

Although \(M\) itself has coefficients outside \(U\), multiplication by \(Y+b\) cancels every \(b^3\)-coordinate:

\[
\begin{aligned}
 A(Y)=(Y+b)M(Y)
 &=Y^7+bY^6+(1+b+b^2)Y^5+(b+b^2)Y^4\\
 &\quad+bY^3+(1+b)Y^2+Y+(1+b^2).
\end{aligned}
\]

Thus \(A\in U[Y]_{<8}\setminus\{0\}\), and \(A(c_1)=A(c_2)=0\).  Replacing \(b^i\) by \(X^i\) gives the explicit binary rectangle polynomial

\[
\boxed{
\begin{aligned}
P(X,Y)={}&1+Y+Y^2+Y^5+Y^7\\
 &+X(Y^2+Y^3+Y^4+Y^5+Y^6)\\
 &+X^2(1+Y^4+Y^5).
\end{aligned}}
\]

It has \(\deg_XP=2<3\), \(\deg_YP=7<8\), and

\[
             P(b,c_1)=P(b,c_2)=0.
\]

By Section 1, this is a nonzero row relation in the \(24\times24\) Theorem 6 matrix, so the two-factor folding fails the \(3\times8\) product test.

**Proved redundant univariate certificate.** For a root $\alpha_u$ of either binary factor, $\beta_u=\alpha_u^{351}$ and $\gamma_u=\alpha_u^{235}$.  Reducing exponents modulo 585 gives

\[
\begin{aligned}
Q(Z)&=P(Z^{351},Z^{235})\pmod{Z^{585}-1}\\
 &=1+Z^5+Z^6+Z^{117}+Z^{121}+Z^{122}+Z^{235}+Z^{236}\\
 &\qquad+Z^{356}+Z^{470}+Z^{471}+Z^{472}+Z^{475}.
\end{aligned}
\]

Straight binary polynomial division gives

\[
                 Q(Z)\bmod f_1(Z)=Q(Z)\bmod f_2(Z)=0.
\]

This certificate does not use a trace convention, a companion-matrix convention, or a choice of field basis.

### 5.4 Separate recurrence/folding verification

**Verified by brute force.** The from-scratch checker generated sequences
directly from the two binary recurrences, folded them only through the CRT
coordinate rule, and performed exhaustive window scans.  It did not import
the finite-field, trace, determinant, or evaluation code used above.

For each factor separately it scanned \(7\cdot585=4095\) windows and found
all 4095 nonzero \(3\times4\) matrices exactly once, with no zero window.
For the degree-24 product it scanned

\[
  28{,}679\cdot585=16{,}777{,}215=2^{24}-1
\]

windows.  It found only \(8{,}388{,}607\) distinct nonzero windows,
\(8{,}388{,}608\) missing nonzero windows, \(8{,}388{,}607\) duplicate
nonzero occurrences, and one zero-window occurrence.  Therefore both
hypotheses hold and the claimed \(3\times8\) conclusion fails.

**Verified by brute force (concrete collision).** The \(3\times8\) matrix

    11110001
    00010011
    11100011

occurs in two distinct shift orbits:

| representative state | top | left |
|---:|---:|---:|
| 1 | 1 | 40 |
| 8 | 4 | 28 |

The first missing nonzero window is

    00100000
    00000000
    00000000

and the all-zero window occurs in representative state 10781 at
\((\mathrm{top},\mathrm{left})=(4,14)\).

**Verified by brute force (provenance).** The frozen record is
implementations/bruteforce/counterexample_frozen.json, SHA-256
ba098b857e2aeeccef726e3440736dd25969732cd6c0bac0cb984a43efaa3b97.
The checker SHA-256 is
ed84442dc519ff07fc24c27f00d4b91366011c89a24e70562349351875ba23f0;
the run used Python 3.12.13 on Linux, with no randomness.

### 5.5 Separate trace-coordinate collision

**Algebraically indicated.** This is an additional trace-coordinate collision, distinct from the recurrence witness just verified.  In the separate polynomial fields $K_u=\mathbf F_2[x]/(f_u)$, take

\[
 \delta_1=x+x^4+x^5+x^9+x^{10}=\texttt{0x632},\qquad
 \delta_2=x+x^2+x^9=\texttt{0x206}.
\]

For $0\le i<3$, $0\le j<8$, the two individual trace matrices

\[
 \operatorname{Tr}_{K_u/\mathbf F_2}
       (\delta_u\beta_u^i\gamma_u^j)
\]

are identical, namely

```text
00100110
11110101
00010110
```

and hence their sum is the all-zero $3\times8$ matrix.  The corresponding right-null vector of the trace matrix, with the $f_1$ block in the low 12 bits, is `0x206632`.

Define two trace-sequence representatives by coefficient pairs

\[
 (\sigma_1,\sigma_2)=(1,1),\qquad
 (\sigma'_1,\sigma'_2)=(1+\delta_1,1+\delta_2)
       =(\texttt{0x633},\texttt{0x207}).
\]

Their folded top-left $3\times8$ windows are both

```text
00010010
00010011
00000010
```

The two sequences are not shifts of one another: a shift would require `0x207` to be a power of the order-585 element $x\bmod f_2$, whereas

\[
        \texttt{0x207}^{585}\bmod \texttt{0x131b}=\texttt{0xd0a}\ne1.
\]

Thus these are distinct shift orbits with an explicit algebraic collision.  The brute-force checker confirms the counterexample through a separately written path, but its frozen collision witness is the different one recorded in Section 5.4.

## 6. Resultants, norms, and Lemma 17 (arXiv Lemma 44)

**Proved (resultant/norm obstruction).** A naive resultant in $X$ forgets that $\beta_u$ and $\gamma_u$ are paired powers of the *same* root and therefore introduces spurious cross-pairings.  A useful norm argument exists precisely in the $d=h$ subfamily: then $U=F$, and divisibility by the distinct $F$-minimal polynomials proves the result.  For $d>h$, the coefficient set is only $U$, not a field; norms and ordinary degree counting do not preserve the coefficient-space restriction.  The identity $A=(Y+b)m_1m_2\in U[Y]$ above is the exact obstruction, not merely a failure to find the right norm.

**Proved (Lemma 17 is inapplicable).** Lemma 17 concerns factors obtained from the paper's \(\vee\)-construction, with a degree-\(n_1\), exponent-\(r_1\) factor separated from degree-\(n_2\), exponent-\(r_2\) factors.  Conjecture 1 instead multiplies arbitrary degree-\(n_1n_2\), exponent-\(r_1r_2\) factors.  In the counterexample \(d=4>h=3\), there is not even a degree-three subfield containing \(b\), so the decomposition required by the \(\vee\)-hierarchy is absent.

## 7. Final status and best continuation

1. **Verified by brute force.** The tuple \((5,117;3,4)\) with factors
   \(f_1,f_2\) above is a counterexample to Conjecture 1 as stated in
   arXiv:2501.12124v4.
2. **Proved.** The sparse rectangle polynomial \(P\), its univariate
   divisibility certificate \(Q\), and the \(F_{16}\)-factorisation explain
   the failure without depending on recurrence conventions.
3. **Proved.** The conjecture remains true for the subfamily
   \(\operatorname{ord}_{r_1}(2)=n_1\), under the original side condition,
   for every \(k\).
4. **Conjectured.** Further counterexamples can be classified efficiently by
   enumerating \(d>h\) and solving for low-degree \(H\) such that
   \(H\prod g_u\in U[Y]\).  This is the most promising route to a corrected
   theorem describing exactly when the hierarchy holds.
