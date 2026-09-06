# PeaceLock

Open-source **chosen silence / chosen inaction receipt** — append-only
quiet windows hash-chained on a temporal lattice (PL-WP-0.1).
`transcript`, `counterfactual_act`, and `inferred_motive` are always
`ABSENT`. HARD_DUTY cannot be bypassed.

**Author:** Aziel Eliab only
**Date:** September 2026 · v0.1.0
**License:** [Apache-2.0](LICENSE)

> Chosen silence is a receipt. Chosen inaction is a receipt.

See the spec: [docs/whitepaper.md](docs/whitepaper.md) ·
[docs/PeaceLock_v0_spec.md](docs/PeaceLock_v0_spec.md) ·
[peacelock_schema.json](peacelock_schema.json).
How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
peacelock ui
```

## One-click install

```bash
curl -fsSL https://peacelock-download-tracker.vibelock.workers.dev/install.sh | bash
```

The script curls the **counted** tarball from this project's Worker
(`/download`, User-Agent `Mozilla/5.0`), extracts, makes a venv, and
`pip install -e .`. Then run `peacelock ui`.

Or use the live software homepage (workspace + counted download):
https://peacelock-download-tracker.vibelock.workers.dev/

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

- Homepage: [https://peacelock-download-tracker.vibelock.workers.dev/](https://peacelock-download-tracker.vibelock.workers.dev/)
- Direct tarball: [peacelock-0.1.0.tar.gz](https://peacelock-download-tracker.vibelock.workers.dev/download?asset=peacelock-0.1.0.tar.gz)
- One-click install: [https://peacelock-download-tracker.vibelock.workers.dev/install.sh](https://peacelock-download-tracker.vibelock.workers.dev/install.sh)
- Skill: [https://peacelock-download-tracker.vibelock.workers.dev/v1/skill](https://peacelock-download-tracker.vibelock.workers.dev/v1/skill)
- OpenAPI: [https://peacelock-download-tracker.vibelock.workers.dev/openapi.json](https://peacelock-download-tracker.vibelock.workers.dev/openapi.json)
- GitHub: [https://github.com/AzielEliab/peacelock](https://github.com/AzielEliab/peacelock)
- Cite: [cite.json](https://peacelock-download-tracker.vibelock.workers.dev/cite.json) — Eliab, Aziel. (2026). PeaceLock 0.1.0 [Software]. Apache-2.0. No Zenodo DOI is invented here; a software deposit is still needed.

Isolated counter: Worker `peacelock-download-tracker`, KV `PEACELOCK_DOWNLOADS`. `/v1` does not increment downloads.

Open http://127.0.0.1:8768 (loopback only). No CDN, no telemetry.

---

## Download

**Counted download page (this project only, ticks automatically):**

# → [https://peacelock-download-tracker.vibelock.workers.dev/](https://peacelock-download-tracker.vibelock.workers.dev/) ←

Direct tarball (also counted): [peacelock-0.1.0.tar.gz](https://peacelock-download-tracker.vibelock.workers.dev/download?asset=peacelock-0.1.0.tar.gz)

- Live count JSON: [https://peacelock-download-tracker.vibelock.workers.dev/count](https://peacelock-download-tracker.vibelock.workers.dev/count)
- Stats: [https://peacelock-download-tracker.vibelock.workers.dev/stats](https://peacelock-download-tracker.vibelock.workers.dev/stats)
- GitHub releases: [https://github.com/AzielEliab/peacelock/releases](https://github.com/AzielEliab/peacelock/releases)

---

## Local UI

`peacelock ui` serves a loopback dashboard at http://127.0.0.1:8768

Binds to `127.0.0.1` only. Self-contained HTML (no CDN). Open / seal /
break / show / verify a local ledger in a process tmp dir. Upload
attaches evidence metadata (file SHA-256 + timestamp + date stamp).
Transcript is always ABSENT.

## CLI smoke

```bash
export PEACELOCK_LEDGER=./peacelock_ledger.jsonl
peacelock open --mode SILENCE --channel email --act-class reply
peacelock seal --pl-id pl_...          # use the id printed by open
peacelock break --pl-id pl_... --reason operator_void
peacelock show
peacelock verify
peacelock upload ./stamp.bin           # hashes bytes; stores timestamp + date stamp
peacelock doctor
```

Default ledger is `./peacelock_ledger.jsonl`. Override with
`PEACELOCK_LEDGER` or `--ledger`.

HARD_DUTY:

```bash
peacelock open --mode SILENCE --channel email --act-class reply --duty-check HARD_DUTY
# exits nonzero, writes nothing
```

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.peacelock`. Offline. No analytics. Dark matte / gold.

