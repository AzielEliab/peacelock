"""CLI: version, open, seal, break, show, verify, upload."""

from __future__ import annotations

import json
from pathlib import Path

from peacelock import __version__
from peacelock.cli import main


def test_cli_version(capsys) -> None:
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == f"peacelock {__version__}"


def test_cli_open_seal_break_verify(tmp_path: Path, capsys) -> None:
    path = tmp_path / "peacelock_ledger.jsonl"
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
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "opened" in out
    pl_id = out.split()[1]
    rc = main(["seal", "--ledger", str(path), "--pl-id", pl_id])
    assert rc == 0
    capsys.readouterr()
    rc = main(["break", "--ledger", str(path), "--pl-id", pl_id, "--reason", "operator_void"])
    assert rc == 0
    capsys.readouterr()
    rc = main(["verify", str(path)])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["length"] == 3
    rc = main(["show", str(path)])
    assert rc == 0
    shown = capsys.readouterr().out
    assert "ABSENT" in shown
    assert "SEALED" in shown
    assert "BROKEN" in shown


def test_cli_upload(tmp_path: Path, capsys, monkeypatch) -> None:
    path = tmp_path / "l.jsonl"
    ev = tmp_path / "stamp.bin"
    ev.write_bytes(b"abc")
    monkeypatch.setenv("PEACELOCK_LEDGER", str(path))
    assert main(["open", "--mode", "INACTION", "--channel", "desk", "--act-class", "file"]) == 0
    capsys.readouterr()
    rc = main(["upload", str(ev)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "envelope" in out
    assert "date_stamp=" in out
    assert main(["verify", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["ok"] is True


def test_cli_verify_missing(tmp_path: Path) -> None:
    assert main(["verify", str(tmp_path / "missing.jsonl")]) == 2
