"""PeaceLock: chosen silence / chosen inaction as a first-class receipt.

PL-WP-0.1. Author: Aziel Eliab only.

Not a gag-order kit. Not a wiretap. Not third-party binding.
HARD_DUTY cannot be bypassed. Forks are welcome and always allowed.
"""

from __future__ import annotations

from peacelock.canon import ABSENT, GENESIS_PREV_HASH, SPEC
from peacelock.chain import Ledger, VerifyResult
from peacelock.errors import (
    AppendOnlyError,
    HardDutyError,
    InvariantError,
    LatticeError,
    LedgerError,
    PeaceLockError,
    ReceiptError,
)
from peacelock.hashing import canonical_bytes, digest
from peacelock.lattice import verify_lattice
from peacelock.receipt import Receipt

__version__ = "0.1.0"
__author__ = "Aziel Eliab"
__all__ = [
    "ABSENT",
    "AppendOnlyError",
    "GENESIS_PREV_HASH",
    "HardDutyError",
    "InvariantError",
    "LatticeError",
    "Ledger",
    "LedgerError",
    "PeaceLockError",
    "Receipt",
    "ReceiptError",
    "SPEC",
    "VerifyResult",
    "canonical_bytes",
    "digest",
    "verify_lattice",
    "__version__",
]
