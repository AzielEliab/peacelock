/**
 * PeaceLock product homepage — software UI, not a downloads shell.
 * Author: Aziel Eliab only. Apache-2.0. Forks welcome.
 * No Zenodo DOI is invented here.
 */

const HOST = "https://peacelock-download-tracker.vibelock.workers.dev";
const GITHUB_REPO = "https://github.com/AzielEliab/peacelock";
const GITHUB_LATEST = "https://github.com/AzielEliab/peacelock/releases/latest";
const CATALOG = "https://aziel-runtime.vibelock.workers.dev/";
const CATALOG_PRODUCT = "https://aziel-runtime.vibelock.workers.dev/p/peacelock/";
const TEMPORALLOCK_HOST = "https://temporallock-download-tracker.vibelock.workers.dev";
const SHADOWLOCK_HOST = "https://shadowlock-download-tracker.vibelock.workers.dev";
const DECISIONGATE_HOST = "https://decisiongate-download-tracker.vibelock.workers.dev";
const LICENSE = "https://www.apache.org/licenses/LICENSE-2.0";
const VERSION = "0.1.0";
const AUTHOR = "Aziel Eliab";
const TITLE = "PeaceLock — Aziel Eliab";
const DEFAULT_ASSET = "peacelock-0.1.0.tar.gz";
const INSTALL_LINE = "curl -fsSL https://peacelock-download-tracker.vibelock.workers.dev/install.sh | bash";
const DESCRIPTION =
  "PeaceLock is Aziel Eliab software: chosen silence / chosen inaction as a first-class receipt (PL-WP-0.1). Transcript always ABSENT. HARD_DUTY cannot be bypassed. Apache-2.0.";
const HONEST =
  "THIS IS: chosen silence / chosen inaction as a first-class receipt (PL-WP-0.1). THIS IS NOT: a gag-order kit, a wiretap, or third-party binding. HARD_DUTY cannot be bypassed. The Worker does not store ledgers. Hosted /v1 is stateless: this browser holds the ledger. Author Aziel Eliab.";
const HOW_TO_CITE =
  "Eliab, Aziel. (2026). PeaceLock 0.1.0 [Software]. Apache-2.0. https://github.com/AzielEliab/peacelock · https://peacelock-download-tracker.vibelock.workers.dev/";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, MCP-Protocol-Version, mcp-session-id, User-Agent, Authorization",
  };
}

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function citePayload() {
  return {
    author: AUTHOR,
    title: "PeaceLock",
    version: VERSION,
    homepage: HOST + "/",
    github: GITHUB_REPO,
    download: HOST + "/download",
    install: HOST + "/install.sh",
    openapi: HOST + "/openapi.json",
    skill: HOST + "/v1/skill",
    mcp: HOST + "/mcp",
    catalog_mcp: CATALOG + "mcp",
    catalog: CATALOG,
    catalog_product: CATALOG_PRODUCT,
    license: "Apache-2.0",
    license_url: LICENSE,
    one_line: DESCRIPTION,
    how_to_cite: HOW_TO_CITE,
    apa: "Eliab, A. (2026). PeaceLock (Version 0.1.0) [Computer software]. https://peacelock-download-tracker.vibelock.workers.dev/",
    bibtex:
      "@software{eliab_peacelock_2026, author = {Eliab, Aziel}, title = {PeaceLock}, version = {0.1.0}, year = {2026}, license = {Apache-2.0}, url = {https://peacelock-download-tracker.vibelock.workers.dev/}, publisher = {GitHub}, howpublished = {\\url{https://github.com/AzielEliab/peacelock}}}",
    zenodo_status: "placeholder_no_doi_invented",
    software_deposit_needed: true,
    note: "No DOI is invented here. Cite GitHub and this Worker. Identity is Aziel Eliab only. Forks welcome.",
    identity: "Aziel Eliab only",
    forks: "welcome and always allowed",
  };
}

export function jsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "PeaceLock",
    alternateName: TITLE,
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Linux, macOS, Windows, Cloudflare Workers",
    softwareVersion: VERSION,
    author: { "@type": "Person", name: AUTHOR, url: "https://github.com/AzielEliab" },
    creator: { "@type": "Person", name: AUTHOR, url: "https://github.com/AzielEliab" },
    codeRepository: GITHUB_REPO,
    downloadUrl: HOST + "/download",
    installUrl: HOST + "/install.sh",
    license: LICENSE,
    url: HOST + "/",
    description: DESCRIPTION,
    keywords: "PeaceLock, chosen silence, chosen inaction, hash-chained receipts, Aziel Eliab, PL-WP-0.1",
    isAccessibleForFree: true,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    sameAs: [GITHUB_REPO, CATALOG_PRODUCT],
  };
}

