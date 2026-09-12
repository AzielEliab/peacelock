"""Worker homepage rose-star brand mark (Aziel Eliab only).

Public HTML uses /sigil.png with empty alt and no everblooming mark copy.
Verify contracts that require Everblooming header/skill strings stay unchanged.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = (ROOT / "workers" / "download-tracker" / "src" / "home.js").read_text(
    encoding="utf-8"
)
RUNTIME = (ROOT / "workers" / "download-tracker" / "src" / "runtime.js").read_text(
    encoding="utf-8"
)
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
PUBLIC_SIGIL = ROOT / "workers" / "download-tracker" / "public" / "sigil.png"

BRANDMARK = (
    '<img class="brandmark" src="/sigil.png" width="40" height="40" alt="" decoding="async">'
)


def test_homepage_brandmark_is_empty_alt_rose_star() -> None:
    assert BRANDMARK in HOME
    assert 'class="brandrow"' in HOME
    assert 'class="brandmark"' in HOME
    assert 'src="/sigil.png"' in HOME
    assert 'alt=""' in HOME
    assert "<p class=\"stamp\">Aziel Eliab</p>" in HOME
    assert "Aziel Eliab" in HOME


def test_ai_runtime_page_matches_homepage_brandmark() -> None:
    assert BRANDMARK in RUNTIME
    assert "<p class=\"stamp\">Aziel Eliab</p>" in RUNTIME
    html = RUNTIME[RUNTIME.index("<!doctype html>") : RUNTIME.rindex("</html>") + 7]
    assert "everblooming" not in html.lower()
    assert "Everblooming sigil" not in RUNTIME


def test_public_html_does_not_name_everblooming_on_the_mark() -> None:
    html = HOME[HOME.index("<!doctype html>") : HOME.rindex("</html>") + 7]
    assert "everblooming" not in html.lower()
    assert "Everblooming sigil" not in HOME
    assert 'alt="everblooming sigil"' not in HOME.lower()
    assert 'title="Home — everblooming sigil"' not in HOME
    assert 'title="Everblooming sigil · Aziel Eliab"' not in HOME
    brand_start = HOME.find('<div class="brandrow">')
    brand_end = HOME.find("</div>", brand_start) + len("</div>")
    brand = HOME[brand_start:brand_end]
    assert BRANDMARK in brand
    assert "everblooming" not in brand.lower()
    assert 'alt=""' in brand


def test_hosted_sigil_is_official_rose_star_png() -> None:
    assert PUBLIC_SIGIL.is_file()
    data = PUBLIC_SIGIL.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    # Official Aziel rose-star is ~75KB. Reject the 4KB placeholder.
    assert 70000 <= len(data) <= 80000
    assert len(data) == 75035


def test_skill_and_runtime_identity_contracts_unchanged() -> None:
    """Header/skill verify strings stay as they were (Aziel Eliab only)."""
    assert "PeaceLock" in SKILL
    assert "Author Aziel Eliab" in SKILL or "Author: **Aziel Eliab**" in SKILL
    assert "const SKILL =" in RUNTIME
    assert "name: PeaceLock" in RUNTIME
    assert "Author Aziel Eliab" in RUNTIME or "Author: **Aziel Eliab**" in RUNTIME
    assert "Aziel Eliab" in RUNTIME
    # Do not rewrite header/skill strings if a verify contract requires
    # the words "Everblooming" — none exist on this public mark.
    assert "Everblooming" not in BRANDMARK
    assert "Everblooming" not in SKILL
