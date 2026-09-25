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
    color-scheme: light;
    --bg: #f7f4ec;
    --panel: #fffdf8;
    --ink: #1c1914;
    --muted: #5e5648;
    --line: #e3d9c4;
    --gold: #c9a227;
    --gold-ink: #1c1914;
    --bad: #8c2f2c;
    --bad-bg: #f8ecea;
    --pass: #1d6b3a;
    --pass-bg: #e7f5ec;
    --shadow: 0 1px 2px rgba(28, 25, 20, 0.06);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      color-scheme: dark;
      --bg: #12110e;
      --panel: #1c1b16;
      --ink: #f4efe4;
      --muted: #c8bfae;
      --line: #3a3428;
      --gold: #c9a227;
      --gold-ink: #1c1914;
      --bad: #f0b4ae;
      --bad-bg: #2a1816;
      --pass: #9ed7b0;
      --pass-bg: #16261c;
      --shadow: none;
    }
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0; background: var(--bg); color: var(--ink);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    line-height: 1.5;
  }
  body {
    max-width: 40rem; margin: 0 auto;
    padding: 2rem 1.25rem 3.5rem;
  }
  header { margin: 0 0 1.25rem; }
  .brand {
    margin: 0; font-size: 0.78rem; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--muted); font-weight: 650;
  }
  h1 { font-size: 1.85rem; font-weight: 650; letter-spacing: -0.02em; margin: 0.2rem 0 0.4rem; }
  .lede { margin: 0; color: var(--muted); max-width: 38rem; }
  .card {
    background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
    padding: 1.15rem 1.15rem 1.25rem; margin: 0 0 0.9rem;
    box-shadow: var(--shadow);
  }
  label { display: block; font-size: 0.92rem; font-weight: 600; margin: 0.85rem 0 0.35rem; }
  label:first-child { margin-top: 0; }
  textarea, input[type="text"], input[type="file"], select {
    width: 100%; max-width: 100%; padding: 0.6rem 0.7rem;
    border: 1px solid var(--line); border-radius: 8px;
    background: var(--bg); color: var(--ink); font: inherit;
  }
  .actions { display: flex; gap: 0.6rem; flex-wrap: wrap; margin: 1rem 0 0; }
  button {
    font: inherit; font-weight: 650; min-height: 2.75rem;
    padding: 0.55rem 1rem; border-radius: 10px;
    border: 1px solid var(--gold); background: var(--gold); color: var(--gold-ink);
    cursor: pointer;
  }
  button.ghost {
    background: transparent; color: var(--ink); border-color: var(--line); font-weight: 600;
  }
  button:focus-visible, select:focus-visible, input:focus-visible,
  summary:focus-visible, a:focus-visible {
    outline: 2px solid var(--gold); outline-offset: 2px;
  }
  .status {
    margin: 0 0 1rem; padding: 0.8rem 0.95rem; border-radius: 12px;
    border: 1px solid var(--line); background: var(--panel);
  }
  .status.ok { color: var(--pass); background: var(--pass-bg); border-color: transparent; }
  .status.bad { color: var(--bad); background: var(--bad-bg); border-color: transparent; }
  details {
    background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
    padding: 0.35rem 1rem 0.9rem; margin: 0 0 0.9rem;
  }
  summary {
    cursor: pointer; font-weight: 650; padding: 0.7rem 0; min-height: 2.75rem;
    display: flex; align-items: center;
  }
  .hint { color: var(--muted); margin: 0.2rem 0 0.6rem; font-size: 0.95rem; }
  pre {
    background: var(--bg); color: var(--ink); border: 1px solid var(--line);
    padding: 0.75rem 0.85rem; border-radius: 8px; font-size: 0.78rem;
    white-space: pre-wrap; word-break: break-word; margin: 0.8rem 0 0;
  }
  footer { color: var(--muted); font-size: 0.9rem; margin-top: 0.4rem; }
  @media (max-width: 480px) {
    body { padding: 1.15rem 1rem 2.5rem; }
    h1 { font-size: 1.55rem; }
    .actions { flex-direction: column; }
    button { width: 100%; }
  }
