"""Experiment 2 - Leakage detection with Welch's t-test (TVLA methodology).

Two classes of guesses are timed against each target, in random order:
  * fixed  : the secret with only the LAST character wrong (maximum match)
  * random : a fresh random guess of the same length for every sample
All guesses (both classes) are generated BEFORE timing starts, so the
measurement loop does exactly the same work for both classes.
If |t| > 4.5 the target is considered to leak (the standard TVLA threshold).
The test is repeated several times to show the verdict is stable.
Output: results/exp2_tvla.csv and results/exp2_tvla.png
"""
import argparse
import csv
import os
import string

import numpy as np
import matplotlib.pyplot as plt

from targets import TARGETS
from measure import measure_list, welch_t

ALPHABET = list(string.ascii_lowercase + string.digits)
THRESHOLD = 4.5


def random_guess(rng, length, avoid):
    """A random guess of `length` chars that is not one of `avoid`."""
    while True:
        g = "".join(rng.choice(ALPHABET, length))
        if g not in avoid:
            return g


def run_once(fn, secret, fixed, n, batch, rng):
    # Exactly n samples per class, in a random order.
    classes = np.repeat([0, 1], n)            # 0 = fixed, 1 = random
    rng.shuffle(classes)
    # Build every input first. Building a string inside the timing loop for
    # only one class would put extra work (and cache/branch-predictor noise)
    # right before the timed call of that class only, which could create a
    # fake difference even for a constant-time target.
    # The fixed class also gets a fresh copy (same content, new object) for
    # every sample: otherwise random guesses would be many different objects
    # spread over memory (often not in the CPU cache) while the fixed guess
    # would be one object that is always cached - a difference caused by our
    # harness, not by the target.
    inputs = ["".join(list(fixed)) if c == 0
              else random_guess(rng, len(secret), (secret, fixed))
              for c in classes]
    times = measure_list(fn, secret, inputs, batch)
    t_fixed, t_rand = times[classes == 0], times[classes == 1]
    # |t| grows with sqrt(n) for ANY real difference, however tiny, so we
    # also report the size of the difference (in ns) to interpret it.
    diff = np.median(t_fixed) - np.median(t_rand)
    return welch_t(t_fixed, t_rand), diff


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--length", type=int, default=16)
    p.add_argument("--samples", type=int, default=200000, help="per class")
    p.add_argument("--batch", type=int, default=50)
    p.add_argument("--repeats", type=int, default=10)
    p.add_argument("--seed", type=int, default=2)
    p.add_argument("--out", default="results")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)

    rng = np.random.default_rng(a.seed)
    secret = "".join(rng.choice(ALPHABET, a.length))
    fixed = secret[:-1] + ("x" if secret[-1] != "x" else "y")

    rows = []
    for name, fn in TARGETS.items():
        for r in range(a.repeats):
            t, diff = run_once(fn, secret, fixed, a.samples, a.batch, rng)
            leak = abs(t) > THRESHOLD
            rows.append([name, r, round(float(t), 3),
                         round(float(diff), 3), leak])
            print(f"[exp2] {name:22s} run {r}: t = {t:9.2f}  "
                  f"median diff = {diff:7.2f} ns  "
                  f"{'LEAK' if leak else 'no leak detected'}")

    with open(os.path.join(a.out, "exp2_tvla.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target", "repeat", "t_value", "median_diff_ns", "leak"])
        w.writerows(rows)

    names = list(TARGETS)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, n in enumerate(names):
        ts = [abs(r[2]) for r in rows if r[0] == n]
        ax.scatter([i] * len(ts), ts, s=40)
    ax.axhline(THRESHOLD, color="red", ls="--", label="|t| = 4.5 threshold")
    ax.set_yscale("symlog")
    ax.set_xticks(range(len(names)), names)
    ax.set_ylabel("|t| (Welch, symlog scale)")
    ax.set_title("Fixed-vs-random leakage test")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "exp2_tvla.png"), dpi=150)
    print("[exp2] done ->", a.out)


if __name__ == "__main__":
    main()
