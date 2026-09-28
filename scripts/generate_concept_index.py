#!/usr/bin/env python3
"""
生成概念索引 INDEX.md
"""

import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/housibo/Documents/dacapo-学习仓库")
CONCEPTS_DIR = BASE_DIR / "concepts" / "core"
OUTPUT_FILE = BASE_DIR / "concepts" / "INDEX.md"

def collect_concepts():
    """收集所有概念及其元数据"""
    concepts = []

    # 收集入度统计
    indeg = defaultdict(int)
    concept_names = set()

    # 第一遍：收集所有概念名
    for filepath in CONCEPTS_DIR.glob("*.md"):
        concept_names.add(filepath.stem)

    # 第二遍：统计入度
    for filepath in CONCEPTS_DIR.glob("*.md"):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取所有双链
        for match in re.findall(r'\[\[([^\]|#]+)', content):
            target = match.strip().split('/')[0].replace('.md', '')
            if target in concept_names and target != filepath.stem:
                indeg[target] += 1

    # 第三遍：收集完整信息
    for filepath in sorted(CONCEPTS_DIR.glob("*.md")):
        name = filepath.stem

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取定义
        definition_match = re.search(r'## 定义\s*\n\s*(.+?)(?:\n\n|\n##|$)', content, re.DOTALL)
        definition = definition_match.group(1).strip() if definition_match else ""

        # 提取首次出现
        first_match = re.search(r'## 首次出现\s*\n\s*(.+?)(?:\n\n|\n##|$)', content, re.DOTALL)
        first_appearance = first_match.group(1).strip() if first_match else ""

        # 提取相关概念数量
        related_matches = re.findall(r'- \[\[([^\]]+)\]\]', content)
        related_count = len(related_matches)

        concepts.append({
            'name': name,
            'definition': definition,
            'first_appearance': first_appearance,
            'inDegree': indeg.get(name, 0),
            'related_count': related_count
        })

    return concepts

def generate_index(concepts):
    """生成索引内容"""

    # 按字母排序
    concepts_sorted = sorted(concepts, key=lambda x: x['name'])

    # 按入度分类
    hub = [c for c in concepts if c['inDegree'] >= 10]
    mid = [c for c in concepts if 3 <= c['inDegree'] < 10]
    leaf = [c for c in concepts if c['inDegree'] < 3]

    content = f"""# 概念索引

**概念总数**: {len(concepts)}
**生成时间**: 自动生成

---

## 📊 统计概览

- **枢纽概念** (入度 ≥10): {len(hub)} 个
- **次级概念** (入度 3-9): {len(mid)} 个
- **叶子概念** (入度 <3): {len(leaf)} 个

---

## 🔤 按字母顺序

"""

    # 按首字母分组
    by_initial = defaultdict(list)
    for c in concepts_sorted:
        initial = c['name'][0].upper()
        # 处理中文首字符
        if '一' <= initial <= '鿿':
            initial = '中文'
        elif not initial.isalpha():
            initial = '#'
        by_initial[initial].append(c)

    for initial in sorted(by_initial.keys()):
        content += f"\n### {initial}\n\n"
        for c in by_initial[initial]:
            indent_label = ""
            if c['inDegree'] >= 10:
                indent_label = "🔴"
            elif c['inDegree'] >= 3:
                indent_label = "🟡"
            else:
                indent_label = "⚪"

            content += f"- {indent_label} [[{c['name']}]] (入度: {c['inDegree']}, 关联: {c['related_count']})\n"
            if c['definition']:
                # 只显示定义的前50字
                short_def = c['definition'][:50] + "..." if len(c['definition']) > 50 else c['definition']
                content += f"  > {short_def}\n"

    content += "\n---\n\n## 🏆 Top 20 核心概念\n\n"
    content += "按入度（被引用次数）排序：\n\n"

    top20 = sorted(concepts, key=lambda x: (-x['inDegree'], x['name']))[:20]
    for i, c in enumerate(top20, 1):
        content += f"{i}. **[[{c['name']}]]** - 入度: {c['inDegree']}, 关联: {c['related_count']}\n"

    content += "\n---\n\n## 📝 说明\n\n"
    content += "- **入度**: 该概念被其他概念引用的次数\n"
    content += "- **关联**: 该概念主动引用的其他概念数量\n"
    content += "- **🔴 枢纽概念**: 入度 ≥10，是学习体系的核心\n"
    content += "- **🟡 次级概念**: 入度 3-9，是重要概念\n"
    content += "- **⚪ 叶子概念**: 入度 <3，是独立或新兴概念\n"
    content += "\n---\n\n*本索引由 `scripts/generate_concept_index.py` 自动生成*\n"

    return content

def main():
    print("=== 生成概念索引 ===\n")

    print(f"📁 扫描目录: {CONCEPTS_DIR}")
    concepts = collect_concepts()

    print(f"✅ 收集到 {len(concepts)} 个概念")

    content = generate_index(concepts)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 索引已生成: {OUTPUT_FILE}\n")

    # 统计信息
    total_indegree = sum(c['inDegree'] for c in concepts)
    total_relations = sum(c['related_count'] for c in concepts)

    print(f"📊 统计:")
    print(f"  - 总入度: {total_indegree}")
    print(f"  - 总关联数: {total_relations}")
    print(f"  - 平均入度: {total_indegree / len(concepts):.2f}")
    print(f"  - 平均关联数: {total_relations / len(concepts):.2f}")

if __name__ == "__main__":
    main()
