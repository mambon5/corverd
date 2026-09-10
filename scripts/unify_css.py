#!/usr/bin/env python3
"""
Unify duplicated WordPress inline CSS into static/css/corverd.css
and convert standalone templates to {% extends 'base_layout.html' %}.
Preserves visual design; page-specific CSS goes to static/css/pages/.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("/var/www/corverd")
TEMPLATES = ROOT / "templates"
CSS_DIR = ROOT / "static" / "css"
PAGES_CSS = CSS_DIR / "pages"

STANDALONE = [
    "index.html",
    "inici.html",
    "sobre.html",
    "serveis.html",
    "recursos.html",
    "faq.html",
    "testimonis.html",
    "blog.html",
    "manifest.html",
    "contacte.html",
    "login.html",
    "entitats.html",
    "entitat_activitats.html",
    "activitats_calendar.html",
    "intranet/dashboard.html",
    "intranet/formulari.html",
]

# Manual page titles when auto-extract is wrong (banner says FAQ etc.)
PAGE_TITLES = {
    "index.html": "",
    "inici.html": "",
    "entitats.html": "Entitats",
    "entitat_activitats.html": "Activitats",
    "activitats_calendar.html": "Calendari d'Activitats",
    "blog.html": "Blog",
}

# Pages that should hide the tertiary title banner (homepage-style)
HIDE_TITLE_BANNER = {"index.html", "inici.html", "blog.html", "activitats_calendar.html"}

# Classifiers for page-specific CSS (selectors that should not go in shared file)
PAGE_CSS_HINTS = {
    "index": [".cover-responsive"],
    "inici": [".cover-responsive"],
    "entitats": [".entitat-card", ".entitats-grid", ".entitat-foto", ".entitat-action", "page-id-31"],
    "entitat_activitats": ["#calendar", ".back-link"],
    "activitats_calendar": [
        ".calendar-layout-container",
        ".event-modal",
        ".fc-custom-event",
        ".filters-toggle",
        ".sidebar",
    ],
    "adhesio": [".adhesio-"],
    "mapa_entitats": [".map-container", ".filter-sidebar", ".entity-filter", ".btn-all", ".btn-none"],
    "noticia_detail": [".comment-section", ".comment"],
}


def strip_style_tags(html: str) -> tuple[str, list[tuple[str | None, str]]]:
    styles: list[tuple[str | None, str]] = []

    def repl(m: re.Match) -> str:
        attrs, css = m.group(1), m.group(2)
        sid = re.search(r"""id=['"]([^'"]+)""", attrs)
        styles.append((sid.group(1) if sid else None, css))
        return ""

    cleaned = re.sub(r"<style([^>]*)>(.*?)</style>", repl, html, flags=re.S | re.I)
    return cleaned, styles


def collect_best_shared_css() -> tuple[str, dict[str, str]]:
    """Merge style blocks across templates; keep longest CSS per id / fingerprint."""
    by_id: dict[str, str] = {}
    anon_by_fp: dict[str, str] = {}

    sources = ["base_layout.html"] + STANDALONE
    for rel in sources:
        path = TEMPLATES / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"<style([^>]*)>(.*?)</style>", text, re.S | re.I):
            attrs, css = m.group(1), m.group(2)
            sid = re.search(r"""id=['"]([^'"]+)""", attrs)
            css_stripped = css.strip()
            if not css_stripped:
                continue
            # Skip clearly page-specific anon blocks (keep for page files later)
            if sid is None and is_page_specific_css(css_stripped):
                continue
            if sid:
                key = sid.group(1)
                if key not in by_id or len(css_stripped) > len(by_id[key]):
                    by_id[key] = css_stripped
            else:
                fp = css_stripped[:120]
                if fp not in anon_by_fp or len(css_stripped) > len(anon_by_fp[fp]):
                    anon_by_fp[fp] = css_stripped

    # Nav submenu CSS
    nav = TEMPLATES / "nav.html"
    if nav.exists():
        _, nav_styles = strip_style_tags(nav.read_text(encoding="utf-8"))
        for _, css in nav_styles:
            anon_by_fp["nav-custom"] = css.strip()

    parts: list[str] = [
        "/* Coordinadora Verda — unified frontend styles (WordPress/Extendable shell) */",
        "/* Generated to remove duplicated inline <style> blocks from templates. */",
        "",
    ]
    # Stable order: known WP ids first (as in base_layout), then remaining, then anon
    preferred_order = [
        "wp-img-auto-sizes-contain-inline-css",
        "wp-block-site-logo-inline-css",
        "wp-block-site-title-inline-css",
        "wp-block-group-inline-css",
        "wp-block-group-theme-inline-css",
        "wp-block-navigation-link-inline-css",
        "wp-block-navigation-inline-css",
        "wp-block-social-links-inline-css",
        "wp-block-template-part-theme-inline-css",
        "wp-block-post-title-inline-css",
        "wp-block-post-featured-image-inline-css",
        "wp-block-post-date-inline-css",
        "wp-block-post-terms-inline-css",
        "wp-block-post-excerpt-inline-css",
        "wp-block-post-template-inline-css",
        "wp-block-heading-inline-css",
        "wp-block-paragraph-inline-css",
        "wp-block-quote-inline-css",
        "wp-block-quote-theme-inline-css",
        "wp-block-image-inline-css",
        "wp-block-image-theme-inline-css",
        "wp-block-gallery-theme-inline-css",
        "wp-block-columns-inline-css",
        "wp-block-button-inline-css",
        "wp-block-buttons-inline-css",
        "wp-block-spacer-inline-css",
        "wp-block-post-content-inline-css",
        "wp-block-media-text-inline-css",
        "wp-block-library-inline-css",
        "global-styles-inline-css",
        "block-style-variation-styles-inline-css",
        "wp-emoji-styles-inline-css",
        "core-block-supports-inline-css",
        "wp-block-template-skip-link-inline-css",
        "charitable-highlight-colour-styles",
    ]
    seen = set()
    for key in preferred_order:
        if key in by_id:
            parts.append(f"/* --- {key} --- */")
            parts.append(by_id[key])
            parts.append("")
            seen.add(key)
    for key, css in sorted(by_id.items()):
        if key in seen:
            continue
        parts.append(f"/* --- {key} --- */")
        parts.append(css)
        parts.append("")

    parts.append("/* --- shared anonymous / fonts / nav --- */")
    for css in anon_by_fp.values():
        parts.append(css)
        parts.append("")

    return "\n".join(parts), by_id


