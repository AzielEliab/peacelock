"""CLI: version, open, seal, break, show, verify, upload."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

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
    rc = main(["verify", "--json", str(path)])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["length"] == 3
    assert set(payload) == {"ok", "length", "first_hash", "last_hash", "errors"}
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
    assert main(["verify", "--json", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["ok"] is True


def test_cli_verify_missing(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.jsonl"
    assert main(["verify", str(missing)]) == 2
    err = capsys.readouterr().err
    assert "No ledger" in err
    assert "peacelock open" in err


def test_cli_welcome_and_help(capsys) -> None:
    assert main([]) == 0
    welcome = capsys.readouterr().out
    assert "peacelock ui" in welcome
    assert "Aziel Eliab" in welcome
    assert "arguments are required" not in welcome
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    help_out = capsys.readouterr().out
    assert "Common commands" in help_out
    assert "Advanced:" in help_out
    assert "peacelock ui" in help_out


def test_cli_unknown_and_incomplete(capsys) -> None:
    with pytest.raises(SystemExit) as unknown:
        main(["bogus"])
    assert unknown.value.code == 2
    err = capsys.readouterr().err
    assert 'Unknown command "bogus"' in err
    assert "peacelock --help" in err
    with pytest.raises(SystemExit) as incomplete:
        main(["open"])
    assert incomplete.value.code == 2
    err = capsys.readouterr().err
    assert "--mode" in err
    assert "Try:" in err


def test_cli_welcome_json(capsys) -> None:
    assert main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["author"] == "Aziel Eliab"
    assert payload["version"] == __version__
    assert "peacelock ui" in payload["next"]


def test_cli_verify_human(tmp_path: Path, capsys) -> None:
    path = tmp_path / "peacelock_ledger.jsonl"
    assert main(["open", "--ledger", str(path), "--mode", "SILENCE", "--channel", "email", "--act-class", "reply"]) == 0
    capsys.readouterr()
    assert main(["verify", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Ledger checks out." in out
    assert not out.lstrip().startswith("{")
