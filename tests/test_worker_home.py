"""Worker homepage is PeaceLock software, not a downloads shell."""

from __future__ import annotations

from pathlib import Path

HOME = Path("workers/download-tracker/src/home.js").read_text(encoding="utf-8")
INDEX = Path("workers/download-tracker/src/index.js").read_text(encoding="utf-8")


def test_title_is_product_not_downloads_shell() -> None:
    assert "PeaceLock — Aziel Eliab" in HOME
    assert "PeaceLock downloads" not in HOME


def test_seo_and_softwareapplication_json_ld() -> None:
    assert "application/ld+json" in HOME
    assert "SoftwareApplication" in HOME
    assert "Aziel Eliab" in HOME
    assert "cite.json" in HOME
    assert "sitemap.xml" in HOME
    assert 'class="brandmark"' in HOME
    assert 'src="/sigil.png"' in HOME
    assert 'alt=""' in HOME
    assert "Everblooming sigil" not in HOME


def test_workspace_calls_real_ops() -> None:
    for path in ("/v1/open", "/v1/seal", "/v1/break", "/v1/show", "/v1/verify", "/v1/upload", "/v1/health", "/v1/skill"):
        assert path in HOME
    assert "btn-open" in HOME
    assert "btn-seal" in HOME
    assert "btn-break" in HOME
    assert "btn-verify" in HOME
    assert "btn-health" in HOME
    assert "btn-skill" in HOME
    assert "btn-doctor" not in HOME
    assert "Use UI" in HOME or "Quiet workspace" in HOME


def test_download_install_and_identity_remain() -> None:
    assert "/download?asset=" in HOME
    assert "peacelock-0.1.0.tar.gz" in HOME
    assert "One-click install" in HOME
    assert "Aziel Eliab only" in HOME
    assert "Apache-2.0" in HOME
    assert "Forks welcome" in HOME or "Forks are welcome" in HOME


def test_no_invented_or_live_zenodo_identifier() -> None:
    assert "identifier:" not in HOME.split("export function jsonLd")[1].split("export function handleSeoRoutes")[0]
    assert "No DOI is invented here" in HOME
    assert "DOI =" not in INDEX
    assert "ZENODO =" not in INDEX


def test_worker_serves_home_and_seo() -> None:
    assert "renderHome" in INDEX
    assert "handleSeoRoutes" in INDEX
    assert 'url.pathname === "/"' in INDEX
    assert "/download" in INDEX
    assert "function totalKey()" in INDEX
    assert "ASSETS.fetch" in INDEX or "env.ASSETS" in INDEX


def test_count_returns_views_downloads_and_total() -> None:
    """YELLOW audit: GET /count must not be {project, total} only."""
    assert 'url.pathname === "/count"' in INDEX
    assert "views: stats.views || 0" in INDEX
    assert "downloads: stats.downloads || 0" in INDEX
    assert "total: stats.total || 0" in INDEX
    assert "json({ project: PROJECT, total: stats.total || 0 })" not in INDEX
    # azhub convention: views from __views__, downloads from download keys, total = downloads
    assert "function viewsKey()" in INDEX
    assert "downloads: shown" in INDEX


def test_upload_stamps_in_home() -> None:
    assert "date_stamp" in HOME
    assert "timestamp" in HOME
    assert "file" in HOME.lower()


def test_home_and_seo_advertise_worker_mcp() -> None:
    assert 'href="/mcp"' in HOME
    assert "/mcp" in HOME
    assert "catalog_mcp" in HOME or "aziel-runtime.vibelock.workers.dev" in HOME


def test_home_live_nodes_strip() -> None:
    assert 'id="meshStrip"' in HOME
    assert "Live Nodes" in HOME
    assert "QNM-BUILD-1.0" in HOME
    assert "QNS-CD-1.0" in HOME
    assert "No Node Gate" in HOME
    assert "No auto-heal" in HOME
    assert "Not an anonymity network" in HOME
    assert "/v1/mesh" in HOME
    assert 'id="meshLiveCount"' in HOME
    assert 'id="node-gate"' not in HOME
    assert 'href="/node-gate"' not in HOME
