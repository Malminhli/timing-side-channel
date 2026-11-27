# Results summary: timing side-channel experiments

Written on 2026-11-27 from the files in `results/` (**run 1**) and `results_run2/` (**run 2**).
Numbers are copied exactly as they appear in the files: CSV values as written, Experiment 1 slopes
and the Experiment 3 summary lines from `log.txt`. Values marked *computed* were calculated from the
CSVs by a separate read-only script. No experiment code, statistic or default parameter was changed.
The quick sanity run (`results_quick/`, not in the package) is **not** for the paper.

## Machine and run conditions

| Item | Value | Source |
|---|---|---|
| CPU | AMD Ryzen 5 7535U with Radeon Graphics (12 CPUs, 2 threads per core, CPU max MHz 4630.4429, min MHz 418.4140) | `machine.txt` (lscpu part) |
| Python | 3.14.9 (main, Oct 25 2026, 14:52:47) [GCC 16.2.1 20260810] | `machine.txt` |
| NumPy | 2.5.5 | `machine.txt` |
| matplotlib | 3.11.2 | pip install output (not recorded in `machine.txt`) |
| Platform | Linux-7.2.14-arch1-1-x86_64-with-glibc2.44 | `machine.txt` |
| `processor:` line | empty (`platform.processor()` returns an empty string on this system; use the lscpu model name instead) | `machine.txt` |
| CPU governor during runs | `performance` (both runs) | `machine.txt` |
| Original governor | `powersave` with energy_performance_preference `balance_performance`, driver `amd-pstate-epp`; switched to `performance` via sysfs before the runs (EPP followed to `performance`) | checked in this session |
| Power | charger connected (`ACAD` online = 1, battery Full, 100 %) | checked in this session |
| Background apps | closed before the runs: mpv, Brave, Nautilus, GNOME Software. Still running: GNOME Shell, terminal, Claude Code (idle during the runs), GNOME file indexer `localsearch-3` (~0.2 % CPU) | checked in this session |
| Clock | clocksource `tsc`; `perf_counter` = `clock_gettime(CLOCK_MONOTONIC)`. Back-to-back `perf_counter_ns()` deltas measured after the runs: 60, 61, 70, 71, 80, 81, 90, 91 ns, so the clock moves in steps of ~10 ns and one sample (batch of 50) is quantized to ~0.2 ns | checked in this session |
| Settings | each script's defaults (`args: --out results` / `--out results_run2`) | `machine.txt` |
| Duration | run 1: "All done in 3.6 min" (08:40 to 08:44); run 2: "All done in 3.7 min" (08:44 to 08:48) | `log.txt`, file times |

## Experiment 1: leakage characterisation (L = 16)

Slope from `log.txt` (printed with 2 decimals); medians from `exp1_leakage.csv`.

| Target | Run 1 slope (ns/char) | Run 1 median k=0 (ns) | Run 1 median k=16 (ns) | Run 2 slope (ns/char) | Run 2 median k=0 (ns) | Run 2 median k=16 (ns) |
|---|---|---|---|---|---|---|
| naive_compare | 17.39 | 202.38 | 477.69 | 18.11 | 206.38 | 490.72 |
| builtin_eq | -0.01 | 28.06 | 27.46 | -0.00 | 27.26 | 27.04 |
| hmac_compare_digest | -0.01 | 110.0 | 110.02 | 0.00 | 108.42 | 108.42 |

Cross-check (*computed*, `np.polyfit` on the CSV medians, same as the script): run 1 = 17.3902 / -0.0118 / -0.0062,
run 2 = 18.1150 / -0.0017 / 0.0003 ns per char, which matches the log values.

## Experiment 2: fixed-vs-random Welch t-test (200000 samples per class, threshold |t| > 4.5)

Values from `exp2_tvla.csv` (`t_value`, `median_diff_ns` = median(fixed) − median(random), `leak` = |t| > 4.5).

### Run 1

| Repeat | naive t | naive diff (ns) | naive leak | builtin t | builtin diff (ns) | builtin leak | hmac t | hmac diff (ns) | hmac leak |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 4293.17 | 281.7 | True | -1.768 | 0.0 | False | 8.322 | 0.0 | True |
| 1 | 5359.98 | 288.74 | True | 1.036 | 0.0 | False | 6.461 | 0.0 | True |
| 2 | 5578.949 | 274.52 | True | -0.601 | 0.0 | False | 9.07 | 0.18 | True |
| 3 | 1713.784 | 263.3 | True | 0.27 | 0.0 | False | 10.625 | 0.2 | True |
| 4 | 5352.171 | 268.5 | True | 0.285 | 0.0 | False | 6.251 | 0.0 | True |
| 5 | 5525.784 | 264.08 | True | -0.085 | 0.0 | False | 11.27 | 0.2 | True |
| 6 | 5275.689 | 273.52 | True | 0.08 | 0.0 | False | 5.98 | 0.18 | True |
| 7 | 5403.064 | 264.92 | True | -0.28 | 0.0 | False | 8.711 | 0.0 | True |
| 8 | 5357.305 | 263.68 | True | 0.162 | 0.0 | False | 13.97 | 0.2 | True |
| 9 | 5393.889 | 255.08 | True | 0.098 | 0.0 | False | 6.498 | 0.0 | True |
| **leaks** | **10/10** | | | **0/10** | | | **10/10** | | |

