"""Hashing helpers for PeaceLock.

Re-exports canonical encoding from ``canon`` so callers can use
``peacelock.hashing.canonical_bytes`` and ``peacelock.hashing.digest``.
Stdlib ``hashlib`` only; no extra crypto packages.
"""

from __future__ import annotations

from peacelock.canon import (
    ABSENT,
    ACTOR_OPERATOR,
    GENESIS_PREV_HASH,
    HASH_FIELDS,
    SPEC,
    canonical_bytes,
    canonical_object,
    digest,
)

__all__ = [
    "ABSENT",
    "ACTOR_OPERATOR",
    "GENESIS_PREV_HASH",
    "HASH_FIELDS",
    "SPEC",
    "canonical_bytes",
    "canonical_object",
    "digest",
]