```bash
cd mobile
flutter create --org com.azieeliab --project-name peacelock .
flutter pub get
flutter run
```

The `android/` and `ios/` folders in this tree are skeleton READMEs until you run `flutter create .` (this machine has no Flutter SDK on PATH). Then open `android/` in Android Studio or `ios/Runner.xcworkspace` in Xcode. Not a store listing.

## What it does

PeaceLock records **quiet windows**. A window is a receipt that the
operator chose SILENCE, INACTION, or BOTH for a channel and an
`act_class` token. The receipt is not a transcript, not a motive, and
not a counterfactual act.

Each event is cryptographically linked to the previous one
(`prev_hash` = SHA-256 of the prior receipt). Upload envelopes chain
the same way and carry a wall-clock ISO timestamp plus a calendar date
stamp. Verify walks the chain.

There is no modify and no delete. OPEN → SEALED → optional BROKEN.
A break appends BROKEN; the original seal stays.

Runtime is stdlib only (`hashlib`, `json`). No extra crypto packages.

## Invariants (enforced)

- **I1** No transcript — always `ABSENT`
- **I2** No counterfactual act — always `ABSENT`; `act_class` closed set
- **I3** No inferred motive — no why; note ≤140
- **I4** Operator only
- **I5** No backdated quiet — `window_start` = open clock or later; extend forward only
- **I6** HARD_DUTY refuses open and seal (exit nonzero, write nothing)
- **I7** Append-only OPEN → SEALED → optional BROKEN
- **I8** Break appends BROKEN; original seal stays

## Cross-links

- [TemporalLock](https://github.com/AzielEliab/temporallock) — timeslate lattice
- [ShadowLock](https://github.com/AzielEliab/shadowlock) — zero-retention observation
- [DecisionGATE](https://github.com/AzielEliab/decisiongate) — five sequential gates
- [FragGate](https://github.com/AzielEliab/fraggate) — one door: discover, route, refuse
- [aziel-runtime](https://github.com/AzielEliab/aziel-runtime) — catalog + MCP + OpenAPI
- [Aziel Digital Library](https://www.azielcorpuslibrary.net/)
- [godlock.uk](https://godlock.uk/)
- [www.azieleliab.com](https://www.azieleliab.com/)

## Use with AI assistants

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients (Cursor, Glama, Claude, and others): `POST https://aziel-runtime.vibelock.workers.dev/mcp`. Public identity: Aziel Eliab only.

- Worker OpenAPI: https://peacelock-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`

Agents use OpenAPI/MCP via aziel-runtime. Humans use the complete Worker UI (open/seal/break/show/verify, upload, import/export, doctor). Dual surface: do not gut the human UI.

Always send `User-Agent: Mozilla/5.0`.

## Honest banner

THIS IS: chosen silence / chosen inaction as a first-class receipt (PL-WP-0.1).
THIS IS NOT: a gag-order kit, a wiretap, or third-party binding. HARD_DUTY cannot be bypassed. The Worker does not store ledgers. Author Aziel Eliab only.

Cite the GitHub repository and this Worker. No Zenodo DOI is invented here (placeholder until a software deposit exists).

Apache-2.0. Forks are welcome and always allowed.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: quiet-window receipts, not transcripts.

- Product homepage (workspace + counted download): https://peacelock-download-tracker.vibelock.workers.dev/
- Catalog product (when listed): https://aziel-runtime.vibelock.workers.dev/p/peacelock/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://peacelock-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://peacelock-download-tracker.vibelock.workers.dev/openapi.json

Local UI: **Import JSONL** and **Export JSONL**. Upload file option hashes bytes and stamps timestamp + date. Then `peacelock doctor`.

Counted download (gzip HTTP 200, no 302): https://peacelock-download-tracker.vibelock.workers.dev/download?asset=peacelock-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/peacelock
