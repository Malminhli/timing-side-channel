"""Experiment 1 - Leakage characterisation.

Question: does the response time depend on how many leading characters
of the guess are correct?

For k = 0..L we build a guess whose first k characters match the secret
and the rest are wrong, then time it against all three targets.
Output: results/exp1_leakage.csv and results/exp1_leakage.png
"""
import argparse
import csv
import os
import string

import numpy as np
import matplotlib.pyplot as plt

from targets import TARGETS
from measure import interleaved

ALPHABET = string.ascii_lowercase + string.digits


def wrong_char(c):
    return "x" if c != "x" else "y"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--length", type=int, default=16)
    p.add_argument("--samples", type=int, default=10000)
    p.add_argument("--batch", type=int, default=50)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--out", default="results")
    a = p.parse_args()
    if a.length < 2:
        p.error("--length must be at least 2")
    os.makedirs(a.out, exist_ok=True)

    rng = np.random.default_rng(a.seed)
    secret = "".join(rng.choice(list(ALPHABET), a.length))
    guesses = []
    for k in range(a.length + 1):
        chars = list(secret[:k]) + [wrong_char(c) for c in secret[k:]]
        guesses.append("".join(chars))
    # Careful: for k = length, `secret[:k] + ""` would return the SAME
    # object as `secret`, and CPython's == has an "is it the same object?"
    # shortcut. That would make builtin_eq look artificially fast at the
    # last point. "".join(list) always builds a new string object.
    assert all(g is not secret for g in guesses)

    rows = []
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, (name, fn) in zip(axes, TARGETS.items()):
        print(f"[exp1] measuring {name} ...")
        t = interleaved(fn, secret, guesses, a.samples, a.batch, rng)
        med = np.median(t, axis=1)
        q1, q3 = np.percentile(t, [25, 75], axis=1)
        for k in range(a.length + 1):
            rows.append([name, k, med[k], q1[k], q3[k]])
        ax.plot(range(a.length + 1), med, "o-")
        ax.fill_between(range(a.length + 1), q1, q3, alpha=0.25)
        ax.set_title(name)
        ax.set_xlabel("correct leading characters (k)")
        ax.set_ylabel("time per call (ns, median + IQR)")
        ax.grid(alpha=0.3)
        slope = np.polyfit(range(a.length + 1), med, 1)[0]
        print(f"         slope = {slope:.2f} ns per correct char")

    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "exp1_leakage.png"), dpi=150)
    with open(os.path.join(a.out, "exp1_leakage.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target", "k", "median_ns", "q1_ns", "q3_ns"])
        w.writerows(rows)
    print("[exp1] done ->", a.out)


if __name__ == "__main__":
    main()
