"""Immutable PeaceLock receipt (quiet window or upload envelope).

A receipt records chosen silence / chosen inaction, or an operator-declared
evidence envelope. It is not a transcript, not a motive, and not a
counterfactual act. Corrections are new receipts; this object cannot be edited.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from peacelock.canon import (
    ABSENT,
    ACT_CLASSES,
    ACTOR_OPERATOR,
    BREAK_REASONS,
    DUTY_CHECKS,
    EVENT_KINDS,
    FORBIDDEN_KEYS,
    GENESIS_PREV_HASH,
    MODES,
    NOTE_MAX,
    SPEC,
    STATES,
    digest,
)
from peacelock.errors import AppendOnlyError, HardDutyError, InvariantError, ReceiptError

_HEX = set("0123456789abcdef")
_ISO_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_PL_ID = re.compile(r"^pl_[0-9a-f]{16}$")


def utc_now() -> str:
    """Operator-clock 'now' as UTC ISO-8601 with a trailing Z, second precision."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def utc_date(ts: str | None = None) -> str:
    """Calendar date stamp (YYYY-MM-DD) from an ISO timestamp or today UTC."""
    if ts:
        return parse_iso(ts).date().isoformat()
    return datetime.now(timezone.utc).date().isoformat()


def parse_iso(ts: str) -> datetime:
    if not isinstance(ts, str) or not _ISO_Z.match(ts):
        raise ReceiptError("timestamp must be UTC ISO-8601 with trailing Z (second precision)")
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def new_pl_id() -> str:
    return "pl_" + secrets.token_hex(8)


def file_sha256(path: str | Path) -> str:
    digest_obj = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest_obj.update(chunk)
    return digest_obj.hexdigest()


def _require_str(name: str, value: Any) -> str:
    if not isinstance(value, str):
        raise ReceiptError(f"{name} must be a string")
    return value


def _optional_str(name: str, value: Any) -> str | None:
    if value is None or value == "":
        return None
    return _require_str(name, value)


def _closed(name: str, value: Any, allowed: tuple[str, ...]) -> str:
    text = _require_str(name, value)
    if text not in allowed:
        raise ReceiptError(f"{name} must be one of {allowed}")
    return text


def _optional_closed(name: str, value: Any, allowed: tuple[str, ...]) -> str | None:
    if value is None or value == "":
        return None
    return _closed(name, value, allowed)


def _hex64(name: str, value: Any) -> str:
    text = _require_str(name, value).strip().lower()
    if len(text) != 64 or any(c not in _HEX for c in text):
        raise ReceiptError(f"{name} must be 64 lowercase hex characters")
    return text


def validate_note(note: Any) -> str:
    if note is None:
        return ""
    text = _require_str("note", note)
    if len(text) > NOTE_MAX:
        raise InvariantError(f"I3: note must be ≤{NOTE_MAX} characters")
    lowered = text.lower()
    if lowered.startswith("because ") or lowered.startswith("why ") or " why:" in f" {lowered}":
        raise InvariantError("I3: note must not infer motive (no why)")
    return text


def validate_pl_id(pl_id: Any) -> str:
    text = _require_str("pl_id", pl_id)
    if not _PL_ID.match(text):
        raise ReceiptError("pl_id must match pl_[0-9a-f]{16}")
    return text


def validate_iso_or_none(name: str, value: Any) -> str | None:
    if value is None or value == "":
        return None
    parse_iso(_require_str(name, value))
    return value


def assert_no_leakage(data: Mapping[str, Any]) -> None:
    """I1–I3: refuse transcripts, counterfactual acts, inferred motives."""
    extra = set(data.keys()) & FORBIDDEN_KEYS
    if extra:
        raise InvariantError(f"I1–I3: forbidden keys {sorted(extra)}")
    for key in ("transcript", "counterfactual_act", "inferred_motive"):
        val = data.get(key, ABSENT)
        if val not in (None, "", ABSENT):
            raise InvariantError(f"I1–I3: {key} must be ABSENT, not a {key}")
    if data.get("actor") not in (None, "", ACTOR_OPERATOR):
        raise InvariantError("I4: actor must be operator")


def refuse_hard_duty(duty_check: str, action: str) -> None:
    if duty_check == "HARD_DUTY":
        raise HardDutyError(
            f"I6: HARD_DUTY refuses {action}; write nothing. "
            "PeaceLock is not a gag-order kit and cannot bypass a hard duty."
        )


