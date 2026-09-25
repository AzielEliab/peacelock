"""Command-line interface for PeaceLock.

    peacelock
    peacelock ui
    peacelock open --mode SILENCE --channel email --act-class reply
    peacelock seal --pl-id pl_...
    peacelock break --pl-id pl_... --reason speech_occurred
    peacelock show
    peacelock verify
    peacelock upload FILE
    peacelock doctor

Default ledger: ./peacelock_ledger.jsonl
Override: PEACELOCK_LEDGER or --ledger.

Human text is the default. Pass --json for the machine document.
Author: Aziel Eliab.
"""

from __future__ import annotations

import argparse
import json
import re
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

_NEXT = "Try: peacelock ui   or   peacelock --help"
_OPEN_EXAMPLE = "peacelock open --mode SILENCE --channel email --act-class reply"


def _root_help() -> str:
    return f"""peacelock {__version__}

Record a quiet window you chose — silence, inaction, or both — as a receipt
on this computer.

Usage:
  peacelock
  peacelock <command> [options]

Common commands:
  ui        Open the local app
  open      Start a quiet window
  seal      Seal an open window
  break     Record that the window ended
  show      List receipts in the ledger
  verify    Check that the ledger is intact
  doctor    Local self-check (no network)

Advanced:
  upload    Hash a file and attach an envelope
  lattice   Check links and window states
  import    Read a JSON document into local state
  export    Write local state and the ledger to a JSON document
  version   Print the version

Options:
  --json    Print the machine document instead of human text
  -h, --help
            Show this help

Examples:
  peacelock ui
  {_OPEN_EXAMPLE}
  peacelock doctor
  peacelock verify --json

Notes:
  The ledger is append-only. HARD_DUTY refuses open and seal and writes nothing.
  Author: Aziel Eliab
"""


class PeaceParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        if self.prog == "peacelock":
            return _root_help()
        return super().format_help()

    def error(self, message: str) -> None:
        self.exit(2, _plain_arg_error(self.prog, message) + "\n")


def _plain_arg_error(prog: str, message: str) -> str:
    choice = re.search(r"invalid choice: '([^']*)'", message)
    if choice and prog.strip() == "peacelock":
        return f'Unknown command "{choice.group(1)}". {_NEXT}'
    flag_choice = re.search(r"argument (--[\w-]+): invalid choice: '([^']*)'", message)
    if flag_choice:
        flag, value = flag_choice.group(1), flag_choice.group(2)
        command = prog.split()[-1] if prog.split() else "peacelock"
        return f'"{value}" is not a valid {flag}.\nTry: peacelock {command} --help'
    unknown = re.search(r"unrecognized arguments?: (.+)", message)
    if unknown:
        return f'Unknown option {unknown.group(1).strip()}.\nTry: peacelock --help'
    missing_value = re.search(r"argument (.+): expected one argument", message)
    if missing_value:
        return f"{missing_value.group(1)} needs a value.\nTry: peacelock --help"
    if "the following arguments are required" in message:
        if prog.endswith(" open"):
            return (
                "Open needs --mode, --channel, and --act-class.\n"
                f"Try: {_OPEN_EXAMPLE}"
            )
        if prog.endswith(" seal"):
            return (
                "Seal needs the window id printed by open.\n"
                "Try: peacelock seal --pl-id pl_...   or   peacelock show"
            )
        if prog.endswith(" break"):
            return (
                "Break needs --pl-id and --reason.\n"
                "Try: peacelock break --pl-id pl_... --reason operator_void"
            )
        if prog.endswith(" upload"):
            return "Upload needs a file path.\nTry: peacelock upload ./notes.txt"
        if prog.endswith(" import"):
            return "Import needs a file path.\nTry: peacelock import ./document.json"
        if prog.endswith(" export"):
            return "Export needs a file path.\nTry: peacelock export ./document.json"
        return _NEXT
    return f"{message}.\nTry: peacelock --help"


