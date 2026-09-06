"""Temporal hash-chained lattice helpers for PeaceLock.

Each open / seal / break / upload-envelope event chains
``prev_hash → receipt_hash``. Verify walks the chain.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from peacelock.chain import Ledger, VerifyResult
from peacelock.receipt import Receipt

HONEST_SCOPE = (
    "THIS IS: chosen silence / chosen inaction as a first-class receipt "
    "(PL-WP-0.1). THIS IS NOT: a gag-order kit, a wiretap, or third-party "
    "binding. HARD_DUTY cannot be bypassed. Author Aziel Eliab."
)
ROLE = "chosen silence / chosen inaction receipt lattice"


@dataclass(frozen=True)
class LatticeResult:
    ok: bool
    length: int
    quiet: int
    envelopes: int
    first_hash: str | None
    last_hash: str | None
    errors: list[str] = field(default_factory=list)
    receipt_ok: bool = True
    role: str = ROLE
    note: str = HONEST_SCOPE


def verify_lattice(
    receipts: Sequence[Receipt],
    receipt_errors: list[str] | None = None,
) -> LatticeResult:
    """Verify hash links plus quiet-window state machine and envelope stamps."""
    errors = list(receipt_errors or [])
    if receipt_errors is None:
        errors.extend(Ledger(receipts).verify().errors)
    quiet = 0
    envelopes = 0
    last_end: dict[str, str] = {}
    last_state: dict[str, str] = {}
    for i, rec in enumerate(receipts):
        if rec.event_kind == "UPLOAD_ENVELOPE":
            envelopes += 1
            if not rec.timestamp or not rec.date_stamp or not rec.file_sha256:
                errors.append(f"index {i}: upload envelope missing timestamp/date stamp/file hash")
            continue
        quiet += 1
        if rec.state == "OPEN" and rec.pl_id in last_state and last_state[rec.pl_id] != "BROKEN":
            # Multiple windows per pl_id are refused while one is live.
            if last_state[rec.pl_id] == "OPEN":
                errors.append(f"index {i}: I7 duplicate OPEN for {rec.pl_id}")
        if rec.state == "SEALED":
            if last_state.get(rec.pl_id) not in (None, "OPEN"):
                errors.append(f"index {i}: I7 seal without OPEN for {rec.pl_id}")
        if rec.state == "BROKEN":
            if last_state.get(rec.pl_id) != "SEALED":
                errors.append(f"index {i}: I7/I8 break without SEALED for {rec.pl_id}")
        if rec.window_end and rec.pl_id in last_end:
            if rec.window_end < last_end[rec.pl_id]:
                errors.append(f"index {i}: I5 window_end moved backward for {rec.pl_id}")
        if rec.window_end:
            last_end[rec.pl_id] = rec.window_end
        if rec.state:
            last_state[rec.pl_id] = rec.state
    n = len(receipts)
    return LatticeResult(
        ok=not errors,
        length=n,
        quiet=quiet,
        envelopes=envelopes,
        first_hash=receipts[0].receipt_hash if n else None,
        last_hash=receipts[-1].receipt_hash if n else None,
        errors=errors,
        receipt_ok=not (receipt_errors or []),
    )


def walk(ledger: Ledger) -> LatticeResult:
    receipts = ledger.verify()
    return verify_lattice(list(ledger), receipt_errors=receipts.errors)
