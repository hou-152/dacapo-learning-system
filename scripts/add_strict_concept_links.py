#!/usr/bin/env python3
"""
使用严格规则重新生成高质量概念关联
只关联明确相关的：姊妹课程、同系列课程
"""
from pathlib import Path
import re
from collections import defaultdict

DACAPO_ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = DACAPO_ROOT / "concepts"
COURSES_DIR = DACAPO_ROOT / "courses"

def extract_frontmatter(content: str) -> dict:
    """提取 frontmatter"""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            fm[key.strip()] = value.strip()
    return fm

def extract_explicit_links(content: str) -> list:
    """提取简介中显式提到的姊妹课程/相关课程"""
    links = []

    # 查找"姊妹课程"
    match = re.search(r'姊妹课程[：:]\s*\[\[(.+?)\]\]', content)
    if match:
        links.append(("姊妹课程", match.group(1)))

    # 查找"参考课程"、"相关课程"等
    patterns = [
        r'参考课程[：:]\s*\[\[(.+?)\]\]',
        r'相关课程[：:]\s*\[\[(.+?)\]\]',
        r'延伸阅读[：:]\s*\[\[(.+?)\]\]',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            links.append(("相关课程", match.group(1)))

    return links

def detect_series(concept_name: str) -> str:
    """检测课程系列（相同前缀或基础名称）"""
    # 移除版本号、日期等后缀
    base = re.sub(r'--[a-f0-9]+$', '', concept_name)  # 移除 hash
    base = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', base)    # 移除日期
    base = re.sub(r'-重学$', '', base)                 # 移除"重学"
    base = re.sub(r'-\d+$', '', base)                   # 移除数字后缀
    base = re.sub(r'\s+\d+$', '', base)                 # 移除空格+数字

    return base

def find_related_concepts(concept_file: Path, all_concepts: dict) -> list:
    """为单个概念找到相关概念（严格规则）"""
    content = concept_file.read_text(encoding="utf-8")
    concept_name = concept_file.stem

    related = []
    reasons = defaultdict(set)

    # 规则 1: 简介中显式提到的姊妹/相关课程
    explicit_links = extract_explicit_links(content)
    for link_type, target in explicit_links:
        if target in all_concepts:
            related.append(target)
            reasons[target].add(f"显式链接({link_type})")

    # 规则 2: 同系列课程（严格匹配）
    series = detect_series(concept_name)
    if series != concept_name:  # 确实是系列的一部分
        for other_name in all_concepts:
            if other_name == concept_name:
                continue
            other_series = detect_series(other_name)
            if other_series == series:
                related.append(other_name)
                reasons[other_name].add(f"同系列({series})")

    # 去重并排序
    related = sorted(set(related))

    return related, reasons

def add_related_section(concept_file: Path, related: list):
    """添加"相关概念"部分到文件末尾"""
    if not related:
        return False

    content = concept_file.read_text(encoding="utf-8")

    # 如果已有"相关概念"部分，先删除
    content = re.sub(r'\n## 相关概念\n\n(?:- \[\[.+?\]\]\n)+', '', content)

    # 添加新的"相关概念"部分
    content = content.rstrip() + '\n\n## 相关概念\n\n'
    for concept in related:
        content += f'- [[{concept}]]\n'

    concept_file.write_text(content, encoding="utf-8")
    return True

def main():
    print("=== 使用严格规则重新生成概念关联 ===\n")
    print("规则:")
    print("  1. 简介中显式提到的姊妹/相关课程")
    print("  2. 同系列课程（如实所现系列、ABB题库系列）\n")

    # 收集所有概念
    concept_files = sorted(CONCEPT_DIR.glob("*.md"))
    all_concepts = {f.stem: f for f in concept_files}

    print(f"找到 {len(all_concepts)} 个概念\n")

    # 为每个概念生成关联
    total_links = 0
    concepts_with_links = 0

    link_summary = []

    for concept_file in concept_files:
        related, reasons = find_related_concepts(concept_file, all_concepts)

        if related:
            add_related_section(concept_file, related)
            print(f"✓ {concept_file.stem}: {len(related)} 个相关概念")
            for target in related:
                reason_str = ", ".join(reasons[target])
                print(f"    → {target} ({reason_str})")

            total_links += len(related)
            concepts_with_links += 1
            link_summary.append((concept_file.stem, len(related)))

    print(f"\n=== 完成 ===")
    print(f"有关联的概念: {concepts_with_links} / {len(all_concepts)}")
    print(f"总关联数: {total_links} 条")
    print(f"平均每个概念: {total_links/concepts_with_links:.1f} 条" if concepts_with_links > 0 else "")

    # Top 概念
    if link_summary:
        print(f"\n关联最多的概念:")
        for name, count in sorted(link_summary, key=lambda x: -x[1])[:5]:
            print(f"  - {name}: {count} 条")

if __name__ == "__main__":
    main()
