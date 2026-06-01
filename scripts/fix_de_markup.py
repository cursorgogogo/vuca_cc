#!/usr/bin/env python3
"""Fix broken German pages: stray text nodes, nav labels, SVG viewBox."""
import re
from pathlib import Path

DE = Path(__file__).resolve().parent.parent / 'de'

REPLACEMENTS = [
    ('>Heim</a>', '>Startseite</a>'),
    ('>Rahmen</a>', '>Framework</a>'),
    ('>Bewertung</a>', '>Assessment</a>'),
    ('>Englisch</a>', '>English</a>'),
    ('viewbox=', 'viewBox='),
    ('href="https://vuca.cc/framework.html"', 'href="https://vuca.cc/de/framework.html"'),
    ('href="https://vuca.cc/leadership.html"', 'href="https://vuca.cc/de/leadership.html"'),
    ('href="https://vuca.cc/" rel="canonical"', 'href="https://vuca.cc/de/" rel="canonical"'),
]

# Stray comment fragments (HTML comment body was translated to visible text)
STRAY_TO_COMMENT = [
    'Held',
    'Heldenbereich',
    'Framework-Analysematrix',
    'Detaillierte Analyse',
    'Volatilität',
    'Unsicherheit',
    'Komplexität',
    'Mehrdeutigkeit',
    'Implementierungsrahmen',
    'Grundlegende Führungsprinzipien',
    'Grundlegende Fähigkeiten',
    'Führungsmodelle',
    'Schulung und Entwicklung',
    'Häufige Fehler',
    'Fußzeile',
]


def wrap_stray_comments(html: str) -> str:
    """Turn loose text between tags into HTML comments."""
    for label in STRAY_TO_COMMENT:
        html = re.sub(
            rf'\n\s*{re.escape(label)}\s*\n',
            f'\n    <!-- {label} -->\n',
            html,
        )
    return html


def fix_lang_active(html: str, page: str) -> str:
    """Deutsch should be active in lang menu, not English."""
    en_active = 'text-gray-900 bg-emerald-50 font-medium" href="' + page
    if en_active not in html:
        return html
    html = html.replace(
        f'id="lang-link-en" class="block px-4 py-2 text-sm text-gray-900 bg-emerald-50 font-medium" href="{page}"',
        f'id="lang-link-en" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" href="../{page}"',
    )
    html = html.replace(
        f'id="lang-link-de" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" href="de/{page}"',
        f'id="lang-link-de" class="block px-4 py-2 text-sm text-gray-900 bg-emerald-50 font-medium" href="{page}"',
    )
    html = html.replace(
        f'id="lang-link-de" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" href="{page}"',
        f'id="lang-link-de" class="block px-4 py-2 text-sm text-gray-900 bg-emerald-50 font-medium" href="{page}"',
    )
    # mobile
    html = html.replace(
        f'id="lang-link-en-mobile" class="block px-3 py-2 rounded-md text-gray-900 font-medium bg-emerald-50" href="{page}"',
        f'id="lang-link-en-mobile" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600" href="../{page}"',
    )
    html = html.replace(
        f'id="lang-link-de-mobile" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600" href="de/{page}"',
        f'id="lang-link-de-mobile" class="block px-3 py-2 rounded-md text-gray-900 font-medium bg-emerald-50" href="{page}"',
    )
    html = html.replace(
        f'id="lang-link-de-mobile" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600" href="{page}"',
        f'id="lang-link-de-mobile" class="block px-3 py-2 rounded-md text-gray-900 font-medium bg-emerald-50" href="{page}"',
    )
    return html


def main():
    for path in DE.glob('*.html'):
        html = path.read_text(encoding='utf-8')
        orig = html
        for a, b in REPLACEMENTS:
            html = html.replace(a, b)
        html = wrap_stray_comments(html)
        if path.name in ('framework.html', 'leadership.html', 'index.html'):
            html = fix_lang_active(html, path.name)
        if html != orig:
            path.write_text(html, encoding='utf-8')
            print(f'fixed {path.name}')


if __name__ == '__main__':
    main()
