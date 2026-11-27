"""Experiment 3 - End-to-end secret recovery.

The attacker can only call check(guess) and time it. Steps:
  1. Recover the LENGTH: the vulnerable function rejects wrong lengths
     instantly, so the correct length is the slowest one.
  2. Recover characters one position at a time: for each candidate
     character, time `known + c + padding` and keep the slowest.
  3. If the top-two candidates are too close, measure again and add the new
     samples to the old ones (adaptive), up to `retries` rounds.
The last character gives no timing signal (both outcomes do the same
work), so it is found by trying each candidate with the return value.

If step 1 fails, step 2 is still run, but with the TRUE length given to
the attacker. This lets us judge the character stage on its own for every
target. Such a trial never counts as an end-to-end success.

Run several trials with fresh random secrets per target and report
success rate, characters recovered, number of queries and time taken.
Output: results/exp3_attack.csv
"""
import argparse
import csv
import os
import string
import time

import numpy as np

from targets import TARGETS
from measure import interleaved

ALPHABET = list(string.ascii_lowercase + string.digits)


def typical_time(t):
    """Per-guess time estimate: the 10th percentile of its samples.

    Timing samples are often bimodal (the CPU changes frequency or the
    process moves between cores), and the median can jump between the two
    modes. A low percentile tracks the "undisturbed" time much more stably;
    this is the "box test" idea of Crosby et al. (2009).
    """
    return np.percentile(t, 10, axis=1)


def recover_length(fn, secret, max_len, n, batch, rng):
    guesses = ["a" * L for L in range(1, max_len + 1)]
    t = interleaved(fn, secret, guesses, n, batch, rng)
    return int(np.argmax(typical_time(t))) + 1, len(guesses) * n * batch


def recover_secret(fn, secret, length, n, batch, rng, margin=1.5, retries=3):
    known, queries = "", 0
    for pos in range(length - 1):
        pad = "#" * (length - pos - 1)          # '#' is never in ALPHABET
        cands = [known + c + pad for c in ALPHABET]
        t = np.empty((len(cands), 0))
        for _ in range(retries):
            new = interleaved(fn, secret, cands, n, batch, rng)
            t = np.hstack([t, new])             # keep earlier samples too
            queries += len(cands) * n * batch
            med = typical_time(t)
            order = np.argsort(med)[::-1]
            # Confidence check: gap between the slowest and second-slowest
            # candidate, in units of the typical spread of all candidates'
            # times (median absolute deviation). Most candidates are wrong
            # and should take the same time, so their spread is a robust
            # estimate of the measurement noise.
            spread = np.median(np.abs(med - np.median(med))) + 1e-9
            if (med[order[0]] - med[order[1]]) / spread > margin:
                break
        known += ALPHABET[order[0]]
    # last character: use the boolean result itself
    for c in ALPHABET:
        queries += 1
        if fn(secret, known + c):
            return known + c, queries
    return known + "?", queries


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--length", type=int, default=8)
    p.add_argument("--max-len", type=int, default=16)
    p.add_argument("--samples", type=int, default=100)
    p.add_argument("--batch", type=int, default=50)
    p.add_argument("--trials", type=int, default=50)
    p.add_argument("--seed", type=int, default=3)
    p.add_argument("--out", default="results")
    a = p.parse_args()
    if not 2 <= a.length <= a.max_len:
        p.error("need 2 <= --length <= --max-len")
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)

    rows = []
    for name, fn in TARGETS.items():
        for tr in range(a.trials):
            secret = "".join(rng.choice(ALPHABET, a.length))
            t0 = time.perf_counter()
            L, q_len = recover_length(fn, secret, a.max_len, a.samples,
                                      a.batch, rng)
            length_ok = L == len(secret)
            # If the length step failed, give the attacker the true length
            # so the character stage can still be evaluated on its own.
            guess, q = recover_secret(fn, secret, len(secret), a.samples,
                                      a.batch, rng)
            dt = time.perf_counter() - t0
            correct = sum(x == y for x, y in zip(secret, guess))
            ok = length_ok and guess == secret      # true end-to-end success
            rows.append([name, tr, secret, guess, L, length_ok,
                         correct, len(secret), ok, q_len + q, round(dt, 2)])
            note = ("" if length_ok else
                    f" (length step said {L}; true length given)")
            print(f"[exp3] {name:22s} trial {tr}: secret={secret} "
                  f"got={guess} {correct}/{len(secret)} chars "
                  f"{'SUCCESS' if ok else 'fail'}  {dt:.1f}s{note}")

    with open(os.path.join(a.out, "exp3_attack.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target", "trial", "secret", "recovered",
                    "length_found", "length_ok",
                    "chars_correct", "length", "success", "queries",
                    "seconds"])
        w.writerows(rows)

    print("\n[exp3] summary")
    for name in TARGETS:
        r = [x for x in rows if x[0] == name]
        chars = sum(x[6] for x in r) / max(1, sum(x[7] for x in r))
        print(f"  {name:22s} success {sum(x[8] for x in r)}/{len(r)}  "
              f"length found {sum(x[5] for x in r)}/{len(r)}  "
              f"chars correct {100 * chars:.0f}% "
              f"(random guessing ~{100 / len(ALPHABET):.0f}%)")


if __name__ == "__main__":
    main()
