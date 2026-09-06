"""Localhost UI for PeaceLock. Binds 127.0.0.1. Ledger lives in a process tmp dir."""

from __future__ import annotations

import json
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from peacelock import __version__
from peacelock.chain import Ledger
from peacelock.errors import PeaceLockError
from peacelock.lattice import HONEST_SCOPE, walk

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8768
LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})
MAX_BODY = 2 * 1024 * 1024

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PeaceLock</title>
<style>
  :root {
    --bg: #0b0b0b; --panel: #141414; --ink: #e8e0d0; --muted: #8a7219;
    --line: #2a2414; --gold: #c9a227; --focus: #e6d19a; --bad: #d4534b;
    --pass: #3dba7a;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0; background: var(--bg); color: var(--ink);
    font-family: system-ui, "Segoe UI", sans-serif; line-height: 1.45;
  }
  body { max-width: 48rem; margin: 0 auto; padding: 2.1rem 1.2rem 4rem; }
  .tag {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.72rem;
    letter-spacing: 0.14em; text-transform: uppercase; color: var(--gold);
  }
  h1 { font-size: 2rem; font-weight: 650; letter-spacing: 0.04em; margin: 0.35rem 0 0.25rem; }
  .motto { color: var(--gold); font-style: italic; margin: 0 0 0.85rem; font-size: 1.05rem; }
  .lede { color: #b8b09a; margin: 0 0 1.5rem; max-width: 42rem; }
  fieldset {
    border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
    padding: 1.1rem 1.15rem 1.2rem; margin: 0 0 1rem;
  }
  legend {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.72rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--gold); padding: 0 0.4rem;
  }
  label { display: block; font-size: 0.92rem; margin: 0.85rem 0 0.3rem; }
  textarea, input[type="text"], select {
    width: 100%; padding: 0.55rem 0.65rem; border: 1px solid var(--line);
    border-radius: 6px; background: #101010; color: var(--ink); font: inherit;
  }
  .row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem; }
  .actions { display: flex; gap: 0.65rem; flex-wrap: wrap; margin: 0.9rem 0 0; }
  button {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.85rem;
    letter-spacing: 0.04em; padding: 0.65rem 1rem; border-radius: 8px;
    border: 1px solid var(--gold); background: var(--gold); color: var(--bg);
    cursor: pointer; font-weight: 650;
  }
  button.ghost { background: transparent; color: var(--ink); border-color: var(--line); }
  .banner {
    border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c;
    padding: 0.85rem 1rem; border-radius: 10px; margin: 0 0 1.15rem; font-size: 0.92rem;
  }
  .status { margin: 0 0 0.8rem; padding: 0.75rem 0.85rem; border-radius: 10px; border: 1px solid var(--line); }
  .status.ok { color: var(--pass); border-color: #2f6b48; }
  .status.bad { color: var(--bad); border-color: #7a2f2c; }
  pre { background: #101010; padding: 0.75rem 0.9rem; overflow: auto; border-radius: 8px; font-size: 0.78rem; }
  .hash { font-size: 0.72rem; word-break: break-all; color: #9a9278; }
</style>
</head>
<body>
  <p class="tag">PeaceLock · PL-WP-0.1 · Aziel Eliab</p>
  <h1>PeaceLock</h1>
  <p class="motto">Chosen silence / chosen inaction as a first-class receipt.</p>
  <p class="lede">Loopback only. Transcript is always ABSENT. HARD_DUTY cannot be bypassed. Not a gag-order kit.</p>
  <p class="banner">__HONEST__</p>
  <div id="status" class="status">No quiet window yet. Open writes the first lattice node.</div>
  <fieldset>
    <legend>Use</legend>
    <div class="row2">
      <div>
        <label>Mode</label>
        <select id="mode"><option>SILENCE</option><option>INACTION</option><option>BOTH</option></select>
      </div>
      <div>
        <label>act_class</label>
        <select id="act_class">
          <option>reply</option><option>file</option><option>post</option><option>call</option>
          <option>attend</option><option>sign</option><option>pay</option><option>transfer</option>
          <option>delete</option><option>other</option>
        </select>
      </div>
    </div>
    <div class="row2">
      <div>
        <label>Channel</label>
        <input id="channel" type="text" value="email">
      </div>
      <div>
        <label>duty_check</label>
        <select id="duty"><option>NONE</option><option>ADVISORY</option><option>HARD_DUTY</option></select>
      </div>
    </div>
    <label>Note ≤140 (no why)</label>
    <input id="note" type="text" maxlength="140" placeholder="optional operator note">
    <label>pl_id (for seal / break)</label>
    <input id="pl_id" type="text" placeholder="filled after open">
    <label>break_reason</label>
    <select id="reason">
      <option>speech_occurred</option><option>act_occurred</option>
      <option>operator_void</option><option>duty_conflict</option>
    </select>
    <div class="actions">
      <button type="button" id="btn-open">Open</button>
      <button type="button" id="btn-seal">Seal</button>
      <button type="button" class="ghost" id="btn-break">Break</button>
      <button type="button" class="ghost" id="btn-show">Show</button>
      <button type="button" class="ghost" id="btn-verify">Verify</button>
      <button type="button" class="ghost" id="btn-health">Health</button>
      <button type="button" class="ghost" id="btn-skill">Skill</button>
    </div>
  </fieldset>
  <fieldset>
    <legend>Upload envelope</legend>
    <p class="lede">Hashes file bytes. Stores timestamp + date stamp. Does not store unspoken words.</p>
    <input type="file" id="file">
    <div class="actions">
      <button type="button" id="btn-upload">Attach envelope</button>
      <button type="button" class="ghost" id="btn-export">Export JSONL</button>
    </div>
  </fieldset>
  <pre id="out">{}</pre>
<script>
async function api(path, body) {
  var res = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body || {})
  });
  var data = await res.json();
  if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
  return data;
}
function fields() {
  return {
    mode: document.getElementById("mode").value,
    act_class: document.getElementById("act_class").value,
    channel: document.getElementById("channel").value,
    duty_check: document.getElementById("duty").value,
    note: document.getElementById("note").value,
    pl_id: document.getElementById("pl_id").value,
    reason: document.getElementById("reason").value
  };
}
function show(data, kind) {
  var el = document.getElementById("status");
  el.className = "status" + (kind ? " " + kind : "");
  el.textContent = data.error || data.message || JSON.stringify(data.action || data.ok);
  document.getElementById("out").textContent = JSON.stringify(data, null, 2);
  if (data.receipt && data.receipt.pl_id) document.getElementById("pl_id").value = data.receipt.pl_id;
}
async function run(path, extra) {
  try { show(await api(path, Object.assign(fields(), extra || {})), "ok"); }
  catch (err) { show({error: String(err.message || err)}, "bad"); }
}
document.getElementById("btn-open").onclick = function () { run("/open"); };
document.getElementById("btn-seal").onclick = function () { run("/seal"); };
document.getElementById("btn-break").onclick = function () { run("/break"); };
document.getElementById("btn-show").onclick = function () { run("/show"); };
document.getElementById("btn-verify").onclick = function () { run("/verify"); };
document.getElementById("btn-health").onclick = function () { run("/health"); };
document.getElementById("btn-skill").onclick = function () { run("/skill"); };
document.getElementById("btn-export").onclick = function () { run("/export"); };
document.getElementById("btn-upload").onclick = async function () {
  var f = document.getElementById("file").files[0];
  if (!f) { show({error: "choose a file"}, "bad"); return; }
  var buf = await f.arrayBuffer();
  var hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", buf))].map(b => b.toString(16).padStart(2,"0")).join("");
  run("/upload", {file_name: f.name, file_sha256: hash});
};
</script>
</body>
</html>
"""


class _Handler(BaseHTTPRequestHandler):
    server_version = "PeaceLockUI/0.1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("peacelock-ui: " + (fmt % args) + "\n")

    def _json(self, body: dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(body, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict[str, Any]:
        n = int(self.headers.get("Content-Length") or "0")
        if n > MAX_BODY:
            raise PeaceLockError("body too large")
        raw = self.rfile.read(n) if n else b"{}"
        data = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(data, dict):
            raise PeaceLockError("JSON object required")
        return data

    def do_GET(self) -> None:  # noqa: N802
        if urlparse(self.path).path not in ("/", "/index.html"):
            self.send_error(404)
            return
        page = PAGE.replace("__HONEST__", HONEST_SCOPE)
        raw = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        ledger: Ledger = self.server.ledger  # type: ignore[attr-defined]
        try:
            body = self._read_json()
            if path == "/open":
                rec = ledger.open(
                    mode=str(body.get("mode") or "SILENCE"),
                    channel=str(body.get("channel") or "desk"),
                    act_class=str(body.get("act_class") or "other"),
                    duty_check=str(body.get("duty_check") or "NONE"),
                    note=str(body.get("note") or ""),
                )
                return self._json({"ok": True, "action": "opened", "receipt": rec.to_dict(), "version": __version__})
            if path == "/seal":
                rec = ledger.seal(
                    pl_id=str(body.get("pl_id") or ""),
                    duty_check=body.get("duty_check"),
                    note=str(body.get("note") or ""),
                )
                return self._json({"ok": True, "action": "sealed", "receipt": rec.to_dict()})
            if path == "/break":
                rec = ledger.break_window(
                    pl_id=str(body.get("pl_id") or ""),
                    reason=str(body.get("reason") or "operator_void"),
                    note=str(body.get("note") or ""),
                )
                return self._json({"ok": True, "action": "broken", "receipt": rec.to_dict()})
            if path == "/show":
                rows = [r.to_dict() for r in ledger.show(body.get("pl_id"))]
                return self._json({"ok": True, "action": "show", "ledger": rows, "length": len(rows)})
            if path == "/verify":
                result = ledger.verify()
                lat = walk(ledger)
                return self._json({
                    "ok": result.ok and lat.ok,
                    "action": "verify",
                    "length": result.length,
                    "first_hash": result.first_hash,
                    "last_hash": result.last_hash,
                    "errors": result.errors + lat.errors,
                    "lattice": {"quiet": lat.quiet, "envelopes": lat.envelopes},
                })
            if path == "/upload":
                rec = ledger.upload_envelope(
                    file_sha256_hex=str(body.get("file_sha256") or ""),
                    file_name=str(body.get("file_name") or "envelope.bin"),
                    pl_id=body.get("pl_id") or None,
                    note=str(body.get("note") or ""),
                )
                return self._json({"ok": True, "action": "envelope", "receipt": rec.to_dict()})
            if path == "/health":
                return self._json({
                    "ok": True,
                    "action": "health",
                    "product": "peacelock",
                    "version": __version__,
                    "author": "Aziel Eliab",
                    "door": "fraggate",
                    "note": "Local UI health. Catalog FragGate op is health. peacelock doctor remains CLI-only — not a FragGate LIVE_OPS.",
                })
            if path == "/skill":
                return self._json({
                    "ok": True,
                    "action": "skill",
                    "product": "peacelock",
                    "author": "Aziel Eliab",
                    "skill": "PeaceLock PL-WP-0.1. Transcript always ABSENT. HARD_DUTY cannot be bypassed. Catalog LIVE_OPS: open/seal/break/show/verify/stamp/upload_envelope/health/skill.",
                })
            if path == "/doctor":
                from peacelock.doctor import run_doctor
                import io

                buf = io.StringIO()
                old = sys.stdout
                sys.stdout = buf
                try:
                    rc = run_doctor(as_json=True)
                finally:
                    sys.stdout = old
                payload = json.loads(buf.getvalue() or "{}")
                payload["exit"] = rc
                payload["worker_local"] = True
                payload["fraggate_live"] = False
                payload["note"] = "CLI/local self-check. Not a FragGate LIVE_OPS. UI Health maps to /health."
                return self._json(payload, 200 if rc == 0 else 400)
            if path == "/export":
                return self._json({"ok": True, "action": "export", "jsonl": ledger.export_jsonl()})
            return self._json({"error": "not found"}, 404)
        except PeaceLockError as exc:
            self._json({"error": str(exc), "ok": False}, 400)
        except Exception as exc:  # noqa: BLE001
            self._json({"error": str(exc), "ok": False}, 400)


class _Server(ThreadingHTTPServer):
    def __init__(self, host: str, port: int, ledger: Ledger) -> None:
        super().__init__((host, port), _Handler)
        self.ledger = ledger


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    if host not in LOOPBACK:
        raise PeaceLockError("UI binds loopback only")
    tmp = Path(tempfile.mkdtemp(prefix="peacelock-ui-"))
    ledger = Ledger((), path=tmp / "peacelock_ledger.jsonl")
    httpd = _Server(host, port, ledger)
    print(f"PeaceLock UI  http://{host}:{port}  (loopback only)")
    print("Author: Aziel Eliab. Transcript is always ABSENT.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
