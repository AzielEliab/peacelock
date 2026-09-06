"""Local UI page exposes open/seal/break/verify and honest scope."""

from __future__ import annotations

from peacelock.ui import PAGE


def test_ui_has_ops() -> None:
    for token in ("btn-open", "btn-seal", "btn-break", "btn-verify", "btn-upload", "btn-health", "btn-skill"):
        assert token in PAGE
    assert "btn-doctor" not in PAGE
    assert "HARD_DUTY" in PAGE
    assert "ABSENT" in PAGE or "transcript" in PAGE.lower()
    assert "Aziel Eliab" in PAGE
