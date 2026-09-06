"""Command-line interface for PeaceLock.

    peacelock open --mode SILENCE --channel email --act-class reply
    peacelock seal --pl-id pl_...
    peacelock break --pl-id pl_... --reason speech_occurred
    peacelock show
    peacelock verify
    peacelock upload FILE
    peacelock ui
    peacelock doctor

Default ledger: ./peacelock_ledger.jsonl
Override: PEACELOCK_LEDGER or --ledger.

Author: Aziel Eliab only. Not a gag-order kit. HARD_DUTY cannot be bypassed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from peacelock import __version__
from peacelock.chain import Ledger, default_ledger_path
from peacelock.errors import (
    AppendOnlyError,
    HardDutyError,
    InvariantError,
    LatticeError,
    LedgerError,
    PeaceLockError,
    ReceiptError,
)
from peacelock.lattice import HONEST_SCOPE, walk


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="peacelock",
        description=(
            "PeaceLock — chosen silence / chosen inaction as a first-class "
            "receipt (PL-WP-0.1, Aziel Eliab). Not a gag-order kit. "
            "HARD_DUTY cannot be bypassed. Local UI: `peacelock ui`."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version", help="Print package version.")

    p_ui = sub.add_parser("ui", help="Run the localhost UI (127.0.0.1:8768).")
    p_ui.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8768, help="Bind port (default 8768).")

    p_open = sub.add_parser("open", help="Open a quiet window (OPEN). HARD_DUTY refuses and writes nothing.")
    p_open.add_argument("--mode", required=True, choices=["SILENCE", "INACTION", "BOTH"])
    p_open.add_argument("--channel", required=True, help="Operator-declared channel token (e.g. email, desk).")
    p_open.add_argument(
        "--act-class",
        required=True,
        dest="act_class",
        choices=["reply", "file", "post", "call", "attend", "sign", "pay", "transfer", "delete", "other"],
    )
    p_open.add_argument("--duty-check", default="NONE", dest="duty_check", choices=["NONE", "ADVISORY", "HARD_DUTY"])
    p_open.add_argument("--note", default="", help="Optional note ≤140 chars. No why.")
    p_open.add_argument("--window-start", default=None, dest="window_start", help="UTC ISO-8601 Z. Open clock or later.")
    p_open.add_argument("--window-end", default=None, dest="window_end", help="UTC ISO-8601 Z. Forward only.")
    p_open.add_argument("--ledger", default=None, help="JSONL ledger path (default ./peacelock_ledger.jsonl).")

    p_seal = sub.add_parser("seal", help="Seal an OPEN window (SEALED). HARD_DUTY refuses and writes nothing.")
    p_seal.add_argument("--pl-id", required=True, dest="pl_id")
    p_seal.add_argument("--duty-check", default=None, dest="duty_check", choices=["NONE", "ADVISORY", "HARD_DUTY"])
    p_seal.add_argument("--note", default="")
    p_seal.add_argument("--window-end", default=None, dest="window_end")
    p_seal.add_argument("--ledger", default=None)

    p_break = sub.add_parser("break", help="Append BROKEN. Original seal stays (I8).")
    p_break.add_argument("--pl-id", required=True, dest="pl_id")
    p_break.add_argument(
        "--reason",
        required=True,
        choices=["speech_occurred", "act_occurred", "operator_void", "duty_conflict"],
    )
    p_break.add_argument("--note", default="")
    p_break.add_argument("--ledger", default=None)

    p_show = sub.add_parser("show", help="Print receipts in the ledger.")
    p_show.add_argument("--pl-id", default=None, dest="pl_id")
    p_show.add_argument("--ledger", default=None)
    p_show.add_argument("file", nargs="?", default=None, help="Optional JSONL path (alias of --ledger).")

    p_ver = sub.add_parser("verify", help="Walk the lattice; exit 0 if intact, nonzero if broken.")
    p_ver.add_argument("--ledger", default=None)
    p_ver.add_argument("file", nargs="?", default=None)

    p_up = sub.add_parser("upload", help="Hash FILE bytes and append an upload envelope (timestamp + date stamp).")
    p_up.add_argument("file", help="Operator-declared evidence file. Bytes hashed; not stored as a transcript.")
    p_up.add_argument("--pl-id", default=None, dest="pl_id")
    p_up.add_argument("--note", default="")
    p_up.add_argument("--ledger", default=None)

    p_lat = sub.add_parser("lattice", help="Verify receipt links + quiet-window state machine.")
    p_lat.add_argument("--ledger", default=None)
    p_lat.add_argument("file", nargs="?", default=None)

    p_doc = sub.add_parser("doctor", help="Self-check. No network, no telemetry.")
    p_doc.add_argument("--json", action="store_true", dest="as_json")

    p_imp = sub.add_parser("import", help="Import a JSON / JSONL document.")
    p_imp.add_argument("path")

    p_exp = sub.add_parser("export", help="Export a JSON document.")
    p_exp.add_argument("path")

    return parser


def _ledger_path(args: argparse.Namespace) -> Path:
    if getattr(args, "ledger", None):
        return Path(args.ledger)
    if args.cmd in {"show", "verify", "lattice"} and getattr(args, "file", None):
        return Path(args.file)
    return default_ledger_path()


def _print_receipt(rec, index: int | None = None) -> None:
    prefix = f"[{index}] " if index is not None else ""
    print(f"{prefix}{rec.event_kind}  state={rec.state or '-'}  hash={rec.receipt_hash}")
    print(f"    pl_id={rec.pl_id}  prev={rec.prev_hash}")
    if rec.event_kind == "QUIET":
        print(f"    mode={rec.mode}  act_class={rec.act_class}  channel={rec.channel}")
        print(f"    window {rec.window_start} → {rec.window_end or 'open'}")
        print(f"    duty_check={rec.duty_check}  opened_at={rec.opened_at}  sealed_at={rec.sealed_at}")
        if rec.broken_at:
            print(f"    broken_at={rec.broken_at}  reason={rec.break_reason}")
    else:
        print(f"    file={rec.file_name}  sha256={rec.file_sha256}")
        print(f"    timestamp={rec.timestamp}  date_stamp={rec.date_stamp}")
    print(f"    transcript={rec.transcript}  counterfactual_act={rec.counterfactual_act}  inferred_motive={rec.inferred_motive}")
    if rec.note:
        print(f"    note: {rec.note}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        if args.cmd == "version":
            print(f"peacelock {__version__}")
            return 0

        if args.cmd == "ui":
            from peacelock.ui import serve

            serve(host=args.host, port=args.port)
            return 0

        if args.cmd == "open":
            path = _ledger_path(args)
            ledger = Ledger.load(path)
            rec = ledger.open(
                mode=args.mode,
                channel=args.channel,
                act_class=args.act_class,
                duty_check=args.duty_check,
                note=args.note,
                window_start=args.window_start,
                window_end=args.window_end,
            )
            print(f"opened {rec.pl_id}  {rec.receipt_hash}")
            return 0

        if args.cmd == "seal":
            path = _ledger_path(args)
            ledger = Ledger.load(path)
            rec = ledger.seal(pl_id=args.pl_id, duty_check=args.duty_check, note=args.note, window_end=args.window_end)
            print(f"sealed {rec.pl_id}  {rec.receipt_hash}")
            return 0

        if args.cmd == "break":
            path = _ledger_path(args)
            ledger = Ledger.load(path)
            rec = ledger.break_window(pl_id=args.pl_id, reason=args.reason, note=args.note)
            print(f"broken {rec.pl_id}  {rec.receipt_hash}  reason={rec.break_reason}")
            return 0

        if args.cmd == "show":
            path = _ledger_path(args)
            if not path.is_file():
                print(f"not found: {path}", file=sys.stderr)
                return 2
            ledger = Ledger.load(path)
            rows = ledger.show(args.pl_id)
            print(f"peacelock ledger  n={len(rows)}  path={path}")
            for i, rec in enumerate(rows):
                _print_receipt(rec, i)
            return 0

        if args.cmd == "verify":
            path = _ledger_path(args)
            if not path.is_file():
                print(f"not found: {path}", file=sys.stderr)
                return 2
            ledger = Ledger.load(path)
            result = ledger.verify()
            payload = {
                "ok": result.ok,
                "length": result.length,
                "first_hash": result.first_hash,
                "last_hash": result.last_hash,
                "errors": result.errors,
            }
            print(json.dumps(payload, indent=2))
            return 0 if result.ok else 1

        if args.cmd == "lattice":
            path = _ledger_path(args)
            if not path.is_file():
                print(f"not found: {path}", file=sys.stderr)
                return 2
            ledger = Ledger.load(path)
            result = walk(ledger)
            payload = {
                "ok": result.ok,
                "length": result.length,
                "quiet": result.quiet,
                "envelopes": result.envelopes,
                "first_hash": result.first_hash,
                "last_hash": result.last_hash,
                "errors": result.errors,
                "role": result.role,
                "note": result.note,
            }
            print(json.dumps(payload, indent=2))
            return 0 if result.ok else 1

        if args.cmd == "upload":
            path = _ledger_path(args)
            ledger = Ledger.load(path)
            rec = ledger.upload_envelope(file_path=args.file, pl_id=args.pl_id, note=args.note)
            print(f"envelope {rec.pl_id}  {rec.receipt_hash}")
            print(f"file_sha256={rec.file_sha256}")
            print(f"timestamp={rec.timestamp}  date_stamp={rec.date_stamp}")
            return 0

        if args.cmd == "doctor":
            from peacelock.doctor import run_doctor

            return run_doctor(as_json=getattr(args, "as_json", False))

        if args.cmd == "import":
            from peacelock.jsonio import import_json

            rec = import_json(args.path)
            sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
            return 0

        if args.cmd == "export":
            from peacelock.jsonio import export_json

            rec = export_json(args.path)
            sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
            return 0

        parser.error(f"unknown command {args.cmd}")
        return 2
    except HardDutyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (ReceiptError, LedgerError, AppendOnlyError, InvariantError, LatticeError, PeaceLockError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
