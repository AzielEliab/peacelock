"""I6 HARD_DUTY refuses open and seal and writes nothing."""

from __future__ import annotations

from pathlib import Path

import pytest

from peacelock.chain import Ledger
from peacelock.cli import main
from peacelock.errors import HardDutyError


def test_hard_duty_open_writes_nothing(tmp_path: Path) -> None:
    path = tmp_path / "peacelock_ledger.jsonl"
    ledger = Ledger((), path=path)
    with pytest.raises(HardDutyError):
        ledger.open(mode="SILENCE", channel="email", act_class="reply", duty_check="HARD_DUTY")
    assert not path.exists() or path.stat().st_size == 0
    assert len(ledger) == 0


def test_hard_duty_seal_writes_nothing(tmp_path: Path) -> None:
    path = tmp_path / "peacelock_ledger.jsonl"
    ledger = Ledger((), path=path)
    opened = ledger.open(
        mode="INACTION",
        channel="desk",
        act_class="sign",
        opened_at="2026-09-06T12:00:00Z",
        window_start="2026-09-06T12:00:00Z",
    )
    before = path.read_text(encoding="utf-8")
    n = len(ledger)
    with pytest.raises(HardDutyError):
        ledger.seal(pl_id=opened.pl_id, duty_check="HARD_DUTY")
    assert path.read_text(encoding="utf-8") == before
    assert len(ledger) == n


def test_cli_hard_duty_open_nonzero(tmp_path: Path, capsys) -> None:
    path = tmp_path / "l.jsonl"
    rc = main(
        [
            "open",
            "--ledger",
            str(path),
            "--mode",
            "SILENCE",
            "--channel",
            "email",
            "--act-class",
            "reply",
            "--duty-check",
            "HARD_DUTY",
        ]
    )
    assert rc != 0
    err = capsys.readouterr().err
    assert "HARD_DUTY" in err
    assert not path.exists() or path.stat().st_size == 0
