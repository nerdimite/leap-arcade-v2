from leap.games.wiki.html_rewriter import WikiHtmlRewriter


def test_rewriter_strips_script_and_marks_internal_links() -> None:
    raw = """
    <section><script>alert(1)</script><p><a href="/wiki/Foo_bar">Foo</a>
    <a href="https://en.wikipedia.org/wiki/Other_Page">Other</a>
    <a href="https://evil.test/x">bad</a></p></section>
    """
    out = WikiHtmlRewriter().rewrite(raw)
    assert "<script>" not in out.html
    assert 'data-wiki-title="Foo bar"' in out.html
    assert 'data-wiki-title="Other Page"' in out.html
    assert "evil.test" not in out.html
    assert set(out.internal_link_titles) == {"Foo bar", "Other Page"}
