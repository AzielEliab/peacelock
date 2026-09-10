# peacelock download tracker

Isolated Worker `peacelock-download-tracker`. Project `peacelock`.
v0.1.0 serves the quiet-window lattice runtime (PL-WP-0.1).
KV namespace `PEACELOCK_DOWNLOADS` bound as `DOWNLOADS`.
Does **not** 302 to GitHub on `/download`. Serves gzip via `ASSETS.fetch`,
`Cache-Control: private, no-store`.

GET `/` is the product homepage (Use UI + counted download). Increments a **page-view** counter (separate from downloads).
GET `/download` increments **downloads**.
GET `/count` returns `{project, views, downloads, total}` (azhub convention: `total` = downloads).
`/v1` never increments DOWNLOADS KV.
GET `/install.sh` one-click install (does not increment; script curls `/download`).
GET `/v1/skill` returns skill markdown (`text/markdown`). Does not increment views or downloads.
GET `/v1/fraggate/list`, GET `/v1/fraggate/describe`, POST `/v1/fraggate/call` PROXY to aziel-runtime via the `AZIEL_RUNTIME` service binding. Not local ops. `/v1/runtime/{list,describe,call}` aliases map to those door paths.
`/v1/mesh/*` PROXY to aziel-runtime suite mesh (AZIEL_RUNTIME). Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 hub cite (local qnsd in https://github.com/AzielEliab/qnm-node ; runtime catalog in https://github.com/AzielEliab/aziel-runtime). Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Human UI Live Nodes strip polls `GET /v1/mesh`.
GET `/mcp` returns dual-surface MCP docs + FragGate pointer (`slug=peacelock`). Does not increment.
POST `/mcp` is JSON-RPC MCP-over-HTTP (`initialize`, `tools/list`, `tools/call`) doubling catalog labels health/skill/open/seal/break/show/verify.
UI Health / Skill map to catalog LIVE_OPS. `GET /v1/doctor` is Worker-local only — not a FragGate live op.
GET `/cite.json`, `/sitemap.xml`, `/robots.txt`, `/llms.txt` are SEO / cite surfaces. Do not increment downloads.

Host: https://peacelock-download-tracker.vibelock.workers.dev