def _build_parser() -> PeaceParser:
    parser = PeaceParser(prog="peacelock", add_help=True)
    sub = parser.add_subparsers(dest="cmd", required=False, metavar="command")
    fmt = argparse.RawDescriptionHelpFormatter

    sub.add_parser(
        "version",
        help="Print the version.",
        description="Print the PeaceLock version.",
        formatter_class=fmt,
        epilog="Author: Aziel Eliab",
    )

    p_ui = sub.add_parser(
        "ui",
        help="Open the local app.",
        description="Serve the local app on this computer only.",
        formatter_class=fmt,
        epilog="Example:\n  peacelock ui\n\nAuthor: Aziel Eliab",
    )
    p_ui.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8768, help="Bind port (default 8768).")

    p_open = sub.add_parser(
        "open",
        help="Start a quiet window.",
        description="Start a quiet window and append an OPEN receipt.",
        formatter_class=fmt,
        epilog=f"Example:\n  {_OPEN_EXAMPLE}\n\nAdd --json for the receipt document.\nAuthor: Aziel Eliab",
    )
    p_open.add_argument("--mode", required=True, choices=["SILENCE", "INACTION", "BOTH"])
    p_open.add_argument("--channel", required=True, help="Where this window applies (for example email or desk).")
    p_open.add_argument(
        "--act-class",
        required=True,
        dest="act_class",
        choices=["reply", "file", "post", "call", "attend", "sign", "pay", "transfer", "delete", "other"],
        help="Kind of act this window covers.",
    )
    p_open.add_argument("--duty-check", default="NONE", dest="duty_check", choices=["NONE", "ADVISORY", "HARD_DUTY"])
    p_open.add_argument("--note", default="", help="Optional note, 140 characters or fewer.")
    p_open.add_argument("--window-start", default=None, dest="window_start", help="UTC time, ISO-8601 with Z.")
    p_open.add_argument("--window-end", default=None, dest="window_end", help="UTC time, ISO-8601 with Z. Forward only.")
    p_open.add_argument("--ledger", default=None, help="Ledger file (default ./peacelock_ledger.jsonl).")

    p_seal = sub.add_parser(
        "seal",
        help="Seal an open window.",
        description="Seal an OPEN window.",
        formatter_class=fmt,
        epilog="Example:\n  peacelock seal --pl-id pl_...\n\nAuthor: Aziel Eliab",
    )
    p_seal.add_argument("--pl-id", required=True, dest="pl_id", help="Window id printed by open.")
    p_seal.add_argument("--duty-check", default=None, dest="duty_check", choices=["NONE", "ADVISORY", "HARD_DUTY"])
    p_seal.add_argument("--note", default="")
    p_seal.add_argument("--window-end", default=None, dest="window_end")
    p_seal.add_argument("--ledger", default=None)

    p_break = sub.add_parser(
        "break",
        help="Record that the window ended.",
        description="Append a BROKEN receipt. The sealed receipt stays in the ledger.",
        formatter_class=fmt,
        epilog="Example:\n  peacelock break --pl-id pl_... --reason operator_void\n\nAuthor: Aziel Eliab",
    )
    p_break.add_argument("--pl-id", required=True, dest="pl_id")
    p_break.add_argument(
        "--reason",
        required=True,
        choices=["speech_occurred", "act_occurred", "operator_void", "duty_conflict"],
    )
    p_break.add_argument("--note", default="")
    p_break.add_argument("--ledger", default=None)

    p_show = sub.add_parser(
        "show",
        help="List receipts in the ledger.",
        description="List receipts in the ledger.",
        formatter_class=fmt,
        epilog="Example:\n  peacelock show\n  peacelock show --json\n\nAuthor: Aziel Eliab",
    )
    p_show.add_argument("--pl-id", default=None, dest="pl_id")
    p_show.add_argument("--ledger", default=None)
    p_show.add_argument("file", nargs="?", default=None, help="Ledger file (same as --ledger).")

    p_ver = sub.add_parser(
        "verify",
        help="Check that the ledger is intact.",
        description="Check receipt hashes and links. Exit 0 when intact.",
        formatter_class=fmt,
        epilog="Example:\n  peacelock verify\n  peacelock verify --json\n\nAuthor: Aziel Eliab",
    )
    p_ver.add_argument("--ledger", default=None)
    p_ver.add_argument("file", nargs="?", default=None, help="Ledger file (same as --ledger).")

    p_up = sub.add_parser(
        "upload",
        help="Hash a file and attach an envelope.",
        description="Hash file bytes and append an envelope with a timestamp and date stamp.",
        formatter_class=fmt,
        epilog="Example:\n  peacelock upload ./notes.txt\n\nAuthor: Aziel Eliab",
    )
    p_up.add_argument("file", help="File to hash. The bytes are not stored as a transcript.")
    p_up.add_argument("--pl-id", default=None, dest="pl_id")
    p_up.add_argument("--note", default="")
    p_up.add_argument("--ledger", default=None)

    p_lat = sub.add_parser(
        "lattice",
        help="Check links and window states.",
        description="Check receipt links and the quiet-window states.",
        formatter_class=fmt,
        epilog="Example:\n  peacelock lattice --json\n\nAuthor: Aziel Eliab",
    )
    p_lat.add_argument("--ledger", default=None)
    p_lat.add_argument("file", nargs="?", default=None, help="Ledger file (same as --ledger).")

    p_doc = sub.add_parser(
        "doctor",
        help="Local self-check. No network.",
        description="Run the local self-check. No network and no telemetry.",
        formatter_class=fmt,
        epilog="Example:\n  peacelock doctor\n  peacelock doctor --json\n\nAuthor: Aziel Eliab",
    )
    p_doc.add_argument("--json", action="store_true", dest="as_json", help="Print the machine document.")

    p_imp = sub.add_parser(
        "import",
        help="Read a JSON document into local state.",
        description="Read a JSON or JSONL document into .peacelock-state.json.",
        formatter_class=fmt,
        epilog="Example:\n  peacelock import ./document.json\n\nAuthor: Aziel Eliab",
    )
    p_imp.add_argument("path")

    p_exp = sub.add_parser(
        "export",
        help="Write local state and the ledger to a JSON document.",
        description="Write .peacelock-state.json and the default ledger into one JSON document.",
        formatter_class=fmt,
        epilog="Example:\n  peacelock export ./document.json\n\nAuthor: Aziel Eliab",
    )
    p_exp.add_argument("path")

    return parser


