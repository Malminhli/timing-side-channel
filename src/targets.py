"""Target comparison functions studied in this project.

All three answer the same question: does `guess` equal `secret`?
They differ only in *how long* they take to answer.
"""
import hmac


def naive_compare(secret: str, guess: str) -> bool:
    """Character-by-character comparison with early exit (VULNERABLE).

    This is the pattern a beginner writes by hand. It returns as soon as
    it finds the first mismatch, so the running time grows with the number
    of correct leading characters, and it rejects wrong lengths instantly.
    """
    if len(secret) != len(guess):
        return False
    for a, b in zip(secret, guess):
        if a != b:
            return False
    return True


def builtin_eq(secret: str, guess: str) -> bool:
    """Python's built-in `==`.

    In CPython, str == str checks (1) identity, (2) length, (3) character
    width ("kind"), then calls C memcmp() on the raw bytes. memcmp is not
    constant-time, but it compares many bytes per instruction, so the extra
    cost per matching character is a fraction of a nanosecond - far below
    what we can resolve from Python. A wrong LENGTH, however, returns
    before memcmp is even called.
    """
    return secret == guess


def constant_time(secret: str, guess: str) -> bool:
    """hmac.compare_digest: designed to take time independent of content.

    Note: its running time still depends on the LENGTH of the guess (and
    the .encode() calls scale with length too) - the docs only promise it
    does not leak the content.
    """
    return hmac.compare_digest(secret.encode(), guess.encode())


TARGETS = {
    "naive_compare": naive_compare,
    "builtin_eq": builtin_eq,
    "hmac_compare_digest": constant_time,
}
