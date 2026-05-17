"""PRD policy assertions for seed-derived Wikipedia HTML fixtures (no network)."""

import re

import pytest

from leap.games.wiki.html_rewriter import WikiHtmlRewriter

from tests.fixtures.wiki_html_fixtures import SEED_HTML_FIXTURES


def _assert_game_safe_rewritten(html: str) -> None:
    """Stable markers: no external navigation via <a>, no scripts, no raw handlers."""
    lower = html.lower()
    assert "<script" not in lower
    assert "<iframe" not in lower
    assert "onclick=" not in lower
    assert "javascript:" not in lower
    # Anchors must not point off-site (trusted Wikimedia image URLs on <img> are ok)
    assert re.search(r"""<a[^>]*\bhref\s*=\s*["']https?://""", html, re.IGNORECASE) is None


@pytest.mark.parametrize("fixture_name", sorted(SEED_HTML_FIXTURES.keys()))
def test_seed_fixture_rewrites_to_game_safe_html(fixture_name: str) -> None:
    raw = SEED_HTML_FIXTURES[fixture_name]
    out = WikiHtmlRewriter().rewrite(raw)
    _assert_game_safe_rewritten(out.html)


def test_biology_fixture_keeps_upload_wikimedia_image() -> None:
    snippet = (
        '<section><img src="https://upload.wikimedia.org/wikipedia/commons/x.png" alt="x"/>'
        "<p><a href=\"/wiki/Test\">t</a></p></section>"
    )
    out = WikiHtmlRewriter().rewrite(snippet)
    assert "upload.wikimedia.org" in out.html
    _assert_game_safe_rewritten(out.html)


def test_biology_in_fiction_strips_evil_and_cite_links() -> None:
    raw = SEED_HTML_FIXTURES["biology_in_fiction"]
    out = WikiHtmlRewriter().rewrite(raw)
    assert "evil.example" not in out.html
    assert 'data-wiki-title="Intelligent machine"' in out.html
    assert "cite_note" not in out.html
    assert "Some_page" not in out.html