@dataclass
class Receipt:
    """Frozen PeaceLock receipt. Quiet window or upload envelope."""

    spec: str
    pl_id: str
    mode: str | None
    state: str | None
    window_start: str | None
    window_end: str | None
    channel: str | None
    act_class: str | None
    duty_check: str
    actor: str
    note: str
    prev_hash: str
    opened_at: str | None
    sealed_at: str | None
    broken_at: str | None
    break_reason: str | None
    transcript: str
    counterfactual_act: str
    inferred_motive: str
    receipt_hash: str
    event_kind: str = "QUIET"
    file_sha256: str | None = None
    file_name: str | None = None
    timestamp: str | None = None
    date_stamp: str | None = None
    evidence_kind: str | None = None
    _frozen: bool = field(default=False, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "spec", SPEC)
        object.__setattr__(self, "transcript", ABSENT)
        object.__setattr__(self, "counterfactual_act", ABSENT)
        object.__setattr__(self, "inferred_motive", ABSENT)
        object.__setattr__(self, "actor", ACTOR_OPERATOR)
        object.__setattr__(self, "pl_id", validate_pl_id(self.pl_id))
        object.__setattr__(self, "event_kind", _closed("event_kind", self.event_kind, EVENT_KINDS))
        object.__setattr__(self, "duty_check", _closed("duty_check", self.duty_check or "NONE", DUTY_CHECKS))
        object.__setattr__(self, "note", validate_note(self.note))
        object.__setattr__(self, "prev_hash", _hex64("prev_hash", self.prev_hash))
        object.__setattr__(self, "receipt_hash", _hex64("receipt_hash", self.receipt_hash))
        if self.event_kind == "QUIET":
            object.__setattr__(self, "mode", _closed("mode", self.mode, MODES))
            object.__setattr__(self, "state", _closed("state", self.state, STATES))
            object.__setattr__(self, "act_class", _closed("act_class", self.act_class, ACT_CLASSES))
            object.__setattr__(self, "channel", _require_str("channel", self.channel or ""))
            if self.channel.strip() == "":
                raise ReceiptError("channel must be a non-empty string")
            object.__setattr__(self, "window_start", validate_iso_or_none("window_start", self.window_start))
            object.__setattr__(self, "window_end", validate_iso_or_none("window_end", self.window_end))
            object.__setattr__(self, "opened_at", validate_iso_or_none("opened_at", self.opened_at))
            object.__setattr__(self, "sealed_at", validate_iso_or_none("sealed_at", self.sealed_at))
            object.__setattr__(self, "broken_at", validate_iso_or_none("broken_at", self.broken_at))
            object.__setattr__(self, "break_reason", _optional_closed("break_reason", self.break_reason, BREAK_REASONS))
            if self.state == "OPEN" and not self.opened_at:
                raise ReceiptError("OPEN receipt requires opened_at")
            if self.state == "SEALED" and not self.sealed_at:
                raise ReceiptError("SEALED receipt requires sealed_at")
            if self.state == "BROKEN" and (not self.broken_at or not self.break_reason):
                raise ReceiptError("BROKEN receipt requires broken_at and break_reason")
        else:
            object.__setattr__(self, "file_sha256", _hex64("file_sha256", self.file_sha256))
            name = _require_str("file_name", self.file_name or "")
            if "/" in name or "\\" in name or name.strip() == "":
                raise ReceiptError("file_name must be a basename (no path)")
            object.__setattr__(self, "file_name", name)
            object.__setattr__(self, "timestamp", validate_iso_or_none("timestamp", self.timestamp))
            stamp = _optional_str("date_stamp", self.date_stamp)
            if stamp and not _DATE.match(stamp):
                raise ReceiptError("date_stamp must be YYYY-MM-DD")
            object.__setattr__(self, "date_stamp", stamp or utc_date(self.timestamp))
            object.__setattr__(self, "evidence_kind", _require_str("evidence_kind", self.evidence_kind or "operator_declared"))
            object.__setattr__(self, "mode", _optional_closed("mode", self.mode, MODES))
            object.__setattr__(self, "state", _optional_closed("state", self.state, STATES))
            object.__setattr__(self, "act_class", _optional_closed("act_class", self.act_class, ACT_CLASSES))
            object.__setattr__(self, "channel", _optional_str("channel", self.channel))
            object.__setattr__(self, "window_start", validate_iso_or_none("window_start", self.window_start))
            object.__setattr__(self, "window_end", validate_iso_or_none("window_end", self.window_end))
            object.__setattr__(self, "opened_at", validate_iso_or_none("opened_at", self.opened_at))
            object.__setattr__(self, "sealed_at", validate_iso_or_none("sealed_at", self.sealed_at))
            object.__setattr__(self, "broken_at", validate_iso_or_none("broken_at", self.broken_at))
            object.__setattr__(self, "break_reason", _optional_closed("break_reason", self.break_reason, BREAK_REASONS))
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AppendOnlyError("receipts cannot be modified; append a new receipt")
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        raise AppendOnlyError("receipts cannot be deleted; append a new receipt")

    def __hash__(self) -> int:  # type: ignore[override]
        return hash(self.receipt_hash)

    @property
    def hash(self) -> str:
        """Alias used by the lattice walker (prev_hash → receipt_hash)."""
        return self.receipt_hash

    def hash_fields(self) -> dict[str, Any]:
        return {
            "spec": SPEC,
            "pl_id": self.pl_id,
            "mode": self.mode,
            "state": self.state,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "channel": self.channel,
            "act_class": self.act_class,
            "duty_check": self.duty_check,
            "actor": ACTOR_OPERATOR,
            "note": self.note,
            "prev_hash": self.prev_hash,
            "opened_at": self.opened_at,
            "sealed_at": self.sealed_at,
            "broken_at": self.broken_at,
            "break_reason": self.break_reason,
            "transcript": ABSENT,
            "counterfactual_act": ABSENT,
            "inferred_motive": ABSENT,
            "event_kind": self.event_kind,
            "file_sha256": self.file_sha256,
            "file_name": self.file_name,
            "timestamp": self.timestamp,
            "date_stamp": self.date_stamp,
            "evidence_kind": self.evidence_kind,
        }

    def recomputed_hash(self) -> str:
        return digest(self.hash_fields())

    def hash_ok(self) -> bool:
        return self.recomputed_hash() == self.receipt_hash

    def to_dict(self) -> dict[str, Any]:
        body = self.hash_fields()
        body["receipt_hash"] = self.receipt_hash
        return body

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Receipt":
        assert_no_leakage(data)
        missing = [k for k in ("pl_id", "prev_hash", "receipt_hash") if k not in data]
        if missing:
            raise ReceiptError(f"receipt missing fields: {missing}")
        return cls(
            spec=SPEC,
            pl_id=data["pl_id"],
            mode=data.get("mode"),
            state=data.get("state"),
            window_start=data.get("window_start"),
            window_end=data.get("window_end"),
            channel=data.get("channel"),
            act_class=data.get("act_class"),
            duty_check=data.get("duty_check") or "NONE",
            actor=ACTOR_OPERATOR,
            note=data.get("note") or "",
            prev_hash=data["prev_hash"],
            opened_at=data.get("opened_at"),
            sealed_at=data.get("sealed_at"),
            broken_at=data.get("broken_at"),
            break_reason=data.get("break_reason"),
            transcript=ABSENT,
            counterfactual_act=ABSENT,
            inferred_motive=ABSENT,
            receipt_hash=data["receipt_hash"],
            event_kind=data.get("event_kind") or "QUIET",
            file_sha256=data.get("file_sha256"),
            file_name=data.get("file_name"),
            timestamp=data.get("timestamp"),
            date_stamp=data.get("date_stamp"),
            evidence_kind=data.get("evidence_kind"),
        )

    @classmethod
    def create(cls, **fields: Any) -> "Receipt":
        """Mint a receipt, forcing ABSENT constants and computing receipt_hash."""
        assert_no_leakage(fields)
        duty = fields.get("duty_check") or "NONE"
        payload = {
            "spec": SPEC,
            "pl_id": fields["pl_id"],
            "mode": fields.get("mode"),
            "state": fields.get("state"),
            "window_start": fields.get("window_start"),
            "window_end": fields.get("window_end"),
            "channel": fields.get("channel"),
            "act_class": fields.get("act_class"),
            "duty_check": duty,
            "actor": ACTOR_OPERATOR,
            "note": fields.get("note") or "",
            "prev_hash": fields.get("prev_hash") or GENESIS_PREV_HASH,
            "opened_at": fields.get("opened_at"),
            "sealed_at": fields.get("sealed_at"),
            "broken_at": fields.get("broken_at"),
            "break_reason": fields.get("break_reason"),
            "transcript": ABSENT,
            "counterfactual_act": ABSENT,
            "inferred_motive": ABSENT,
            "event_kind": fields.get("event_kind") or "QUIET",
            "file_sha256": fields.get("file_sha256"),
            "file_name": fields.get("file_name"),
            "timestamp": fields.get("timestamp"),
            "date_stamp": fields.get("date_stamp"),
            "evidence_kind": fields.get("evidence_kind"),
        }
        rec_hash = digest(payload)
        return cls(receipt_hash=rec_hash, **payload)


def open_clock_or_later(window_start: str | None, opened_at: str) -> str:
    """I5: window_start is the open clock or later. No backdated quiet."""
    clock = parse_iso(opened_at)
    if window_start is None or window_start == "":
        return opened_at
    start = parse_iso(window_start)
    if start < clock:
        raise InvariantError("I5: no backdated quiet — window_start must be open clock or later")
    return window_start


def extend_forward_only(previous_end: str | None, window_end: str | None, window_start: str) -> str | None:
    """I5: window_end may only move forward."""
    if window_end is None or window_end == "":
        return previous_end
    end = parse_iso(window_end)
    start = parse_iso(window_start)
    if end < start:
        raise InvariantError("I5: window_end must be on or after window_start")
    if previous_end:
        prev = parse_iso(previous_end)
        if end < prev:
            raise InvariantError("I5: extend forward only — window_end cannot move backward")
    return window_end