def is_page_specific_css(css: str) -> bool:
    markers = (
        ".cover-responsive",
        ".entitat-card",
        ".entitats-grid",
        ".entitat-foto",
        ".entitat-action",
        ".adhesio-",
        ".map-container",
        ".filter-sidebar",
        ".entity-filter",
        ".calendar-layout-container",
        ".event-modal",
        ".fc-custom-event",
        ".filters-toggle",
        ".comment-section",
        "page-id-31",
        ".back-link",
        "#calendar {",
        "Eliminem el límit",
    )
    return any(m in css for m in markers)


def extract_page_specific_styles(html: str, page_key: str) -> str:
    chunks: list[str] = []
    for m in re.finditer(r"<style([^>]*)>(.*?)</style>", html, re.S | re.I):
        css = m.group(2).strip()
        if is_page_specific_css(css):
            chunks.append(css)
        elif page_key in PAGE_CSS_HINTS:
            hints = PAGE_CSS_HINTS[page_key]
            if any(h in css for h in hints):
                chunks.append(css)
    return "\n\n".join(chunks)


def extract_entry_content(text: str) -> str | None:
    nav_pos = text.find("{% include 'nav.html' %}")
    search_from = nav_pos if nav_pos >= 0 else 0

    m = re.search(
        r'<div\s+class="entry-content[^"]*"[^>]*>|'
        r"<div\s*\n\s*class=\"entry-content[^\"]*\"[^>]*>",
        text[search_from:],
    )
    if not m:
        # blog / odd layouts: content between </header>…<main> inner and </main>
        main_m = re.search(r"<main[^>]*>", text[search_from:])
        footer_m = re.search(
            r"</main>\s*<footer\s+class=\"wp-block-template-part\"",
            text[search_from:],
        )
        if main_m and footer_m:
            main_start = search_from + main_m.end()
            main_end = search_from + footer_m.start()
            inner = text[main_start:main_end]
            # Prefer everything after title banner if present, else whole main inner
            return inner.strip()
        return None

    start = search_from + m.end()
    footer_m = re.search(
        r"</div>\s*</main>\s*<footer\s+class=\"wp-block-template-part\"",
        text[start:],
    )
    if footer_m:
        return text[start : start + footer_m.start()].strip()

    footer_m = re.search(
        r"<footer\s+class=\"wp-block-template-part\"", text[start:]
    )
    if not footer_m:
        return None
    before = text[start : start + footer_m.start()]
    before = re.sub(r"</div>\s*</main>\s*$", "", before.strip())
    before = re.sub(r"</div>\s*$", "", before.strip())
    return before.strip()


def extract_document_title(text: str, fallback: str) -> str:
    tm = re.search(r"<title>(.*?)</title>", text, re.S)
    if tm:
        return tm.group(1).strip()
    return fallback


