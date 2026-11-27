# References (IEEE style)

For: "Measuring Timing Side-Channel Leakage in String Comparison: A Practical Replication in Python"

All entries below were checked against the publisher, the venue, or an official source on 2026-11-27. The "Use for" line says where the paper should cite each one.

---

[1] P. C. Kocher, "Timing attacks on implementations of Diffie-Hellman, RSA, DSS, and other systems," in *Advances in Cryptology - CRYPTO '96*, N. Koblitz, Ed., Lecture Notes in Computer Science, vol. 1109. Berlin, Germany: Springer, 1996, pp. 104-113, doi: 10.1007/3-540-68697-5_9.
- Use for: the first timing side-channel attack and the idea that how long a computation takes can leak secrets. Cite it first in the introduction and background.

[2] D. Brumley and D. Boneh, "Remote timing attacks are practical," in *Proc. 12th USENIX Security Symp. (USENIX Security '03)*, Washington, DC, USA, Aug. 2003. [Online]. Available: https://www.usenix.org/conference/12th-usenix-security-symposium/remote-timing-attacks-are-practical
- Use for: showing that timing attacks also work over a network, against OpenSSL. This supports the threat model for the end-to-end recovery attack.

[3] S. A. Crosby, D. S. Wallach, and R. H. Riedi, "Opportunities and limits of remote timing attacks," *ACM Trans. Inf. Syst. Secur.*, vol. 12, no. 3, Art. no. 17, Jan. 2009, doi: 10.1145/1455526.1455530.
- Use for: how to measure timing with jitter and noise (for example, low-percentile filtering and many repeated samples), and how small a difference can be detected over a LAN versus the Internet. Cite it when explaining why the experiment uses many samples or robust statistics, and when discussing local versus remote feasibility.

[4] G. Goodwill, B. Jun, J. Jaffe, and P. Rohatgi, "A testing methodology for side-channel resistance validation," presented at the NIST Non-Invasive Attack Testing Workshop (NIAT 2011), Nara, Japan, Sep. 2011. [Online]. Available: https://csrc.nist.gov/CSRC/media/Events/Non-Invasive-Attack-Testing-Workshop/documents/08_Goodwill.pdf
- Use for: where TVLA comes from. It uses Welch's t-test with the pass/fail threshold |t| > 4.5; the paper states "the pass fail criteria is C > 4.5 or C < -4.5". Cite it in the methodology when defining the leakage test and threshold.

[5] T. Schneider and A. Moradi, "Leakage assessment methodology," in *Cryptographic Hardware and Embedded Systems - CHES 2015*, Lecture Notes in Computer Science, vol. 9293. Berlin, Germany: Springer, 2015, pp. 495-513, doi: 10.1007/978-3-662-48324-4_25. (Extended version: IACR Cryptology ePrint Archive, Paper 2015/207, https://eprint.iacr.org/2015/207)
- Use for: a detailed, practical guide to Welch's t-test leakage assessment, covering how to collect traces and how to interpret the test. Cite it next to [4] to justify the fixed-vs-random (or fixed-vs-fixed) TVLA design and the 4.5 threshold.

[6] Python Software Foundation, "hmac - Keyed-hashing for message authentication," *The Python Standard Library*, Python 3 documentation. [Online]. Available: https://docs.python.org/3/library/hmac.html#hmac.compare_digest
- Use for: the official behaviour of `hmac.compare_digest`. The docs say it "uses an approach designed to prevent timing analysis by avoiding content-based short circuiting behaviour". They also say that if lengths differ, "a timing attack could theoretically reveal information about the types and lengths of a and b - but not their values". The function was "Added in version 3.3", and since 3.10 it uses OpenSSL's `CRYPTO_memcmp()` when available. The docs also warn to use `compare_digest()` "instead of the == operator to reduce the vulnerability to timing attacks."

[7] Python Software Foundation, "What's new in Python 3.3: hmac," *Python 3 documentation*. [Online]. Available: https://docs.python.org/3/whatsnew/3.3.html#hmac
- Use for: the release note stating that `compare_digest()` "has been added to prevent side channel attacks on digests through timing analysis" (contributed by N. Coghlan and C. Heimes, bpo-15061).

[8] C. Heimes, "hmac.secure_compare() leaks information about length of strings," Python issue tracker, bpo-15061, Jun. 2012 (migrated to GitHub as python/cpython#59266). [Online]. Available: https://github.com/python/cpython/issues/59266 (original: https://bugs.python.org/issue15061)
- Use for: the history of the function. It was first a pure-Python `secure_compare` that leaked length. Then it was renamed and moved into C as `operator._compare_digest` (commit by C. Heimes, 24 Jun. 2012). This is optional; it is useful if the paper discusses why length still leaks.

[9] J. B. Almeida, M. Barbosa, G. Barthe, F. Dupressoir, and M. Emmi, "Verifying constant-time implementations," in *Proc. 25th USENIX Security Symp. (USENIX Security '16)*, Austin, TX, USA, Aug. 2016, pp. 53-70. [Online]. Available: https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/almeida
- Use for: the formal definition of constant-time programming (no secret-dependent branches or memory accesses). Cite it in the countermeasures and discussion section as background for why `compare_digest` avoids early exit.

[10] The MITRE Corporation, "CWE-208: Observable timing discrepancy," *Common Weakness Enumeration*. [Online]. Available: https://cwe.mitre.org/data/definitions/208.html
- Use for: the standard name for the weakness class this paper studies. Its observed examples include CVE-2019-10071 (HMAC compared with non-constant-time equality) and CVE-2014-0984 (password check that stops at the first wrong character).

[11] "CVE-2019-10071: Apache Tapestry HMAC timing side channel," CVE Program / NVD, Sep. 16, 2019. [Online]. Available: https://nvd.nist.gov/vuln/detail/CVE-2019-10071
- Use for: a real case. In Apache Tapestry 5.4.0-5.4.3, the code that checks the HMAC on form submissions "used String.equals() for comparisons, which results in a timing side channel for the comparison of the HMAC signatures. This could lead to remote code execution...". This is exactly the early-exit bug the paper studies. The description was confirmed via the CVE Program record (cveawg.mitre.org API); the NVD page renders with JavaScript and could not be fetched as text.

[12] "CVE-2026-21713: Node.js non-constant-time HMAC verification," CVE Program, Mar. 30, 2026. [Online]. Available: https://nodejs.org/en/blog/vulnerability/march-2026-security-releases
- Use for: a recent example showing the bug class still appears in major runtimes. The flaw is that "Node.js HMAC verification uses a non-constant-time comparison when validating user-provided signatures, potentially leaking timing information proportional to the number of matching bytes." This is optional. The description was confirmed via the CVE Program record. The Node.js advisory URL is the reference listed in that record but was not opened directly.

---

## Not included / UNVERIFIED

- Xbox 360 HMAC timing bug (memcmp in the bootloader, around 2007): UNVERIFIED. I did not search for or confirm a primary source, so it is not listed. If the paper wants it, find a primary write-up first.
- BearSSL "Constant-Time Crypto" page (https://www.bearssl.org/constanttime.html): UNVERIFIED. Not checked; Almeida et al. [9] was chosen instead.
- Exact end page for [3]: the bibliographic record gave only "17:1-17:??". Check the ACM Digital Library page for the article length before final submission, or cite only by article number as above (this is acceptable in IEEE style).
