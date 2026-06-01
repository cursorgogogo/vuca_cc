#!/usr/bin/env python3
"""Move dated dimension example cards to the top of each V/C/U/A grid (newest first)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Unique title markers per dimension (must match exactly in each locale file)
LOCALE_MARKERS = {
    "examples.html": [
        "Global IT Outage (2024)",
        "AI & Data Regulation (2024-2026)",
        "Shipping Route Disruptions (2024-2025)",
        "Agentic AI ROI (2025-2026)",
    ],
    "de/examples.html": [
        "Globaler IT-Ausfall (2024)",
        "KI- & Datenregulierung (2024-2026)",
        "Schifffahrtsstörungen (2024-2025)",
        "Agenten-KI-ROI (2025-2026)",
    ],
    "zh/examples.html": [
        "全球 IT 中断（2024）",
        "AI 与数据监管（2024-2026）",
        "航运路线扰动（2024-2025）",
        "智能体 AI 投资回报（2025-2026）",
    ],
    "ja/examples.html": [
        "世界規模IT障害（2024）",
        "AI・データ規制（2024-2026）",
        "海運ルートの混乱（2024-2025）",
        "エージェントAIのROI（2025-2026）",
    ],
}

CARD_TEMPLATE = (
    r'(\n\s*<div class="bg-white rounded-xl p-6 border border-\w+-100">\s*'
    r'<p class="font-bold[^"]*">{}</p>'
    r'[\s\S]*?'
    r'\n\s*</div>)'
)


def move_card_to_grid_top(html: str, title: str, section_heading: str) -> str:
    pat = CARD_TEMPLATE.format(re.escape(title))
    m = re.search(pat, html)
    if not m:
        raise ValueError(f"Card not found: {title!r}")
    card = m.group(1)
    without = html[: m.start()] + html[m.end() :]
    heading_pos = without.find(section_heading)
    if heading_pos == -1:
        raise ValueError(f"Section not found: {section_heading!r}")
    grid_open = '<div class="grid md:grid-cols-2 gap-6">'
    pos = without.find(grid_open, heading_pos)
    if pos == -1:
        raise ValueError(f"Grid not found after {section_heading!r}")
    insert = without.find(">", pos) + 1
    return without[:insert] + card + without[insert:]


SECTION_HEADINGS = {
    "examples.html": [
        "Volatility Examples",
        "Uncertainty Examples",
        "Complexity Examples",
        "Ambiguity Examples",
    ],
    "de/examples.html": [
        "Beispiele für Volatilität",
        "Beispiele für Unsicherheit",
        "Komplexitätsbeispiele",
        "Beispiele für Mehrdeutigkeit",
    ],
    "zh/examples.html": [
        "易变性示例",
        "不确定性示例",
        "复杂性示例",
        "模糊性示例",
    ],
    "ja/examples.html": [
        "変動性の事例",
        "不確実性の事例",
        "複雑性の事例",
        "曖昧性の事例",
    ],
}


def process_file(rel_path: str) -> None:
    path = ROOT / rel_path
    text = path.read_text(encoding="utf-8")
    for title, heading in zip(LOCALE_MARKERS[rel_path], SECTION_HEADINGS[rel_path]):
        text = move_card_to_grid_top(text, title, heading)
    path.write_text(text, encoding="utf-8")
    print(f"Updated {rel_path}")


def main() -> None:
    for rel in LOCALE_MARKERS:
        process_file(rel)


if __name__ == "__main__":
    main()
