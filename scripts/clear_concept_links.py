#!/usr/bin/env python3
"""
清空所有自动生成的概念关联
为重新生成高质量关联做准备
"""
from pathlib import Path
import re

DACAPO_ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = DACAPO_ROOT / "concepts"

def remove_related_concepts(concept_file: Path):
    """删除概念文件中的"相关概念"部分"""
    content = concept_file.read_text(encoding="utf-8")

    # 查找"相关概念"部分（从标题到文件末尾或下一个二级标题）
    pattern = r'\n## 相关概念\n\n(?:- \[\[.+?\]\]\n)+'

    match = re.search(pattern, content)
    if not match:
        return False

    # 删除该部分
    new_content = content[:match.start()] + content[match.end():]

    # 如果末尾有多余空行，清理一下
    new_content = new_content.rstrip() + '\n'

    concept_file.write_text(new_content, encoding="utf-8")
    return True

def main():
    print("=== 清空概念关联 ===\n")
    print("⚠️  即将删除所有自动生成的概念关联\n")

    concept_files = sorted(CONCEPT_DIR.glob("*.md"))

    removed = 0
    skipped = 0

    for concept_file in concept_files:
        if remove_related_concepts(concept_file):
            print(f"✓ {concept_file.stem}")
            removed += 1
        else:
            skipped += 1

    print(f"\n=== 完成 ===")
    print(f"清空: {removed} 个概念文件")
    print(f"跳过: {skipped} 个（无关联或已清空）")
    print(f"\n下一步: 使用更严格的规则重新生成关联")

if __name__ == "__main__":
    main()