def _split_json(argv: Sequence[str]) -> tuple[list[str], bool]:
    as_json = False
    cleaned: list[str] = []
    for token in argv:
        if token == "--json":
            as_json = True
        else:
            cleaned.append(token)
    return cleaned, as_json


def _ledger_path(args: argparse.Namespace) -> Path:
    if getattr(args, "ledger", None):
        return Path(args.ledger)
    if args.cmd in {"show", "verify", "lattice"} and getattr(args, "file", None):
        return Path(args.file)
    return default_ledger_path()


def _emit(as_json: bool, human: str, payload: dict) -> None:
    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    else:
        print(human)


def _print_receipt(rec, index: int | None = None) -> str:
    prefix = f"[{index}] " if index is not None else ""
    lines = [
        f"{prefix}{rec.event_kind}  state={rec.state or '-'}  hash={rec.receipt_hash}",
        f"    pl_id={rec.pl_id}  prev={rec.prev_hash}",
    ]
    if rec.event_kind == "QUIET":
        lines.append(f"    mode={rec.mode}  act_class={rec.act_class}  channel={rec.channel}")
        lines.append(f"    window {rec.window_start} → {rec.window_end or 'open'}")
        lines.append(f"    duty_check={rec.duty_check}  opened_at={rec.opened_at}  sealed_at={rec.sealed_at}")
        if rec.broken_at:
            lines.append(f"    broken_at={rec.broken_at}  reason={rec.break_reason}")
    else:
        lines.append(f"    file={rec.file_name}  sha256={rec.file_sha256}")
        lines.append(f"    timestamp={rec.timestamp}  date_stamp={rec.date_stamp}")
    lines.append(
        f"    transcript={rec.transcript}  counterfactual_act={rec.counterfactual_act}  inferred_motive={rec.inferred_motive}"
    )
    if rec.note:
        lines.append(f"    note: {rec.note}")
    return "\n".join(lines)


