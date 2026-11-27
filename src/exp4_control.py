"""Experiment 4 - Control tests for the Experiment 2 result.

In Experiment 2, hmac.compare_digest crossed |t| = 4.5 with a median
difference below 0.5 ns. That can mean two different things:
  (a) the target's time really depends on the content of the guess, or
  (b) the test harness itself creates a tiny difference between the classes
      (for example, one fixed string vs many different strings, or strings
      built in different ways end up in different memory/cache states).

To separate them, we run three tests per target. In ALL of them both
classes are built the same way ("".join(list(s)) -> a fresh object per
sample), all inputs are built before timing, and classes are shuffled.

  C1  random vs random   : both classes are random guesses.
                           Nothing differs -> any "leak" here is harness bias.
  C2  fixed vs random    : like Experiment 2 (near-match vs random guesses),
                           but with identical construction for both classes.
  C3  fixed vs fixed     : near-match (last char wrong) vs a fixed far-match
                           (first char wrong). Both classes are ONE repeated
                           content, so data diversity is equal; only the
                           number of matching characters differs.

Reading the results:
  C1 leaks                    -> harness bias, Exp 2 verdict is not reliable
  C1 clean, C3 leaks          -> time depends on how many chars match
  C1 clean, C2 leaks, C3 clean -> time depends on input diversity
                                  (same vs varying data), not on matching
  all clean                   -> the Exp 2 result came from construction
Output: results/exp4_control.csv
"""
import argparse
import csv
import os
import string

import numpy as np

from targets import TARGETS
from measure import measure_list, welch_t

ALPHABET = list(string.ascii_lowercase + string.digits)
THRESHOLD = 4.5


def copy(s):
    """Same content, new string object, built the same way for every input."""
    return "".join(list(s))


def random_guess(rng, length, avoid):
    while True:
        g = "".join(rng.choice(ALPHABET, length))
        if g not in avoid:
            return g


def run_once(fn, secret, make0, make1, n, batch, rng):
    classes = np.repeat([0, 1], n)
    rng.shuffle(classes)
    inputs = [copy(make0()) if c == 0 else copy(make1()) for c in classes]
    times = measure_list(fn, secret, inputs, batch)
    a, b = times[classes == 0], times[classes == 1]
    return welch_t(a, b), np.median(a) - np.median(b)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--length", type=int, default=16)
    p.add_argument("--samples", type=int, default=200000, help="per class")
    p.add_argument("--batch", type=int, default=50)
    p.add_argument("--repeats", type=int, default=10)
    p.add_argument("--seed", type=int, default=4)
    p.add_argument("--targets", default="builtin_eq,hmac_compare_digest")
    p.add_argument("--out", default="results")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)

    rng = np.random.default_rng(a.seed)
    secret = "".join(rng.choice(ALPHABET, a.length))
    near = secret[:-1] + ("x" if secret[-1] != "x" else "y")   # 15 match
    far = ("x" if secret[0] != "x" else "y") + secret[1:]       # 0 match
    avoid = (secret, near, far)
    rnd = lambda: random_guess(rng, a.length, avoid)

    tests = {
        "C1_random_vs_random": (rnd, rnd),
        "C2_fixed_vs_random": (lambda: near, rnd),
        "C3_fixed_vs_fixed": (lambda: near, lambda: far),
    }

    rows = []
    for name in a.targets.split(","):
        fn = TARGETS[name]
        for test, (m0, m1) in tests.items():
            for r in range(a.repeats):
                t, diff = run_once(fn, secret, m0, m1, a.samples, a.batch, rng)
                leak = abs(t) > THRESHOLD
                rows.append([name, test, r, round(float(t), 3),
                             round(float(diff), 3), leak])
                print(f"[exp4] {name:20s} {test:20s} run {r}: t = {t:8.2f}  "
                      f"median diff = {diff:6.2f} ns  "
                      f"{'LEAK' if leak else 'no leak detected'}", flush=True)

    with open(os.path.join(a.out, "exp4_control.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target", "test", "repeat", "t_value", "median_diff_ns",
                    "leak"])
        w.writerows(rows)

    print("\n[exp4] summary (repeats with |t| > 4.5)")
    for name in a.targets.split(","):
        for test in tests:
            r = [x for x in rows if x[0] == name and x[1] == test]
            ts = [x[3] for x in r]
            print(f"  {name:20s} {test:20s} {sum(x[5] for x in r)}/{len(r)}"
                  f"   t from {min(ts):.2f} to {max(ts):.2f}")
    print("[exp4] done ->", a.out)


if __name__ == "__main__":
    main()
