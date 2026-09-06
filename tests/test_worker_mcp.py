"""Worker /mcp is a dual-surface JSON-RPC double of safe PeaceLock ops."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = (ROOT / "workers/download-tracker/src/runtime.js").read_text(encoding="utf-8")
INDEX = (ROOT / "workers/download-tracker/src/index.js").read_text(encoding="utf-8")
WRANGLER = (ROOT / "workers/download-tracker/wrangler.toml").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")

THIN_TOOLS = (
    "peacelock_health",
    "peacelock_skill",
    "peacelock_open",
    "peacelock_seal",
    "peacelock_verify",
)


def test_wrangler_runs_worker_first_for_mcp() -> None:
    assert '"/mcp"' in WRANGLER or '"/mcp",' in WRANGLER
    assert "/mcp/" in WRANGLER
    assert "run_worker_first" in WRANGLER


def test_runtime_handles_mcp_and_mcp_slash() -> None:
    assert 'stripped === "/mcp"' in RUNTIME
    assert "handleMcp" in RUNTIME
    assert "handleMcpJson" in RUNTIME
    assert "replace(/\\/+$/, " in RUNTIME or 'replace(/\\/+$/' in RUNTIME


def test_jsonrpc_methods_and_thin_doubles() -> None:
    for method in ("initialize", "tools/list", "tools/call", "ping"):
        assert method in RUNTIME
    for tool in THIN_TOOLS:
        assert tool in RUNTIME
    assert "protocolVersion" in RUNTIME
    assert "jsonrpc" in RUNTIME


def test_mcp_points_at_fraggate_slug_peacelock() -> None:
    assert 'slug: "peacelock"' in RUNTIME or "slug=peacelock" in RUNTIME
    assert "aziel-runtime.vibelock.workers.dev" in RUNTIME
    assert "/v1/fraggate/call" in RUNTIME
    assert 'door: "fraggate"' in RUNTIME or "door: 'fraggate'" in RUNTIME


def test_mcp_refuses_transcript_and_duty_bypass() -> None:
    for name in ("transcript", "motive", "counterfactual", "waive-duty", "bypass-duty"):
        assert name in RUNTIME
    assert "PL-REFUSE" in RUNTIME
    assert "HARD_DUTY" in RUNTIME


def test_mcp_does_not_increment_downloads() -> None:
    assert "kv_increment: false" in RUNTIME
    assert "Does not increment" in RUNTIME or "does not increment" in RUNTIME.lower()


def test_docs_advertise_worker_mcp() -> None:
    assert "peacelock-download-tracker.vibelock.workers.dev/mcp" in README
    assert "peacelock-download-tracker.vibelock.workers.dev/mcp" in SKILL
    assert "aziel-runtime.vibelock.workers.dev/mcp" in README
    assert "Aziel Eliab" in README
    assert "handleRuntimeApi" in INDEX