</style>
</head>
<body>
  <header>
    <p class="brand">PeaceLock</p>
    <h1>Quiet window</h1>
    <p class="lede">Record a silence or an inaction you chose, as a receipt on this computer.</p>
  </header>
  <p id="status" class="status" role="status">No quiet window yet. Choose Open quiet window when you are ready.</p>
  <section class="card">
    <label for="mode">What you are keeping</label>
    <select id="mode">
      <option value="SILENCE">Silence</option>
      <option value="INACTION">Inaction</option>
      <option value="BOTH">Silence and inaction</option>
    </select>
    <label for="channel">Where</label>
    <input id="channel" type="text" value="email" autocomplete="off">
    <label for="act_class">Kind of act</label>
    <select id="act_class">
      <option value="reply">Reply</option>
      <option value="file">File</option>
      <option value="post">Post</option>
      <option value="call">Call</option>
      <option value="attend">Attend</option>
      <option value="sign">Sign</option>
      <option value="pay">Pay</option>
      <option value="transfer">Transfer</option>
      <option value="delete">Delete</option>
      <option value="other">Other</option>
    </select>
    <div class="actions">
      <button type="button" id="btn-open">Open quiet window</button>
      <button type="button" class="ghost" id="btn-verify">Check ledger</button>
    </div>
  </section>
  <details>
    <summary>Advanced</summary>
    <p class="hint">Seal, break, list, and file hash. The first screen only opens a window.</p>
    <label for="duty">Duty check</label>
    <select id="duty">
      <option value="NONE">None</option>
      <option value="ADVISORY">Advisory</option>
      <option value="HARD_DUTY">HARD_DUTY</option>
    </select>
    <label for="note">Note (140 characters or fewer)</label>
    <input id="note" type="text" maxlength="140" placeholder="Optional">
    <label for="pl_id">Window id</label>
    <input id="pl_id" type="text" placeholder="Filled in after you open a window" autocomplete="off">
    <label for="reason">If the window ended</label>
    <select id="reason">
      <option value="speech_occurred">Speech occurred</option>
      <option value="act_occurred">An act occurred</option>
      <option value="operator_void">You voided it</option>
      <option value="duty_conflict">Duty conflict</option>
    </select>
    <div class="actions">
      <button type="button" id="btn-seal">Seal window</button>
      <button type="button" class="ghost" id="btn-break">Record a break</button>
      <button type="button" class="ghost" id="btn-show">List receipts</button>
    </div>
    <label for="file">File to hash</label>
    <input type="file" id="file">
    <div class="actions">
      <button type="button" id="btn-upload">Attach file</button>
      <button type="button" class="ghost" id="btn-export">Export ledger</button>
      <button type="button" class="ghost" id="btn-health">App status</button>
      <button type="button" class="ghost" id="btn-skill">Skill note</button>
    </div>
    <pre id="out" hidden></pre>
  </details>
  <details>
    <summary>About</summary>
    <p class="hint">Author: Aziel Eliab. A receipt stores no transcript. Those fields stay ABSENT. HARD_DUTY refuses and writes nothing.</p>
    <p class="hint">__HONEST__</p>
  </details>
  <footer>Aziel Eliab</footer>
