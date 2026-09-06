"""Self-check for PeaceLock. No network, no telemetry.

    peacelock doctor
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Callable

from peacelock import __version__

AUTHOR = "Aziel Eliab"
Check = tuple[str, bool, str]


def _ok(name: str, detail: str = "") -> Check:
    return name, True, detail


def _fail(name: str, detail: str) -> Check:
    return name, False, detail


def _check_version() -> Check:
    if __version__:
        return _ok("version", str(__version__))
    return _fail("version", "missing")


def _check_identity() -> Check:
    try:
        mod = __import__(__name__.split(".")[0])
        author = str(getattr(mod, "__author__", AUTHOR))
    except Exception as exc:  # noqa: BLE001
        return _fail("identity", str(exc))
    blob = author + " " + AUTHOR
    forbidden = ("Col" + "lin H" + "orton", "Ja" + "ck Al" + "tman", "GodLock" + ".AZ", "Reve" + "aler")
    if any(x in blob for x in forbidden):
        return _fail("identity", "forbidden identity label")
    if "Aziel Eliab" not in blob:
        return _fail("identity", author)
    return _ok("identity", AUTHOR)


def _check_json_roundtrip() -> Check:
    from peacelock.jsonio import export_json, import_json

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "in.json"
        out = Path(tmp) / "out.json"
        src.write_text(
            json.dumps({"product": "peacelock", "author": AUTHOR, "ok": True}, indent=2),
            encoding="utf-8",
        )
        rec = import_json(src)
        if not rec.get("ok"):
            return _fail("import", str(rec))
        rec2 = export_json(out)
        if not rec2.get("ok") or not out.exists():
            return _fail("export", str(rec2))
        doc = json.loads(out.read_text(encoding="utf-8"))
        if doc.get("author") != AUTHOR:
            return _fail("export author", str(doc.get("author")))
        return _ok("json import/export", "roundtrip")


def _check_core_hash_stable() -> Check:
    from peacelock.canon import ABSENT, ACTOR_OPERATOR, GENESIS_PREV_HASH, SPEC, digest

    payload = {
        "act_class": "reply",
        "actor": ACTOR_OPERATOR,
        "break_reason": None,
        "broken_at": None,
        "channel": "email",
        "counterfactual_act": ABSENT,
        "date_stamp": None,
        "duty_check": "NONE",
        "event_kind": "QUIET",
        "evidence_kind": None,
        "file_name": None,
        "file_sha256": None,
        "inferred_motive": ABSENT,
        "mode": "SILENCE",
        "note": "",
        "opened_at": "2026-09-06T00:00:00Z",
        "pl_id": "pl_0123456789abcdef",
        "prev_hash": GENESIS_PREV_HASH,
        "sealed_at": None,
        "spec": SPEC,
        "state": "OPEN",
        "timestamp": None,
        "transcript": ABSENT,
        "window_end": None,
        "window_start": "2026-09-06T00:00:00Z",
    }
    known = digest(payload)
    again = digest(payload)
    if known != again or len(known) != 64:
        return _fail("PL-WP-0.1 core hash", known)
    return _ok("PL-WP-0.1 core hash", "stable")


def _check_hard_duty() -> Check:
    from peacelock.chain import Ledger
    from peacelock.errors import HardDutyError

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        ledger = Ledger((), path=path)
        try:
            ledger.open(mode="SILENCE", channel="email", act_class="reply", duty_check="HARD_DUTY")
            return _fail("hard-duty", "HARD_DUTY open was accepted")
        except HardDutyError:
            pass
        if path.exists() and path.stat().st_size > 0:
            return _fail("hard-duty", "HARD_DUTY wrote bytes")
        return _ok("HARD_DUTY refuse", "open writes nothing")


def _check_lattice() -> Check:
    from peacelock.chain import Ledger
    from peacelock.lattice import walk

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        ledger = Ledger((), path=path)
        opened = ledger.open(
            mode="BOTH",
            channel="desk",
            act_class="post",
            opened_at="2026-09-06T00:00:00Z",
            window_start="2026-09-06T00:00:00Z",
        )
        ledger.seal(pl_id=opened.pl_id, sealed_at="2026-09-06T01:00:00Z", window_end="2026-09-06T01:00:00Z")
        ev = Path(tmp) / "stamp.txt"
        ev.write_bytes(b"operator envelope")
        ledger.upload_envelope(file_path=ev, pl_id=opened.pl_id, timestamp="2026-09-06T01:05:00Z")
        ledger.break_window(pl_id=opened.pl_id, reason="operator_void", broken_at="2026-09-06T01:10:00Z")
        result = walk(ledger)
        if not result.ok or result.quiet != 3 or result.envelopes != 1:
            return _fail("lattice", str(result.errors))
        if not path.read_text(encoding="utf-8").count('"state":"SEALED"'):
            return _fail("I8", "original seal missing")
        return _ok("lattice", f"quiet={result.quiet} envelopes={result.envelopes}")


def _check_no_transcript() -> Check:
    from peacelock.errors import InvariantError
    from peacelock.receipt import Receipt, assert_no_leakage

    try:
        assert_no_leakage({"transcript": "hello there", "pl_id": "pl_0123456789abcdef"})
        return _fail("I1", "transcript words accepted")
    except InvariantError:
        pass
    try:
        Receipt.create(
            pl_id="pl_0123456789abcdef",
            mode="SILENCE",
            state="OPEN",
            channel="email",
            act_class="reply",
            opened_at="2026-09-06T00:00:00Z",
            window_start="2026-09-06T00:00:00Z",
            words="draft of unspoken reply",
        )
        return _fail("I1", "words key accepted")
    except InvariantError:
        return _ok("no transcript leakage", "I1")


CHECKS: tuple[Callable[[], Check], ...] = (
    _check_version,
    _check_identity,
    _check_json_roundtrip,
    _check_core_hash_stable,
    _check_hard_duty,
    _check_lattice,
    _check_no_transcript,
)


def run_doctor(*, as_json: bool = False) -> int:
    results = []
    failed = 0
    for fn in CHECKS:
        name, ok, detail = fn()
        results.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            failed += 1
        mark = "ok" if ok else "FAIL"
        if not as_json:
            print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    payload = {
        "ok": failed == 0,
        "failed": failed,
        "checks": results,
        "version": __version__,
        "author": AUTHOR,
        "role": "chosen silence / chosen inaction receipt lattice",
        "network": False,
        "telemetry": False,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("doctor", "passed" if failed == 0 else "failed")
    return 0 if failed == 0 else 1
