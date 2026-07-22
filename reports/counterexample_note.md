# A counterexample to Conjecture 1 on pseudo-random array codes

Cathal Ryan Hynes  
P.I.G.M.I.E. Ltd. / PolieBotics  
Draft: 21 July 2026

**[proved]** Blackburn, Chee, Etzion and Lao ask for a proof or counterexample
to Conjecture 1; version of record IEEE Transactions on Information
Theory 72(8):6204-6221, August 2026, DOI 10.1109/TIT.2026.3686267
(arXiv:2501.12124v4).

**[verified by brute force]** The following is a counterexample for \(k=2\).

Take

\[
(r_1,r_2;n_1,n_2)=(5,117;3,4)
\]

and

\[
\begin{aligned}
f_1(x)&=x^{12}+x^{10}+x^6+x^5+x^3+x+1,\\
f_2(x)&=x^{12}+x^9+x^8+x^4+x^3+x+1.
\end{aligned}
\]

**[proved]** The two polynomials are irreducible of degree 12 and exponent 585.
Also \(3<5<6\), \(\gcd(5,117)=1\), and \(585\mid2^{12}-1\).

**[verified by brute force]** Each polynomial separately gives a
\((5,117;3,4)\)-PRAC. An exhaustive
recurrence-and-folding check finds every one of the 4,095 nonzero
\(3\times4\) matrices exactly once for each factor.

**[verified by brute force]** Their product does not give a
\((5,117;3,8)\)-PRAC. One \(3\times8\) matrix
appearing twice is

```text
11110001
00010011
11100011
```

With codewords represented by the smallest state in each recurrence orbit,
this window occurs in the orbit represented by state 1 at zero-based position
\((1,40)\), and in the distinct orbit represented by state 8 at position
\((4,28)\).

**[verified by brute force]** The check was exhaustive: it enumerated all
28,679 nonzero shift orbits and all
16,777,215 windows. There were 8,388,607 distinct nonzero windows, one zero
window, 8,388,607 repeated nonzero occurrences, and 8,388,608 missing nonzero
windows.

**[proved]** There is also a short algebraic certificate. With
\(47\cdot5-2\cdot117=1\), put
\(\beta_u=\alpha_u^{351}\) and \(\gamma_u=\alpha_u^{235}\) for roots of the two
factors. Then

\[
\begin{aligned}
P(X,Y)={}&1+Y+Y^2+Y^5+Y^7\\
&+X(Y^2+Y^3+Y^4+Y^5+Y^6)\\
&+X^2(1+Y^4+Y^5)
\end{aligned}
\]

satisfies \(P(\beta_u,\gamma_u)=0\) for both factors. This gives a nonzero row
relation in the \(24\times24\) matrix of Theorem 6 (arXiv Theorem 47).

**[algebraically indicated]** Direct computation gives product rank 23; the
two single-factor matrices have rank 12.

**[proved]** The repository contains a dependency-free finite-field implementation, a
separate full recurrence/CRT implementation, a second standalone witness
checker, and a third check using the Python `galois` package. The recurrence
implementations share no algebraic-test code. All were separately written,
reusing no source code from one another, with knowledge of the claimed
witness.

**[proved]** This claims resolution only of Conjecture 1 as stated in the version of record. It does not
claim a general classification or priority beyond this counterexample.

## AI-assistance disclosure

**[proved]** From a research brief written by Anthropic's Claude (Fable),
OpenAI's Sol Ultra, running in the ChatGPT web interface, found the
counterexample and the sufficient-condition theorem; Fable separately
rebuilt the entire verification, reusing no source code, and matched
every count; a
separate Sol Ultra session contributed two further audit rounds. Cathal Ryan
Hynes set the target and the verification standard, checked the certificate
himself, and stands behind this release. The repository preserves
the source, deterministic ledger, exhaustive outputs, separately written
witness path, versions, and hashes so the result can be checked without
trusting the language model.
