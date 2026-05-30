"""Pure HTML transformation for Wikimedia REST article snippets."""

import re
from typing import List, Optional, Set, Tuple
from urllib.parse import parse_qs, unquote, urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag

from leap.types.wiki import RewrittenWikiHtmlDTO

_WIKI_PATH_PREFIX = "/wiki/"
_HOSTS = {"en.wikipedia.org", "en.m.wikipedia.org"}
_DISALLOWED_TITLE_PREFIXES = (
    "Talk:",
    "Category:",
    "File:",
    "Special:",
    "Help:",
    "Wikipedia:",
    "Template:",
    "Draft:",
    "User:",
    "Portal:",
    "MediaWiki:",
)

# Hosts that serve static images for Wikimedia projects (PRD: trusted Wikimedia images).
_TRUSTED_IMAGE_HOST_SUFFIXES = (".wikimedia.org",)


def _normalize_href_for_parse(href: str) -> str:
    if href.startswith("//"):
        return f"https:{href}"
    return href


def _tag_classes(tag: Tag) -> List[str]:
    raw = tag.get("class")
    if raw is None:
        return []
    if isinstance(raw, str):
        return raw.split()
    if isinstance(raw, list):
        return [str(c) for c in raw]
    return [str(raw)]


def _is_red_link(tag: Tag) -> bool:
    return "new" in _tag_classes(tag) or "mw-redlink" in _tag_classes(tag)


def _decode_wiki_title_from_path(path: str) -> str:
    """Extract MediaWiki page title from a /wiki/... path segment."""
    if not path.startswith(_WIKI_PATH_PREFIX):
        return ""
    raw = path[len(_WIKI_PATH_PREFIX) :]
    anchor = raw.find("#")
    if anchor >= 0:
        raw = raw[:anchor]
    title = unquote(raw).replace("_", " ")
    return title.strip()


def _decode_wiki_title_from_relative_href(href: str) -> str:
    """Extract MediaWiki page title from Parsoid-style relative article hrefs."""
    raw = href.strip()
    while raw.startswith("./"):
        raw = raw[2:]
    while raw.startswith("../"):
        raw = raw[3:]
    anchor = raw.find("#")
    if anchor >= 0:
        raw = raw[:anchor]
    query = raw.find("?")
    if query >= 0:
        raw = raw[:query]
    if not raw:
        return ""
    return unquote(raw).replace("_", " ").strip()


def _is_disallowed_article_title(title: str) -> bool:
    return any(title.startswith(p) for p in _DISALLOWED_TITLE_PREFIXES)


def _fragment_is_disallowed_citation(fragment: str) -> bool:
    """PRD: citation jumps disabled."""
    if not fragment:
        return False
    lower = fragment.lower()
    if lower in {
        "references",
        "refs",
        "notes",
        "footnotes",
        "bibliography",
        "sources",
        "external_links",
        "further_reading",
    }:
        return True
    for prefix in ("cite_", "cite-", "cite_ref", "cite_note", "citerf"):
        if lower.startswith(prefix):
            return True
    return False


def _same_page_hash_only(href: str) -> bool:
    return href.startswith("#") and len(href) > 1


def _href_is_edit(url: str) -> bool:
    parsed = urlparse(_normalize_href_for_parse(url))
    if "/w/index.php" in url or (parsed.path or "").endswith("/index.php"):
        qs = parse_qs(parsed.query)
        acts = qs.get("action", [])
        return "edit" in acts
    return "action=edit" in url


def _host_trusted_for_images(hostname: str) -> bool:
    h = (hostname or "").lower()
    if h == "commons.wikimedia.org" or h == "upload.wikimedia.org":
        return True
    return any(h.endswith(sfx) for sfx in _TRUSTED_IMAGE_HOST_SUFFIXES)


def _img_url_is_trusted(raw: str) -> bool:
    if not raw or not isinstance(raw, str):
        return False
    p = urlparse(_normalize_href_for_parse(raw.strip()))
    return _host_trusted_for_images(p.hostname or "")


def _sanitize_srcset(srcset: str) -> Optional[str]:
    """Return a filtered srcset or None if nothing trusted remains."""
    parts_out: List[str] = []
    for chunk in srcset.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        bits = chunk.rsplit(None, 1)
        url = bits[0]
        if len(bits) == 2 and (bits[1].endswith("w") or bits[1].endswith("x")):
            descriptor = bits[1]
            if _img_url_is_trusted(url):
                parts_out.append(f"{url} {descriptor}")
        else:
            if _img_url_is_trusted(bits[0]):
                parts_out.append(chunk)
    if not parts_out:
        return None
    return ", ".join(parts_out)