<script>
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
function humanError(msg) {
  if (/HARD_DUTY/i.test(msg)) return "A hard duty check refuses this and writes nothing.";
  if (/no OPEN window|open first/i.test(msg)) return "There is no open window with that id.";
  if (/no quiet window/i.test(msg)) return "That window id is not in this ledger.";
  if (/already BROKEN/i.test(msg)) return "This window is already recorded as broken. The sealed receipt stays.";
  if (/break requires SEALED/i.test(msg)) return "Seal the window before recording a break.";
  if (/Choose a file/i.test(msg)) return "Choose a file.";
  return msg;
}
function plain(data) {
  if (data.error) return humanError(String(data.error));
  if (data.action === "opened") {
    var id = data.receipt && data.receipt.pl_id;
    return id ? "Quiet window open. Id " + id + "." : "Quiet window open.";
  }
  if (data.action === "sealed") return "Window sealed. The receipt is in the ledger.";
  if (data.action === "broken") return "Recorded as broken. The earlier seal stays in the ledger.";
  if (data.action === "show") {
    var n = data.length || 0;
    return n === 1 ? "1 receipt in this ledger." : n + " receipts in this ledger.";
  }
  if (data.action === "verify") return data.ok ? "Ledger checks out." : "Ledger check failed.";
  if (data.action === "envelope") return "File hash attached to the ledger.";
  if (data.action === "health") return "This app is running on this computer.";
  if (data.action === "skill") return "PeaceLock records a quiet window you chose.";
  if (data.action === "export") return "Export is ready in the response below.";
  return "Done.";
}
function nextStep(message) {
  var msg = String(message || "");
  if (/HARD_DUTY/i.test(msg)) return " Nothing was written. Set duty check to None, then try again.";
  if (/pl_id|open first|no OPEN|window id/i.test(msg)) return " Open a quiet window first. Its id is filled in for you.";
  if (/file|choose/i.test(msg)) return " Choose a file, then choose Attach file.";
  return " Try Open quiet window, or open About.";
}
function show(data, kind) {
  var el = document.getElementById("status");
  el.className = "status" + (kind ? " " + kind : "");
  var message = plain(data);
  if (kind === "bad") message += nextStep(data.error || message);
  el.textContent = message;
  el.scrollIntoView({block: "nearest"});
  var out = document.getElementById("out");
  out.hidden = false;
  out.textContent = JSON.stringify(data, null, 2);
  if (data.receipt && data.receipt.pl_id) document.getElementById("pl_id").value = data.receipt.pl_id;
}
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
  if (!f) { show({error: "Choose a file"}, "bad"); return; }
  var buf = await f.arrayBuffer();
  var hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", buf))].map(function (b) {
    return b.toString(16).padStart(2, "0");
  }).join("");
  run("/upload", {file_name: f.name, file_sha256: hash});
};
</script>
</body>
</html>
"""


def wants_json(accept: str | None) -> bool:
    """True when the caller prefers application/json over text/html."""
    if not accept:
        return False
    ranked: list[tuple[float, int, str]] = []
    for index, raw in enumerate(accept.split(",")):
        item = raw.strip()
        if not item:
            continue
        quality = 1.0
        if ";q=" in item:
            media, _, qv = item.partition(";q=")
            item = media.strip()
            try:
                quality = float(qv.split(";")[0].strip())
            except ValueError:
                quality = 0.0
        else:
            item = item.split(";")[0].strip()
        ranked.append((quality, -index, item.lower()))
    ranked.sort(reverse=True)
    for _, _, media in ranked:
        if media in {"application/json", "text/html", "*/*"}:
            return media == "application/json"
    return False


def render_page() -> str:
    return PAGE.replace("__HONEST__", HONEST_SCOPE)


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
        path = urlparse(self.path).path
        if path not in ("/", "/index.html"):
            if wants_json(self.headers.get("Accept")):
                self._json({"ok": False, "error": "not found"}, 404)
            else:
                self.send_error(404)
            return
        if wants_json(self.headers.get("Accept")):
            ledger: Ledger = self.server.ledger  # type: ignore[attr-defined]
            self._json({
                "ok": True,
                "product": "peacelock",
                "version": __version__,
                "author": "Aziel Eliab",
                "loopback": True,
                "ledger_length": len(ledger),
            })
            return
        raw = render_page().encode("utf-8")
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
    print(f"Open http://{host}:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
