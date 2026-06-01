#!/usr/bin/env python3
"""Rebuild de/zh examples, resources, assessment from English with proper HTML."""
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent.parent
PAGES = ['examples.html', 'resources.html', 'assessment.html']

DE_NAV = {
    'home': 'Startseite', 'framework': 'Framework', 'leadership': 'Führung',
    'action': 'Aktionsleitfaden', 'examples': 'Beispiele', 'resources': 'Ressourcen',
    'assessment': 'Assessment', 'lang': 'Sprache', 'learn': 'Lernen', 'practice': 'Üben',
}
ZH_NAV = {
    'home': '首页', 'framework': '框架', 'leadership': '领导力',
    'action': '行动指南', 'examples': '案例', 'resources': '资源',
    'assessment': '评估', 'lang': '语言', 'learn': '学习', 'practice': '实践',
}

META = {
    'examples.html': {
        'de': {
            'title': 'VUCA-Beispiele: Fallstudien und Geschäftsanwendungen',
            'desc': 'Lernen Sie aus realen VUCA-Beispielen aus verschiedenen Branchen. Fallstudien zu Volatilität, Unsicherheit, Komplexität und Mehrdeutigkeit.',
        },
        'zh': {
            'title': 'VUCA 案例：真实案例研究与商业应用',
            'desc': '从跨行业的真实 VUCA 案例中学习。探索组织如何应对易变性、不确定性、复杂性和模糊性。',
        },
    },
    'resources.html': {
        'de': {
            'title': 'VUCA-Ressourcen: Bücher, Tools, Vorlagen und Schulungsmaterialien',
            'desc': 'Umfassende VUCA-Ressourcen: Bücher, praktische Tools, Vorlagen, Fallstudien und Schulungsmaterialien für Führungskräfte und Organisationen.',
        },
        'zh': {
            'title': 'VUCA 资源：书籍、工具、模板与培训材料',
            'desc': '全面的 VUCA 资源，包括必读书籍、实用工具、模板、案例研究以及面向领导者与组织的培训材料。',
        },
    },
    'assessment.html': {
        'de': {
            'title': 'VUCA-Führungsbewertung: Bewerten Sie Ihren Führungsstil',
            'desc': 'Bewerten Sie Ihren Führungsstil und Ihre Anpassungsfähigkeit in VUCA-Umgebungen. Personalisierte Erkenntnisse zu Stärken und Entwicklungsfeldern.',
        },
        'zh': {
            'title': 'VUCA 领导力评估：评估您的领导风格',
            'desc': '评估您在 VUCA 环境中的领导风格与适应能力，获取关于优势与发展领域的个性化洞察。',
        },
    },
}


