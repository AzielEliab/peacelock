---
name: PeaceLock
description: Use when opening, sealing, breaking, or verifying a chosen-silence / chosen-inaction receipt (PL-WP-0.1). Transcript always ABSENT. HARD_DUTY cannot be bypassed. Hosted API is stateless. Dual surface: Worker /v1 + POST /mcp, or aziel-runtime FragGate slug peacelock. This Worker /v1/fraggate/* and /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 hub cite (local qnsd in qnm-node). Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Author Aziel Eliab.
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
| GET | `/v1/health` | Liveness. FragGate LIVE_OPS. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. FragGate LIVE_OPS. Does not increment downloads. |
| GET | `/v1/example` | Sample open payload. Worker-local. Does not increment downloads. |
| GET | `/v1/doctor` | Worker-local self-check (no writes). **Not** a FragGate LIVE_OPS — do not invent `doctor` on the catalog door. |
| GET | `/v1/fraggate/list` | PROXY to aziel-runtime GET /v1/fraggate/list via AZIEL_RUNTIME. Not a local op. |
| GET | `/v1/fraggate/describe` | PROXY to aziel-runtime GET /v1/fraggate/describe (`?name=` / `?slug=`). Not a local op. |
| POST | `/v1/fraggate/call` | PROXY to aziel-runtime POST /v1/fraggate/call. Not a local op. |
| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. QNM live\|locked\|isolated. QNS-CD-1.0 hub cite. Never enables. |
| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster (5-minute presence) + QNS-CD-1.0 cross-map. |
| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path. |
| POST | `/v1/open` | Open a quiet window. HARD_DUTY refused. FragGate LIVE_OPS. |
| POST | `/v1/seal` | Seal OPEN → SEALED. HARD_DUTY refused. FragGate LIVE_OPS. |
| POST | `/v1/break` | Append BROKEN. Original seal stays. FragGate LIVE_OPS. |
| POST | `/v1/show` | Return the client-held ledger (filtered by pl_id). FragGate LIVE_OPS. |
| POST | `/v1/verify` | Walk hashes and prev links. Not stored. FragGate LIVE_OPS. |
| POST | `/v1/lattice` | Verify receipt links + state machine. Worker-local extra (not catalog live). |
| POST | `/v1/upload` | Attach evidence envelope (file hash + timestamp + date stamp). Catalog name `upload_envelope`. |
| GET | `/mcp` | Dual-surface MCP docs + FragGate pointer. Does not increment downloads. |
| POST | `/mcp` | JSON-RPC MCP-over-HTTP. Thin doubles of catalog labels health/skill/open/seal/break/show/verify (plus Worker-local lattice/upload/doctor/example). |

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
curl -s -A 'Mozilla/5.0' https://peacelock-download-tracker.vibelock.workers.dev/v1/mesh
```

FragGate LIVE_OPS (slug `peacelock`): open, seal, break, show, verify, stamp, upload_envelope, health, skill.
UI labels match that catalog set: Open / Seal / Break / Show / Verify / Health / Skill.
Worker-local extras (not catalog live ops): doctor, lattice, example. `peacelock doctor` stays a local CLI self-check.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients (Cursor, Glama, Claude, and others): `POST` this Worker `/mcp` (thin doubles of the human buttons) or the catalog MCP endpoint (FragGate slug peacelock). This Worker `/v1/fraggate/*` and `/v1/mesh/*` PROXY to aziel-runtime via AZIEL_RUNTIME. Catalog MCP `mesh_*` + FragGate `slug=mesh`. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / mesh cross-map only (local qnsd: https://github.com/AzielEliab/qnm-node ; runtime cites: https://github.com/AzielEliab/aziel-runtime). Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity.

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

Local UI labels match catalog: Open / Seal / Break / Show / Verify / Health / Skill. Upload hashes file bytes and stamps timestamp + date. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF) and shows the QNS-CD-1.0 cross-map. CLI `peacelock doctor` remains a local self-check — not a FragGate live op.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients: `POST https://peacelock-download-tracker.vibelock.workers.dev/mcp` or catalog `POST https://aziel-runtime.vibelock.workers.dev/mcp`. Suite mesh: `GET /v1/mesh` PROXY (default OFF). QNS-CD-1.0 hub cite only. Catalog MCP `mesh_*` + FragGate `slug=mesh`.

Counted download (gzip HTTP 200, no 302): https://peacelock-download-tracker.vibelock.workers.dev/download?asset=peacelock-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/peacelock
