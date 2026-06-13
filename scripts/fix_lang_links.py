#!/usr/bin/env python3
"""Fix language switcher static hrefs, JS updaters, and invalid script comments site-wide."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    "index.html",
    "framework.html",
    "leadership.html",
    "action-guide.html",
    "examples.html",
    "resources.html",
    "assessment.html",
]

LANG_IDS = [
    ("lang-link-en", "en"),
    ("lang-link-ja", "ja"),
    ("lang-link-de", "de"),
    ("lang-link-zh", "zh"),
]


def expected_hrefs(locale: str, page: str) -> dict[str, str]:
    if page == "index.html":
        return {"en": "/", "ja": "/ja/", "de": "/de/", "zh": "/zh/"}
    if locale == "":
        return {
            "en": page,
            "ja": f"ja/{page}",
            "de": f"de/{page}",
            "zh": f"zh/{page}",
        }
    return {
        "en": f"../{page}",
        "ja": page if locale == "ja" else f"../ja/{page}",
        "de": page if locale == "de" else f"../de/{page}",
        "zh": page if locale == "zh" else f"../zh/{page}",
    }


def js_iife(locale: str) -> str:
    if locale == "":
        return """
        (function() {
            const currentPage = window.location.pathname.split('/').pop() || 'index.html';
            const langLinkEn = document.getElementById('lang-link-en');
            const langLinkJa = document.getElementById('lang-link-ja');
            const langLinkDe = document.getElementById('lang-link-de');
            const langLinkZh = document.getElementById('lang-link-zh');
            const langLinkEnMobile = document.getElementById('lang-link-en-mobile');
            const langLinkJaMobile = document.getElementById('lang-link-ja-mobile');
            const langLinkDeMobile = document.getElementById('lang-link-de-mobile');
            const langLinkZhMobile = document.getElementById('lang-link-zh-mobile');

            const enHref = currentPage === 'index.html' ? '/' : currentPage;
            const jaHref = currentPage === 'index.html' ? '/ja/' : 'ja/' + currentPage;
            const deHref = currentPage === 'index.html' ? '/de/' : 'de/' + currentPage;
            const zhHref = currentPage === 'index.html' ? '/zh/' : 'zh/' + currentPage;

            if (langLinkEn) langLinkEn.href = enHref;
            if (langLinkJa) langLinkJa.href = jaHref;
            if (langLinkDe) langLinkDe.href = deHref;
            if (langLinkZh) langLinkZh.href = zhHref;
            if (langLinkEnMobile) langLinkEnMobile.href = enHref;
            if (langLinkJaMobile) langLinkJaMobile.href = jaHref;
            if (langLinkDeMobile) langLinkDeMobile.href = deHref;
            if (langLinkZhMobile) langLinkZhMobile.href = zhHref;
        })();"""

    def loc_href(loc: str) -> str:
        if loc == locale:
            return "currentPage"
        return f"'../{loc}/' + currentPage"

    return f"""
        (function() {{
            const currentPage = window.location.pathname.split('/').pop() || 'index.html';
            const langLinkEn = document.getElementById('lang-link-en');
            const langLinkJa = document.getElementById('lang-link-ja');
            const langLinkDe = document.getElementById('lang-link-de');
            const langLinkZh = document.getElementById('lang-link-zh');
            const langLinkEnMobile = document.getElementById('lang-link-en-mobile');
            const langLinkJaMobile = document.getElementById('lang-link-ja-mobile');
            const langLinkDeMobile = document.getElementById('lang-link-de-mobile');
            const langLinkZhMobile = document.getElementById('lang-link-zh-mobile');

            if (currentPage === 'index.html') {{
                if (langLinkEn) langLinkEn.href = '/';
                if (langLinkJa) langLinkJa.href = '/ja/';
                if (langLinkDe) langLinkDe.href = '/de/';
                if (langLinkZh) langLinkZh.href = '/zh/';
                if (langLinkEnMobile) langLinkEnMobile.href = '/';
                if (langLinkJaMobile) langLinkJaMobile.href = '/ja/';
                if (langLinkDeMobile) langLinkDeMobile.href = '/de/';
                if (langLinkZhMobile) langLinkZhMobile.href = '/zh/';
            }} else {{
                if (langLinkEn) langLinkEn.href = '../' + currentPage;
                if (langLinkJa) langLinkJa.href = {loc_href('ja')};
                if (langLinkDe) langLinkDe.href = {loc_href('de')};
                if (langLinkZh) langLinkZh.href = {loc_href('zh')};
                if (langLinkEnMobile) langLinkEnMobile.href = '../' + currentPage;
                if (langLinkJaMobile) langLinkJaMobile.href = {loc_href('ja')};
                if (langLinkDeMobile) langLinkDeMobile.href = {loc_href('de')};
                if (langLinkZhMobile) langLinkZhMobile.href = {loc_href('zh')};
            }}
        }})();"""


def fix_lang_href_attr(text: str, element_id: str, new_href: str) -> str:
    pattern = rf'(<a\b[^>]*\bid="{re.escape(element_id)}"[^>]*\bhref=")([^"]*)(")'
    if re.search(pattern, text):
        return re.sub(pattern, rf"\1{new_href}\3", text, count=1)
    pattern = rf'(<a\b[^>]*\bhref=")([^"]*)("[^>]*\bid="{re.escape(element_id)}")'
    return re.sub(pattern, rf"\1{new_href}\3", text, count=1)


def fix_static_lang_links(text: str, locale: str, page: str) -> str:
    hrefs = expected_hrefs(locale, page)
    for element_id, lang in LANG_IDS:
        text = fix_lang_href_attr(text, element_id, hrefs[lang])
        text = fix_lang_href_attr(text, element_id + "-mobile", hrefs[lang])
    return text


def fix_invalid_js_comment(text: str) -> str:
    return text.replace("<!-- e.stopPropagation(); -->", "e.stopPropagation();")


def replace_lang_iife(text: str, locale: str) -> str:
    if "lang-link-en" not in text:
        return text

    iife = js_iife(locale).strip()
    block = re.compile(
        r"\n\s*\(function\(\)\s*\{[\s\S]*?langLinkEn[\s\S]*?langLinkZhMobile[\s\S]*?\}\)\(\);",
        re.MULTILINE,
    )
    if block.search(text):
        return block.sub("\n" + iife, text, count=1)

    # Append before first </script> after lang-button handler when missing
    marker = "        if (langButton && langMenu) {"
    if marker in text and "langLinkEn.href" not in text:
        insert_at = text.find("        }\n    </script>", text.find(marker))
        if insert_at != -1:
            return text[:insert_at] + "        }\n\n" + iife + "\n    </script>" + text[insert_at + len("        }\n    </script>") :]
    return text


def remove_duplicate_index_footer_script(text: str) -> str:
    marker = "</footer>\n<script>\n        const mobileMenuButton"
    idx = text.rfind(marker)
    if idx == -1:
        return text
    end = text.rfind("</script>\n</body>")
    if end == -1 or end <= idx:
        return text
    return text[:idx] + "</footer>\n" + text[end + len("</script>\n") :]


def fix_file(path: Path, locale: str) -> bool:
    page = path.name
    text = path.read_text(encoding="utf-8")
    original = text

    text = fix_invalid_js_comment(text)
    if "lang-link-en" in text:
        text = fix_static_lang_links(text, locale, page)
        text = replace_lang_iife(text, locale)
    if page == "index.html" and locale:
        text = remove_duplicate_index_footer_script(text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = []
    for page in PAGES:
        path = ROOT / page
        if path.exists() and fix_file(path, ""):
            changed.append(page)
    for locale in ("ja", "de", "zh"):
        for page in PAGES:
            path = ROOT / locale / page
            if path.exists() and fix_file(path, locale):
                changed.append(f"{locale}/{page}")
    print("Updated", len(changed), "files:")
    for c in changed:
        print(" ", c)


if __name__ == "__main__":
    main()
