"""PL-WP-0.1 invariants I1–I8."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from peacelock.canon import ABSENT, GENESIS_PREV_HASH
from peacelock.chain import Ledger
from peacelock.errors import AppendOnlyError, HardDutyError, InvariantError, LedgerError, ReceiptError
from peacelock.receipt import Receipt, assert_no_leakage


def _open(path: Path, **kwargs) -> Ledger:
    ledger = Ledger((), path=path)
    ledger.open(
        mode=kwargs.get("mode", "SILENCE"),
        channel=kwargs.get("channel", "email"),
        act_class=kwargs.get("act_class", "reply"),
        duty_check=kwargs.get("duty_check", "NONE"),
        note=kwargs.get("note", ""),
        window_start=kwargs.get("window_start", "2026-09-06T12:00:00Z"),
        opened_at=kwargs.get("opened_at", "2026-09-06T12:00:00Z"),
    )
    return ledger


def test_i1_transcript_always_absent(tmp_path: Path) -> None:
    ledger = _open(tmp_path / "l.jsonl")
    rec = ledger[0]
    assert rec.transcript == ABSENT
    line = (tmp_path / "l.jsonl").read_text(encoding="utf-8")
    assert '"transcript":"ABSENT"' in line
    assert "unspoken" not in line
    assert "draft" not in line


def test_i1_words_and_drafts_refused() -> None:
    with pytest.raises(InvariantError):
        assert_no_leakage({"transcript": "I would have said hello"})
    with pytest.raises(InvariantError):
        Receipt.create(
            pl_id="pl_0123456789abcdef",
            mode="SILENCE",
            state="OPEN",
            channel="email",
            act_class="reply",
            opened_at="2026-09-06T12:00:00Z",
            window_start="2026-09-06T12:00:00Z",
            draft="a paraphrase of unspoken words",
        )


def test_i2_counterfactual_act_absent_and_closed_act_class(tmp_path: Path) -> None:
    ledger = _open(tmp_path / "l.jsonl")
    assert ledger[0].counterfactual_act == ABSENT
    assert ledger[0].act_class == "reply"
    with pytest.raises(ReceiptError):
        Receipt.create(
            pl_id="pl_0123456789abcdef",
            mode="SILENCE",
            state="OPEN",
            channel="email",
            act_class="shout",
            opened_at="2026-09-06T12:00:00Z",
            window_start="2026-09-06T12:00:00Z",
        )


def test_i3_no_inferred_motive_and_note_cap(tmp_path: Path) -> None:
    ledger = _open(tmp_path / "l.jsonl", note="desk closed")
    assert ledger[0].inferred_motive == ABSENT
    with pytest.raises(InvariantError):
        _open(tmp_path / "n.jsonl", note="x" * 141)
    with pytest.raises(InvariantError):
        _open(tmp_path / "w.jsonl", note="because I feared the reply")


def test_i4_operator_only() -> None:
    with pytest.raises(InvariantError):
        assert_no_leakage({"actor": "third-party"})


def test_i5_no_backdated_quiet(tmp_path: Path) -> None:
    ledger = Ledger((), path=tmp_path / "l.jsonl")
    with pytest.raises(InvariantError):
        ledger.open(
            mode="SILENCE",
            channel="email",
            act_class="reply",
            opened_at="2026-09-06T12:00:00Z",
            window_start="2026-09-06T11:00:00Z",
        )


def test_i5_extend_forward_only(tmp_path: Path) -> None:
    ledger = _open(tmp_path / "l.jsonl", window_start="2026-09-06T12:00:00Z")
    pl_id = ledger[0].pl_id
    ledger.seal(pl_id=pl_id, window_end="2026-09-06T13:00:00Z", sealed_at="2026-09-06T13:00:00Z")
    with pytest.raises(InvariantError):
        # cannot open a new seal path that moves end backward — seal already consumed OPEN
        ledger2 = Ledger.load(tmp_path / "l.jsonl")
        # break then try to seal again is I7; instead test helper via a fresh open
        ledger2.open(
            mode="SILENCE",
            channel="email",
            act_class="reply",
            opened_at="2026-09-07T12:00:00Z",
            window_start="2026-09-07T12:00:00Z",
            window_end="2026-09-07T11:00:00Z",
        )


def test_i7_append_only_state_machine(tmp_path: Path) -> None:
    ledger = _open(tmp_path / "l.jsonl")
    pl_id = ledger[0].pl_id
    with pytest.raises(LedgerError):
        ledger.break_window(pl_id=pl_id, reason="operator_void")
    sealed = ledger.seal(pl_id=pl_id, sealed_at="2026-09-06T13:00:00Z")
    assert sealed.state == "SEALED"
    broken = ledger.break_window(pl_id=pl_id, reason="speech_occurred", broken_at="2026-09-06T14:00:00Z")
    assert broken.state == "BROKEN"
    states = [r.state for r in ledger if r.event_kind == "QUIET"]
    assert states == ["OPEN", "SEALED", "BROKEN"]


def test_i8_break_keeps_original_seal(tmp_path: Path) -> None:
    ledger = _open(tmp_path / "l.jsonl")
    pl_id = ledger[0].pl_id
    sealed = ledger.seal(pl_id=pl_id, sealed_at="2026-09-06T13:00:00Z")
    seal_hash = sealed.receipt_hash
    ledger.break_window(pl_id=pl_id, reason="act_occurred", broken_at="2026-09-06T14:00:00Z")
    assert any(r.receipt_hash == seal_hash and r.state == "SEALED" for r in ledger)
    text = (tmp_path / "l.jsonl").read_text(encoding="utf-8")
    assert text.count('"state":"SEALED"') == 1
    assert text.count('"state":"BROKEN"') == 1


def test_cannot_edit_receipt_or_ledger(tmp_path: Path) -> None:
    ledger = _open(tmp_path / "l.jsonl")
    with pytest.raises(AppendOnlyError):
        ledger[0].note = "edit"
    with pytest.raises(AppendOnlyError):
        ledger.pop()
    with pytest.raises(AppendOnlyError):
        del ledger[0]


def test_genesis_prev_hash(tmp_path: Path) -> None:
    ledger = _open(tmp_path / "l.jsonl")
    assert ledger[0].prev_hash == GENESIS_PREV_HASH