def nav_block(locale: str, page: str, active: str) -> str:
    n = DE_NAV if locale == 'de' else ZH_NAV
    prefix = locale
    home_href = f'/{prefix}/'
    lang_btn = 'DE' if locale == 'de' else '中文'

    def link(name, href, label):
        cls = 'text-gray-900 hover:text-emerald-600 font-medium' if name == active else 'text-gray-700 hover:text-emerald-600'
        mob = 'block px-3 py-2 rounded-md text-gray-900 font-medium bg-emerald-50' if name == active else 'block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600'
        return f'                    <a href="{href}" class="{cls}">{label}</a>\n', f'                <a href="{href}" class="{mob}">{label}</a>\n'

    desktop, mobile = [], []
    for name, href, key in [
        ('home', home_href, 'home'), ('framework', 'framework.html', 'framework'),
        ('leadership', 'leadership.html', 'leadership'), ('action', 'action-guide.html', 'action'),
        ('examples', 'examples.html', 'examples'), ('resources', 'resources.html', 'resources'),
        ('assessment', 'assessment.html', 'assessment'),
    ]:
        d, m = link(name, href, n[key])
        desktop.append(d)
        mobile.append(m)

    overflow_cls = ' class="overflow-x-hidden"' if page == 'assessment.html' else ''
    lang_attr = 'de' if locale == 'de' else 'zh-CN'
    meta = META[page][locale]

    if locale == 'de':
        js_links = '''            if (langLinkEn) langLinkEn.href = '../' + currentPage;
            if (langLinkJa) langLinkJa.href = '../ja/' + currentPage;
            if (langLinkDe) langLinkDe.href = currentPage;
            if (langLinkZh) langLinkZh.href = '../zh/' + currentPage;
            if (langLinkEnMobile) langLinkEnMobile.href = '../' + currentPage;
            if (langLinkJaMobile) langLinkJaMobile.href = '../ja/' + currentPage;
            if (langLinkDeMobile) langLinkDeMobile.href = currentPage;
            if (langLinkZhMobile) langLinkZhMobile.href = '../zh/' + currentPage;'''
    else:
        js_links = '''            if (langLinkEn) langLinkEn.href = '../' + currentPage;
            if (langLinkJa) langLinkJa.href = '../ja/' + currentPage;
            if (langLinkDe) langLinkDe.href = '../de/' + currentPage;
            if (langLinkZh) langLinkZh.href = currentPage;
            if (langLinkEnMobile) langLinkEnMobile.href = '../' + currentPage;
            if (langLinkJaMobile) langLinkJaMobile.href = '../ja/' + currentPage;
            if (langLinkDeMobile) langLinkDeMobile.href = '../de/' + currentPage;
            if (langLinkZhMobile) langLinkZhMobile.href = currentPage;'''

    return f'''<!DOCTYPE html>
<html lang="{lang_attr}"{overflow_cls}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta['title']}</title>
    <meta name="description" content="{meta['desc']}">
    <link rel="canonical" href="https://vuca.cc/{prefix}/{page}">
    <link rel="icon" type="image/svg+xml" href="../V.svg">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-white text-gray-900{" overflow-x-hidden" if page == "assessment.html" else ""}">
    
    <!-- Navigation -->
    <nav class="border-b border-gray-200 bg-white sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center">
                    <a href="{home_href}" class="text-2xl font-bold text-emerald-600">VUCA</a>
                </div>
                <div class="hidden md:flex space-x-8 items-center">
{"".join(desktop)}                    <div class="relative ml-4">
                        <button id="lang-button" class="flex items-center text-gray-700 hover:text-emerald-600 focus:outline-none">
                            <span class="text-sm font-medium">{lang_btn}</span>
                            <svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                            </svg>
                        </button>
                        <div id="lang-menu" class="hidden absolute right-0 mt-2 w-36 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                            <a id="lang-link-en" href="../{page}" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">English</a>
                            <a id="lang-link-ja" href="../ja/{page}" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">日本語</a>
                            <a id="lang-link-de" href="{"../de/" if locale != "de" else ""}{page}" class="block px-4 py-2 text-sm {"text-gray-900 bg-emerald-50 font-medium" if locale == "de" else "text-gray-700 hover:bg-gray-50"}">Deutsch</a>
                            <a id="lang-link-zh" href="{"../zh/" if locale != "zh" else ""}{page}" class="block px-4 py-2 text-sm {"text-gray-900 bg-emerald-50 font-medium" if locale == "zh" else "text-gray-700 hover:bg-gray-50"}">中文</a>
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
{"".join(mobile)}                <div class="border-t border-gray-200 mt-2 pt-2">
                    <div class="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">{n['lang']}</div>
                    <a id="lang-link-en-mobile" href="../{page}" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600">English</a>
                    <a id="lang-link-ja-mobile" href="../ja/{page}" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-50 hover:text-emerald-600">日本語</a>
                    <a id="lang-link-de-mobile" href="{"../de/" if locale != "de" else ""}{page}" class="block px-3 py-2 rounded-md {"text-gray-900 font-medium bg-emerald-50" if locale == "de" else "text-gray-700 hover:bg-gray-50 hover:text-emerald-600"}">Deutsch</a>
                    <a id="lang-link-zh-mobile" href="{"../zh/" if locale != "zh" else ""}{page}" class="block px-3 py-2 rounded-md {"text-gray-900 font-medium bg-emerald-50" if locale == "zh" else "text-gray-700 hover:bg-gray-50 hover:text-emerald-600"}">中文</a>
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
            const currentPage = window.location.pathname.split('/').pop() || 'index.html';
            const langLinkEn = document.getElementById('lang-link-en');
            const langLinkJa = document.getElementById('lang-link-ja');
            const langLinkDe = document.getElementById('lang-link-de');
            const langLinkZh = document.getElementById('lang-link-zh');
            const langLinkEnMobile = document.getElementById('lang-link-en-mobile');
            const langLinkJaMobile = document.getElementById('lang-link-ja-mobile');
            const langLinkDeMobile = document.getElementById('lang-link-de-mobile');
            const langLinkZhMobile = document.getElementById('lang-link-zh-mobile');

{js_links}
        }})();
    </script>
'''


def active_page_key(page: str) -> str:
    if 'examples' in page:
        return 'examples'
    if 'resources' in page:
        return 'resources'
    return 'assessment'


def extract_body(en_html: str) -> str:
    """Content from first hero/section after nav script to end."""
    m = re.search(
        r'</script>\s*(<!--[^>]*-->\s*)?(<section[\s\S]*)',
        en_html,
        re.IGNORECASE,
    )
    if not m:
        raise ValueError('Could not find body start')
    return (m.group(1) or '') + m.group(2)


def translate_js_strings(script: str, tr: GoogleTranslator, cache: dict) -> str:
    """Translate single-quoted user-facing strings in assessment JS."""
    if 'feedbackMessages' not in script and 'getRecommendations' not in script:
        return script

    def translate_text(s: str) -> str:
        key = s.strip()
        if len(key) < 4 or re.match(r'^[\d\s\W]+$', key):
            return s
        if key in cache:
            return cache[key]
        try:
            t = tr.translate(key)
            cache[key] = t
            time.sleep(0.02)
            return t
        except Exception:
            return s

    def repl(m):
        inner = m.group(1)
        if '\n' in inner or len(inner) > 500:
            return m.group(0)
        return "'" + translate_text(inner) + "'"

    return re.sub(r"'((?:[^'\\]|\\.)*)'", repl, script)


