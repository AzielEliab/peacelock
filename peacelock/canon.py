"""Canonical encoding for PeaceLock receipts (PL-WP-0.1).

Canonical encoding
------------------
UTF-8 JSON with **sorted keys** and **no extra whitespace**
(``separators=(",", ":")``, ``sort_keys=True``, ``ensure_ascii=False``).

``receipt_hash`` is **excluded** from the encoding. Constants on every
record: ``transcript=ABSENT``, ``counterfactual_act=ABSENT``,
``inferred_motive=ABSENT``.

Genesis ``prev_hash`` is 64 zero hex characters (GENESIS).

Algorithm: SHA-256 of the canonical UTF-8 bytes; digest is lowercase hex.
Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

SPEC = "PL-WP-0.1"
ABSENT = "ABSENT"
ACTOR_OPERATOR = "operator"
GENESIS_PREV_HASH = "0" * 64

MODES = ("SILENCE", "INACTION", "BOTH")
STATES = ("OPEN", "SEALED", "BROKEN")
EVENT_KINDS = ("QUIET", "UPLOAD_ENVELOPE")
DUTY_CHECKS = ("NONE", "ADVISORY", "HARD_DUTY")
ACT_CLASSES = (
    "reply",
    "file",
    "post",
    "call",
    "attend",
    "sign",
    "pay",
    "transfer",
    "delete",
    "other",
)
BREAK_REASONS = ("speech_occurred", "act_occurred", "operator_void", "duty_conflict")
NOTE_MAX = 140

# Hashed fields (lexicographic via sort_keys). receipt_hash is excluded.
HASH_FIELDS = (
    "act_class",
    "actor",
    "break_reason",
    "broken_at",
    "channel",
    "counterfactual_act",
    "date_stamp",
    "duty_check",
    "event_kind",
    "evidence_kind",
    "file_name",
    "file_sha256",
    "inferred_motive",
    "mode",
    "note",
    "opened_at",
    "pl_id",
    "prev_hash",
    "sealed_at",
    "spec",
    "state",
    "timestamp",
    "transcript",
    "window_end",
    "window_start",
)

FORBIDDEN_KEYS = frozenset(
    {
        "words",
        "draft",
        "paraphrase",
        "unspoken",
        "why",
        "motive",
        "transcript_text",
        "said",
        "would_have",
        "unspoken_words",
        "counterfactual",
        "inferred_why",
    }
)


def canonical_object(record: Mapping[str, Any]) -> dict[str, Any]:
    """Build the hashed object. Constants are forced ABSENT. Actor is operator."""
    payload: dict[str, Any] = {}
    for key in HASH_FIELDS:
        payload[key] = record.get(key, None)
    payload["spec"] = SPEC
    payload["transcript"] = ABSENT
    payload["counterfactual_act"] = ABSENT
    payload["inferred_motive"] = ABSENT
    payload["actor"] = ACTOR_OPERATOR
    return payload


def canonical_bytes(record: Mapping[str, Any]) -> bytes:
    """Return the PL-WP-0.1 canonical UTF-8 encoding (sorted keys, no extra space)."""
    payload = canonical_object(record)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return raw.encode("utf-8")


def digest(record: Mapping[str, Any]) -> str:
    """SHA-256 (lowercase hex) of ``canonical_bytes(record)``."""
    return hashlib.sha256(canonical_bytes(record)).hexdigest()
