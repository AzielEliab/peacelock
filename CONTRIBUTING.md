# Contributing to PeaceLock

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute. Pull requests are welcome
if you want a change upstream. Keep a fork forever if you do not.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Python 3.10+. Core is stdlib only (`hashlib`, `json`, `argparse`).
pytest is the dev extra. No network.

## Ground rules

1. **Identity is Aziel Eliab only.** Do not credit other names.
2. **I1 No transcript.** `transcript` is always `ABSENT`. Do not store
   unspoken words, drafts, or paraphrases.
3. **I2 No counterfactual act.** `counterfactual_act` is always `ABSENT`.
   `act_class` is a closed-set token only.
4. **I3 No inferred motive.** No why. Optional `note` ≤ 140 characters.
5. **I4 Operator only.** `actor` is always `operator`.
6. **I5 No backdated quiet.** `window_start` is the open clock or later.
   Extend `window_end` forward only.
7. **I6 HARD_DUTY refuses open and seal.** Exit nonzero. Write nothing.
   HARD_DUTY cannot be bypassed.
8. **I7 Append-only** OPEN → SEALED → optional BROKEN.
9. **I8 Break appends BROKEN.** The original seal stays.
10. **Not a gag-order kit, wiretap, or third-party binding.**
11. **Door vs local op.** `/v1/fraggate/*`, `/v1/runtime/*`, and
    `/v1/mesh/*` PROXY to aziel-runtime. Local ops are `/v1/{op}` only.
    Never treat `fraggate/call` or `mesh/status` as a local op name.
    Suite mesh default OFF; QNM rollup live|locked|isolated; QNS-CD-1.0
    hub cite only (no public qnsd proxy); no Node Gate; no auto-heal;
    not anonymity.
12. New behavior needs a test that fails without the change.

## Where to change things

- Canonical encoding / SHA-256: `peacelock/canon.py`, `peacelock/hashing.py`
- Receipt dataclass: `peacelock/receipt.py`
- Ledger / lattice: `peacelock/chain.py`, `peacelock/lattice.py`
- CLI: `peacelock/cli.py`
- Errors: `peacelock/errors.py`
- Suite mesh / QNM Live Nodes + QNS-CD-1.0 cross-map: `workers/download-tracker/src/mesh.js` (`/v1/mesh/*` PROXY to aziel-runtime; hub cite only).

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
Author: Aziel Eliab only.