def _internal_wiki_title_from_href(href: str) -> Optional[Tuple[str, str]]:
    """
    If href targets an enwiki article path, return (decoded_title, url_fragment).
    Otherwise None. Does not apply namespace / redlink policy.
    """
    h = _normalize_href_for_parse(href.strip())
    parsed = urlparse(h)
    path = parsed.path or ""
    frag = parsed.fragment or ""

    host = (parsed.hostname or "").lower()
    scheme = (parsed.scheme or "").lower()

    if scheme in ("http", "https") and host in _HOSTS and path.startswith(_WIKI_PATH_PREFIX):
        title = _decode_wiki_title_from_path(path)
        return (title, frag)

    if (not host or scheme == "") and path.startswith(_WIKI_PATH_PREFIX):
        title = _decode_wiki_title_from_path(path)
        return (title, frag)

    if raw_h := href.strip():
        if raw_h.startswith("./") or raw_h.startswith("../"):
            title = _decode_wiki_title_from_relative_href(raw_h)
            if title:
                return (title, frag)

    return None


# Inline style declarations that would fight the frontend light-island skin.
# Wikimedia/Parsoid markup ships navbox/sidebar/infobox cells with their own
# background + text colours; on the dark app surface those render as black
# boxes. We strip colour-bearing declarations (and the legacy `bgcolor` attr)
# so the scoped `.leap-wiki-skin` CSS fully owns the palette.
_COLOR_STYLE_PROPS = frozenset(
    {
        "background",
        "background-color",
        "background-image",
        "color",
        "border-color",
        "box-shadow",
        "filter",
    }
)


def _neutralize_inline_colors(tag: Tag) -> int:
    """Drop colour-related inline styles/attrs so the light skin controls them."""
    removed = 0
    if tag.has_attr("bgcolor"):
        del tag["bgcolor"]
        removed += 1
    raw_style = tag.get("style")
    if isinstance(raw_style, str) and raw_style.strip():
        kept: List[str] = []
        for decl in raw_style.split(";"):
            if not decl.strip():
                continue
            prop, sep, _value = decl.partition(":")
            if sep and prop.strip().lower() in _COLOR_STYLE_PROPS:
                removed += 1
                continue
            kept.append(decl.strip())
        if kept:
            tag["style"] = "; ".join(kept)
        else:
            del tag["style"]
    return removed


def _strip_untrusted_img(tag: Tag) -> None:
    raw_src = tag.get("src")
    raw_srcset = tag.get("srcset")
    src_ok = bool(raw_src and _img_url_is_trusted(str(raw_src)))
    filtered_set: Optional[str] = None
    if raw_srcset and isinstance(raw_srcset, str):
        filtered_set = _sanitize_srcset(raw_srcset)

    if not src_ok and filtered_set:
        first_chunk = filtered_set.split(",")[0].strip().split()
        if first_chunk:
            tag["src"] = first_chunk[0]
        tag["srcset"] = filtered_set
        return

    if not src_ok:
        tag.decompose()
        return

    if raw_srcset and isinstance(raw_srcset, str):
        if filtered_set:
            tag["srcset"] = filtered_set
        else:
            del tag["srcset"]


class WikiHtmlRewriter:
    """Rewrite Wikimedia HTML into game-safe markup (PRD link policy)."""

    def rewrite(self, html: str) -> RewrittenWikiHtmlDTO:
        parsed = BeautifulSoup(html, "html.parser")
        body = parsed.body
        fragment_html = body.decode_contents() if body is not None else html
        soup = BeautifulSoup(fragment_html, "html.parser")
        removed = 0
        internal_titles: Set[str] = set()

        for tag in soup.find_all("script"):
            tag.decompose()
        for tag in soup.find_all("style"):
            tag.decompose()
        for tag in soup.find_all(["base", "head", "html", "body", "meta", "link", "title"]):
            tag.decompose()
        for tag in soup.find_all(["iframe", "object", "embed"]):
            tag.decompose()

        for tag in soup.find_all(True):
            for attr in list(tag.attrs):
                if attr.startswith("on"):
                    del tag[attr]
                    removed += 1
            removed += _neutralize_inline_colors(tag)

        for img in soup.find_all("img"):
            _strip_untrusted_img(img)

        for a in soup.find_all("a"):
            href = a.get("href")
            if not href or not isinstance(href, str):
                a.unwrap()
                removed += 1
                continue

            low = href.strip().lower()
            if (
                low.startswith("javascript:")
                or low.startswith("data:")
                or low.startswith("vbscript:")
            ):
                a.unwrap()
                removed += 1
                continue

            if _href_is_edit(href):
                a.unwrap()
                removed += 1
                continue

            if _same_page_hash_only(href):
                frag = href[1:]
                if _fragment_is_disallowed_citation(frag):
                    a.unwrap()
                    removed += 1
                continue

            parsed_internal = _internal_wiki_title_from_href(href)
            if parsed_internal is not None:
                title, frag = parsed_internal
                if frag and _fragment_is_disallowed_citation(frag):
                    a.unwrap()
                    removed += 1
                    continue
                if title and not _is_disallowed_article_title(title) and not _is_red_link(a):
                    internal_titles.add(title)
                    a["data-wiki-title"] = title
                    a["href"] = "#"
                else:
                    a.unwrap()
                    removed += 1
                continue

            # External / non-enwiki navigation → leave text only
            a.unwrap()
            removed += 1

        out_html = str(soup)
        out_html = re.sub(r"<br\s*/>", "<br/>", out_html)
        return RewrittenWikiHtmlDTO(
            html=out_html,
            internal_link_titles=sorted(internal_titles),
            removed_link_count=removed,
        )
