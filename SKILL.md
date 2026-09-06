---
name: PeaceLock
description: Use when opening, sealing, breaking, or verifying a chosen-silence / chosen-inaction receipt (PL-WP-0.1). Transcript always ABSENT. HARD_DUTY cannot be bypassed. Hosted API is stateless. Dual surface: Worker /v1 + POST /mcp, or aziel-runtime FragGate slug peacelock. Author Aziel Eliab.
---

# PeaceLock

Chosen silence / chosen inaction as a first-class receipt.

Author: **Aziel Eliab**.

Use when recording that an operator chose SILENCE, INACTION, or BOTH
for a window. No transcript of unspoken words. No counterfactual act.
No inferred motive. HARD_DUTY refuses open and seal and writes nothing.
Hosted API is stateless and does not store ledgers.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Endpoints (this Worker)

Host: `https://peacelock-download-tracker.vibelock.workers.dev`

| Method | Path | What |
|--------|------|------|
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/example` | Sample open payload. Does not increment downloads. |
| GET | `/v1/doctor` | Hosted self-check (no writes). Does not increment downloads. |
| POST | `/v1/open` | Open a quiet window. HARD_DUTY refused. Client may send ledger. |
| POST | `/v1/seal` | Seal OPEN → SEALED. HARD_DUTY refused. |
| POST | `/v1/break` | Append BROKEN. Original seal stays. |
| POST | `/v1/show` | Return the client-held ledger (filtered by pl_id). |
| POST | `/v1/verify` | Walk hashes and prev links. Not stored. |
| POST | `/v1/lattice` | Verify receipt links + state machine. |
| POST | `/v1/upload` | Attach evidence envelope (file hash + timestamp + date stamp). |
| GET | `/mcp` | Dual-surface MCP docs + FragGate pointer. Does not increment downloads. |
| POST | `/mcp` | JSON-RPC MCP-over-HTTP. Thin doubles of health/skill/open/seal/verify (plus break/show/lattice/upload/doctor). |

OpenAPI: `https://peacelock-download-tracker.vibelock.workers.dev/openapi.json`

Catalog OpenAPI: `https://aziel-runtime.vibelock.workers.dev/openapi.json`

This Worker MCP: `POST https://peacelock-download-tracker.vibelock.workers.dev/mcp`

Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp` (FragGate slug `peacelock`)

Catalog aliases under `/p/peacelock/…` when listed.

TemporalLock (timeslate lattice): `https://temporallock-download-tracker.vibelock.workers.dev/`

ShadowLock: `https://shadowlock-download-tracker.vibelock.workers.dev/`

DecisionGATE: `https://decisiongate-download-tracker.vibelock.workers.dev/`

FragGate kernel: `https://github.com/AzielEliab/fraggate`

## How to call (Mozilla/5.0)

```bash
curl -s -A 'Mozilla/5.0' https://peacelock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' -X POST https://peacelock-download-tracker.vibelock.workers.dev/v1/open \
  -H 'content-type: application/json' \
  -d '{"mode":"SILENCE","channel":"email","act_class":"reply"}'
curl -s -A 'Mozilla/5.0' -X POST https://peacelock-download-tracker.vibelock.workers.dev/v1/verify \
  -H 'content-type: application/json' \
  -d '{"ledger":[]}'
curl -s -A 'Mozilla/5.0' https://peacelock-download-tracker.vibelock.workers.dev/v1/skill
```

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients (Cursor, Glama, Claude, and others): `POST` this Worker `/mcp` (thin doubles of the human buttons) or the catalog MCP endpoint (FragGate slug peacelock).

## Local (after one-click install)

```bash
curl -fsSL https://peacelock-download-tracker.vibelock.workers.dev/install.sh | bash
peacelock ui
peacelock doctor
```

Then open http://127.0.0.1:8768 (this computer only).

## Honest banner

THIS IS: chosen silence / chosen inaction as a first-class receipt (PL-WP-0.1). THIS IS NOT: a gag-order kit, a wiretap, or third-party binding. HARD_DUTY cannot be bypassed. The Worker does not store ledgers. Author Aziel Eliab.

Cite the GitHub repository and this Worker. No Zenodo DOI is invented here; a software deposit is still needed.

Apache-2.0 (or the repo LICENSE). Forks are welcome and always allowed.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: quiet-window receipts, not transcripts.

- Product homepage (workspace + counted download): https://peacelock-download-tracker.vibelock.workers.dev/
- Catalog product (when listed): https://aziel-runtime.vibelock.workers.dev/p/peacelock/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker MCP (dual surface): `POST https://peacelock-download-tracker.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://peacelock-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://peacelock-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://peacelock-download-tracker.vibelock.workers.dev/v1/example`

Local UI: **Import JSONL file** (`type=file`) and **Export JSONL**. Upload hashes file bytes and stamps timestamp + date. Then `peacelock doctor`.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients: `POST https://peacelock-download-tracker.vibelock.workers.dev/mcp` or catalog `POST https://aziel-runtime.vibelock.workers.dev/mcp`.

Counted download (gzip HTTP 200, no 302): https://peacelock-download-tracker.vibelock.workers.dev/download?asset=peacelock-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/peacelock
