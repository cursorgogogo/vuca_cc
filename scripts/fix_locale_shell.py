#!/usr/bin/env python3
"""Fix de/zh index, framework, leadership shells and stray comment text."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DE_STRAYS = [
    'Held', 'Heldenbereich', 'Bewertungstool – Empfohlener Abschnitt',
    'Schlüsselkennzahlen', 'Was ist VUCA', 'VUCA Dimensionsvisualisierung',
    'Hintergrundkreis', 'Zentraler Knotenpunkt', 'Volatilität – Top',
    'Unsicherheit – Richtig', 'Komplexität – Unten', 'Mehrdeutigkeit – Links',
    'Verbindungslinien', 'Herkunft und Geschichte',
    'Framework-Analysematrix', 'Detaillierte Analyse', 'Volatilität', 'Unsicherheit',
    'Komplexität', 'Mehrdeutigkeit', 'Implementierungsrahmen', 'Fußzeile',
    'Grundlegende Führungsprinzipien', 'Grundlegende Fähigkeiten', 'Führungsmodelle',
    'Schulung und Entwicklung', 'Häufige Fehler',
]

ZH_REPLACEMENTS = [
    ('>家</a>', '>首页</a>'),
    ('>领导</a>', '>领导力</a>'),
    ('>示例</a>', '>案例</a>'),
    ('>英语</a>', '>English</a>'),
    ('>德语</a>', '>Deutsch</a>'),
    ('日本语</a>', '日本語</a>'),
    ('<span class="text-sm font-medium">CN</span>', '<span class="text-sm font-medium">中文</span>'),
    ('viewbox=', 'viewBox='),
    ('preserveaspectratio=', 'preserveAspectRatio='),
    ('lang="en"', 'lang="zh-CN"'),
    (' 导航 \n', '    <!-- Navigation -->\n'),
    (' 英雄区 \n', '    <!-- Hero Section -->\n'),
    ('href="https://vuca.cc/" rel="canonical"', 'href="https://vuca.cc/zh/" rel="canonical"'),
]

DE_REPLACEMENTS = [
    ('>Heim</a>', '>Startseite</a>'),
    ('>Rahmen</a>', '>Framework</a>'),
    ('>Bewertung</a>', '>Assessment</a>'),
    ('>Englisch</a>', '>English</a>'),
    ('viewbox=', 'viewBox='),
    ('preserveaspectratio=', 'preserveAspectRatio='),
]


def wrap_strays(html: str, labels: list) -> str:
    for label in labels:
        html = re.sub(
            rf'\n\s*{re.escape(label)}\s*\n',
            f'\n    <!-- {label} -->\n',
            html,
        )
    return html


def fix_stray_text_lines(html: str) -> str:
    """Convert orphan text lines (broken HTML comments) to proper comments."""
    out = []
    for line in html.split('\n'):
        s = line.strip()
        if not s or s.startswith('<') or s.startswith('{') or s.startswith('@'):
            out.append(line)
            continue
        if any(x in s for x in ('const ', '=>', 'function', '});', 'getElement', '.classList', 'addEventListener')):
            out.append(line)
            continue
        if '<' in line or '>' in line:
            out.append(line)
            continue
        if re.match(r'^[\w\s\u4e00-\u9fff\u3040-\u30ff–—\-•,.:;!?()&]+$', s) and len(s) < 120:
            indent = line[: len(line) - len(line.lstrip())]
            out.append(f'{indent}<!-- {s} -->')
            continue
        out.append(line)
    return '\n'.join(out)


def index_nav(locale: str) -> str:
    n = {
        'de': {
            'lang': 'de', 'btn': 'DE', 'home': 'Startseite', 'framework': 'Framework',
            'leadership': 'Führung', 'action': 'Aktionsleitfaden', 'examples': 'Beispiele',
            'resources': 'Ressourcen', 'assessment': 'Assessment', 'lang_label': 'Sprache',
            'title': 'VUCA: Die VUCA-Welt verstehen',
            'desc': 'Beherrschen Sie VUCA: Frameworks, Führungsstrategien und praktische Ansätze für volatile, unsichere, komplexe und mehrdeutige Umgebungen.',
            'canonical': 'https://vuca.cc/de/',
            'home_href': '/de/',
        },
        'zh': {
            'lang': 'zh-CN', 'btn': '中文', 'home': '首页', 'framework': '框架',
            'leadership': '领导力', 'action': '行动指南', 'examples': '案例',
            'resources': '资源', 'assessment': '评估', 'lang_label': '语言',
            'title': 'VUCA：理解多变商业环境',
            'desc': '掌握 VUCA：学习框架、领导力策略与应对易变、不确定、复杂、模糊环境的实用方法。',
            'canonical': 'https://vuca.cc/zh/',
            'home_href': '/zh/',
        },
    }[locale]
    overflow = ' class="overflow-x-hidden"' if locale == 'zh' else ' class="overflow-x-hidden"'

    js = '''            if (langLinkEn) langLinkEn.href = '/';
            if (langLinkJa) langLinkJa.href = '/ja/';
            if (langLinkDe) langLinkDe.href = '/de/';
            if (langLinkZh) langLinkZh.href = '/zh/';
            if (langLinkEnMobile) langLinkEnMobile.href = '/';
            if (langLinkJaMobile) langLinkJaMobile.href = '/ja/';
            if (langLinkDeMobile) langLinkDeMobile.href = '/de/';
            if (langLinkZhMobile) langLinkZhMobile.href = '/zh/';'''
    en_href, ja_href, de_href, zh_href = '/', '/ja/', '/de/', '/zh/'
    en_active = 'text-gray-700 hover:bg-gray-50'
    de_cls = 'text-gray-900 bg-emerald-50 font-medium' if locale == 'de' else en_active
    zh_cls = 'text-gray-900 bg-emerald-50 font-medium' if locale == 'zh' else en_active

    return f'''<!DOCTYPE html>
<html lang="{n["lang"]}"{overflow}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{n["title"]}</title>
    <meta name="description" content="{n["desc"]}">
    <link rel="canonical" href="{n["canonical"]}">
    <link rel="icon" type="image/svg+xml" href="../V.svg">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-white text-gray-900 overflow-x-hidden">

    <!-- Navigation -->
    <nav class="border-b border-gray-200 bg-white sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center">
                    <a href="{n["home_href"]}" class="text-2xl font-bold text-emerald-600">VUCA</a>
                </div>
                <div class="hidden md:flex space-x-8 items-center">
                    <a href="{n["home_href"]}" class="text-gray-900 hover:text-emerald-600 font-medium">{n["home"]}</a>
                    <a href="framework.html" class="text-gray-700 hover:text-emerald-600">{n["framework"]}</a>
                    <a href="leadership.html" class="text-gray-700 hover:text-emerald-600">{n["leadership"]}</a>
                    <a href="action-guide.html" class="text-gray-700 hover:text-emerald-600">{n["action"]}</a>
                    <a href="examples.html" class="text-gray-700 hover:text-emerald-600">{n["examples"]}</a>
                    <a href="resources.html" class="text-gray-700 hover:text-emerald-600">{n["resources"]}</a>
                    <a href="assessment.html" class="text-gray-700 hover:text-emerald-600">{n["assessment"]}</a>
                    <div class="relative ml-4">
                        <button id="lang-button" class="flex items-center text-gray-700 hover:text-emerald-600 focus:outline-none">
                            <span class="text-sm font-medium">{n["btn"]}</span>
                            <svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                            </svg>
                        </button>
                        <div id="lang-menu" class="hidden absolute right-0 mt-2 w-36 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                            <a id="lang-link-en" href="{en_href}" class="block px-4 py-2 text-sm {en_active}">English</a>
                            <a id="lang-link-ja" href="{ja_href}" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">日本語</a>
                            <a id="lang-link-de" href="{de_href}" class="block px-4 py-2 text-sm {de_cls}">Deutsch</a>
                            <a id="lang-link-zh" href="{zh_href}" class="block px-4 py-2 text-sm {zh_cls}">中文</a>
                        </div>
                    </div>
                </div>
                <div class="md:hidden flex items-center">
                    <button id="mobile-menu-button" class="text-gray-700 hover:text-emerald-600 focus:outline-none">
                        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path id="menu-icon" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                            <path id="close-icon" class="hidden" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
        <div id="mobile-menu" class="hidden md:hidden border-t border-gray-200">
            <div class="px-2 pt-2 pb-3 space-y-1">
                <a href="{n["home_href"]}" class="block px-3 py-2 rounded-md text-gray-900 font-medium bg-emerald-50">{n["home"]}</a>
                <a href="framework.html" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600">{n["framework"]}</a>
                <a href="leadership.html" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600">{n["leadership"]}</a>
                <a href="action-guide.html" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600">{n["action"]}</a>
                <a href="examples.html" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600">{n["examples"]}</a>
                <a href="resources.html" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600">{n["resources"]}</a>
                <a href="assessment.html" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600">{n["assessment"]}</a>
                <div class="border-t border-gray-200 mt-2 pt-2">
                    <div class="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">{n["lang_label"]}</div>
                    <a id="lang-link-en-mobile" href="{en_href}" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600">English</a>
                    <a id="lang-link-ja-mobile" href="{ja_href}" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600">日本語</a>
                    <a id="lang-link-de-mobile" href="{de_href}" class="block px-3 py-2 rounded-md {"text-gray-900 font-medium bg-emerald-50" if locale == "de" else "text-gray-700 hover:bg-gray-50 hover:text-emerald-600"}">Deutsch</a>
                    <a id="lang-link-zh-mobile" href="{zh_href}" class="block px-3 py-2 rounded-md {"text-gray-900 font-medium bg-emerald-50" if locale == "zh" else "text-gray-700 hover:bg-gray-50 hover:text-emerald-600"}">中文</a>
                </div>
            </div>
        </div>
    </nav>

    <script>
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        const menuIcon = document.getElementById('menu-icon');
        const closeIcon = document.getElementById('close-icon');
        const langButton = document.getElementById('lang-button');
        const langMenu = document.getElementById('lang-menu');

        mobileMenuButton.addEventListener('click', () => {{
            mobileMenu.classList.toggle('hidden');
            menuIcon.classList.toggle('hidden');
            closeIcon.classList.toggle('hidden');
        }});

        if (langButton && langMenu) {{
            langButton.addEventListener('click', (e) => {{
                e.stopPropagation();
                langMenu.classList.toggle('hidden');
            }});

            document.addEventListener('click', (e) => {{
                if (!langButton.contains(e.target) && !langMenu.contains(e.target)) {{
                    langMenu.classList.add('hidden');
                }}
            }});
        }}

        (function() {{
            const langLinkEn = document.getElementById('lang-link-en');
            const langLinkJa = document.getElementById('lang-link-ja');
            const langLinkDe = document.getElementById('lang-link-de');
            const langLinkZh = document.getElementById('lang-link-zh');
            const langLinkEnMobile = document.getElementById('lang-link-en-mobile');
            const langLinkJaMobile = document.getElementById('lang-link-ja-mobile');
            const langLinkDeMobile = document.getElementById('lang-link-de-mobile');
            const langLinkZhMobile = document.getElementById('lang-link-zh-mobile');
{js}
        }})();
    </script>

'''


def rebuild_index(locale: str):
    path = ROOT / locale / 'index.html'
    html = path.read_text(encoding='utf-8')
    m = re.search(r'(<section[\s\S]*)', html)
    if not m:
        raise ValueError(f'No body in {path}')
    body = fix_stray_text_lines(m.group(1))
    path.write_text(index_nav(locale) + body, encoding='utf-8')
    print(f'rebuilt {locale}/index.html')


def fix_all_html(folder: str, replacements: list, strays: list | None = None):
    for path in (ROOT / folder).glob('*.html'):
        if path.name == 'index.html':
            continue
        html = path.read_text(encoding='utf-8')
        orig = html
        for a, b in replacements:
            html = html.replace(a, b)
        if strays:
            html = wrap_strays(html, strays)
        html = fix_stray_text_lines(html)
        html = html.replace('日本语', '日本語')
        if html != orig:
            path.write_text(html, encoding='utf-8')
            print(f'fixed {folder}/{path.name}')


def main():
    rebuild_index('de')
    rebuild_index('zh')
    fix_all_html('de', DE_REPLACEMENTS, DE_STRAYS)
    fix_all_html('zh', ZH_REPLACEMENTS)
    for p in (ROOT / 'zh').glob('*.html'):
        t = p.read_text(encoding='utf-8')
        t2 = t.replace('日本语', '日本語')
        if t2 != t:
            p.write_text(t2, encoding='utf-8')
    print('done')


if __name__ == '__main__':
    main()