### Run 2

| Repeat | naive t | naive diff (ns) | naive leak | builtin t | builtin diff (ns) | builtin leak | hmac t | hmac diff (ns) | hmac leak |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2951.279 | 267.08 | True | 1.245 | 0.02 | False | 2.23 | 0.02 | False |
| 1 | 4496.984 | 265.28 | True | 2.089 | 0.0 | False | 8.017 | 0.2 | True |
| 2 | 3832.304 | 264.88 | True | 2.323 | 0.02 | False | 5.47 | 0.2 | True |
| 3 | 4982.628 | 287.72 | True | 2.071 | 0.0 | False | 7.172 | 0.2 | True |
| 4 | 5141.349 | 284.92 | True | 1.582 | 0.02 | False | 7.984 | 0.02 | True |
| 5 | 3670.565 | 267.3 | True | 1.71 | 0.0 | False | 3.909 | 0.2 | False |
| 6 | 5012.331 | 275.52 | True | 2.033 | 0.0 | False | 6.105 | 0.2 | True |
| 7 | 4695.626 | 264.28 | True | 2.162 | 0.0 | False | 13.412 | 0.4 | True |
| 8 | 5328.292 | 269.08 | True | 1.934 | 0.0 | False | 5.162 | 0.2 | True |
| 9 | 5165.168 | 272.12 | True | 1.266 | 0.0 | False | 8.289 | 0.38 | True |
| **leaks** | **10/10** | | | **0/10** | | | **8/10** | | |

## Experiment 3: end-to-end attack (L = 8, max length 16, 50 trials per target)

Success, length found and chars correct are from `exp3_attack.csv` (the log's summary line, which rounds the
percentage to a whole number, is shown in brackets). Median queries and mean time are *computed* from the
`queries` and `seconds` columns (`seconds` is already rounded to 0.01 s per trial by the script).
"Queries" counts every call of the target function (one sample = 50 calls), including the length step.
Random guessing would get 1/36 = 2.78 % of characters (log: "~3%").

| Target | Run | Success | Length found | Chars correct | Median queries | Mean time per trial (s) |
|---|---|---|---|---|---|---|
| naive_compare | 1 | 50/50 | 50/50 | 400/400 = 100.00 % [log: 100%] | 1340021.5 | 0.3700 |
| naive_compare | 2 | 50/50 | 50/50 | 400/400 = 100.00 % [log: 100%] | 1340021.5 | 0.3502 |
| builtin_eq | 1 | 0/50 | 50/50 | 9/400 = 2.25 % [log: 2%] | 2420036.0 | 0.0806 |
| builtin_eq | 2 | 0/50 | 50/50 | 13/400 = 3.25 % [log: 3%] | 2780036.0 | 0.0956 |
| hmac_compare_digest | 1 | 0/50 | 0/50 | 8/400 = 2.00 % [log: 2%] | 1970036.0 | 0.2632 |
| hmac_compare_digest | 2 | 0/50 | 0/50 | 8/400 = 2.00 % [log: 2%] | 3050036.0 | 0.3744 |

Extra detail (*computed*): queries ranged naive 1340001 to 1340036 (both runs), builtin_eq 1340036 to 3860036 (run 1)
and 1340036 to 3500036 (run 2), hmac 1340036 to 2960036 (run 1) and 1880036 to 3860036 (run 2).
`length_found` for hmac_compare_digest: run 1: 15 ×34, 14 ×13, 13 ×3; run 2: 15 ×33, 14 ×12, 13 ×5 (never 8, never 16).

## Surprising or inconsistent points

1. **hmac_compare_digest is flagged as leaking in Experiment 2**: 10/10 repeats in run 1 and 8/10 in run 2
   (run 2 repeats 0 and 5 stay below 4.5: t = 2.23 and 3.909). All 20 hmac t values are **positive**
   (fixed class slower), ranging from 2.23 to 13.97, while the median differences are only 0.0 to 0.4 ns.
   At the same time Experiment 1 shows no slope for hmac (-0.01 / 0.00 ns per char) and Experiment 3 recovers
   only 2.00 % of characters (chance level). So there is a small, repeatable fixed-vs-random difference that the
   t-test detects with 200000 samples per class, but it is far too small to exploit with these settings.
   These data cannot tell whether it comes from `hmac.compare_digest` / `.encode()` itself or from the harness
   (for example, the two classes' strings are built in different ways: fixed = `"".join(list(fixed))`,
   random = `"".join` over a NumPy array). This needs a careful explanation in the paper, or a follow-up test.
