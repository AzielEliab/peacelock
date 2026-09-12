/**
 * PeaceLock hosted runtime (port of canon/receipt/chain).
 * Stateless: client sends the ledger JSON in the body. Transcript always ABSENT.
 * /v1 never touches DOWNLOADS KV.
 * Door paths (`/v1/fraggate/*`, `/v1/runtime/*`, `/v1/mesh/*`) PROXY to aziel-runtime via AZIEL_RUNTIME.
 * Local ops are single-segment `/v1/{op}` only.
 * Author: Aziel Eliab only.
 */
import { classifyV1Path, doorTargetUrl } from "./door.js";
import { attachQnsCd, meshOpenApiPaths, meshPointer } from "./mesh.js";
const PRODUCT = "peacelock";
const VERSION = "0.1.0";
const MOTTO = "Chosen silence / chosen inaction as a first-class receipt.";
const ROLE = "chosen silence / chosen inaction receipt lattice";
const AUTHOR = "Aziel Eliab";
const SPEC = "PL-WP-0.1";
const ABSENT = "ABSENT";
const ACTOR = "operator";
const HOST = "https://peacelock-download-tracker.vibelock.workers.dev";
const SKILL = `---
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

Always send \`User-Agent: Mozilla/5.0\`. Cloudflare Workers may 403 an empty agent.

## Endpoints (this Worker)

Host: \`https://peacelock-download-tracker.vibelock.workers.dev\`

| Method | Path | What |
|--------|------|------|
| GET | \`/v1/health\` | Liveness. FragGate LIVE_OPS. Does not increment downloads. |
| GET | \`/v1/skill\` | This markdown. FragGate LIVE_OPS. Does not increment downloads. |
| GET | \`/v1/example\` | Sample open payload. Worker-local. Does not increment downloads. |
| GET | \`/v1/doctor\` | Worker-local self-check (no writes). **Not** a FragGate LIVE_OPS — do not invent \`doctor\` on the catalog door. |
| GET | \`/v1/fraggate/list\` | PROXY to aziel-runtime GET /v1/fraggate/list via AZIEL_RUNTIME. Not a local op. |
| GET | \`/v1/fraggate/describe\` | PROXY to aziel-runtime GET /v1/fraggate/describe (\`?name=\` / \`?slug=\`). Not a local op. |
| POST | \`/v1/fraggate/call\` | PROXY to aziel-runtime POST /v1/fraggate/call. Not a local op. |
| GET | \`/v1/mesh\` | PROXY suite mesh status. Default OFF. QNM live\\|locked\\|isolated. QNS-CD-1.0 hub cite. Never enables. |
| GET | \`/v1/mesh/nodes\` | PROXY Live Nodes roster (5-minute presence) + QNS-CD-1.0 cross-map. |
| POST | \`/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}\` | PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path. |
| POST | \`/v1/open\` | Open a quiet window. HARD_DUTY refused. FragGate LIVE_OPS. |
| POST | \`/v1/seal\` | Seal OPEN → SEALED. HARD_DUTY refused. FragGate LIVE_OPS. |
| POST | \`/v1/break\` | Append BROKEN. Original seal stays. FragGate LIVE_OPS. |
| POST | \`/v1/show\` | Return the client-held ledger (filtered by pl_id). FragGate LIVE_OPS. |
| POST | \`/v1/verify\` | Walk hashes and prev links. Not stored. FragGate LIVE_OPS. |
| POST | \`/v1/lattice\` | Verify receipt links + state machine. Worker-local extra (not catalog live). |
| POST | \`/v1/upload\` | Attach evidence envelope (file hash + timestamp + date stamp). Catalog name \`upload_envelope\`. |
| GET | \`/mcp\` | Dual-surface MCP docs + FragGate pointer. Does not increment downloads. |
| POST | \`/mcp\` | JSON-RPC MCP-over-HTTP. Thin doubles of catalog labels health/skill/open/seal/break/show/verify (plus Worker-local lattice/upload/doctor/example). |

OpenAPI: \`https://peacelock-download-tracker.vibelock.workers.dev/openapi.json\`

Catalog OpenAPI: \`https://aziel-runtime.vibelock.workers.dev/openapi.json\`

This Worker MCP: \`POST https://peacelock-download-tracker.vibelock.workers.dev/mcp\`

Catalog MCP: \`POST https://aziel-runtime.vibelock.workers.dev/mcp\` (FragGate slug \`peacelock\`)

Catalog aliases under \`/p/peacelock/…\` when listed.

TemporalLock (timeslate lattice): \`https://temporallock-download-tracker.vibelock.workers.dev/\`

ShadowLock: \`https://shadowlock-download-tracker.vibelock.workers.dev/\`

DecisionGATE: \`https://decisiongate-download-tracker.vibelock.workers.dev/\`

FragGate kernel: \`https://github.com/AzielEliab/fraggate\`

## How to call (Mozilla/5.0)

\`\`\`bash
curl -s -A 'Mozilla/5.0' https://peacelock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' -X POST https://peacelock-download-tracker.vibelock.workers.dev/v1/open \\
  -H 'content-type: application/json' \\
  -d '{"mode":"SILENCE","channel":"email","act_class":"reply"}'
curl -s -A 'Mozilla/5.0' -X POST https://peacelock-download-tracker.vibelock.workers.dev/v1/verify \\
  -H 'content-type: application/json' \\
  -d '{"ledger":[]}'
curl -s -A 'Mozilla/5.0' https://peacelock-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://peacelock-download-tracker.vibelock.workers.dev/v1/mesh
\`\`\`

FragGate LIVE_OPS (slug \`peacelock\`): open, seal, break, show, verify, stamp, upload_envelope, health, skill.
UI labels match that catalog set: Open / Seal / Break / Show / Verify / Health / Skill.
Worker-local extras (not catalog live ops): doctor, lattice, example. \`peacelock doctor\` stays a local CLI self-check.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients (Cursor, Glama, Claude, and others): \`POST\` this Worker \`/mcp\` (thin doubles of the human buttons) or the catalog MCP endpoint (FragGate slug peacelock). This Worker \`/v1/fraggate/*\` and \`/v1/mesh/*\` PROXY to aziel-runtime via AZIEL_RUNTIME. Catalog MCP \`mesh_*\` + FragGate \`slug=mesh\`. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / mesh cross-map only (local qnsd: https://github.com/AzielEliab/qnm-node ; runtime cites: https://github.com/AzielEliab/aziel-runtime). Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity.

## Local (after one-click install)

\`\`\`bash
curl -fsSL https://peacelock-download-tracker.vibelock.workers.dev/install.sh | bash
peacelock ui
peacelock doctor
\`\`\`

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
- Catalog MCP: \`POST https://aziel-runtime.vibelock.workers.dev/mcp\`
- This Worker MCP (dual surface): \`POST https://peacelock-download-tracker.vibelock.workers.dev/mcp\`
- This Worker skill: \`GET https://peacelock-download-tracker.vibelock.workers.dev/v1/skill\`
- This Worker OpenAPI: https://peacelock-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: \`GET https://peacelock-download-tracker.vibelock.workers.dev/v1/example\`

Local UI labels match catalog: Open / Seal / Break / Show / Verify / Health / Skill. Upload hashes file bytes and stamps timestamp + date. Worker homepage Live Nodes strip polls \`GET /v1/mesh\` (default OFF) and shows the QNS-CD-1.0 cross-map. CLI \`peacelock doctor\` remains a local self-check — not a FragGate live op.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients: \`POST https://peacelock-download-tracker.vibelock.workers.dev/mcp\` or catalog \`POST https://aziel-runtime.vibelock.workers.dev/mcp\`. Suite mesh: \`GET /v1/mesh\` PROXY (default OFF). QNS-CD-1.0 hub cite only. Catalog MCP \`mesh_*\` + FragGate \`slug=mesh\`.

Counted download (gzip HTTP 200, no 302): https://peacelock-download-tracker.vibelock.workers.dev/download?asset=peacelock-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/peacelock
`;
const GENESIS_PREV_HASH = "0".repeat(64);
const HASH_FIELDS = [
  "act_class", "actor", "break_reason", "broken_at", "channel", "counterfactual_act",
  "date_stamp", "duty_check", "event_kind", "evidence_kind", "file_name", "file_sha256",
  "inferred_motive", "mode", "note", "opened_at", "pl_id", "prev_hash", "sealed_at",
  "spec", "state", "timestamp", "transcript", "window_end", "window_start",
];
const MODES = ["SILENCE", "INACTION", "BOTH"];
const STATES = ["OPEN", "SEALED", "BROKEN"];
const ACT_CLASSES = ["reply", "file", "post", "call", "attend", "sign", "pay", "transfer", "delete", "other"];
const BREAK_REASONS = ["speech_occurred", "act_occurred", "operator_void", "duty_conflict"];
const FORBIDDEN = ["words", "draft", "paraphrase", "unspoken", "why", "motive", "transcript_text", "said", "would_have", "unspoken_words", "counterfactual", "inferred_why"];

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, HEAD, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, MCP-Protocol-Version, mcp-session-id, User-Agent, Authorization",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

