"""Append-only PeaceLock ledger (hash-chained JSONL lattice).

``ledger.append(...)`` only. No modify, no delete. OPEN → SEALED →
optional BROKEN. A break appends BROKEN; the original seal stays.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

from peacelock.canon import GENESIS_PREV_HASH
from peacelock.errors import AppendOnlyError, HardDutyError, LedgerError
from peacelock.receipt import (
    Receipt,
    extend_forward_only,
    file_sha256,
    new_pl_id,
    open_clock_or_later,
    refuse_hard_duty,
    utc_date,
    utc_now,
)

DEFAULT_LEDGER_NAME = "peacelock_ledger.jsonl"


def default_ledger_path() -> Path:
    env = os.environ.get("PEACELOCK_LEDGER")
    if env:
        return Path(env)
    return Path(DEFAULT_LEDGER_NAME)


@dataclass(frozen=True)
class VerifyResult:
    """Result of walking a ledger: hashes and links, nothing interpretive."""

    ok: bool
    length: int
    first_hash: str | None
    last_hash: str | None
    errors: list[str] = field(default_factory=list)


def _receipt_json_line(receipt: Receipt) -> str:
    return json.dumps(receipt.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _append_line(path: Path, receipt: Receipt) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(_receipt_json_line(receipt))
        fh.write("\n")
        fh.flush()


class Ledger:
    """In-memory and/or JSONL-backed append-only PeaceLock lattice."""

    def __init__(
        self,
        receipts: Sequence[Receipt] | None = None,
        path: str | Path | None = None,
    ) -> None:
        self._receipts: tuple[Receipt, ...] = tuple(receipts or ())
        self._path: Path | None = Path(path) if path is not None else None

    @property
    def path(self) -> Path | None:
        return self._path

    def __len__(self) -> int:
        return len(self._receipts)

    def __iter__(self) -> Iterator[Receipt]:
        return iter(self._receipts)

    def __getitem__(self, index: int) -> Receipt:
        return self._receipts[index]

    def __bool__(self) -> bool:
        return bool(self._receipts)

    def _refuse(self, action: str) -> None:
        raise AppendOnlyError(
            f"cannot {action}: PeaceLock is append-only (I7); "
            "record a new receipt instead"
        )

    def pop(self, *args: object, **kwargs: object) -> None:
        self._refuse("pop")

    def insert(self, *args: object, **kwargs: object) -> None:
        self._refuse("insert")

    def remove(self, *args: object, **kwargs: object) -> None:
        self._refuse("remove")

    def clear(self) -> None:
        self._refuse("clear")

    def reverse(self) -> None:
        self._refuse("reverse")

    def __setitem__(self, *args: object, **kwargs: object) -> None:
        self._refuse("replace")

    def __delitem__(self, *args: object, **kwargs: object) -> None:
        self._refuse("delete")

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Ledger":
        path = Path(path) if path is not None else default_ledger_path()
        receipts: list[Receipt] = []
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                receipts.append(Receipt.from_dict(json.loads(line)))
        return cls(receipts, path=path)

    def _tip_hash(self) -> str:
        return self._receipts[-1].receipt_hash if self._receipts else GENESIS_PREV_HASH

    def _commit(self, receipt: Receipt) -> Receipt:
        if self._path is not None:
            _append_line(self._path, receipt)
        self._receipts = self._receipts + (receipt,)
        return receipt

    def latest_for(self, pl_id: str, *, state: str | None = None, event_kind: str = "QUIET") -> Receipt | None:
        found: Receipt | None = None
        for rec in self._receipts:
            if rec.pl_id != pl_id:
                continue
            if rec.event_kind != event_kind:
                continue
            if state is not None and rec.state != state:
                continue
            found = rec
        return found

    def open(
        self,
        *,
        mode: str,
        channel: str,
        act_class: str,
        duty_check: str = "NONE",
        note: str = "",
        window_start: str | None = None,
        window_end: str | None = None,
        pl_id: str | None = None,
        opened_at: str | None = None,
    ) -> Receipt:
        """Open a quiet window. I6 HARD_DUTY refuses and writes nothing."""
        refuse_hard_duty(duty_check, "open")
        opened = opened_at or utc_now()
        start = open_clock_or_later(window_start, opened)
        end = extend_forward_only(None, window_end, start)
        receipt = Receipt.create(
            event_kind="QUIET",
            pl_id=pl_id or new_pl_id(),
            mode=mode,
            state="OPEN",
            window_start=start,
            window_end=end,
            channel=channel,
            act_class=act_class,
            duty_check=duty_check,
            note=note,
            prev_hash=self._tip_hash(),
            opened_at=opened,
        )
        return self._commit(receipt)

    def seal(
        self,
        *,
        pl_id: str,
        duty_check: str | None = None,
        note: str = "",
        window_end: str | None = None,
        sealed_at: str | None = None,
    ) -> Receipt:
        """Seal an OPEN window. I6 HARD_DUTY refuses and writes nothing."""
        current = self.latest_for(pl_id, event_kind="QUIET")
        if current is None or current.state != "OPEN":
            raise LedgerError(f"no OPEN window for {pl_id}; open first")
        check = duty_check or current.duty_check
        refuse_hard_duty(check, "seal")
        sealed = sealed_at or utc_now()
        start = current.window_start or current.opened_at or sealed
        proposed_end = window_end
        if proposed_end is None:
            proposed_end = sealed if sealed >= start else start
        end = extend_forward_only(current.window_end, proposed_end, start)
        receipt = Receipt.create(
            event_kind="QUIET",
            pl_id=current.pl_id,
            mode=current.mode,
            state="SEALED",
            window_start=current.window_start,
            window_end=end,
            channel=current.channel,
            act_class=current.act_class,
            duty_check=check,
            note=note or current.note,
            prev_hash=self._tip_hash(),
            opened_at=current.opened_at,
            sealed_at=sealed,
        )
        return self._commit(receipt)

    def break_window(
        self,
        *,
        pl_id: str,
        reason: str,
        note: str = "",
        broken_at: str | None = None,
    ) -> Receipt:
        """I8: append BROKEN. The original SEALED receipt stays."""
        current = self.latest_for(pl_id, event_kind="QUIET")
        if current is None:
            raise LedgerError(f"no quiet window for {pl_id}")
        if current.state == "OPEN":
            raise LedgerError("I7: break requires SEALED (OPEN → SEALED → optional BROKEN)")
        if current.state == "BROKEN":
            raise LedgerError(f"{pl_id} is already BROKEN; original seal stays")
        broken = broken_at or utc_now()
        receipt = Receipt.create(
            event_kind="QUIET",
            pl_id=current.pl_id,
            mode=current.mode,
            state="BROKEN",
            window_start=current.window_start,
            window_end=current.window_end,
            channel=current.channel,
            act_class=current.act_class,
            duty_check=current.duty_check,
            note=note or current.note,
            prev_hash=self._tip_hash(),
            opened_at=current.opened_at,
            sealed_at=current.sealed_at,
            broken_at=broken,
            break_reason=reason,
        )
        return self._commit(receipt)

    def upload_envelope(
        self,
        *,
        file_path: str | Path | None = None,
        file_sha256_hex: str | None = None,
        file_name: str | None = None,
        pl_id: str | None = None,
        note: str = "",
        timestamp: str | None = None,
        date_stamp: str | None = None,
    ) -> Receipt:
        """Attach operator-declared evidence metadata. File bytes may be hashed.

        Does not store unspoken words or transcripts (I1–I3).
        """
        ts = timestamp or utc_now()
        name = file_name
        digest_hex = file_sha256_hex
        if file_path is not None:
            path = Path(file_path)
            if not path.is_file():
                raise LedgerError(f"not found: {path}")
            name = name or path.name
            digest_hex = digest_hex or file_sha256(path)
        if not digest_hex or not name:
            raise LedgerError("upload envelope requires file bytes hash and basename")
        attach = pl_id
        if attach is None:
            quiet = None
            for rec in reversed(self._receipts):
                if rec.event_kind == "QUIET":
                    quiet = rec
                    break
            attach = quiet.pl_id if quiet is not None else new_pl_id()
        receipt = Receipt.create(
            event_kind="UPLOAD_ENVELOPE",
            pl_id=attach,
            duty_check="NONE",
            note=note,
            prev_hash=self._tip_hash(),
            file_sha256=digest_hex,
            file_name=name,
            timestamp=ts,
            date_stamp=date_stamp or utc_date(ts),
            evidence_kind="operator_declared",
        )
        return self._commit(receipt)

    def verify(self) -> VerifyResult:
        """Walk the chain. Check each hash and each consecutive prev_hash link."""
        errors: list[str] = []
        n = len(self._receipts)
        first = self._receipts[0].receipt_hash if n else None
        last = self._receipts[-1].receipt_hash if n else None

        for i, rec in enumerate(self._receipts):
            expected = rec.recomputed_hash()
            if rec.receipt_hash != expected:
                errors.append(
                    f"index {i}: stored receipt_hash {rec.receipt_hash} != recomputed {expected}"
                )
            if rec.transcript != "ABSENT" or rec.counterfactual_act != "ABSENT" or rec.inferred_motive != "ABSENT":
                errors.append(f"index {i}: I1–I3 leakage (ABSENT constants violated)")
            if rec.actor != "operator":
                errors.append(f"index {i}: I4 actor must be operator")
            if i == 0:
                if rec.prev_hash != GENESIS_PREV_HASH:
                    errors.append(
                        f"index 0: prev_hash {rec.prev_hash} != GENESIS zeros"
                    )
                continue
            prev = self._receipts[i - 1]
            if rec.prev_hash != prev.receipt_hash:
                errors.append(
                    f"index {i}: prev_hash {rec.prev_hash} != previous.receipt_hash {prev.receipt_hash}"
                )

        return VerifyResult(
            ok=not errors,
            length=n,
            first_hash=first,
            last_hash=last,
            errors=errors,
        )

    def show(self, pl_id: str | None = None) -> list[Receipt]:
        if pl_id is None:
            return list(self._receipts)
        return [r for r in self._receipts if r.pl_id == pl_id]

    def export_jsonl(self) -> str:
        return "".join(_receipt_json_line(r) + "\n" for r in self._receipts)

    def import_rows(self, rows: Sequence[Mapping[str, Any]]) -> "Ledger":
        """Replace in-memory view from imported rows. Does not rewrite the file."""
        receipts = [Receipt.from_dict(row) for row in rows]
        self._receipts = tuple(receipts)
        return self


# Alias used by TemporalLock-shaped callers.
Chain = Ledger
