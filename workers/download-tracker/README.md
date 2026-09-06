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
GET `/mcp` returns dual-surface MCP docs + FragGate pointer (`slug=peacelock`). Does not increment.
POST `/mcp` is JSON-RPC MCP-over-HTTP (`initialize`, `tools/list`, `tools/call`) doubling health/skill/open/seal/verify.
GET `/cite.json`, `/sitemap.xml`, `/robots.txt`, `/llms.txt` are SEO / cite surfaces. Do not increment downloads.

Host: https://peacelock-download-tracker.vibelock.workers.dev