def _hint_for(exc: BaseException) -> str:
    text = str(exc)
    if isinstance(exc, HardDutyError):
        return "Nothing was written. Leave the duty check off, then try the command again."
    if "no OPEN window" in text or "open first" in text:
        return f"Try: {_OPEN_EXAMPLE}"
    if "break requires SEALED" in text:
        return "Seal the window first.\nTry: peacelock seal --pl-id pl_..."
    if "already BROKEN" in text:
        return "The sealed receipt is still in the ledger.\nTry: peacelock show"
    if "not found" in text.lower() or isinstance(exc, FileNotFoundError):
        return "Check the path, then try again.\nTry: peacelock --help"
    if "loopback" in text:
        return "Try: peacelock ui"
    if isinstance(exc, OSError):
        return "Check the path and permissions.\nTry: peacelock --help"
    return "Try: peacelock --help"


def _report(exc: BaseException) -> int:
    print(f"{exc}\n{_hint_for(exc)}", file=sys.stderr)
    return 2


def _welcome(as_json: bool) -> int:
    summary = (
        "PeaceLock records a quiet window you chose — silence, inaction, or both — "
        "as a receipt on this computer."
    )
    if as_json:
        _emit(
            True,
            "",
            {
                "ok": True,
                "product": "peacelock",
                "version": __version__,
                "author": "Aziel Eliab",
                "summary": summary,
                "next": ["peacelock ui", "peacelock doctor", "peacelock --help"],
            },
        )
        return 0
    print(
        f"{summary}\n\n"
        "Next, open the local app:\n"
        "  peacelock ui\n\n"
        "Or check this install:\n"
        "  peacelock doctor\n\n"
        "Help:\n"
        "  peacelock --help\n\n"
        "Author: Aziel Eliab"
    )
    return 0