def extract_page_title(text: str, rel: str) -> str:
    if rel in PAGE_TITLES:
        return PAGE_TITLES[rel]
    nav_pos = text.find("{% include 'nav.html' %}")
    search = text[nav_pos:] if nav_pos >= 0 else text
    # Only the title banner h1 (has-text-align-center wp-block-post-title)
    hm = re.search(
        r'class="[^"]*wp-block-post-title[^"]*"[^>]*>(.*?)</h1>',
        search,
        re.S,
    )
    if hm:
        return re.sub(r"<[^>]+>", "", hm.group(1)).strip()
    return ""


def extract_extra_head_links(text: str) -> str:
    """Keep page-specific stylesheet links (Leaflet, WPForms, etc.)."""
    keep_patterns = (
        "leaflet",
        "wpforms",
        "fullcalendar",
        "cdn.jsdelivr",
        "unpkg.com",
    )
    links = []
    for m in re.finditer(r"<link[^>]+>", text, re.I):
        tag = m.group(0)
        low = tag.lower()
        if "stylesheet" not in low:
            continue
        if any(p in low for p in keep_patterns):
            links.append(tag)
    return "\n".join(links)


def extract_extra_scripts(text: str) -> str:
    """Scripts that appear after WP shell scripts and are page-specific."""
    # Take scripts between end of main content area markers — simpler: scripts after footer
    footer = text.find('<footer class="wp-block-template-part"')
    if footer < 0:
        return ""
    after = text[footer:]
    # Remove common shared scripts that base_layout already has
    shared_markers = (
        "block-library/navigation/view.min.js",
        "wp-block-template-skip-link",
        "charitable-frontend",
        "extendable-navigation",
        "wp-emoji",
        "WP_MENU_JS_FIX",
        "trp-language-switcher",
        "speculationrules",
    )
    scripts = []
    for m in re.finditer(
        r"<script\b[^>]*>.*?</script>|<script\b[^>]*src=[^>]*>\s*</script>",
        after,
        re.S | re.I,
    ):
        block = m.group(0)
        if any(s in block for s in shared_markers):
            continue
        if "tp-language" in block:
            continue
        scripts.append(block)
    # Also inline scripts inside entry-content stay in content; this is for bottom scripts
    return "\n".join(scripts)


def build_child_template(
    rel: str,
    title: str,
    page_title: str,
    content: str,
    page_css_href: str | None,
    extra_links: str,
    extra_js: str,
    hide_banner: bool,
) -> str:
    # Remove inline styles from content (moved to page css)
    content_clean, _ = strip_style_tags(content)
    content_clean = content_clean.strip()

    parts = [
        "{% extends 'base_layout.html' %}",
        "",
        f"{{% block title %}}{title}{{% endblock %}}",
        "",
    ]
    if hide_banner:
        parts.append("{% block page_title_banner %}{% endblock %}")
        parts.append("")
    elif page_title:
        parts.append(f"{{% block page_title %}}{page_title}{{% endblock %}}")
        parts.append("")

    if page_css_href or extra_links:
        parts.append("{% block extra_css %}")
        if extra_links:
            parts.append(extra_links)
        if page_css_href:
            parts.append(
                f'<link rel="stylesheet" href="{{{{ STATIC_URL|default:\'/static/\' }}}}{page_css_href}">'
            )
            # Prefer {% static %} if available — use plain /static/ for consistency with rest of site
            parts[-1] = f'<link rel="stylesheet" href="/static/{page_css_href}">'
        parts.append("{% endblock %}")
        parts.append("")

    parts.append("{% block content %}")
    parts.append(content_clean)
    parts.append("{% endblock %}")

    if extra_js.strip():
        parts.append("")
        parts.append("{% block extra_js %}")
        parts.append(extra_js.strip())
        parts.append("{% endblock %}")

    parts.append("")
    return "\n".join(parts)


def update_base_layout() -> None:
    path = TEMPLATES / "base_layout.html"
    text = path.read_text(encoding="utf-8")

    # Remove all inline style blocks in head
    text2, _ = strip_style_tags(text)

    # Insert unified CSS link before extra_css block (after favicons / before extra_css)
    link = (
        '\t<link rel="stylesheet" id="corverd-unified-css" '
        'href="/static/css/corverd.css" media="all" />\n'
    )
    if "corverd.css" not in text2:
        text2 = text2.replace(
            "{% block extra_css %}{% endblock %}",
            link + "{% block extra_css %}{% endblock %}",
        )

    # Wrap page title banner in a block so pages can hide it
    banner_start = text2.find(
        '<div class="wp-block-group alignfull has-tertiary-background-color'
    )
    banner_end_marker = (
        '</div>\n\n\t\t\t<div\n\t\t\t\tclass="entry-content wp-block-post-content'
    )
    # Try flexible match
    m = re.search(
        r'(<div class="wp-block-group alignfull has-tertiary-background-color.*?'
        r'</div>\s*</div>\s*</div>\s*)'
        r'(<div\s+class="entry-content)',
        text2,
        re.S,
    )
    if m and "page_title_banner" not in text2:
        banner = m.group(1)
        text2 = (
            text2[: m.start(1)]
            + "{% block page_title_banner %}\n"
            + banner
            + "{% endblock %}\n\t\t\t"
            + m.group(2)
            + text2[m.end(2) :]
        )

    path.write_text(text2, encoding="utf-8")
    print(f"Updated base_layout.html ({path.stat().st_size} bytes)")


