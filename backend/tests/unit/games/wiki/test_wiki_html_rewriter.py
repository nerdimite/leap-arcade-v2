"""WikiHtmlRewriter policy tests (PRD link sanitization)."""

from leap.games.wiki.html_rewriter import WikiHtmlRewriter


def test_internal_article_link_becomes_game_link_with_data_title() -> None:
    html = '<p><a href="/wiki/Foo_bar">Foo</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert 'data-wiki-title="Foo bar"' in out.html
    assert 'href="#"' in out.html
    assert "Foo bar" in out.internal_link_titles


def test_cross_page_wiki_link_uses_page_title_only() -> None:
    html = '<p><a href="/wiki/Other_page#Section">Jump</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert 'data-wiki-title="Other page"' in out.html
    assert "#Section" not in out.html


def test_relative_parsoid_article_link_becomes_game_link() -> None:
    html = '<p><a href="./Personal_computer">Personal computer</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert 'data-wiki-title="Personal computer"' in out.html
    assert 'href="#"' in out.html
    assert "Personal computer" in out.internal_link_titles


def test_relative_parsoid_article_link_with_fragment_uses_page_title_only() -> None:
    html = '<p><a href="./ThinkCentre#S50">ThinkCentre</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert 'data-wiki-title="ThinkCentre"' in out.html
    assert "#S50" not in out.html


def test_full_document_wrappers_and_base_are_removed() -> None:
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <base href="//en.wikipedia.org/wiki/">
        <title>Biology</title>
        <meta charset="utf-8">
        <link rel="stylesheet" href="/w/load.php?foo=bar">
      </head>
      <body>
        <section><p><a href="/wiki/Cell_(biology)">Cell</a></p></section>
      </body>
    </html>
    """
    out = WikiHtmlRewriter().rewrite(html)
    lowered = out.html.lower()
    assert "<html" not in lowered
    assert "<head" not in lowered
    assert "<body" not in lowered
    assert "<base" not in lowered
    assert "<title" not in lowered
    assert "<meta" not in lowered
    assert "<link" not in lowered
    assert 'data-wiki-title="Cell (biology)"' in out.html


def test_same_page_hash_link_keeps_fragment_for_scroll() -> None:
    html = '<p><a href="#See_also">See also</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert 'href="#See_also"' in out.html
    assert "data-wiki-title" not in out.html


def test_talk_namespace_disabled() -> None:
    html = '<p><a href="/wiki/Talk:Science">Discuss</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "data-wiki-title" not in out.html
    assert "<a " not in out.html


def test_category_namespace_disabled() -> None:
    html = '<p><a href="/wiki/Category:Fish">Cat</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "data-wiki-title" not in out.html


def test_file_namespace_disabled() -> None:
    html = '<p><a href="/wiki/File:Example.png">img</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "data-wiki-title" not in out.html


def test_special_page_disabled() -> None:
    html = '<p><a href="/wiki/Special:Search">Search</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "data-wiki-title" not in out.html


def test_red_link_class_new_disabled() -> None:
    html = '<p><a href="/wiki/Nonexistent" class="new">red</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "data-wiki-title" not in out.html


def test_external_href_disabled() -> None:
    html = '<p><a href="https://evil.example/phish">Outside</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "evil.example" not in out.html
    assert "Outside" in out.html


def test_citation_note_fragment_disabled() -> None:
    html = '<p><a href="#cite_note-1">[1]</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "<a " not in out.html
    assert "[1]" in out.html


def test_script_removed() -> None:
    html = '<section><script>x()</script><p>a</p></section>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "<script" not in out.html
    assert "onload" not in out.html


def test_on_click_stripped() -> None:
    html = '<p onclick="alert(1)">Hi</p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "onclick" not in out.html


def test_inline_background_color_stripped_for_light_skin() -> None:
    # Parsoid navbox/sidebar cells ship their own backgrounds; on the dark app
    # surface those render as black boxes, so colour declarations are removed.
    html = '<table class="navbox" style="background-color:#0a0a0a;color:#fff;width:22em">x</table>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "background-color" not in out.html
    assert "color:#fff" not in out.html
    # Non-colour layout declarations survive.
    assert "width:22em" in out.html


def test_legacy_bgcolor_attribute_removed() -> None:
    html = '<td bgcolor="#000000">cell</td>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "bgcolor" not in out.html
    assert "cell" in out.html


def test_style_attribute_dropped_when_only_colors() -> None:
    html = '<div style="background:#111;color:#eee">series</div>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "style=" not in out.html
    assert "series" in out.html


def test_protocol_relative_enwiki_link_rewritten() -> None:
    html = '<p><a href="//en.wikipedia.org/wiki/Protocol_rel">x</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert 'data-wiki-title="Protocol rel"' in out.html
    assert "Protocol rel" in out.internal_link_titles


def test_javascript_href_removed() -> None:
    html = '<p><a href="javascript:alert(1)">bad</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "<a " not in out.html
    assert "javascript" not in out.html


def test_wiki_link_with_cite_fragment_is_plain_text() -> None:
    html = '<p><a href="/wiki/Some_article#cite_note-2">note</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "data-wiki-title" not in out.html
    assert "note" in out.html


def test_iframe_removed() -> None:
    html = '<iframe src="https://evil.example/x"></iframe><p>ok</p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "iframe" not in out.html.lower()
    assert "evil.example" not in out.html


def test_trusted_wikimedia_image_keeps_src() -> None:
    html = (
        '<p><img src="https://upload.wikimedia.org/wikipedia/commons/x.png" alt="i"/></p>'
    )
    out = WikiHtmlRewriter().rewrite(html)
    assert "upload.wikimedia.org" in out.html
    assert "<img " in out.html


def test_untrusted_image_removed() -> None:
    html = '<p><img src="https://evil.example/track.gif" alt="x"/></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "<img " not in out.html
    assert "evil.example" not in out.html


def test_user_namespace_disabled() -> None:
    html = '<p><a href="/wiki/User:Someone">user</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "data-wiki-title" not in out.html


def test_portal_namespace_disabled() -> None:
    html = '<p><a href="/wiki/Portal:Technology">portal</a></p>'
    out = WikiHtmlRewriter().rewrite(html)
    assert "data-wiki-title" not in out.html
