"""No transcript leakage in ledger JSONL or receipt dicts."""

from __future__ import annotations

import json
from pathlib import Path

from peacelock.canon import ABSENT, FORBIDDEN_KEYS
from peacelock.chain import Ledger


def test_jsonl_has_no_unspoken_words(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ledger = Ledger((), path=path)
    ledger.open(
        mode="SILENCE",
        channel="email",
        act_class="reply",
        note="window only",
        opened_at="2026-09-06T12:00:00Z",
        window_start="2026-09-06T12:00:00Z",
    )
    blob = path.read_text(encoding="utf-8")
    obj = json.loads(blob)
    assert obj["transcript"] == ABSENT
    assert obj["counterfactual_act"] == ABSENT
    assert obj["inferred_motive"] == ABSENT
    assert set(obj) & FORBIDDEN_KEYS == set()
    for token in ("I would have", "draft reply", "unspoken", "paraphrase"):
        assert token not in blob


def test_show_does_not_invent_words(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ledger = Ledger((), path=path)
    ledger.open(
        mode="BOTH",
        channel="desk",
        act_class="call",
        opened_at="2026-09-06T12:00:00Z",
        window_start="2026-09-06T12:00:00Z",
    )
    dumped = ledger[0].to_dict()
    assert dumped["transcript"] == ABSENT
    assert "words" not in dumped
