"""Example: open, seal, upload envelope, verify. Author: Aziel Eliab."""

from __future__ import annotations

from pathlib import Path

from peacelock.chain import Ledger


def main() -> None:
    path = Path("examples/_out") / "peacelock_ledger.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    ledger = Ledger((), path=path)
    opened = ledger.open(mode="SILENCE", channel="email", act_class="reply")
    print("opened", opened.pl_id, opened.receipt_hash)
    sealed = ledger.seal(pl_id=opened.pl_id)
    print("sealed", sealed.receipt_hash)
    ev = path.parent / "stamp.txt"
    ev.write_text("operator envelope\n", encoding="utf-8")
    env = ledger.upload_envelope(file_path=ev, pl_id=opened.pl_id)
    print("envelope", env.timestamp, env.date_stamp, env.file_sha256)
    print(ledger.verify())


if __name__ == "__main__":
    main()