class ReceiptError extends Error { constructor(msg) { super(msg); this.name = "ReceiptError"; } }
class LedgerError extends Error { constructor(msg) { super(msg); this.name = "LedgerError"; } }
class HardDutyError extends Error { constructor(msg) { super(msg); this.name = "HardDutyError"; } }
class InvariantError extends Error { constructor(msg) { super(msg); this.name = "InvariantError"; } }

function utcNow() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

function utcDate(ts) {
  const src = ts || utcNow();
  return src.slice(0, 10);
}

function requireStr(name, value) {
  if (typeof value !== "string") throw new ReceiptError(`${name} must be a string`);
  return value;
}

function assertNoLeakage(data) {
  for (const key of FORBIDDEN) {
    if (Object.prototype.hasOwnProperty.call(data || {}, key)) {
      throw new InvariantError(`I1–I3: forbidden keys ${key}`);
    }
  }
  for (const key of ["transcript", "counterfactual_act", "inferred_motive"]) {
    const val = data && data[key];
    if (val != null && val !== "" && val !== ABSENT) {
      throw new InvariantError(`I1–I3: ${key} must be ABSENT`);
    }
  }
  if (data && data.actor && data.actor !== ACTOR) {
    throw new InvariantError("I4: actor must be operator");
  }
}

function refuseHardDuty(duty, action) {
  if (duty === "HARD_DUTY") {
    throw new HardDutyError(`I6: HARD_DUTY refuses ${action}; write nothing. PeaceLock is not a gag-order kit and cannot bypass a hard duty.`);
  }
}

function validateNote(note) {
  const text = note == null ? "" : String(note);
  if (text.length > 140) throw new InvariantError("I3: note must be ≤140 characters");
  const lowered = text.toLowerCase();
  if (lowered.startsWith("because ") || lowered.startsWith("why ") || ` ${lowered}`.includes(" why:")) {
    throw new InvariantError("I3: note must not infer motive (no why)");
  }
  return text;
}

function parseIso(ts) {
  if (typeof ts !== "string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(ts)) {
    throw new ReceiptError("timestamp must be UTC ISO-8601 with trailing Z (second precision)");
  }
  return Date.parse(ts);
}

function openClockOrLater(windowStart, openedAt) {
  if (!windowStart) return openedAt;
  if (parseIso(windowStart) < parseIso(openedAt)) {
    throw new InvariantError("I5: no backdated quiet — window_start must be open clock or later");
  }
  return windowStart;
}

function extendForwardOnly(previousEnd, windowEnd, windowStart) {
  if (!windowEnd) return previousEnd || null;
  if (parseIso(windowEnd) < parseIso(windowStart)) {
    throw new InvariantError("I5: window_end must be on or after window_start");
  }
  if (previousEnd && parseIso(windowEnd) < parseIso(previousEnd)) {
    throw new InvariantError("I5: extend forward only — window_end cannot move backward");
  }
  return windowEnd;
}