def translate_html_chunk(html: str, tr: GoogleTranslator, cache: dict) -> str:
    parts = re.split(r'(<script[\s\S]*?</script>)', html)
    out = []

    def translate_text(s: str) -> str:
        key = s.strip()
        if len(key) < 2 or re.match(r'^[\d\s\W]+$', key):
            return s
        if key in cache:
            t = cache[key]
        else:
            try:
                t = tr.translate(key)
                cache[key] = t
                time.sleep(0.02)
            except Exception:
                return s
        lead = s[: len(s) - len(s.lstrip())]
        trail = s[len(s.rstrip()) :]
        return lead + t + trail

    for part in parts:
        if part.startswith('<script'):
            # Never auto-translate assessment logic (breaks IDs, Tailwind, events)
            out.append(part)
            continue
        part = re.sub(
            r'(<meta name="description" content=")([^"]*)(")',
            lambda m: m.group(1) + translate_text(m.group(2)) + m.group(3),
            part,
        )
        part = re.sub(r'(>)([^<]+)(<)', lambda m: m.group(1) + translate_text(m.group(2)) + m.group(3), part)
        out.append(part)
    return ''.join(out)


def localize_footer(html: str, locale: str) -> str:
    prefix = locale
    n = DE_NAV if locale == 'de' else ZH_NAV
    html = html.replace('href="/"', f'href="/{prefix}/"')
    html = html.replace('>Home</a>', f'>{n["home"]}</a>')
    html = html.replace('>Framework</a>', f'>{n["framework"]}</a>')
    html = html.replace('>Leadership</a>', f'>{n["leadership"]}</a>')
    html = html.replace('>Action Guide</a>', f'>{n["action"]}</a>')
    html = html.replace('>Examples</a>', f'>{n["examples"]}</a>')
    html = html.replace('>Resources</a>', f'>{n["resources"]}</a>')
    html = html.replace('>Assessment</a>', f'>{n["assessment"]}</a>')
    html = html.replace('>Learn</h4>', f'>{n["learn"]}</h4>')
    html = html.replace('>Practice</h4>', f'>{n["practice"]}</h4>')
    if locale == 'de':
        html = html.replace('What is VUCA', 'Was ist VUCA')
        html = html.replace('VUCA Framework', 'VUCA-Framework')
        html = html.replace('Real Examples', 'Echte Beispiele')
        html = html.replace('Leadership Strategies', 'Führungsstrategien')
        html = html.replace('Industry Examples', 'Branchenbeispiele')
        html = html.replace('Books & Articles', 'Bücher und Artikel')
        html = html.replace('Tools & Templates', 'Tools und Vorlagen')
        html = html.replace('Case Studies', 'Fallstudien')
        html = html.replace('Self Assessment', n['assessment'])
        html = html.replace('Professional resource for VUCA education and leadership development.',
                            'Professionelle Ressource für VUCA-Ausbildung und Führungskräfteentwicklung.')
    else:
        html = html.replace('What is VUCA', '什么是 VUCA')
        html = html.replace('VUCA Framework', 'VUCA 框架')
        html = html.replace('Real Examples', '真实案例')
        html = html.replace('Leadership Strategies', '领导力策略')
        html = html.replace('Industry Examples', '行业案例')
        html = html.replace('Books & Articles', '书籍与文章')
        html = html.replace('Tools & Templates', '工具与模板')
        html = html.replace('Case Studies', '案例研究')
        html = html.replace('Self Assessment', '自我评估')
        html = html.replace('Professional resource for VUCA education and leadership development.',
                            '专业的 VUCA 教育与领导力发展资源。')
    return html


def rebuild(page: str, locale: str):
    print(f'  {locale}/{page}...', flush=True)
    en = (ROOT / page).read_text(encoding='utf-8')
    body = extract_body(en)
    active = active_page_key(page)
    head = nav_block(locale, page, active)
    target = 'de' if locale == 'de' else 'zh-CN'
    tr = GoogleTranslator(source='en', target=target)
    cache = {}
    body_tr = translate_html_chunk(body, tr, cache)
    body_tr = localize_footer(body_tr, locale)
    out = head + body_tr
    out = re.sub(r'\n{3,}', '\n\n', out)
    if not out.rstrip().endswith('</html>'):
        out = out.rstrip() + '\n'
    (ROOT / locale / page).write_text(out.rstrip() + '\n', encoding='utf-8')


def main():
    for page in PAGES:
        print(page, flush=True)
        rebuild(page, 'de')
        rebuild(page, 'zh')
    print('Done.')


if __name__ == '__main__':
    main()
