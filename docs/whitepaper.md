# PeaceLock

**Chosen silence / chosen inaction as a first-class receipt**

Aziel Eliab
September 2026
License: Apache-2.0
Spec: PL-WP-0.1

> Chosen silence is a receipt. Chosen inaction is a receipt. Unspoken words are not stored.

## Abstract

PeaceLock is an open-source, append-only system for recording that an
**operator** chose silence, inaction, or both, for a named window.
The receipt is first-class. It is not a transcript of words that were
never said, not a counterfactual act, and not an inferred motive.

Receipts are cryptographically linked with SHA-256. The sequence cannot
be altered without detection. A break on contradiction appends
`BROKEN`; the original seal stays. HARD_DUTY refuses open and seal and
writes nothing.

This document is the specification implemented by the `peacelock`
Python package (v0.1.0). Forks are welcome and always allowed.

---

## 1. Purpose

People sometimes choose not to speak, and sometimes choose not to act.
That choice is useful to record. It becomes harmful when the log later
invents the unspoken sentence, the act that "would have" happened, or
the why.

PeaceLock separates the **receipt of quiet** from any **story about
quiet**.

- A receipt says: an operator opened (and maybe sealed) a window of
  SILENCE, INACTION, or BOTH, for this channel and this act_class.
- A receipt does not say: here is the draft, here is the motive, here
  is what a third party is bound to do.

PeaceLock is **not** a gag-order kit, **not** a wiretap, and **not**
third-party binding. HARD_DUTY cannot be bypassed.

---

## 2. Invariants

| Id | Rule |
|----|------|
| I1 | No transcript. `transcript` is always `ABSENT` (not words, drafts, or paraphrase). |
| I2 | No counterfactual act. `counterfactual_act` is always `ABSENT`. `act_class` is a closed-set token only. |
| I3 | No inferred motive. No why. Optional `note` ≤ 140 characters. |
| I4 | Operator only. `actor` is always `operator`. |
| I5 | No backdated quiet. `window_start` is the open clock or later. Extend `window_end` forward only. |
| I6 | `duty_check=HARD_DUTY` refuses **open** and **seal**. Exit nonzero. Write nothing. |
| I7 | Append-only. OPEN → SEALED → optional BROKEN. |
| I8 | Break on contradiction appends BROKEN. The original seal stays. |

---

## 3. Data model

Modes: `SILENCE` | `INACTION` | `BOTH`

`act_class` closed set: `reply`, `file`, `post`, `call`, `attend`,
`sign`, `pay`, `transfer`, `delete`, `other`

`duty_check`: `NONE` | `ADVISORY` | `HARD_DUTY`

`break_reason`: `speech_occurred` | `act_occurred` | `operator_void` |
`duty_conflict`

Constants on every record:

```
transcript = ABSENT
counterfactual_act = ABSENT
inferred_motive = ABSENT
actor = operator
spec = PL-WP-0.1
```

Fields:

| Field | Meaning |
|-------|---------|
| `spec` | `PL-WP-0.1` |
| `pl_id` | Quiet-window id (`pl_` + 16 hex) |
| `mode` | SILENCE / INACTION / BOTH |
| `state` | OPEN / SEALED / BROKEN |
| `window_start` | UTC ISO-8601 Z. Open clock or later. |
| `window_end` | UTC ISO-8601 Z or null. Forward only. |
| `channel` | Operator-declared channel token |
| `act_class` | Closed-set token |
| `duty_check` | NONE / ADVISORY / HARD_DUTY |
| `actor` | `operator` |
| `note` | Optional, ≤140, no why |
| `prev_hash` | Previous `receipt_hash`. First is GENESIS (64 zero hex). |
| `opened_at` / `sealed_at` / `broken_at` | UTC ISO-8601 Z |
| `break_reason` | Closed-set token or null |
| `receipt_hash` | SHA-256 of canonical bytes (this field excluded) |

Upload envelopes (optional lattice events) add operator-declared
evidence metadata: file SHA-256, basename, wall-clock `timestamp`,
calendar `date_stamp`. File bytes may be hashed. Forbidden transcripts
of unspoken words are not stored.

---

## 4. Canonical encoding

UTF-8 JSON, **sorted keys**, no extra whitespace
(`separators=(",", ":")`, `sort_keys=True`, `ensure_ascii=False`).

`receipt_hash = SHA-256(canonical bytes)`.

The ledger is JSONL. Default path `./peacelock_ledger.jsonl`.
Override: `PEACELOCK_LEDGER`.

---

## 5. Lattice

Each open / seal / break / upload-envelope event chains
`prev_hash → receipt_hash`. Verify walks the chain. A decreasing
`window_end` is refused (I5). HARD_DUTY never writes (I6).

PeaceLock sits beside [TemporalLock](https://github.com/AzielEliab/temporallock)
(timeslate lattice) and [ShadowLock](https://github.com/AzielEliab/shadowlock)
(zero-retention observation). It does not replace them.

---

## 6. CLI

```
peacelock open / seal / break / show / verify
```

HARD_DUTY on open or seal exits nonzero and writes nothing.

---

## 7. Honesty

THIS IS: chosen silence / chosen inaction as a first-class receipt.

THIS IS NOT: a gag-order kit, a wiretap, third-party binding, a
transcript of unspoken words, or a motive engine.

Author: **Aziel Eliab** only.
License: Apache-2.0. Forks are welcome and always allowed.

No Zenodo DOI is invented here. Cite GitHub and the Worker when
deposited.
