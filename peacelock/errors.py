"""PeaceLock errors. Author: Aziel Eliab only."""

from __future__ import annotations


class PeaceLockError(Exception):
    """Base error for PeaceLock."""


class AppendOnlyError(PeaceLockError):
    """Raised on any attempt to edit, pop, replace, or delete a receipt."""


class ReceiptError(PeaceLockError):
    """Raised when a receipt field is invalid."""


class LedgerError(PeaceLockError):
    """Raised for ledger-level problems (missing open, empty seal)."""


class HardDutyError(PeaceLockError):
    """I6: HARD_DUTY refuses open and seal. Write nothing."""


class InvariantError(PeaceLockError):
    """Raised when an invariant (I1–I8) would be violated."""


class LatticeError(PeaceLockError):
    """Raised when a lattice walk fails or a backdated window is refused."""
