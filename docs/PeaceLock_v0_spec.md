# PeaceLock v0 spec (PL-WP-0.1)

Author: Aziel Eliab only. Apache-2.0. Version 0.1.0.

This is the machine-facing companion to [docs/whitepaper.md](whitepaper.md).

## Record

Every quiet record and every upload envelope carries:

```
transcript = "ABSENT"
counterfactual_act = "ABSENT"
inferred_motive = "ABSENT"
actor = "operator"
spec = "PL-WP-0.1"
```

`receipt_hash` is SHA-256 of canonical JSON (sorted keys, UTF-8, no
extra whitespace). `receipt_hash` itself is excluded from the hash.

First `prev_hash` is GENESIS: 64 zero hex characters.

## Closed sets

- `mode`: SILENCE | INACTION | BOTH
- `state`: OPEN | SEALED | BROKEN
- `event_kind`: QUIET | UPLOAD_ENVELOPE
- `duty_check`: NONE | ADVISORY | HARD_DUTY
- `act_class`: reply, file, post, call, attend, sign, pay, transfer, delete, other
- `break_reason`: speech_occurred, act_occurred, operator_void, duty_conflict

## State machine

1. `open` appends OPEN (unless HARD_DUTY → refuse, write nothing).
2. `seal` appends SEALED from the latest OPEN for that `pl_id` (HARD_DUTY refuse).
3. `break` appends BROKEN from the latest SEALED. Original SEALED stays.
4. `upload` appends UPLOAD_ENVELOPE with `file_sha256`, basename,
   wall-clock ISO `timestamp`, calendar `date_stamp`.

## CLI

```
peacelock open --mode SILENCE --channel email --act-class reply
peacelock seal --pl-id pl_...
peacelock break --pl-id pl_... --reason speech_occurred
peacelock show
peacelock verify
```

Default ledger: `./peacelock_ledger.jsonl`
Override: `PEACELOCK_LEDGER` or `--ledger`.

## Schema

See [`../peacelock_schema.json`](../peacelock_schema.json).