def update_nav() -> None:
    path = TEMPLATES / "nav.html"
    text = path.read_text(encoding="utf-8")
    text2, _ = strip_style_tags(text)
    # remove leading blank lines from removed style
    text2 = text2.lstrip("\n")
    path.write_text(text2, encoding="utf-8")
    print(f"Updated nav.html (styles moved to corverd.css)")


def convert_extends_templates_css() -> None:
    """Move inline CSS from already-extending templates into page CSS files."""
    mapping = {
        "adhesio.html": "adhesio.css",
        "mapa_entitats.html": "mapa_entitats.css",
        "noticia_detail.html": "noticia_detail.css",
    }
    for rel, css_name in mapping.items():
        path = TEMPLATES / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        page_css = extract_page_specific_styles(text, rel.replace(".html", ""))
        if not page_css:
            # all style blocks
            _, styles = strip_style_tags(text)
            page_css = "\n\n".join(c for _, c in styles if c.strip())
        if page_css:
            out = PAGES_CSS / css_name
            out.write_text(
                f"/* Page styles: {rel} */\n{page_css}\n", encoding="utf-8"
            )
            text2, _ = strip_style_tags(text)
            # Ensure extra_css links the file
            link = f'<link rel="stylesheet" href="/static/css/pages/{css_name}">'
            if "extra_css" in text2:
                text2 = re.sub(
                    r"\{%\s*block extra_css\s*%\}.*?\{%\s*endblock\s*%\}",
                    "{% block extra_css %}\n"
                    + link
                    + "\n{% endblock %}",
                    text2,
                    count=1,
                    flags=re.S,
                )
            else:
                # noticia_detail may not extend — leave content styles removed only if extends
                if "{% extends" in text2:
                    text2 = text2.replace(
                        "{% block content %}",
                        "{% block extra_css %}\n"
                        + link
                        + "\n{% endblock %}\n\n{% block content %}",
                        1,
                    )
            path.write_text(text2, encoding="utf-8")
            print(f"  Moved CSS for {rel} -> pages/{css_name}")


def convert_standalone() -> None:
    for rel in STANDALONE:
        path = TEMPLATES / rel
        text = path.read_text(encoding="utf-8")
        if "{% extends" in text:
            print(f"SKIP already extends: {rel}")
            continue

        page_key = Path(rel).stem
        content = extract_entry_content(text)
        if content is None:
            print(f"FAIL extract content: {rel}")
            continue

        title = extract_document_title(text, page_key)
        page_title = extract_page_title(text, rel)
        hide = rel in HIDE_TITLE_BANNER

        page_css = extract_page_specific_styles(text, page_key)
        # For calendar/entitats: also grab anon styles in head that are page specific
        page_css_href = None
        if page_css.strip():
            css_name = f"{page_key}.css"
            (PAGES_CSS / css_name).write_text(
                f"/* Page styles: {rel} */\n{page_css}\n", encoding="utf-8"
            )
            page_css_href = f"css/pages/{css_name}"

        extra_links = extract_extra_head_links(text)
        extra_js = extract_extra_scripts(text)

        # Blog: content is whole main inner including title area — strip header leftovers
        if rel == "blog.html":
            # blog has no entry-content; content is main inner — may include title banner
            # Keep as-is inside content block; hide page_title_banner from base
            hide = True
            page_title = ""

        new_html = build_child_template(
            rel,
            title,
            page_title,
            content,
            page_css_href,
            extra_links,
            extra_js,
            hide,
        )
        path.write_text(new_html, encoding="utf-8")
        print(
            f"Converted {rel}: {len(text)} -> {len(new_html)} bytes "
            f"(content {len(content)})"
        )


def main() -> None:
    CSS_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_CSS.mkdir(parents=True, exist_ok=True)

    print("=== Building unified corverd.css ===")
    css, by_id = collect_best_shared_css()
    out = CSS_DIR / "corverd.css"
    out.write_text(css, encoding="utf-8")
    print(f"Wrote {out} ({len(css)} bytes, {len(by_id)} named blocks)")

    print("\n=== Updating base_layout & nav ===")
    update_base_layout()
    update_nav()

    print("\n=== Converting standalone templates ===")
    convert_standalone()

    print("\n=== Page CSS for extending templates ===")
    convert_extends_templates_css()

    print("\nDone.")


if __name__ == "__main__":
    main()
