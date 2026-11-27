"""Timing measurement helpers.

One *sample* = wall time of `batch` back-to-back calls, divided by `batch`.
Batching lifts the signal above the resolution of the clock, and the
garbage collector is paused so it cannot fire in the middle of a sample.
"""
import gc
import time

import numpy as np


def sample(fn, secret, guess, batch=50):
    """Average time (ns) of one call, measured over `batch` calls."""
    t0 = time.perf_counter_ns()
    for _ in range(batch):
        fn(secret, guess)
    return (time.perf_counter_ns() - t0) / batch


def measure_list(fn, secret, inputs, batch=50):
    """Time `fn(secret, g)` for every g in `inputs`, in the given order.

    All inputs must be built BEFORE calling this, so that nothing except the
    target function runs inside the timed region, and every input goes
    through exactly the same code path. The garbage collector is paused.

    Returns a numpy array of times in nanoseconds (one per input).
    """
    out = np.empty(len(inputs))
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for i, g in enumerate(inputs):
            out[i] = sample(fn, secret, g, batch)
    finally:
        if gc_was_enabled:
            gc.enable()
    return out


def interleaved(fn, secret, guesses, n_samples=200, batch=50, rng=None):
    """Measure several guesses in random interleaved order.

    Interleaving matters: if we measured guess A 200 times and then guess B
    200 times, a change in CPU frequency or background load between the two
    blocks would look like a timing difference. Shuffling spreads that drift
    evenly across all guesses.

    Returns an array of shape (len(guesses), n_samples) in nanoseconds.
    """
    rng = rng or np.random.default_rng()
    order = np.repeat(np.arange(len(guesses)), n_samples)
    rng.shuffle(order)
    times = measure_list(fn, secret, [guesses[i] for i in order], batch)
    out = np.empty((len(guesses), n_samples))
    for i in range(len(guesses)):
        out[i] = times[order == i]
    return out


def welch_t(a, b):
    """Welch's t-statistic between two sets of samples (TVLA style)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    return (a.mean() - b.mean()) / np.sqrt(va + vb)