2. **builtin_eq Experiment 2 sign differs between runs**: run 1 t values have mixed signs (-1.768 to 1.036),
   while run 2 values are all positive (1.245 to 2.323). None crosses 4.5 in either run.
3. **Timer quantization**: the clock moves in ~10 ns steps, so per-call samples are quantized to ~0.2 ns
   (e.g. builtin_eq run 1 at k=0: q1 / median / q3 = 27.86 / 28.06 / 28.46 ns). The builtin_eq and hmac median differences
   (0.0, 0.02, 0.18, 0.2, 0.38, 0.4 ns) are 0 to 2 of these steps, so they cannot resolve anything below ~0.2 ns.
4. **Absolute levels shift a little between runs**: naive_compare slope 17.39 vs 18.11 ns/char, naive k=16
   477.69 vs 490.72 ns; hmac level 110.0 vs 108.42 ns; builtin_eq 28.06 vs 27.26 ns at k=0.
5. **naive_compare step from k=15 to k=16 is about half the others** (469.28 to 477.69 = 8.41 ns in run 1;
   482.1 to 490.72 = 8.62 ns in run 2). This follows from the code: at k=15 and k=16 both guesses compare all
   16 characters; only the final return differs. The fitted slope includes this point.
6. **builtin_eq exact match (k=16) is slightly faster** than every k < 16 in both runs (run 1: 27.46 vs 28.06 ns;
   run 2: 27.04 vs 27.26 to 27.44 ns).
7. **builtin_eq leaks the length**: the length step found the correct length in 50/50 trials in both runs
   (`==` returns before `memcmp` when lengths differ), but characters stay at chance level (2.25 % / 3.25 %).
8. **hmac length step never picked 16** (or 8): it chose 13, 14 or 15 in every trial (counts above).
9. **Experiment 3 does not attack the same secrets in both runs**: the first 51 of 150 rows (all 50 naive_compare
   trials and builtin_eq trial 0) have identical secrets; after that they differ, because the adaptive retries
   (which depend on timing) use the same random generator that makes the secrets. That is why naive_compare has
   the same median queries (1340021.5) in both runs: naive_compare never needed a retry (queries
   = 1340000 + 1 to 36 for the last character), and its secrets were identical.
10. **Exp3 retries differ between runs for builtin_eq and hmac**: hmac median queries 1970036.0 vs 3050036.0
    and mean time 0.2632 vs 0.3744 s. builtin_eq: 2420036.0 vs 2780036.0 and 0.0806 vs 0.0956 s. The number
    of rounds depends on noise, so these two columns are not stable for the non-leaking targets.

## Files

`results/` and `results_run2/` each contain: `machine.txt`, `log.txt`, `exp1_leakage.csv`, `exp1_leakage.png`,
`exp2_tvla.csv`, `exp2_tvla.png`, `exp3_attack.csv`. This file is `results/SUMMARY.md`.

---

## Experiment 4: control tests for the Experiment 2 hmac result (`src/exp4_control.py`)

Added by Mohammed after runs 1 and 2. Run unchanged with its defaults (`--length 16 --samples 200000 --batch 50
--repeats 10 --seed 4 --targets builtin_eq,hmac_compare_digest`), once into `results/` and once into `results_run2/`.
Run 1: 08:59:30 to 09:03:35, run 2: 09:03:35 to 09:07:41 (2026-11-27), both exit code 0. Conditions were checked
before and after: governor `performance` on all 12 CPUs (EPP `performance`), charger connected, mpv / Brave /
Nautilus / GNOME Software closed. Exp 4 does not write its own `machine.txt`. Same machine and venv as runs 1 and 2.