def _missing_ledger(path: Path) -> int:
    print(
        f"No ledger at {path}.\nTry: {_OPEN_EXAMPLE}",
        file=sys.stderr,
    )
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    raw = list(argv) if argv is not None else sys.argv[1:]
    cleaned, flag_json = _split_json(raw)
    parser = _build_parser()
    args = parser.parse_args(cleaned)
    as_json = flag_json or bool(getattr(args, "as_json", False))

    try:
        if args.cmd is None:
            return _welcome(as_json)

        if args.cmd == "version":
            _emit(as_json, f"peacelock {__version__}", {"ok": True, "version": __version__, "author": "Aziel Eliab"})
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
            _emit(
                as_json,
                f"opened {rec.pl_id}  {rec.receipt_hash}",
                {
                    "ok": True,
                    "action": "opened",
                    "pl_id": rec.pl_id,
                    "receipt_hash": rec.receipt_hash,
                    "receipt": rec.to_dict(),
                },
            )
            return 0

        if args.cmd == "seal":
            path = _ledger_path(args)
            ledger = Ledger.load(path)
            rec = ledger.seal(pl_id=args.pl_id, duty_check=args.duty_check, note=args.note, window_end=args.window_end)
            _emit(
                as_json,
                f"sealed {rec.pl_id}  {rec.receipt_hash}",
                {
                    "ok": True,
                    "action": "sealed",
                    "pl_id": rec.pl_id,
                    "receipt_hash": rec.receipt_hash,
                    "receipt": rec.to_dict(),
                },
            )
            return 0

        if args.cmd == "break":
            path = _ledger_path(args)
            ledger = Ledger.load(path)
            rec = ledger.break_window(pl_id=args.pl_id, reason=args.reason, note=args.note)
            _emit(
                as_json,
                f"broken {rec.pl_id}  {rec.receipt_hash}  reason={rec.break_reason}",
                {
                    "ok": True,
                    "action": "broken",
                    "pl_id": rec.pl_id,
                    "receipt_hash": rec.receipt_hash,
                    "reason": rec.break_reason,
                    "receipt": rec.to_dict(),
                },
            )
            return 0

        if args.cmd == "show":
            path = _ledger_path(args)
            if not path.is_file():
                return _missing_ledger(path)
            ledger = Ledger.load(path)
            rows = ledger.show(args.pl_id)
            body = "\n".join(
                [f"{len(rows)} receipt(s) in {path}"] + [_print_receipt(rec, i) for i, rec in enumerate(rows)]
            )
            _emit(
                as_json,
                body,
                {
                    "ok": True,
                    "action": "show",
                    "path": str(path),
                    "length": len(rows),
                    "ledger": [rec.to_dict() for rec in rows],
                },
            )
            return 0

        if args.cmd == "verify":
            path = _ledger_path(args)
            if not path.is_file():
                return _missing_ledger(path)
            ledger = Ledger.load(path)
            result = ledger.verify()
            payload = {
                "ok": result.ok,
                "length": result.length,
                "first_hash": result.first_hash,
                "last_hash": result.last_hash,
                "errors": result.errors,
            }
            if result.ok:
                human = f"Ledger checks out.\nReceipts: {result.length}"
            else:
                lines = ["Ledger check failed.", f"Receipts: {result.length}"]
                lines.extend(f"- {err}" for err in result.errors)
                lines.append("Try: peacelock show")
                human = "\n".join(lines)
            _emit(as_json, human, payload)
            return 0 if result.ok else 1

        if args.cmd == "lattice":
            from peacelock.lattice import walk

            path = _ledger_path(args)
            if not path.is_file():
                return _missing_ledger(path)
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
            if result.ok:
                head = "Links and window states check out."
            else:
                head = "Links or window states need attention."
            lines = [
                head,
                f"Receipts: {result.length}",
                f"Quiet events: {result.quiet}",
                f"File envelopes: {result.envelopes}",
            ]
            lines.extend(f"- {err}" for err in result.errors)
            if not result.ok:
                lines.append("Try: peacelock show")
            _emit(as_json, "\n".join(lines), payload)
            return 0 if result.ok else 1

        if args.cmd == "upload":
            path = _ledger_path(args)
            ledger = Ledger.load(path)
            rec = ledger.upload_envelope(file_path=args.file, pl_id=args.pl_id, note=args.note)
            _emit(
                as_json,
                (
                    f"envelope {rec.pl_id}  {rec.receipt_hash}\n"
                    f"file_sha256={rec.file_sha256}\n"
                    f"timestamp={rec.timestamp}  date_stamp={rec.date_stamp}"
                ),
                {
                    "ok": True,
                    "action": "envelope",
                    "pl_id": rec.pl_id,
                    "receipt_hash": rec.receipt_hash,
                    "file_sha256": rec.file_sha256,
                    "timestamp": rec.timestamp,
                    "date_stamp": rec.date_stamp,
                    "receipt": rec.to_dict(),
                },
            )
            return 0

        if args.cmd == "doctor":
            from peacelock.doctor import run_doctor

            return run_doctor(as_json=as_json)

        if args.cmd == "import":
            from peacelock.jsonio import import_json

            rec = import_json(args.path)
            _emit(
                as_json,
                f"Imported {rec.get('imported')}\nStored {rec.get('stored')}\nRecords: {rec.get('count')}",
                rec,
            )
            return 0

        if args.cmd == "export":
            from peacelock.jsonio import export_json

            rec = export_json(args.path)
            _emit(as_json, f"Exported {rec.get('exported')}", rec)
            return 0

        parser.error(f"unknown command {args.cmd}")
        return 2
    except (HardDutyError, ReceiptError, LedgerError, AppendOnlyError, InvariantError, LatticeError, PeaceLockError, OSError) as exc:
        return _report(exc)


if __name__ == "__main__":
    raise SystemExit(main())