function newPlId() {
  const bytes = new Uint8Array(8);
  crypto.getRandomValues(bytes);
  return "pl_" + [...bytes].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function canonicalObject(record) {
  const payload = {};
  for (const key of HASH_FIELDS) payload[key] = record[key] == null ? null : record[key];
  payload.spec = SPEC;
  payload.transcript = ABSENT;
  payload.counterfactual_act = ABSENT;
  payload.inferred_motive = ABSENT;
  payload.actor = ACTOR;
  return payload;
}

function sortedJsonBytes(payload) {
  const keys = Object.keys(payload).sort();
  const raw = "{" + keys.map((k) => JSON.stringify(k) + ":" + JSON.stringify(payload[k])).join(",") + "}";
  return new TextEncoder().encode(raw);
}

async function sha256HexBytes(bytes) {
  const buf = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function digest(record) {
  return sha256HexBytes(sortedJsonBytes(canonicalObject(record)));
}

function closed(name, value, allowed) {
  const text = requireStr(name, value);
  if (!allowed.includes(text)) throw new ReceiptError(`${name} must be one of ${allowed.join(",")}`);
  return text;
}

async function createReceipt(fields) {
  assertNoLeakage(fields);
  const payload = {
    spec: SPEC,
    pl_id: fields.pl_id,
    mode: fields.mode == null ? null : fields.mode,
    state: fields.state == null ? null : fields.state,
    window_start: fields.window_start || null,
    window_end: fields.window_end || null,
    channel: fields.channel == null ? null : fields.channel,
    act_class: fields.act_class == null ? null : fields.act_class,
    duty_check: fields.duty_check || "NONE",
    actor: ACTOR,
    note: validateNote(fields.note),
    prev_hash: fields.prev_hash || GENESIS_PREV_HASH,
    opened_at: fields.opened_at || null,
    sealed_at: fields.sealed_at || null,
    broken_at: fields.broken_at || null,
    break_reason: fields.break_reason || null,
    transcript: ABSENT,
    counterfactual_act: ABSENT,
    inferred_motive: ABSENT,
    event_kind: fields.event_kind || "QUIET",
    file_sha256: fields.file_sha256 || null,
    file_name: fields.file_name || null,
    timestamp: fields.timestamp || null,
    date_stamp: fields.date_stamp || null,
    evidence_kind: fields.evidence_kind || null,
  };
  if (payload.event_kind === "QUIET") {
    payload.mode = closed("mode", payload.mode, MODES);
    payload.state = closed("state", payload.state, STATES);
    payload.act_class = closed("act_class", payload.act_class, ACT_CLASSES);
    payload.channel = requireStr("channel", payload.channel || "");
    if (!payload.channel.trim()) throw new ReceiptError("channel must be a non-empty string");
  } else {
    if (!payload.file_sha256 || !payload.file_name) throw new LedgerError("upload envelope requires file hash and basename");
    if (String(payload.file_name).includes("/") || String(payload.file_name).includes("\\")) {
      throw new ReceiptError("file_name must be a basename (no path)");
    }
    payload.timestamp = payload.timestamp || utcNow();
    payload.date_stamp = payload.date_stamp || utcDate(payload.timestamp);
    payload.evidence_kind = payload.evidence_kind || "operator_declared";
  }
  payload.receipt_hash = await digest(payload);
  return payload;
}

function parseLedger(body) {
  if (body == null) return [];
  let raw = body;
  if (typeof body === "string") {
    const text = body.trim();
    if (!text) return [];
    if (text.startsWith("[")) raw = JSON.parse(text);
    else {
      const rows = [];
      for (const line of text.split("\n")) {
        const t = line.trim();
        if (!t) continue;
        rows.push(JSON.parse(t));
      }
      return rows;
    }
  }
  if (Array.isArray(raw)) return raw;
  if (raw && typeof raw === "object") {
    if (Array.isArray(raw.ledger)) return raw.ledger;
    if (Array.isArray(raw.chain)) return raw.chain;
    if (Array.isArray(raw.receipts)) return raw.receipts;
  }
  return [];
}

function tipHash(ledger) {
  return ledger.length ? ledger[ledger.length - 1].receipt_hash : GENESIS_PREV_HASH;
}

function latestQuiet(ledger, plId, state) {
  let found = null;
  for (const rec of ledger) {
    if (rec.event_kind !== "QUIET") continue;
    if (rec.pl_id !== plId) continue;
    if (state && rec.state !== state) continue;
    found = rec;
  }
  return found;
}

async function recomputedHash(rec) {
  const copy = { ...rec };
  delete copy.receipt_hash;
  return digest(copy);
}

async function verify(ledger) {
  const errors = [];
  const n = ledger.length;
  const first = n ? ledger[0].receipt_hash : null;
  const last = n ? ledger[n - 1].receipt_hash : null;
  for (let i = 0; i < n; i++) {
    const rec = ledger[i];
    const expected = await recomputedHash(rec);
    if (rec.receipt_hash !== expected) {
      errors.push(`index ${i}: stored receipt_hash ${rec.receipt_hash} != recomputed ${expected}`);
    }
    if (rec.transcript !== ABSENT || rec.counterfactual_act !== ABSENT || rec.inferred_motive !== ABSENT) {
      errors.push(`index ${i}: I1–I3 leakage`);
    }
    if (i === 0) {
      if (rec.prev_hash !== GENESIS_PREV_HASH) errors.push(`index 0: prev_hash != GENESIS`);
      continue;
    }
    if (rec.prev_hash !== ledger[i - 1].receipt_hash) {
      errors.push(`index ${i}: prev_hash != previous.receipt_hash`);
    }
  }
  return { ok: errors.length === 0, length: n, first_hash: first, last_hash: last, errors };
}

async function verifyLattice(ledger, receiptErrors) {
  const errors = Array.isArray(receiptErrors) ? [...receiptErrors] : [];
  let quiet = 0;
  let envelopes = 0;
  const lastState = {};
  for (let i = 0; i < ledger.length; i++) {
    const rec = ledger[i];
    if (rec.event_kind === "UPLOAD_ENVELOPE") {
      envelopes += 1;
      if (!rec.timestamp || !rec.date_stamp || !rec.file_sha256) {
        errors.push(`index ${i}: upload envelope missing timestamp/date stamp/file hash`);
      }
      continue;
    }
    quiet += 1;
    if (rec.state === "BROKEN" && lastState[rec.pl_id] !== "SEALED") {
      errors.push(`index ${i}: I7/I8 break without SEALED`);
    }
    if (rec.state) lastState[rec.pl_id] = rec.state;
  }
  return {
    ok: errors.length === 0,
    length: ledger.length,
    quiet,
    envelopes,
    first_hash: ledger.length ? ledger[0].receipt_hash : null,
    last_hash: ledger.length ? ledger[ledger.length - 1].receipt_hash : null,
    errors,
    role: ROLE,
    note: "THIS IS: chosen silence / chosen inaction as a first-class receipt (PL-WP-0.1). THIS IS NOT: a gag-order kit, a wiretap, or third-party binding. HARD_DUTY cannot be bypassed. Author Aziel Eliab.",
  };
}

async function openWindow(body) {
  assertNoLeakage(body);
  const duty = body.duty_check || "NONE";
  refuseHardDuty(duty, "open");
  const ledger = parseLedger(body);
  const openedAt = body.opened_at || utcNow();
  const start = openClockOrLater(body.window_start || null, openedAt);
  const end = extendForwardOnly(null, body.window_end || null, start);
  const rec = await createReceipt({
    event_kind: "QUIET",
    pl_id: body.pl_id || newPlId(),
    mode: body.mode,
    state: "OPEN",
    window_start: start,
    window_end: end,
    channel: body.channel,
    act_class: body.act_class,
    duty_check: duty,
    note: body.note || "",
    prev_hash: tipHash(ledger),
    opened_at: openedAt,
  });
  return wrap("opened", rec, [...ledger, rec]);
}

async function sealWindow(body) {
  assertNoLeakage(body);
  const ledger = parseLedger(body);
  const current = latestQuiet(ledger, body.pl_id);
  if (!current || current.state !== "OPEN") throw new LedgerError(`no OPEN window for ${body.pl_id}; open first`);
  const check = body.duty_check || current.duty_check;
  refuseHardDuty(check, "seal");
  const sealedAt = body.sealed_at || utcNow();
  const start = current.window_start || current.opened_at || sealedAt;
  let proposedEnd = body.window_end;
  if (!proposedEnd) proposedEnd = sealedAt >= start ? sealedAt : start;
  const end = extendForwardOnly(current.window_end, proposedEnd, start);
  const rec = await createReceipt({
    event_kind: "QUIET",
    pl_id: current.pl_id,
    mode: current.mode,
    state: "SEALED",
    window_start: current.window_start,
    window_end: end,
    channel: current.channel,
    act_class: current.act_class,
    duty_check: check,
    note: body.note || current.note,
    prev_hash: tipHash(ledger),
    opened_at: current.opened_at,
    sealed_at: sealedAt,
  });
  return wrap("sealed", rec, [...ledger, rec]);
}

async function breakWindow(body) {
  const ledger = parseLedger(body);
  const current = latestQuiet(ledger, body.pl_id);
  if (!current) throw new LedgerError(`no quiet window for ${body.pl_id}`);
  if (current.state === "OPEN") throw new LedgerError("I7: break requires SEALED (OPEN → SEALED → optional BROKEN)");
  if (current.state === "BROKEN") throw new LedgerError(`${body.pl_id} is already BROKEN; original seal stays`);
  if (!BREAK_REASONS.includes(body.reason)) throw new ReceiptError("break_reason closed set");
  const rec = await createReceipt({
    event_kind: "QUIET",
    pl_id: current.pl_id,
    mode: current.mode,
    state: "BROKEN",
    window_start: current.window_start,
    window_end: current.window_end,
    channel: current.channel,
    act_class: current.act_class,
    duty_check: current.duty_check,
    note: body.note || current.note,
    prev_hash: tipHash(ledger),
    opened_at: current.opened_at,
    sealed_at: current.sealed_at,
    broken_at: body.broken_at || utcNow(),
    break_reason: body.reason,
  });
  return wrap("broken", rec, [...ledger, rec]);
}

async function uploadEnvelope(body) {
  assertNoLeakage(body);
  const ledger = parseLedger(body);
  let plId = body.pl_id;
  if (!plId) {
    for (let i = ledger.length - 1; i >= 0; i--) {
      if (ledger[i].event_kind === "QUIET") { plId = ledger[i].pl_id; break; }
    }
    if (!plId) plId = newPlId();
  }
  const rec = await createReceipt({
    event_kind: "UPLOAD_ENVELOPE",
    pl_id: plId,
    duty_check: "NONE",
    note: body.note || "",
    prev_hash: tipHash(ledger),
    file_sha256: body.file_sha256 || body.sha256,
    file_name: body.file_name || body.file || "envelope.bin",
    timestamp: body.timestamp || utcNow(),
    date_stamp: body.date_stamp || null,
    evidence_kind: "operator_declared",
  });
  return wrap("envelope", rec, [...ledger, rec]);
}

function wrap(action, rec, ledger) {
  return {
    product: PRODUCT,
    version: VERSION,
    motto: MOTTO,
    role: ROLE,
    author: AUTHOR,
    spec: SPEC,
    action,
    receipt: rec,
    ledger,
    chain: ledger,
  };
}

function openapiSpec() {
  const ledgerSchema = { oneOf: [{ type: "array", items: { type: "object" } }, { type: "string" }] };
  return {
    openapi: "3.1.0",
    info: {
      title: "PeaceLock runtime",
      version: VERSION,
      description: "Chosen silence / chosen inaction as a first-class receipt (PL-WP-0.1). Client sends the ledger JSON (stateless). Transcript always ABSENT. HARD_DUTY cannot be bypassed. Author " + AUTHOR + ". Suite mesh /v1/mesh/* PROXY to aziel-runtime (AZIEL_RUNTIME). Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 hub cite (local qnsd in qnm-node). Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Aziel Eliab only.",
    },
    servers: [{ url: HOST }],
    paths: {
      "/v1/skill": { get: { operationId: "peacelock_skill", summary: "Return skill markdown. FragGate LIVE_OPS. Does not increment download KV.", responses: { "200": { description: "markdown" } } } },
      "/v1/health": { get: { operationId: "health", summary: "Liveness. FragGate LIVE_OPS.", responses: { "200": { description: "ok" } } } },
      "/v1/doctor": { get: { operationId: "doctor", summary: "Worker-local self-check. No writes. Not a FragGate LIVE_OPS — catalog live ops are open/seal/break/show/verify/stamp/upload_envelope/health/skill.", responses: { "200": { description: "ok" } } } },
      "/v1/fraggate/list": { get: { operationId: "peacelock_fraggate_list_proxy", summary: "PROXY to aziel-runtime GET /v1/fraggate/list via AZIEL_RUNTIME. Not a local op.", responses: { "200": { description: "hashed registry" } } } },
      "/v1/fraggate/describe": { get: { operationId: "peacelock_fraggate_describe_proxy", summary: "PROXY to aziel-runtime GET /v1/fraggate/describe (?name= / ?slug=). Not a local op.", responses: { "200": { description: "describe" } } } },
      "/v1/fraggate/call": { post: { operationId: "peacelock_fraggate_call_proxy", summary: "PROXY to aziel-runtime POST /v1/fraggate/call via AZIEL_RUNTIME. Not a local op.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "FragGate ResultEnvelope" } } } },
      ...meshOpenApiPaths(),
      "/v1/open": { post: { operationId: "open", summary: "Open a quiet window. HARD_DUTY refused.", requestBody: { required: true, content: { "application/json": { schema: { type: "object", required: ["mode", "channel", "act_class"], properties: { mode: { type: "string" }, channel: { type: "string" }, act_class: { type: "string" }, duty_check: { type: "string" }, note: { type: "string" }, ledger: ledgerSchema } } } } }, responses: { "200": { description: "opened" } } } },
      "/v1/seal": { post: { operationId: "seal", summary: "Seal OPEN → SEALED. HARD_DUTY refused.", requestBody: { required: true, content: { "application/json": { schema: { type: "object", required: ["pl_id"], properties: { pl_id: { type: "string" }, ledger: ledgerSchema } } } } }, responses: { "200": { description: "sealed" } } } },
      "/v1/break": { post: { operationId: "break", summary: "Append BROKEN. Original seal stays.", requestBody: { required: true, content: { "application/json": { schema: { type: "object", required: ["pl_id", "reason"], properties: { pl_id: { type: "string" }, reason: { type: "string" }, ledger: ledgerSchema } } } } }, responses: { "200": { description: "broken" } } } },
      "/v1/show": { post: { operationId: "show", summary: "Return the client-held ledger.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "show" } } } },
      "/v1/verify": { post: { operationId: "verify", summary: "Walk hashes and links.", requestBody: { content: { "application/json": { schema: { type: "object", properties: { ledger: ledgerSchema } } } } }, responses: { "200": { description: "verify" } } } },
      "/v1/lattice": { post: { operationId: "lattice", summary: "Verify receipt links + state machine.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "lattice" } } } },
      "/v1/upload": { post: { operationId: "upload", summary: "Attach evidence envelope (file hash + timestamp + date stamp). No transcript.", requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { file_sha256: { type: "string" }, file_name: { type: "string" }, timestamp: { type: "string" }, date_stamp: { type: "string" }, ledger: ledgerSchema } } } } }, responses: { "200": { description: "envelope" } } } },
      "/v1/example": { get: { operationId: "example", summary: "Sample open payload.", responses: { "200": { description: "example" } } } },
      "/mcp": {
        get: { operationId: "peacelock_mcp_docs", summary: "Dual-surface MCP docs + FragGate pointer (slug peacelock).", responses: { "200": { description: "docs" } } },
        post: { operationId: "peacelock_mcp", summary: "JSON-RPC MCP-over-HTTP. Thin doubles of health/skill/open/seal/verify.", responses: { "200": { description: "rpc" } } },
      },
    },
  };
}

function aiHtml() {
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PeaceLock — Aziel Eliab · AI runtime</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1.25rem 3rem; background: #0b0b0b; color: #e8e0d0; }
  code { background: #151922; padding: .15rem .4rem; border-radius: 4px; }
  a { color: #e6d19a; }
  .motto { color: #c9a227; font-style: italic; }
  .brandrow{display:flex;align-items:center;gap:12px;margin:0 0 10px}
  .brandmark{width:40px;height:40px;border-radius:10px;object-fit:cover;flex:0 0 auto;box-shadow:0 0 0 1px #d4af3733}
  .stamp{margin:0;color:#c9a227;font-size:.88rem}
</style>
<body>
  <div class="brandrow">
    <img class="brandmark" src="/sigil.png" width="40" height="40" alt="" decoding="async">
    <p class="stamp">Aziel Eliab</p>
  </div>
  <h1>PeaceLock live API</h1>
  <p class="motto">${MOTTO}</p>
  <p>Chosen silence / chosen inaction as a first-class receipt. Stateless: send the ledger JSON in the body. Transcript is always ABSENT. HARD_DUTY cannot be bypassed. Author ${AUTHOR}.</p>
  <h2>Use with AI assistants</h2>
  <p>Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Author ${AUTHOR} only.</p>
  <h2>OpenAPI import</h2>
  <p>Paste this OpenAPI URL into GPT Actions, custom HTTP tools, Grok custom tools, or any other OpenAPI-capable assistant:</p>
  <p><code>${HOST}/openapi.json</code></p>
  <p>Custom tools can also point at <code>POST ${HOST}/v1/open</code>, <code>/v1/seal</code>, <code>/v1/break</code>, <code>/v1/verify</code>, <code>/v1/upload</code>.</p>
  <h2>MCP catalog</h2>
  <p>This Worker doubles the human buttons: <code>POST ${HOST}/mcp</code> (JSON-RPC <code>initialize</code>, <code>tools/list</code>, <code>tools/call</code>). Canonical catalog MCP remains <code>https://aziel-runtime.vibelock.workers.dev/mcp</code> (FragGate slug <code>peacelock</code>; catalog <code>mesh_*</code> + FragGate <code>slug=mesh</code>).</p>
  <p>Suite mesh: <code>GET ${HOST}/v1/mesh</code> PROXY to aziel-runtime. Default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity. Author: ${AUTHOR} only.</p>
  <p><a href="/openapi.json">openapi.json</a> · <a href="/mcp">/mcp</a> · <a href="/v1/health">health</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="/">PeaceLock software</a> · <a href="/cite.json">cite.json</a></p>
</body>
</html>`;
}

const CATALOG = "https://aziel-runtime.vibelock.workers.dev";
const FRAGGATE_CALL = CATALOG + "/v1/fraggate/call";
const CATALOG_MCP = CATALOG + "/mcp";
/** Catalog LIVE_OPS for slug peacelock. doctor is Worker-local — not in this list. */
const FRAGGATE_LIVE_OPS = ["open", "seal", "break", "show", "verify", "stamp", "upload_envelope", "health", "skill"];
const MCP_OPS = ["health", "skill", "open", "seal", "verify", "break", "show", "lattice", "upload", "doctor", "example"];
const MCP_TOOLS = MCP_OPS.map((op) => "peacelock_" + op);
const MCP_REFUSED = [
  "transcript", "transcribe", "motive", "counterfactual", "invent",
  "waive-duty", "bypass-duty", "waive_duty", "bypass_duty",
];

function mcpDocs() {
  return {
    ok: true,
    product: PRODUCT,
    version: VERSION,
    spec: SPEC,
    door: "fraggate",
    slug: "peacelock",
    identity: "Aziel Eliab only",
    author: AUTHOR,
    transport: "JSON-RPC MCP-over-HTTP",
    endpoint: "POST /mcp",
    methods: ["initialize", "tools/list", "tools/call", "ping"],
    auth: "none (public)",
    this_worker_mcp: HOST + "/mcp",
    catalog_mcp: CATALOG_MCP,
    catalog_openapi: CATALOG + "/openapi.json",
    worker_openapi: HOST + "/openapi.json",
    agent_path: FRAGGATE_CALL,
    this_worker_fraggate: HOST + "/v1/fraggate/call",
    body: { slug: "peacelock", op: "health", payload: {} },
    mesh: meshPointer(),
    mesh_body: { slug: "mesh", op: "status", payload: {} },
    ops: MCP_OPS,
    live_ops: FRAGGATE_LIVE_OPS,
    tools: MCP_TOOLS,
    note: "POST JSON-RPC here to double the human quiet-window buttons (health/skill/open/seal/break/show/verify). This Worker /v1/fraggate/* and /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. FragGate LIVE_OPS: open/seal/break/show/verify/stamp/upload_envelope/health/skill. doctor is Worker-local, not a catalog live op. Canonical agent path is the catalog MCP on aziel-runtime (FragGate slug peacelock). Catalog MCP mesh_* + FragGate slug=mesh. Suite mesh default OFF. QNM rollup live|locked|isolated. No Node Gate. No auto-heal. Not anonymity.",
    kv_increment: false,
    kernel: "https://github.com/AzielEliab/fraggate",
  };
}

function mcpInitialize() {
  return {
    protocolVersion: "2025-03-26",
    capabilities: { tools: { listChanged: false } },
    serverInfo: { name: "peacelock", version: VERSION },
    instructions:
      "PeaceLock PL-WP-0.1 — chosen silence / chosen inaction as a first-class receipt. Dual surface: human Worker UI and this MCP share health/skill/open/seal/break/show/verify. Transcript always ABSENT. HARD_DUTY cannot be bypassed. This Worker /v1/fraggate/* and /v1/mesh/* PROXY via AZIEL_RUNTIME. FragGate LIVE_OPS: open/seal/break/show/verify/stamp/upload_envelope/health/skill. doctor is Worker-local, not a catalog live op. Catalog MCP mesh_* + FragGate slug=mesh. Suite mesh default OFF. Canonical catalog agent path is POST " +
      CATALOG_MCP +
      " or FragGate POST " +
      FRAGGATE_CALL +
      " {slug:peacelock,op,payload}. Author Aziel Eliab only.",
  };
}

function mcpToolSchemas() {
  const ledger = { oneOf: [{ type: "array", items: { type: "object" } }, { type: "string" }] };
  return [
    { name: "peacelock_health", description: "Liveness. Same as GET /v1/health. Does not increment downloads.", inputSchema: { type: "object", properties: {} } },
    { name: "peacelock_skill", description: "Return PeaceLock skill markdown. Same as GET /v1/skill.", inputSchema: { type: "object", properties: {} } },
    { name: "peacelock_open", description: "Open a quiet window. HARD_DUTY refused. Same as POST /v1/open.", inputSchema: { type: "object", properties: { mode: { type: "string" }, channel: { type: "string" }, act_class: { type: "string" }, duty_check: { type: "string" }, note: { type: "string" }, ledger }, required: ["mode", "channel", "act_class"] } },
    { name: "peacelock_seal", description: "Seal OPEN → SEALED. HARD_DUTY refused. Same as POST /v1/seal.", inputSchema: { type: "object", properties: { pl_id: { type: "string" }, duty_check: { type: "string" }, note: { type: "string" }, ledger }, required: ["pl_id"] } },
    { name: "peacelock_verify", description: "Walk hashes and prev links. Same as POST /v1/verify.", inputSchema: { type: "object", properties: { ledger } } },
    { name: "peacelock_break", description: "Append BROKEN. Original seal stays. Same as POST /v1/break.", inputSchema: { type: "object", properties: { pl_id: { type: "string" }, reason: { type: "string" }, note: { type: "string" }, ledger }, required: ["pl_id", "reason"] } },
    { name: "peacelock_show", description: "Return the client-held ledger. Same as POST /v1/show.", inputSchema: { type: "object", properties: { pl_id: { type: "string" }, ledger } } },
    { name: "peacelock_lattice", description: "Verify receipt links + state machine. Same as POST /v1/lattice.", inputSchema: { type: "object", properties: { ledger } } },
    { name: "peacelock_upload", description: "Attach evidence envelope (file hash + timestamp + date stamp). Same as POST /v1/upload.", inputSchema: { type: "object", properties: { file_sha256: { type: "string" }, file_name: { type: "string" }, timestamp: { type: "string" }, date_stamp: { type: "string" }, ledger } } },
    { name: "peacelock_doctor", description: "Worker-local self-check. No writes. Same as GET /v1/doctor. Not a FragGate LIVE_OPS — UI Health maps to peacelock_health.", inputSchema: { type: "object", properties: {} } },
    { name: "peacelock_example", description: "Sample open payload. Same as GET /v1/example.", inputSchema: { type: "object", properties: {} } },
  ];
}

function resolveMcpOp(name) {
  if (typeof name !== "string" || !name) return null;
  const raw = name.trim();
  const stripped = raw.startsWith("peacelock_") ? raw.slice("peacelock_".length) : raw;
  if (stripped === "upload_envelope") return "upload";
  if (MCP_OPS.includes(stripped)) return stripped;
  return null;
}

function refusedMcpOp(name) {
  if (typeof name !== "string" || !name) return null;
  const raw = name.trim();
  const stripped = raw.startsWith("peacelock_") ? raw.slice("peacelock_".length) : raw;
  return MCP_REFUSED.includes(stripped) ? stripped : null;
}

async function runMcpOp(op, body) {
  const payload = body && typeof body === "object" ? body : {};
  if (op === "health") {
    return { ok: true, product: PRODUCT, version: VERSION, author: AUTHOR, role: ROLE, motto: MOTTO, spec: SPEC, kv_increment: false, door: "fraggate", slug: "peacelock", live_ops: FRAGGATE_LIVE_OPS, mesh: meshPointer(), note: "Hosted /v1 and /mcp do not store ledgers. Transcript is always ABSENT. FragGate LIVE_OPS: open/seal/break/show/verify/stamp/upload_envelope/health/skill. Suite mesh /v1/mesh/* PROXY to aziel-runtime. Default OFF." };
  }
  if (op === "skill") return { skill: SKILL };
  if (op === "doctor") {
    return { ok: true, product: PRODUCT, version: VERSION, author: AUTHOR, identity: "Aziel Eliab only", hard_duty: "refuse open and seal", transcript: ABSENT, network: false, worker_local: true, fraggate_live: false, note: "Worker-local self-check. Not a FragGate LIVE_OPS. UI Health maps to GET /v1/health." };
  }
  if (op === "example") {
    return { mode: "SILENCE", channel: "email", act_class: "reply", duty_check: "NONE", note: "window only", author: AUTHOR, spec: SPEC };
  }
  if (op === "open") return openWindow(payload);
  if (op === "seal") return sealWindow(payload);
  if (op === "break") return breakWindow(payload);
  if (op === "upload") return uploadEnvelope(payload);
  if (op === "show") {
    let ledger = parseLedger(payload);
    if (payload.pl_id) ledger = ledger.filter((r) => r.pl_id === payload.pl_id);
    return { product: PRODUCT, version: VERSION, author: AUTHOR, action: "show", ledger, length: ledger.length };
  }
  if (op === "verify") {
    const ledger = parseLedger(payload);
    return { product: PRODUCT, version: VERSION, motto: MOTTO, role: ROLE, author: AUTHOR, ...(await verify(ledger)) };
  }
  if (op === "lattice") {
    const ledger = parseLedger(payload);
    const rec = await verify(ledger);
    return { product: PRODUCT, version: VERSION, author: AUTHOR, ...(await verifyLattice(ledger, rec.errors)) };
  }
  throw new ReceiptError("unknown op");
}

async function callMcpTool(name, args) {
  const refused = refusedMcpOp(name);
  if (refused) {
    return {
      isError: true,
      content: [{
        type: "text",
        text: JSON.stringify({
          ok: false,
          error: "I1–I6 refuse: " + refused + " is not a PeaceLock op. Transcript, motive, and counterfactual stay ABSENT. HARD_DUTY cannot be bypassed.",
          code: "PL-REFUSE",
          door: "fraggate",
          slug: "peacelock",
        }, null, 2),
      }],
    };
  }
  const op = resolveMcpOp(name);
  if (!op) {
    return {
      isError: true,
      content: [{
        type: "text",
        text: JSON.stringify({
          ok: false,
          error: "Unknown MCP tool. Use peacelock_health, peacelock_skill, peacelock_open, peacelock_seal, peacelock_verify (plus break/show/lattice/upload/doctor). Canonical catalog MCP: " + CATALOG_MCP + " slug=peacelock.",
          door: "fraggate",
          slug: "peacelock",
          agent_path: FRAGGATE_CALL,
        }, null, 2),
      }],
    };
  }
  try {
    if (op === "skill") {
      return { content: [{ type: "text", text: SKILL }] };
    }
    const data = await runMcpOp(op, args);
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  } catch (err) {
    return {
      isError: true,
      content: [{
        type: "text",
        text: JSON.stringify({ ok: false, error: String(err.message || err), motto: MOTTO }, null, 2),
      }],
    };
  }
}

async function handleMcpJson(request) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }, 400);
  }
  const id = body && Object.prototype.hasOwnProperty.call(body, "id") ? body.id : null;
  const method = body && body.method;
  const params = (body && body.params) || {};
  if (method === "initialize") {
    return json({ jsonrpc: "2.0", id, result: mcpInitialize() });
  }
  if (method === "notifications/initialized" || method === "initialized") {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }
  if (method === "ping") {
    return json({ jsonrpc: "2.0", id, result: {} });
  }
  if (method === "tools/list") {
    return json({ jsonrpc: "2.0", id, result: { tools: mcpToolSchemas() } });
  }
  if (method === "tools/call") {
    const name = params.name;
    const args = params.arguments && typeof params.arguments === "object" ? params.arguments : {};
    return json({ jsonrpc: "2.0", id, result: await callMcpTool(name, args) });
  }
  return json({
    jsonrpc: "2.0",
    id,
    error: { code: -32601, message: "Method not found. Use initialize, tools/list, tools/call." },
  });
}

async function handleMcp(request) {
  if (request.method === "GET" || request.method === "HEAD") {
    if (request.method === "HEAD") return new Response(null, { status: 200, headers: corsHeaders() });
    return json(mcpDocs());
  }
  if (request.method === "POST") return handleMcpJson(request);
  return json({ error: "method not allowed", hint: "GET or POST /mcp" }, 405);
}

function runtimeFetcher(env) {
  if (env && env.AZIEL_RUNTIME && typeof env.AZIEL_RUNTIME.fetch === "function") return env.AZIEL_RUNTIME;
  return null;
}

function isMeshCitePath(pathname) {
  const path = String(pathname || "").replace(/\/+$/, "") || "/";
  return path === "/v1/mesh" || path === "/v1/mesh/status" || path === "/v1/mesh/nodes";
}

/** Attach QNS-CD-1.0 hub cite to mesh GET JSON. Does not enable mesh or proxy qnsd. */
async function decorateMeshCite(request, pathname, res, headers) {
  if (request.method === "HEAD" || request.method !== "GET") return null;
  if (!isMeshCitePath(pathname)) return null;
  const ctype = String(headers.get("content-type") || "").toLowerCase();
  if (!ctype.includes("json")) return null;
  try {
    const body = await res.clone().json();
    headers.delete("content-length");
    headers.set("X-Aziel-Qns-Cd", "QNS-CD-1.0");
    return new Response(JSON.stringify(attachQnsCd(body), null, 2), {
      status: res.status,
      statusText: res.statusText,
      headers,
    });
  } catch {
    return null;
  }
}

async function proxyDoor(request, url, env) {
  const dest = doorTargetUrl(url.pathname, request.url, env);
  if (!dest) {
    return json({ ok: false, error: "not a door path", path: url.pathname, door: "fraggate" }, 404);
  }
  const headers = new Headers();
  const pass = ["content-type", "accept", "authorization", "user-agent", "mcp-protocol-version", "mcp-session-id", "x-aziel-runtime-token"];
  for (const name of pass) {
    const v = request.headers.get(name);
    if (v) headers.set(name, v);
  }
  if (!headers.has("User-Agent")) headers.set("User-Agent", "Mozilla/5.0 PeaceLock/0.1.0");
  const init = { method: request.method, headers, redirect: "follow" };
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
    init.duplex = "half";
  }
  try {
    const fetcher = runtimeFetcher(env);
    const res = fetcher ? await fetcher.fetch(dest, init) : await fetch(dest, init);
    const outHeaders = new Headers(res.headers);
    for (const [k, v] of Object.entries(corsHeaders())) outHeaders.set(k, v);
    outHeaders.set("X-Aziel-Door", "proxy");
    outHeaders.set("X-Aziel-Door-Origin", dest);
    const decorated = await decorateMeshCite(request, url.pathname, res, outHeaders);
    if (decorated) return decorated;
    return new Response(res.body, { status: res.status, statusText: res.statusText, headers: outHeaders });
  } catch (exc) {
    return json({
      ok: false,
      error: "fraggate_proxy_failed",
      detail: String(exc).slice(0, 240),
      origin: dest,
      agent_path: FRAGGATE_CALL,
      door: "fraggate",
      slug: "peacelock",
    }, 502);
  }
}

export async function handleRuntimeApi(request, url, env) {
  const stripped = url.pathname.replace(/\/+$/, "") || "/";
  if (stripped === "/mcp") {
    try {
      return await handleMcp(request);
    } catch (err) {
      const status = err instanceof HardDutyError ? 409 : 400;
      return json({ error: String(err.message || err), motto: MOTTO, ok: false }, status);
    }
  }
  const classified = classifyV1Path(url.pathname);
  if (classified.kind === "door") {
    return proxyDoor(request, url, env);
  }
  const path = url.pathname;
  const isApi = path === "/v1" || path.startsWith("/v1/") || path === "/openapi.json" || path === "/ai";
  if (!isApi) return null;
  if (classified.kind === "multi") {
    return json({
      ok: false,
      error: "not a local op",
      code: "NOT_LOCAL_OP",
      path: classified.path,
      hint: "Local ops are GET|POST /v1/{op} only (single segment). FragGate door is /v1/fraggate/list, /v1/fraggate/describe, /v1/fraggate/call (proxied to aziel-runtime via AZIEL_RUNTIME). Suite mesh is /v1/mesh/* (proxied to aziel-runtime; default OFF).",
      agent_path: FRAGGATE_CALL,
      live_ops: FRAGGATE_LIVE_OPS,
    }, 404);
  }
  try {
    if (path === "/v1/health" && request.method === "GET") {
      return json({ ok: true, product: PRODUCT, version: VERSION, author: AUTHOR, role: ROLE, motto: MOTTO, spec: SPEC, door: "fraggate", slug: "peacelock", live_ops: FRAGGATE_LIVE_OPS, mesh: meshPointer(), note: "Hosted /v1 does not store ledgers. Transcript is always ABSENT. FragGate LIVE_OPS: open/seal/break/show/verify/stamp/upload_envelope/health/skill. Suite mesh /v1/mesh/* PROXY to aziel-runtime. Default OFF." });
    }
    if (path === "/v1/skill" && request.method === "GET") {
      return new Response(SKILL, { status: 200, headers: { "Content-Type": "text/markdown; charset=utf-8", "Cache-Control": "private, no-store", ...corsHeaders() } });
    }
    if (path === "/openapi.json" && request.method === "GET") return json(openapiSpec());
    if (path === "/ai" && request.method === "GET") {
      return new Response(aiHtml(), { headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() } });
    }
    if (path === "/v1/doctor" && request.method === "GET") {
      return json({ ok: true, product: PRODUCT, version: VERSION, author: AUTHOR, identity: "Aziel Eliab only", hard_duty: "refuse open and seal", transcript: ABSENT, network: false, worker_local: true, fraggate_live: false, note: "Worker-local self-check. Not a FragGate LIVE_OPS. UI Health maps to GET /v1/health." });
    }
    if (path === "/v1/example" && request.method === "GET") {
      return json({ mode: "SILENCE", channel: "email", act_class: "reply", duty_check: "NONE", note: "window only", author: AUTHOR, spec: SPEC });
    }
    async function readBody() {
      try { return await request.json(); } catch { return {}; }
    }
    if (path === "/v1/open" && request.method === "POST") return json(await openWindow(await readBody()));
    if (path === "/v1/seal" && request.method === "POST") return json(await sealWindow(await readBody()));
    if (path === "/v1/break" && request.method === "POST") return json(await breakWindow(await readBody()));
    if (path === "/v1/upload" && request.method === "POST") return json(await uploadEnvelope(await readBody()));
    if (path === "/v1/show" && request.method === "POST") {
      const body = await readBody();
      let ledger = parseLedger(body);
      if (body.pl_id) ledger = ledger.filter((r) => r.pl_id === body.pl_id);
      return json({ product: PRODUCT, version: VERSION, author: AUTHOR, action: "show", ledger, length: ledger.length });
    }
    if (path === "/v1/verify" && request.method === "POST") {
      const ledger = parseLedger(await readBody());
      return json({ product: PRODUCT, version: VERSION, motto: MOTTO, role: ROLE, author: AUTHOR, ...(await verify(ledger)) });
    }
    if (path === "/v1/lattice" && request.method === "POST") {
      const ledger = parseLedger(await readBody());
      const rec = await verify(ledger);
      return json({ product: PRODUCT, version: VERSION, author: AUTHOR, ...(await verifyLattice(ledger, rec.errors)) });
    }
    return json({ error: "not found", hint: "GET /v1/health GET /v1/skill POST /v1/{open,seal,break,show,verify} GET /v1/fraggate/list GET /v1/fraggate/describe POST /v1/fraggate/call GET /v1/mesh", live_ops: FRAGGATE_LIVE_OPS }, 404);
  } catch (err) {
    const status = err instanceof HardDutyError ? 409 : 400;
    return json({ error: String(err.message || err), motto: MOTTO, ok: false }, status);
  }
}
