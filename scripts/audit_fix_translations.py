#!/usr/bin/env python3
"""Audit fixes: translation quality and neutral wording for sensitive topics."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (path_glob_relative, old, new) — path None means all listed locale files
REPLACEMENTS = [
    # --- Neutral geopolitical wording (oil prices) ---
    ('examples.html', 'then back above $120 during Ukraine crisis',
     'then back above $120 amid geopolitical tensions affecting global energy markets'),
    ('de/examples.html', 'stiegen dann während der Ukraine-Krise wieder auf über 120 US-Dollar',
     'stiegen dann bei geopolitischen Spannungen auf den Energiemärkten wieder auf über 120 US-Dollar'),
    ('zh/examples.html', '然后在乌克兰危机期间又回到 120 美元以上',
     '随后在地缘政治紧张推高能源市场波动期间又回到 120 美元以上'),
]

JA_OIL_OLD = 'その後ウクライナ危機中に120ドル以上に戻りました'
JA_OIL_NEW = 'その後、地政学リスクによるエネルギー市場の変動期に120ドル以上に戻りました'

ZH_GLOBAL = [
    ('不稳定、不确定、复杂和模糊', '易变、不确定、复杂和模糊'),
    ('波动率', '易变性'),
    ('VUCA 方面 的具体示例', 'VUCA 各维度的具体示例'),
    ('<!-- 波动率示例 -->', '<!-- 易变性示例 -->'),
    ('<!-- 方面 Scores -->', '<!-- 维度得分 -->'),
    ('波动率分析', '易变性分析'),
    ('模棱两可', '模糊'),
    ('你在模棱两可的情况下茁壮成长', '您在模糊环境中表现出色'),
    ('你很好地处理了歧义', '您对模糊性的应对较好'),
    ('你能很好地处理不确定性', '您对不确定性的应对较好'),
    ('不确定性可能对你来说很困难', '不确定性可能是您的挑战'),
    ('复杂性可能会让你不知所措', '复杂性可能令您感到难以应对'),
    ('模糊性可能对你来说是一个挑战', '模糊性可能是您的挑战'),
    ('您对波动表现出中等的适应能力', '您对易变性的适应处于中等水平'),
    ('对不稳定环境的强大适应能力', '对易变环境的强大适应能力'),
    ('The 实践 of 适应性领导', '《适应性领导实践》'),
    ('Thinking in Systems', '《系统思考》'),
    ('Team of Teams', '《团队赋能》'),
    ('The Lean Startup', '《精益创业》'),
    ('Leaders Make the Future', '《领导者创造未来》'),
    ('Antifragile', '《反脆弱》'),
    ('弹力', '反脆弱'),
    ('关于调整组织结构以适应 VUCA 环境的军事课程', '关于在 VUCA 环境中调整组织结构的组织管理实践（源自军事管理研究）'),
    ('军事战略', '组织变革'),
    ('处理歧义的方法', '应对模糊性的方法'),
    ('function reset评估()', 'function resetAssessment()'),
    ('onclick="reset评估()"', 'onclick="resetAssessment()"'),
]

DE_GLOBAL = [
    ('Volatility, Uncertainty, Complexity, and Ambiguity steht',
     'Volatilität, Unsicherheit, Komplexität und Mehrdeutigkeit steht'),
    ('Ursprung im US Army War College', 'Ursprung am U.S. Army War College'),
    ('schnelle politische Änderungen und Veränderungen im Verbraucherverhalten',
     'schnelle regulatorische Anpassungen und Veränderungen im Verbraucherverhalten'),
    ('politische Änderungen</li>', 'regulatorische Anpassungen</li>'),
    ('In-depth guide to the VUCA framework. Learn how to analyze, respond to, and leverage Volatility, Uncertainty, Complexity, and Ambiguity in your organization.',
     'Vertiefender Leitfaden zum VUCA-Framework: Volatilität, Unsicherheit, Komplexität und Mehrdeutigkeit analysieren und nutzen.'),
]


def apply_file(path: Path, pairs: list):
    if not path.exists():
        return False
    text = path.read_text(encoding='utf-8')
    orig = text
    for old, new in pairs:
        text = text.replace(old, new)
    if text != orig:
        path.write_text(text, encoding='utf-8')
        return True
    return False


def main():
    changed = []
    for rel, old, new in REPLACEMENTS:
        p = ROOT / rel
        if apply_file(p, [(old, new)]):
            changed.append(rel)

    ja_ex = ROOT / 'ja/examples.html'
    if apply_file(ja_ex, [(JA_OIL_OLD, JA_OIL_NEW)]):
        changed.append('ja/examples.html')

    for name in ['index.html', 'examples.html', 'framework.html', 'leadership.html',
                 'action-guide.html', 'resources.html', 'assessment.html']:
        p = ROOT / 'zh' / name
        if apply_file(p, ZH_GLOBAL):
            changed.append(f'zh/{name}')

    for name in ['index.html', 'framework.html', 'examples.html']:
        p = ROOT / 'de' / name
        if apply_file(p, DE_GLOBAL):
            changed.append(f'de/{name}')

    print('Updated:', *sorted(set(changed)), sep='\n  ')


if __name__ == '__main__':
    main()