Tests (from the script's docstring): **C1** random vs random (nothing differs: any leak = harness bias),
**C2** fixed near-match (last char wrong) vs random (like Exp 2), **C3** fixed near-match vs fixed far-match
(first char wrong; both have exactly one wrong character, only its position differs).
`median_diff_ns` = median(class 0) − median(class 1), where class 0 is the first-named class (random / fixed near-match / fixed near-match).

Values from `exp4_control.csv` (repeats with |t| > 4.5 = `leak` column; ranges are min to max of the CSV values;
the last column is a *computed* count of t-value signs).

| Target | Test | Run | \|t\| > 4.5 | t range | Median diff range (ns) | t < 0 / t > 0 |
|---|---|---|---|---|---|---|
| builtin_eq | C1 random vs random | 1 | 0/10 | -2.054 to 1.365 | 0.0 to 0.0 | 5 / 5 |
| builtin_eq | C1 random vs random | 2 | 0/10 | -2.375 to 1.435 | 0.0 to 0.0 | 4 / 6 |
| builtin_eq | C2 fixed vs random | 1 | 0/10 | -2.523 to -0.525 | 0.0 to 0.0 | 10 / 0 |
| builtin_eq | C2 fixed vs random | 2 | 0/10 | -3.385 to 1.281 | -0.02 to 0.0 | 7 / 3 |
| builtin_eq | C3 fixed vs fixed | 1 | 0/10 | -1.63 to 1.972 | 0.0 to 0.0 | 6 / 4 |
| builtin_eq | C3 fixed vs fixed | 2 | 0/10 | -2.47 to 2.497 | -0.02 to 0.0 | 4 / 6 |
| hmac_compare_digest | C1 random vs random | 1 | 0/10 | -1.975 to 1.569 | 0.0 to 0.02 | 5 / 5 |
| hmac_compare_digest | C1 random vs random | 2 | 0/10 | -1.805 to 1.401 | 0.0 to 0.0 | 3 / 7 |
| hmac_compare_digest | **C2 fixed vs random** | 1 | **10/10** | -14.953 to -6.316 | -0.6 to -0.02 | 10 / 0 |
| hmac_compare_digest | **C2 fixed vs random** | 2 | **8/10** | -13.746 to -1.911 | -0.22 to 0.0 | 10 / 0 |
| hmac_compare_digest | C3 fixed vs fixed | 1 | 0/10 | -1.371 to 1.703 | 0.0 to 0.0 | 4 / 6 |
| hmac_compare_digest | C3 fixed vs fixed | 2 | 0/10 | -1.0 to 1.951 | -0.18 to 0.0 | 4 / 6 |

In run 2, the two hmac C2 repeats below the threshold are repeat 1 (t = -1.911) and repeat 2 (t = -4.209).

### Which reading the data support

- **hmac_compare_digest: "C1 clean, C2 leaks, C3 clean"**, in **both runs**. The docstring reads this as
  "time depends on input diversity (same vs varying data), not on matching". C1 being clean means two
  identically built classes do not produce a false leak. C3 being clean means that, with 200000 samples per class,
  there is no detectable dependence on how many leading characters match (15 vs 0), which is the property that
  matters for the attack.
- **builtin_eq: all clean** (0/10 in C1, C2 and C3, both runs). This agrees with Exp 2, where builtin_eq was
  also 0/10 in both runs, and with its flat Exp 1 slope.
- **The two runs agree** on these readings. Run 2's hmac C2 result is weaker (8/10 instead of 10/10), but in both
  runs all 10 hmac C2 t values have the same sign.

### Caveats to mention in the paper

1. **C2 construction is not fully identical (agreed with Mohammed before the runs).** The docstring says
   both classes are built the same way in all tests. That is true for the final step (every input is a fresh
   `"".join(list(s))`), but in C2 each random guess first goes through `random_guess()`, which creates a NumPy
   array and a temporary string that are then freed, while the fixed guess does not. So the C2 classes still
   differ in allocation history just before each final string is created. C1 and C3 do not have this problem.
   As a result, a "C2 leaks, C1 and C3 clean" outcome cannot separate "same vs varying content" from
   "leftover differences in how the inputs were allocated".
2. **The sign is opposite to Experiment 2.** In Exp 2 all 20 hmac t values (both runs) were **positive**
   (fixed class slower). In Exp 4 C2 all 20 hmac t values (both runs) are **negative** (fixed class faster).
   Between the two tests, the fixed class is built the same way (`"".join(list(...))`); what changed is that
   the random class gets an extra `"".join(list(...))` copy in Exp 4, and the secret is different (seed 2 vs
   seed 4). These data cannot separate those two changes. The flip fits the idea that the fixed-vs-random
   difference depends on how the inputs are created, not on the comparison of contents, but that is not proven here.
3. **The effect is at the timer's step size.** hmac C2 median differences are -0.6 to -0.02 ns (run 1) and
   -0.22 to 0.0 ns (run 2), i.e. 0 to 3 steps of the ~0.2 ns per-sample quantum (clock steps of ~10 ns,
   batch of 50). Example of the quantization: hmac C3 run 2, repeat 9 has t = 0.295 but median diff = -0.18 ns.
4. builtin_eq C2 in run 1 has all 10 t values negative (-2.523 to -0.525) but none past the threshold;
   in run 2 the signs are mixed (7 negative, 3 positive).

Files added: `results/exp4_control.csv`, `results/log_exp4.txt`, `results_run2/exp4_control.csv`,
`results_run2/log_exp4.txt`.
