#!/usr/bin/env python3
"""Audit internal links across vuca.cc static HTML site."""
import re
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
PAGES = {
    "index.html",
    "framework.html",
    "leadership.html",
    "action-guide.html",
    "examples.html",
    "resources.html",
    "assessment.html",
}
LOCALES = {"", "ja", "de", "zh"}
BAD_DOUBLE_LOCALE = re.compile(r"/(de|ja|zh)/(de|ja|zh)/")

HREF_RE = re.compile(r'\bhref=["\']([^"\']+)["\']', re.I)


def file_web_path(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    parts = rel.split("/")
    if len(parts) == 2 and parts[1] == "index.html":
        return f"/{parts[0]}/"
    return "/" + rel


def resolve_href(from_file: Path, href: str) -> str | None:
    href = href.strip()
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(href)
    if parsed.scheme in ("http", "https"):
        if "vuca.cc" in parsed.netloc:
            return parsed.path or "/"
        return None
    if href.startswith("/"):
        return href.split("#")[0] or "/"
    base = file_web_path(from_file)
    if not base.endswith("/"):
        base = str(PurePosixPath(base).parent) + "/"
    joined = urljoin(base, href.split("#")[0])
    return joined


def path_exists(web_path: str) -> bool:
    web_path = web_path.rstrip("/") or "/"
    if web_path == "/":
        return (ROOT / "index.html").exists()
    rel = web_path.lstrip("/")
    if rel.endswith("/"):
        return (ROOT / rel / "index.html").exists() or (ROOT / rel.rstrip("/") / "index.html").exists()
    p = ROOT / rel
    return p.exists()


def locale_of(web_path: str) -> str:
    parts = [p for p in web_path.strip("/").split("/") if p]
    if parts and parts[0] in ("ja", "de", "zh"):
        return parts[0]
    return ""


def expected_lang_href(from_file: Path, target_locale: str, page: str) -> str:
    from_locale = locale_of(file_web_path(from_file))
    if page == "index.html":
        if target_locale == "":
            return "/"
        return f"/{target_locale}/"
    if target_locale == from_locale:
        return page
    if target_locale == "":
        return f"../{page}"
    return f"../{target_locale}/{page}"


def audit():
    issues: list[str] = []
    warnings: list[str] = []
    html_files = sorted(ROOT.rglob("*.html"))

    for f in html_files:
        if f.parent != ROOT and f.parent.name not in LOCALES - {""}:
            continue
        text = f.read_text(encoding="utf-8")
        rel = f.relative_to(ROOT).as_posix()

        # Broken JS in script tags
        for m in re.finditer(r"<script[^>]*>([\s\S]*?)</script>", text, re.I):
            body = m.group(1)
            if "<!--" in body and re.search(r"<!--\s*[a-zA-Z_$]", body):
                issues.append(f"{rel}: HTML comment inside <script> (breaks JS parsing)")

        # Lang switcher static hrefs
        page = f.name
        if page in PAGES and "lang-link-en" in text:
            for lang_id, loc in [
                ("lang-link-en", ""),
                ("lang-link-ja", "ja"),
                ("lang-link-de", "de"),
                ("lang-link-zh", "zh"),
            ]:
                for suffix in ("", "-mobile"):
                    pid = lang_id + suffix
                    m = re.search(rf'id="{pid}"[^>]*href="([^"]+)"', text)
                    if not m:
                        m = re.search(rf'href="([^"]+)"[^>]*id="{pid}"', text)
                    if not m:
                        continue
                    href = m.group(1)
                    from_loc = locale_of(file_web_path(f))
                    if from_loc and not href.startswith("/") and not href.startswith("../"):
                        if re.match(rf"^(de|ja|zh)/", href):
                            issues.append(
                                f"{rel}: {pid} href={href!r} → resolves to "
                                f"/{from_loc}/{href} (double locale)"
                            )
                    exp = expected_lang_href(f, loc, page)
                    if href.startswith("/") or href.startswith("../") or not re.match(r"^(de|ja|zh)/", href):
                        if from_loc and page != "index.html":
                            if loc == from_loc and href != page and not href.endswith(f"/{page}"):
                                if href != f"/{from_loc}/{page}":
                                    warnings.append(f"{rel}: {pid} current-locale href={href!r} (expected {exp!r})")
                            elif loc != from_loc and loc == "" and not href.startswith("../") and page != "index.html":
                                warnings.append(f"{rel}: {pid} EN href={href!r} (expected {exp!r})")

        # All hrefs → missing targets
        for href in HREF_RE.findall(text):
            resolved = resolve_href(f, href)
            if resolved is None:
                continue
            if BAD_DOUBLE_LOCALE.search(resolved):
                issues.append(f"{rel}: href={href!r} → {resolved} (double locale path)")
            if resolved.endswith((".html", "/")) or resolved == "/":
                if not path_exists(resolved):
                    issues.append(f"{rel}: href={href!r} → {resolved} (target missing)")

        # Missing lang link updater
        if page in PAGES and "lang-link-en" in text and "langLinkEn" not in text and "langLinkEn.href" not in text:
            issues.append(f"{rel}: language menu present but no JS href updater")

        # Duplicate nav scripts on index
        if f.name == "index.html":
            script_count = len(re.findall(r"langLinkEn\.href", text))
            if script_count > 1:
                warnings.append(f"{rel}: {script_count} lang-link updater blocks (possible duplicate)")

    # de subpages without index.html branch in JS
    for loc in ("de", "ja", "zh"):
        for page in PAGES:
            if page == "index.html":
                continue
            p = ROOT / loc / page
            if not p.exists():
                continue
            t = p.read_text(encoding="utf-8")
            if "lang-link-en" in t and "currentPage === 'index.html'" not in t:
                warnings.append(f"{loc}/{page}: lang JS lacks index.html branch (OK if subpage-only logic)")

    return issues, warnings, html_files


def main():
    issues, warnings, files = audit()
    print(f"Scanned {len(files)} HTML files\n")
    if issues:
        print(f"=== ISSUES ({len(issues)}) ===")
        for i in sorted(set(issues)):
            print(f"  - {i}")
    else:
        print("=== ISSUES: none ===")
    if warnings:
        print(f"\n=== WARNINGS ({len(warnings)}) ===")
        for w in sorted(set(warnings))[:40]:
            print(f"  - {w}")
        if len(set(warnings)) > 40:
            print(f"  ... and {len(set(warnings)) - 40} more")
    else:
        print("\n=== WARNINGS: none ===")


if __name__ == "__main__":
    main()
