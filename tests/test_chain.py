"""Lattice verify, upload envelopes, tamper detection."""

from __future__ import annotations

import json
from pathlib import Path

from peacelock.chain import Ledger
from peacelock.lattice import walk
from peacelock.receipt import file_sha256


def test_prev_hash_chains_and_verify(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ledger = Ledger((), path=path)
    a = ledger.open(
        mode="BOTH",
        channel="desk",
        act_class="post",
        opened_at="2026-09-06T12:00:00Z",
        window_start="2026-09-06T12:00:00Z",
    )
    b = ledger.seal(pl_id=a.pl_id, sealed_at="2026-09-06T13:00:00Z", window_end="2026-09-06T13:00:00Z")
    assert b.prev_hash == a.receipt_hash
    assert ledger.verify().ok
    lat = walk(ledger)
    assert lat.ok
    assert lat.quiet == 2


def test_tamper_fails_verify(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ledger = Ledger((), path=path)
    ledger.open(
        mode="SILENCE",
        channel="email",
        act_class="reply",
        opened_at="2026-09-06T12:00:00Z",
        window_start="2026-09-06T12:00:00Z",
    )
    lines = path.read_text(encoding="utf-8").splitlines()
    obj = json.loads(lines[0])
    obj["note"] = "TAMPERED"
    path.write_text(json.dumps(obj) + "\n", encoding="utf-8")
    loaded = Ledger.load(path)
    result = loaded.verify()
    assert not result.ok
    assert result.errors


def test_upload_envelope_timestamp_and_date_stamp(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ev = tmp_path / "receipt.bin"
    ev.write_bytes(b"operator declared envelope")
    ledger = Ledger((), path=path)
    opened = ledger.open(
        mode="INACTION",
        channel="desk",
        act_class="file",
        opened_at="2026-09-06T12:00:00Z",
        window_start="2026-09-06T12:00:00Z",
    )
    env = ledger.upload_envelope(
        file_path=ev,
        pl_id=opened.pl_id,
        timestamp="2026-09-06T12:30:00Z",
        note="stamp only",
    )
    assert env.event_kind == "UPLOAD_ENVELOPE"
    assert env.timestamp == "2026-09-06T12:30:00Z"
    assert env.date_stamp == "2026-09-06"
    assert env.file_sha256 == file_sha256(ev)
    assert env.file_name == "receipt.bin"
    assert env.transcript == "ABSENT"
    assert env.prev_hash == opened.receipt_hash
    text = path.read_text(encoding="utf-8")
    assert "operator declared envelope" not in text
    assert ledger.verify().ok
    lat = walk(ledger)
    assert lat.ok
    assert lat.envelopes == 1


def test_first_prev_hash_is_genesis(tmp_path: Path) -> None:
    from peacelock.canon import GENESIS_PREV_HASH

    ledger = Ledger((), path=tmp_path / "l.jsonl")
    rec = ledger.open(
        mode="SILENCE",
        channel="x",
        act_class="other",
        opened_at="2026-09-06T12:00:00Z",
        window_start="2026-09-06T12:00:00Z",
    )
    assert rec.prev_hash == GENESIS_PREV_HASH