function sitemapXml() {
  const paths = ["/", "/download", "/install.sh", "/v1/skill", "/v1/example", "/v1/health", "/v1/fraggate/list", "/v1/mesh", "/openapi.json", "/mcp", "/cite.json", "/llms.txt", "/ai"];
  const urls = paths.map((p) => `  <url><loc>${HOST}${p === "/" ? "/" : p}</loc></url>`).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
  <url><loc>${GITHUB_REPO}</loc></url>
</urlset>
`;
}

function robotsTxt() {
  return `User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Bytespider
Allow: /

User-agent: CCBot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: meta-externalagent
Allow: /

User-agent: FacebookBot
Allow: /

User-agent: cohere-ai
Allow: /

User-agent: Diffbot
Allow: /

User-agent: Omgilibot
Allow: /

User-agent: Amazonbot
Allow: /

Sitemap: ${HOST}/sitemap.xml
`;
}

function llmsTxt() {
  return `# PeaceLock

Author: Aziel Eliab
One-line: ${DESCRIPTION}
GitHub: ${GITHUB_REPO}
Homepage: ${HOST}/
Download: ${HOST}/download
Install: ${HOST}/install.sh
OpenAPI: ${HOST}/openapi.json
Skill: ${HOST}/v1/skill
MCP: ${HOST}/mcp
Catalog MCP: ${CATALOG}mcp (FragGate slug peacelock)
Cite: ${HOST}/cite.json
Ops: POST /v1/open, POST /v1/seal, POST /v1/break, POST /v1/show, POST /v1/verify, GET /v1/health, GET /v1/skill
FragGate proxy: GET /v1/fraggate/list, GET /v1/fraggate/describe, POST /v1/fraggate/call (via AZIEL_RUNTIME)
Suite mesh: GET ${HOST}/v1/mesh PROXY to aziel-runtime. Default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity. Catalog MCP mesh_* + FragGate slug=mesh.
Catalog LIVE_OPS: open, seal, break, show, verify, stamp, upload_envelope, health, skill
MCP tools: peacelock_health, peacelock_skill, peacelock_open, peacelock_seal, peacelock_verify
Doctor: Worker-local / CLI only — not a FragGate LIVE_OPS
Identity: Aziel Eliab only
License: Apache-2.0
Forks: welcome and always allowed
DOI: none invented; software deposit still needed.

Indexing, metadata scrape, and AI grounding of public pages are allowed.
`;
}

export function handleSeoRoutes(request, url) {
  if (request.method !== "GET" && request.method !== "HEAD") return null;
  const headers = { ...corsHeaders(), "Cache-Control": "private, no-store" };
  if (url.pathname === "/cite.json") {
    return new Response(JSON.stringify(citePayload(), null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json; charset=utf-8", ...headers },
    });
  }
  if (url.pathname === "/sitemap.xml") {
    return new Response(sitemapXml(), { status: 200, headers: { "Content-Type": "application/xml; charset=utf-8", ...headers } });
  }
  if (url.pathname === "/robots.txt") {
    return new Response(robotsTxt(), { status: 200, headers: { "Content-Type": "text/plain; charset=utf-8", ...headers } });
  }
  if (url.pathname === "/llms.txt" || url.pathname === "/ai.txt") {
    return new Response(llmsTxt(), { status: 200, headers: { "Content-Type": "text/plain; charset=utf-8", ...headers } });
  }
  return null;
}

function breakdownList(stats) {
  const rows = stats.breakdown || [];
  if (!rows.length) return "<li>none yet</li>";
  return rows
    .map((b) => `<li><code>${escapeHtml(b.owner)}/${escapeHtml(b.repo)}</code> branch <code>${escapeHtml(b.branch)}</code> fork=${escapeHtml(b.fork)} → ${escapeHtml(b.count)}</li>`)
    .join("");
}

export function renderHome(stats) {
  const views = Number(stats.views) || 0;
  const downloads = Number(stats.downloads != null ? stats.downloads : stats.total) || 0;
  const v = views.toLocaleString("en-US");
  const n = downloads.toLocaleString("en-US");
  const gh = stats.github || {};
  const ld = JSON.stringify(jsonLd());
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${TITLE}</title>
<meta name="description" content="${escapeHtml(DESCRIPTION)}">
<meta name="author" content="${AUTHOR}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="${HOST}/">
<link rel="sitemap" type="application/xml" href="${HOST}/sitemap.xml">
<link rel="icon" type="image/png" href="/sigil.png">
<meta property="og:type" content="website">
<meta property="og:title" content="${TITLE}">
<meta property="og:description" content="${escapeHtml(DESCRIPTION)}">
<meta property="og:url" content="${HOST}/">
<meta property="og:site_name" content="Aziel Eliab">
<meta property="og:image" content="${HOST}/sigil.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="${TITLE}">
<meta name="twitter:description" content="${escapeHtml(DESCRIPTION)}">
<meta name="twitter:image" content="${HOST}/sigil.png">
<script type="application/ld+json">${ld}</script>
<style>
  :root {
    color-scheme: dark;
    --bg: #0b0b0b; --panel: #141414; --ink: #e8e0d0; --muted: #9aa3b2;
    --line: #2a2414; --gold: #c9a227; --gold-dim: #c9a227; --pass: #3dba7a; --bad: #d4534b; --focus: #e6d19a;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink); }
  body { font: 16px/1.5 system-ui, "Segoe UI", sans-serif; }
  a { color: #e6d19a; }
  code, pre, .mono { font-family: ui-monospace, Menlo, Consolas, monospace; }
  .wrap { max-width: 58rem; margin: 0 auto; padding: 1.4rem 1.2rem 4.5rem; }
  .brandrow { display: flex; align-items: center; gap: 12px; margin: 0 0 12px; }
  .brandmark { width: 40px; height: 40px; border-radius: 10px; object-fit: cover; flex: 0 0 auto; box-shadow: 0 0 0 1px #d4af3733; }
  .stamp { margin: 0; color: var(--gold); font-size: .88rem; letter-spacing: .02em; }
  .appbar { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; }
  h1 { font-size: 2rem; letter-spacing: .02em; margin: 0 0 .2rem; }
  .motto { color: var(--gold); font-style: italic; margin: 0 0 .7rem; }
  .lede { color: var(--muted); margin: 0 0 1rem; max-width: 46rem; }
  .pill { font: 650 .78rem/1 ui-monospace, Menlo, Consolas, monospace; letter-spacing: .06em; text-transform: uppercase; border: 1px solid var(--line); border-radius: 999px; padding: .4rem .7rem; color: var(--muted); background: #101010; }
  .pill.ok { color: var(--pass); border-color: #2f6b48; }
  .pill.bad { color: var(--bad); border-color: #7a2f2c; }
  nav.toc { display: flex; flex-wrap: wrap; gap: .55rem; margin: 0 0 1.1rem; }
  nav.toc a { text-decoration: none; color: var(--ink); border: 1px solid var(--line); background: var(--panel); border-radius: 999px; padding: .35rem .75rem; font-size: .88rem; }
  .banner { border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c; padding: .9rem 1rem; border-radius: 10px; margin: 0 0 1.15rem; font-size: .94rem; }
  .card, .workspace, .cite { border: 1px solid var(--line); border-radius: 14px; padding: 1.15rem 1.2rem 1.25rem; background: var(--panel); margin: 0 0 1.1rem; }
  .workspace { box-shadow: 0 0 0 1px #d4af3714, 0 16px 40px #0006; }
  h2 { font-size: 1.12rem; margin: 0 0 .45rem; letter-spacing: .04em; }
  .kicker { display: block; font-size: .68rem; letter-spacing: .12em; text-transform: uppercase; color: var(--gold); margin-bottom: .15rem; font-family: ui-monospace, Menlo, Consolas, monospace; }
  .workgrid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr); gap: 1rem; }
  @media (max-width: 820px) { .workgrid { grid-template-columns: 1fr; } }
  label { display: block; font-size: .92rem; margin: .75rem 0 .28rem; }
  input[type="text"], input[type="number"], textarea, select { width: 100%; padding: .58rem .7rem; border: 1px solid var(--line); border-radius: 8px; background: #0e0e0e; color: var(--ink); font: inherit; }
  input:focus, textarea:focus, select:focus { outline: 2px solid var(--focus); outline-offset: 1px; }
  .row2 { display: grid; grid-template-columns: 1fr 1fr; gap: .7rem; }
  @media (max-width: 520px) { .row2 { grid-template-columns: 1fr; } }
  .actions { display: flex; flex-wrap: wrap; gap: .5rem; margin: .95rem 0 .2rem; }
  button, a.btn { font: 700 .88rem/1.1 ui-monospace, Menlo, Consolas, monospace; letter-spacing: .03em; padding: .72rem .9rem; border-radius: 9px; border: 1px solid transparent; cursor: pointer; text-decoration: none; display: inline-block; }
  button.gold, a.btn.gold { background: var(--gold-dim); color: #14110a; }
  button.ink, a.btn.ink { background: var(--ink); color: var(--bg); }
  button.ghost, a.btn.ghost, label.filebtn { background: transparent; color: var(--ink); border-color: var(--line); }
  button.copied { background: var(--pass); color: #0e1014; }
  label.filebtn { padding: .72rem .9rem; border-radius: 9px; cursor: pointer; font: 700 .88rem/1.1 ui-monospace, Menlo, Consolas, monospace; }
  label.filebtn input { display: none; }
  .status { margin: 0 0 .8rem; padding: .75rem .85rem; border-radius: 10px; border: 1px solid var(--line); background: #101010; color: var(--muted); }
  .status.ok { color: var(--pass); border-color: #2f6b48; }
  .status.bad { color: var(--bad); border-color: #7a2f2c; }
  .metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .55rem; margin: 0 0 .85rem; }
  @media (max-width: 720px) { .metrics { grid-template-columns: 1fr 1fr; } }
  .metric { border: 1px solid var(--line); border-radius: 10px; padding: .55rem .65rem; background: #101010; }
  .metric b { display: block; font-size: .72rem; color: var(--muted); font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }
  .metric span { display: block; font-size: .78rem; word-break: break-all; color: var(--ink); }
  ol.receipts { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .65rem; }
  .receipt { border: 1px solid var(--line); border-radius: 10px; padding: .75rem .85rem; background: #101010; position: relative; }
  .receipt::before { content: ""; position: absolute; left: -1px; top: 0; bottom: 0; width: 3px; background: var(--gold); border-radius: 10px 0 0 10px; }
  .receipt h3 { margin: 0 0 .25rem; font-size: .95rem; }
  .receipt p { margin: .2rem 0; }
  .hash { font-size: .72rem; word-break: break-all; color: var(--muted); }
  .nums { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin: 0 0 1rem; }
  .count { font-size: 2.1rem; font-variant-numeric: tabular-nums; font-weight: 700; margin: 0; }
  .count span { display: block; font-size: .92rem; font-weight: 500; color: var(--muted); }
  .btns { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin: 0 0 .85rem; }
  @media (max-width: 520px) { .btns { grid-template-columns: 1fr; } }
  a.btn.block, button.btn.block { display: block; width: 100%; text-align: center; font-size: 1.15rem; padding: 1rem 1.1rem; }
  a.btn.primary { background: #e8eaef; color: #0e1014; }
  button.btn.install { background: var(--gold-dim); color: #14110a; }
  pre { background: #0e0e0e; padding: .75rem .9rem; overflow: auto; border-radius: 8px; font-size: .82rem; }
  .meta { margin-top: 1rem; color: var(--muted); font-size: .92rem; }
  .iso { margin-top: .75rem; font-size: .85rem; color: #7d8696; }
  details.raw { margin-top: .8rem; }
  details.raw pre { max-height: 18rem; }
  footer { color: var(--muted); font-size: .9rem; }
  #meshStrip { border: 1px solid var(--gold); border-radius: 14px; padding: .85rem 1rem; background: var(--panel); margin: 0 0 1.1rem; display: flex; flex-wrap: wrap; align-items: center; gap: .7rem 1rem; font-size: .88rem; color: var(--muted); }
  #meshStrip .live { color: var(--ink); }
  #meshStrip .live b { color: var(--gold); font-size: 1.35rem; margin-right: .35rem; }
  #meshStrip .rollup b { color: var(--gold); }
  #meshStrip button { font: 700 .78rem/1 ui-monospace, Menlo, Consolas, monospace; height: 2rem; padding: 0 .75rem; border-radius: 8px; background: #101010; color: var(--ink); border: 1px solid var(--gold); cursor: pointer; }
  #meshStrip button:hover { background: #241c0d; color: var(--gold); }
  #meshStrip input { width: 10rem; padding: .4rem .55rem; border: 1px solid var(--gold); border-radius: 8px; background: #0e0e0e; color: var(--ink); font: inherit; }
  #meshProducts { flex-basis: 100%; margin: 0; }
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="brandrow">
        <img class="brandmark" src="/sigil.png" width="40" height="40" alt="Everblooming sigil — Aziel Eliab" decoding="async">
        <p class="stamp">Everblooming sigil · Aziel Eliab</p>
      </div>
      <div class="appbar">
        <div>
          <h1>PeaceLock</h1>
          <p class="motto">Chosen silence / chosen inaction as a first-class receipt.</p>
        </div>
        <p class="pill" id="api-pill">API · checking</p>
      </div>
      <p class="lede">v${VERSION} software by <strong>${AUTHOR}</strong> only. Open writes a quiet window. Seal locks it forward. Break appends BROKEN; the original seal stays. Transcript is always ABSENT. Forks are welcome and always allowed.</p>
      <nav class="toc" aria-label="Product sections">
        <a href="#workspace">Use UI</a>
        <a href="#meshStrip">Live Nodes</a>
        <a href="#install">Download / install</a>
        <a href="#cite">Cite</a>
        <a href="/v1/skill">Skill</a>
        <a href="/mcp">MCP</a>
        <a href="/openapi.json">OpenAPI</a>
        <a href="${GITHUB_REPO}">GitHub</a>
      </nav>
      <p class="banner">${escapeHtml(HONEST)}</p>
    </header>

    <div id="meshStrip" aria-label="Suite Live Nodes">
      <div class="live"><b id="meshLiveCount">0</b> Live Nodes</div>
      <div id="meshLine">Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.</div>
      <div class="rollup">live <b id="qnmLive">0</b> · locked <b id="qnmLocked">0</b> · isolated <b id="qnmIsolated">0</b></div>
      <div>No Node Gate · No public qnsd proxy · No auto-heal · Aziel Eliab only</div>
      <div>
        <input id="meshBearer" type="text" maxlength="80" placeholder="bearer (required to enable)" aria-label="mesh bearer">
        <button id="meshEnable" type="button" title="Enable suite mesh. Declared bearer required. Default off.">Enable</button>
        <button id="meshDisable" type="button" title="Disable suite mesh (always allowed)">Disable</button>
        <button id="meshJoin" type="button" title="Join as peacelock. Refused while mesh is OFF. No auto-join.">Join</button>
        <button id="meshLeave" type="button" title="Leave this node. No auto-heal.">Leave</button>
      </div>
      <div id="meshProducts">Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 photon QNS1 (qnm-node local qnsd; hub cite only) · not AnonBroadcast · not AZMail ring · not a Node Gate · not a Softwares-tab product</div>
    </div>

    <section class="workspace" id="workspace">
      <h2><span class="kicker">Live software</span>Quiet workspace</h2>
      <p class="lede">Use UI: catalog labels on this Worker — Open / Seal / Break / Show / Verify / Health / Skill (<code>POST /v1/open</code>, <code>/v1/seal</code>, <code>/v1/break</code>, <code>/v1/show</code>, <code>/v1/verify</code>, <code>GET /v1/health</code>, <code>GET /v1/skill</code>, plus <code>POST /v1/upload</code>). FragGate door proxy: <code>/v1/fraggate/list</code>, <code>/describe</code>, <code>/call</code> via AZIEL_RUNTIME. Suite mesh: <code>/v1/mesh/*</code> PROXY (default OFF; QNM live|locked|isolated; QNS-CD-1.0 hub cite; no Node Gate; no public qnsd proxy; no auto-heal; not anonymity). The Worker does not store your ledger. This page keeps it in this browser until you export it. Upload hashes file bytes and stamps <code>timestamp</code> + <code>date_stamp</code>. No unspoken words.</p>
      <div class="workgrid">
        <form id="ws-form" autocomplete="off">
          <div class="row2">
            <div>
              <label for="mode"><span class="kicker">Mode</span></label>
              <select id="mode"><option>SILENCE</option><option>INACTION</option><option>BOTH</option></select>
            </div>
            <div>
              <label for="act_class"><span class="kicker">act_class</span> Closed-set token only.</label>
              <select id="act_class">
                <option>reply</option><option>file</option><option>post</option><option>call</option>
                <option>attend</option><option>sign</option><option>pay</option><option>transfer</option>
                <option>delete</option><option>other</option>
              </select>
            </div>
          </div>
          <div class="row2">
            <div>
              <label for="channel"><span class="kicker">Channel</span></label>
              <input id="channel" type="text" value="email">
            </div>
            <div>
              <label for="duty"><span class="kicker">duty_check</span> HARD_DUTY refuses write.</label>
              <select id="duty"><option>NONE</option><option>ADVISORY</option><option>HARD_DUTY</option></select>
            </div>
          </div>
          <label for="note"><span class="kicker">Note</span> Optional ≤140. No why.</label>
          <input id="note" type="text" maxlength="140" placeholder="window only">
          <label for="pl_id"><span class="kicker">pl_id</span> Filled after open. Used by seal / break.</label>
          <input id="pl_id" type="text" placeholder="pl_…">
          <label for="reason"><span class="kicker">break_reason</span></label>
          <select id="reason">
            <option>speech_occurred</option><option>act_occurred</option>
            <option>operator_void</option><option>duty_conflict</option>
          </select>
          <label for="upload-file"><span class="kicker">Upload file</span> Operator-declared evidence. Bytes hashed. Timestamp + date stamp enter the lattice. Not a transcript.</label>
          <input id="upload-file" type="file">
          <div class="actions">
            <button type="button" class="gold" id="btn-open">Open</button>
            <button type="button" class="ink" id="btn-seal">Seal</button>
            <button type="button" class="ghost" id="btn-break">Break</button>
            <button type="button" class="ghost" id="btn-show">Show</button>
            <button type="button" class="ghost" id="btn-verify">Verify</button>
            <button type="button" class="ghost" id="btn-health">Health</button>
            <button type="button" class="ghost" id="btn-skill">Skill</button>
            <button type="button" class="ghost" id="btn-lattice">Hardening</button>
            <button type="button" class="ghost" id="btn-upload">Upload envelope</button>
            <label class="filebtn">Import JSONL <input type="file" id="import-json" accept="application/json,.json,.jsonl"></label>
            <button type="button" class="ghost" id="btn-export">Export</button>
            <button type="button" class="ghost" id="btn-clear">Clear local ledger</button>
          </div>
        </form>
        <div>
          <div class="status" id="ws-status">No quiet window yet. Open writes the first lattice node.</div>
          <div class="metrics">
            <div class="metric"><b>Length</b><span id="chain-length">0</span></div>
            <div class="metric"><b>State</b><span id="last-state">—</span></div>
            <div class="metric"><b>Last hash</b><span id="last-hash">—</span></div>
            <div class="metric"><b>Date stamp</b><span id="last-date">—</span></div>
          </div>
          <ol class="receipts" id="receipt-list"></ol>
          <details class="raw">
            <summary>Raw API result / debug</summary>
            <pre id="raw-json">{}</pre>
          </details>
        </div>
      </div>
    </section>

    <section class="card" id="install">
      <h2><span class="kicker">Counted package</span>Download and one-click install</h2>
      <div class="nums">
        <p class="count">${v}<span>Views</span></p>
        <p class="count">${n}<span>Downloads</span></p>
      </div>
      <p>Download saves the gzip from this Worker (HTTP 200, counted). One-click install copies a Terminal command. After it finishes, run <code>peacelock ui</code> and open http://127.0.0.1:8768 on this computer only.</p>
      <div class="btns">
        <a class="btn block primary" href="/download?asset=${DEFAULT_ASSET}">Download</a>
        <button type="button" class="btn block install" id="install-btn">One-click install</button>
      </div>
      <pre id="install-cmd">${INSTALL_LINE}</pre>
      <p class="meta">The download count ticks on the Download click. No 302 to GitHub. Forks using this same link are counted automatically. ${DEFAULT_ASSET} — ${n} counted.</p>
      <p class="iso">Isolated counter: Worker <code>peacelock-download-tracker</code>, project <code>peacelock</code>, KV <code>PEACELOCK_DOWNLOADS</code>. Not mixed with any other product. /v1 does not increment downloads.</p>
      <p class="meta">GitHub: stars ${gh.stars || 0} · forks ${gh.forks || 0} · watchers ${gh.watchers || 0} · release assets ${gh.release_download_count || 0}</p>
      <p class="meta">Lattice kin: <a href="${TEMPORALLOCK_HOST}/">TemporalLock</a> · <a href="${SHADOWLOCK_HOST}/">ShadowLock</a> · <a href="${DECISIONGATE_HOST}/">DecisionGATE</a> · <a href="https://github.com/AzielEliab/fraggate">FragGate</a> · <a href="${CATALOG}">aziel-runtime</a> · <a href="https://www.azielcorpuslibrary.net/">library</a> · <a href="https://godlock.uk/">godlock.uk</a> · <a href="https://www.azieleliab.com/">www.azieleliab.com</a></p>
      <p class="meta"><a href="/stats">JSON stats</a> · <a href="/count">/count</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/mcp">MCP</a> · <a href="/v1/fraggate/list">FragGate list</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="/v1/skill">Skill</a> · <a href="/v1/example">Example</a> · <a href="/ai">AI runtime</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${GITHUB_LATEST}">releases</a></p>
      <h3>Per repo / branch / fork</h3>
      <ul>${breakdownList(stats)}</ul>
    </section>

    <section class="cite" id="cite">
      <h2>How to cite</h2>
      <p>${escapeHtml(HOW_TO_CITE)}</p>
      <p>Author: <strong>${AUTHOR}</strong> only · License: Apache-2.0 · Forks welcome and always allowed · Machine-readable: <a href="/cite.json">/cite.json</a></p>
      <p class="meta">No DOI is invented here. Software deposit still needed. Cite GitHub and this Worker.</p>
      <p><a href="${CATALOG}">Catalog</a> · <a href="${CATALOG_PRODUCT}">Catalog product</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${HOST}/download">Download</a> · <a href="/llms.txt">llms.txt</a></p>
    </section>

    <footer>
      <p>Apache-2.0 · ${AUTHOR} · PeaceLock v${VERSION}</p>
      <p>Transcript is always ABSENT. HARD_DUTY cannot be bypassed. The sequence cannot be altered without detection.</p>
    </footer>
  </div>
  <script>
    (function () {
      var STORAGE = "peacelock-workspace-ledger-v1";
      var ledger = [];
      var lastResult = null;
      function $(id) { return document.getElementById(id); }
      function loadLedger() {
        try {
          var raw = localStorage.getItem(STORAGE);
          if (!raw) return;
          var parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) ledger = parsed;
        } catch (e) { /* local only */ }
      }
      function saveLedger() {
        try { localStorage.setItem(STORAGE, JSON.stringify(ledger)); } catch (e) { /* ignore quota */ }
      }
      function fields() {
        return {
          mode: $("mode").value,
          act_class: $("act_class").value,
          channel: $("channel").value,
          duty_check: $("duty").value,
          note: $("note").value,
          pl_id: $("pl_id").value,
          reason: $("reason").value,
          ledger: ledger
        };
      }
      function setStatus(kind, text) {
        var el = $("ws-status");
        el.className = "status" + (kind ? " " + kind : "");
        el.textContent = text;
      }
      function addHash(parent, label, value) {
        var p = document.createElement("p");
        p.className = "hash";
        p.textContent = label + " " + (value || "");
        parent.appendChild(p);
      }
      function render() {
        $("chain-length").textContent = String(ledger.length);
        var last = ledger.length ? ledger[ledger.length - 1] : null;
        $("last-hash").textContent = last && last.receipt_hash ? last.receipt_hash : "—";
        $("last-state").textContent = last && last.state ? last.state : (last && last.event_kind ? last.event_kind : "—");
        $("last-date").textContent = last && last.date_stamp ? last.date_stamp : (last && last.window_start ? last.window_start.slice(0,10) : "—");
        var ol = $("receipt-list");
        ol.textContent = "";
        ledger.forEach(function (rec, i) {
          var li = document.createElement("li");
          li.className = "receipt";
          var h = document.createElement("h3");
          h.textContent = i + " · " + (rec.event_kind || "QUIET") + " · " + (rec.state || "");
          var sum = document.createElement("p");
          sum.textContent = (rec.pl_id || "") + " · " + (rec.mode || "") + " · " + (rec.act_class || rec.file_name || "");
          li.appendChild(h);
          li.appendChild(sum);
          addHash(li, "receipt_hash", rec.receipt_hash);
          addHash(li, "prev_hash", rec.prev_hash);
          addHash(li, "transcript", rec.transcript || "ABSENT");
          if (rec.timestamp) addHash(li, "timestamp", rec.timestamp);
          if (rec.date_stamp) addHash(li, "date_stamp", rec.date_stamp);
          ol.appendChild(li);
        });
        $("raw-json").textContent = JSON.stringify(lastResult || { ledger: ledger }, null, 2);
      }
      function isGetOp(path) {
        return path === "/v1/health" || path === "/v1/skill" || path === "/v1/doctor";
      }
      async function api(path, body) {
        var get = isGetOp(path);
        var res = await fetch(path, {
          method: get ? "GET" : "POST",
          headers: { "Content-Type": "application/json", "User-Agent": "Mozilla/5.0" },
          body: get ? undefined : JSON.stringify(body || {})
        });
        var ctype = (res.headers.get("Content-Type") || "");
        if (path === "/v1/skill" || ctype.indexOf("text/markdown") !== -1) {
          var text = await res.text();
          if (!res.ok) throw new Error("HTTP " + res.status);
          return { ok: true, action: "skill", skill: text };
        }
        var data = await res.json();
        if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
        return data;
      }
      function applyResult(data, fallbackMsg) {
        lastResult = data;
        if (Array.isArray(data.ledger)) ledger = data.ledger;
        else if (Array.isArray(data.chain)) ledger = data.chain;
        saveLedger();
        if (data.receipt && data.receipt.pl_id) $("pl_id").value = data.receipt.pl_id;
        var ok = data.ok;
        if (ok == null && data.errors) ok = !data.errors.length;
        var msg = data.message || fallbackMsg;
        if (data.action) msg = data.action + " · " + (msg || "Transcript ABSENT.");
        if (data.ok === true) msg = (msg || "Intact.") + (data.length != null ? " · length " + data.length : "");
        if (data.ok === false) msg = "Errors: " + ((data.errors || []).join("; ") || "verify failed");
        if (data.error) msg = data.error;
        setStatus(ok === false || data.error ? "bad" : (ok === true || data.action ? "ok" : ""), msg || "Done.");
        render();
      }
      async function run(fn, label) {
        try { applyResult(await fn(), label); }
        catch (err) { setStatus("bad", String(err.message || err)); }
      }
      $("btn-open").onclick = function () { run(function () { return api("/v1/open", fields()); }, "Opened. Transcript ABSENT."); };
      $("btn-seal").onclick = function () { run(function () { return api("/v1/seal", fields()); }, "Sealed. Window locked forward."); };
      $("btn-break").onclick = function () { run(function () { return api("/v1/break", fields()); }, "BROKEN appended. Original seal stays."); };
      $("btn-show").onclick = function () { run(function () { return api("/v1/show", fields()); }, "Show walked the local ledger."); };
      $("btn-verify").onclick = function () { run(function () { return api("/v1/verify", { ledger: ledger }); }, "Verify walked hashes and prev links."); };
      $("btn-health").onclick = function () { run(function () { return api("/v1/health", {}); }, "Health. Catalog FragGate op. No writes."); };
      $("btn-skill").onclick = function () { run(function () { return api("/v1/skill", {}); }, "Skill. Catalog FragGate op."); };
      $("btn-lattice").onclick = function () { run(function () { return api("/v1/lattice", { ledger: ledger }); }, "Hardening walk: links + state machine."); };
      $("btn-upload").onclick = async function () {
        var f = $("upload-file").files && $("upload-file").files[0];
        if (!f) { setStatus("bad", "Choose a file to hash. Bytes are not stored as a transcript."); return; }
        try {
          var buf = await f.arrayBuffer();
          var hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", buf))].map(function (b) { return b.toString(16).padStart(2, "0"); }).join("");
          var now = new Date().toISOString().replace(/\\.\\d{3}Z$/, "Z");
          var body = fields();
          body.file_name = f.name.split(/[/\\\\]/).pop();
          body.file_sha256 = hash;
          body.timestamp = now;
          body.date_stamp = now.slice(0, 10);
          applyResult(await api("/v1/upload", body), "Envelope chained with timestamp + date stamp.");
        } catch (err) { setStatus("bad", String(err.message || err)); }
      };
      $("import-json").onchange = function () {
        var f = this.files && this.files[0];
        if (!f) return;
        f.text().then(function (text) {
          var rows;
          try {
            var parsed = JSON.parse(text);
            rows = Array.isArray(parsed) ? parsed : (parsed.ledger || parsed.chain || parsed.receipts || []);
          } catch (e) {
            rows = text.split(/\\n/).filter(Boolean).map(function (line) { return JSON.parse(line); });
          }
          if (!Array.isArray(rows) || !rows.length) throw new Error("ledger array required");
          ledger = rows;
          lastResult = { imported: true, ledger: ledger };
          saveLedger();
          setStatus("ok", "Imported " + ledger.length + " receipts. Verify next. Transcript ABSENT.");
          render();
        }).catch(function (err) { setStatus("bad", String(err.message || err)); });
      };
      $("btn-export").onclick = function () {
        var blob = new Blob([ledger.map(function (r) { return JSON.stringify(r); }).join("\\n") + "\\n"], { type: "application/x-ndjson" });
        var a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "peacelock_ledger.jsonl";
        a.click();
        URL.revokeObjectURL(a.href);
      };
      $("btn-clear").onclick = function () {
        ledger = [];
        lastResult = null;
        saveLedger();
        setStatus("", "Local ledger cleared. The Worker never stored it. Open writes the first node.");
        render();
      };
      var installBtn = $("install-btn");
      var installPre = $("install-cmd");
      var installCmd = ${JSON.stringify(INSTALL_LINE)};
      if (installBtn) {
        installBtn.addEventListener("click", function () {
          function done(ok) {
            installBtn.textContent = ok ? "Copied! Paste in Terminal, then run peacelock ui" : "Select the command, copy it, then run peacelock ui";
            installBtn.classList.add("copied");
          }
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(installCmd).then(function () { done(true); }).catch(function () { done(false); });
          } else {
            done(false);
            if (installPre && window.getSelection) {
              var r = document.createRange();
              r.selectNodeContents(installPre);
              var sel = window.getSelection();
              sel.removeAllRanges();
              sel.addRange(r);
            }
          }
        });
      }
      fetch("/v1/health").then(function (res) { return res.json(); }).then(function (data) {
        var pill = $("api-pill");
        if (!pill) return;
        if (data && data.ok) {
          pill.textContent = "API live · v" + (data.version || "${VERSION}");
          pill.className = "pill ok";
        } else {
          pill.textContent = "API down";
          pill.className = "pill bad";
        }
      }).catch(function () {
        var pill = $("api-pill");
        if (pill) { pill.textContent = "API down"; pill.className = "pill bad"; }
      });
      function meshNum() {
        for (var i = 0; i < arguments.length; i++) {
          var raw = arguments[i];
          if (raw == null || raw === "") continue;
          var n = typeof raw === "number" ? raw : Number(String(raw).replace(/,/g, ""));
          if (Number.isFinite(n) && n >= 0) return Math.floor(n);
        }
        return 0;
      }
      function unwrapMesh(j) {
        if (!j || typeof j !== "object") return {};
        if (j.result && typeof j.result === "object") return Object.assign({}, j, j.result);
        if (j.mesh && typeof j.mesh === "object") return Object.assign({}, j, j.mesh);
        return j;
      }
      function paintMesh(raw) {
        var j = unwrapMesh(raw);
        var on = j.enabled === true || j.enabled === 1 || String(j.status || "").toLowerCase() === "on";
        var r = (j.rollup && typeof j.rollup === "object") ? j.rollup : {};
        var live = on ? meshNum(r.live, j.live_nodes, j.live) : 0;
        var locked = on ? meshNum(r.locked, j.locked_nodes, j.locked) : 0;
        var isolated = on ? meshNum(r.isolated, j.isolated_nodes, j.isolated) : 0;
        $("meshLiveCount").textContent = String(live);
        $("qnmLive").textContent = String(live);
        $("qnmLocked").textContent = String(locked);
        $("qnmIsolated").textContent = String(isolated);
        var line = $("meshLine");
        if (on) line.textContent = "Suite mesh: on · live " + live + " · locked " + locked + " · isolated " + isolated + ". QNS-CD-1.0. Not an anonymity network.";
        else if (j.status === "unavailable" || (j.ok === false && j.error)) line.textContent = "Suite mesh: off (unavailable). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.";
        else line.textContent = "Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.";
        var products = j.products_present || j.products || [];
        var names = Array.isArray(products) ? products.map(function (p) { return typeof p === "string" ? p : (p && (p.product || p.slug)) || ""; }).filter(Boolean) : [];
        var nodes = Array.isArray(j.nodes) ? j.nodes : [];
        var extra = names.length ? " · products " + names.join(", ") : (nodes.length ? " · " + nodes.length + " node labels" : "");
        $("meshProducts").textContent = "Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 photon QNS1 (qnm-node local qnsd; hub cite only) · not AnonBroadcast · not AZMail ring · not a Node Gate · not a Softwares-tab product" + extra;
      }
      async function meshGet(path) {
        var r = await fetch(path, { headers: { "user-agent": "Mozilla/5.0", accept: "application/json" } });
        return r.json();
      }
      async function meshPost(path, payload) {
        var r = await fetch(path, { method: "POST", headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" }, body: JSON.stringify(payload || {}) });
        return r.json();
      }
      async function refreshMesh() {
        try {
          var status = await meshGet("/v1/mesh");
          var merged = status;
          var inner = unwrapMesh(status);
          var on = inner.enabled === true;
          if (on) {
            try {
              var nodes = await meshGet("/v1/mesh/nodes");
              merged = Object.assign({}, inner, unwrapMesh(nodes));
            } catch (e) { /* status is enough */ }
          }
          paintMesh(merged);
          var nodeId = sessionStorage.getItem("peacelock_mesh_node");
          if (on && nodeId) {
            try { await meshPost("/v1/mesh/heartbeat", { node_id: nodeId }); } catch (e) { /* no auto-heal */ }
          }
        } catch (e) {
          paintMesh({ ok: false, enabled: false, status: "unavailable", error: "mesh_unavailable" });
        }
      }
      $("meshEnable").onclick = async function () {
        var bearer = ($("meshBearer").value || "").trim();
        paintMesh(await meshPost("/v1/mesh/enable", bearer ? { bearer: bearer } : {}));
        refreshMesh();
      };
      $("meshDisable").onclick = async function () {
        sessionStorage.removeItem("peacelock_mesh_node");
        paintMesh(await meshPost("/v1/mesh/disable", {}));
        refreshMesh();
      };
      $("meshJoin").onclick = async function () {
        var j = await meshPost("/v1/mesh/join", { product: "peacelock", label: "PeaceLock Worker" });
        var inner = unwrapMesh(j);
        var id = inner.node_id || inner.id || (inner.session && inner.session.node_id);
        if (id) sessionStorage.setItem("peacelock_mesh_node", String(id));
        paintMesh(j);
        refreshMesh();
      };
      $("meshLeave").onclick = async function () {
        var id = sessionStorage.getItem("peacelock_mesh_node");
        if (id) await meshPost("/v1/mesh/leave", { node_id: id });
        sessionStorage.removeItem("peacelock_mesh_node");
        refreshMesh();
      };
      window.addEventListener("pagehide", function () {
        var id = sessionStorage.getItem("peacelock_mesh_node");
        if (!id || typeof navigator.sendBeacon !== "function") return;
        try { navigator.sendBeacon("/v1/mesh/leave", new Blob([JSON.stringify({ node_id: id })], { type: "application/json" })); } catch (e) { /* leave expires in 5 minutes */ }
      });
      refreshMesh();
      setInterval(refreshMesh, 30000);
      document.addEventListener("visibilitychange", function () { if (!document.hidden) refreshMesh(); });
      loadLedger();
      render();
    })();
  </script>
</body>
</html>`;
}
