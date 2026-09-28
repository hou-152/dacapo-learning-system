#!/usr/bin/env python3
"""从概念页双链生成 Mermaid 学习图谱"""
import re
from pathlib import Path
from collections import defaultdict

DACAPO_ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = DACAPO_ROOT / "concepts"
OUTPUT_FILE = DACAPO_ROOT / "CONCEPT-GRAPH.md"

HUB_MIN = 10
MID_MIN = 3

def collect_links(concept_dir: Path):
    """收集所有概念文件中的双链"""
    files = list(concept_dir.glob("*.md"))
    concept_names = {f.stem for f in files}

    indeg = defaultdict(int)
    edges = []

    for file in files:
        name = file.stem
        text = file.read_text(encoding="utf-8")

        # 提取 WikiLink [[概念名]]
        for match in re.findall(r'\[\[([^\]|#]+)', text):
            target = match.strip().split('/')[0]
            # 移除文件扩展名
            target = target.replace('.md', '')

            if target in concept_names and target != name:
                indeg[target] += 1
                edges.append((name, target))

    # 添加没有被引用的概念（入度为 0）
    for name in concept_names:
        if name not in indeg:
            indeg[name] = 0

    return dict(indeg), edges

def generate_graph(indeg: dict) -> str:
    """生成 Mermaid 分层图谱"""
    hub = sorted((n for n in indeg if indeg[n] >= HUB_MIN), key=lambda n: (-indeg[n], n))
    mid = sorted((n for n in indeg if MID_MIN <= indeg[n] < HUB_MIN), key=lambda n: (-indeg[n], n))
    leaf = sorted((n for n in indeg if indeg[n] < MID_MIN), key=lambda n: (-indeg[n], n))

    layers = [
        ('hub', f'枢纽层 · 被 {HUB_MIN} 个以上概念页引用', hub),
        ('mid', f'次级层 · 被引用 {MID_MIN}—{HUB_MIN - 1} 次', mid),
        ('leaf', f'叶子层 · 被引用 {MID_MIN - 1} 次以下', leaf)
    ]

    lines = ['```mermaid', 'graph TD']
    index = 0

    for key, title, nodes in layers:
        if not nodes:
            continue
        lines.append(f'    subgraph {key}["{title}"]')
        lines.append('        direction LR')
        for name in nodes:
            safe_name = name.replace('"', "'").replace('[', '（').replace(']', '）')
            lines.append(f'        n{index}["{safe_name} · {indeg[name]}"]')
            index += 1
        lines.append('    end')

    lines.append('```')
    return '\n'.join(lines)

def main():
    print("=== DaCapo 概念图谱生成 ===\n")

    if not CONCEPT_DIR.exists():
        print(f"❌ 概念目录不存在: {CONCEPT_DIR}")
        return 1

    print(f"📁 扫描目录: {CONCEPT_DIR}")
    indeg, edges = collect_links(CONCEPT_DIR)

    total = len(indeg)
    linked = sum(1 for n in indeg if indeg[n] > 0)

    print(f"✓ 找到 {total} 个概念")
    print(f"✓ 有被引用的概念: {linked} / {total}")
    print(f"✓ 引用关系: {len(edges)} 条\n")

    # 生成统计
    hub_count = sum(1 for v in indeg.values() if v >= HUB_MIN)
    mid_count = sum(1 for v in indeg.values() if MID_MIN <= v < HUB_MIN)
    leaf_count = sum(1 for v in indeg.values() if v < MID_MIN)

    print(f"📊 分层统计:")
    print(f"  - 枢纽层 (≥{HUB_MIN}): {hub_count} 个")
    print(f"  - 次级层 ({MID_MIN}-{HUB_MIN-1}): {mid_count} 个")
    print(f"  - 叶子层 (<{MID_MIN}): {leaf_count} 个\n")

    # 生成图谱
    graph = generate_graph(indeg)

    # 生成完整报告
    content = f"""# DaCapo 概念图谱

**生成时间**: {Path(__file__).stat().st_mtime}
**概念总数**: {total}
**有引用的概念**: {linked} / {total}
**引用关系**: {len(edges)} 条

---

## 概念分层

{graph}

---

## 统计说明

- **枢纽层**: 被 {HUB_MIN} 个以上概念页引用，是核心概念
- **次级层**: 被引用 {MID_MIN}—{HUB_MIN - 1} 次，是重要概念
- **叶子层**: 被引用 {MID_MIN - 1} 次以下，是边缘或独立概念

数字表示该概念被其他概念页引用的次数（入度）。

---

## Top 10 枢纽概念

"""

    # 添加 Top 10
    top10 = sorted(indeg.items(), key=lambda x: (-x[1], x[0]))[:10]
    for i, (name, count) in enumerate(top10, 1):
        content += f"{i}. **{name}** - 被引用 {count} 次\n"

    content += f"\n---\n\n*本图谱由 `scripts/generate_concept_graph.py` 自动生成*\n"

    # 写入文件
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✓ 图谱已生成: {OUTPUT_FILE}\n")

    return 0

if __name__ == "__main__":
    exit(main())
